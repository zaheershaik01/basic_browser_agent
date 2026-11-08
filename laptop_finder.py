import re, csv
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright

# ---------- EDIT YOUR SPECS HERE ----------
QUERY = "HP laptop 12th Gen Intel Core i5 16GB RAM 512GB SSD"

PATTERNS = {                      # every result is checked against these
    "brand":      r"\bHP\b",
    "ram":        r"\b16\s*GB\b",
    "generation": r"12th\s*Gen|\bi5[- ]?12\d{2,3}",
    "cpu":        r"\bi5\b",
    "storage":    r"\b512\s*GB\b",
}
HEADLESS = False                  # True = no visible window, a bit faster
# ------------------------------------------

def find_price(text):
    m = re.search(r"₹\s?[\d,]+", text)
    return m.group(0) if m else ""

def scrape_amazon(page):
    page.goto(f"https://www.amazon.in/s?k={quote_plus(QUERY)}",
              timeout=30000, wait_until="domcontentloaded")
    if page.locator("input#captchacharacters").count():
        print("  Amazon showed a CAPTCHA, skipping.")
        return []
    cards_sel = 'div[data-component-type="s-search-result"]'
    try:
        page.wait_for_selector(cards_sel, timeout=10000)
    except Exception:
        return []
    out = []
    for card in page.locator(cards_sel).all():
        try:
            title = card.locator("h2").first.inner_text().strip()
            link = card.locator("h2 a, a:has(h2)").first.get_attribute("href") or ""
            if link.startswith("/"):
                link = "https://www.amazon.in" + link
            price = ""
            if card.locator("span.a-price-whole").count():
                price = "₹" + card.locator("span.a-price-whole").first.inner_text().strip()
            out.append({"site": "Amazon.in", "title": title, "text": title,
                        "price": price, "link": link})
        except Exception:
            continue
    return out

def scrape_flipkart(page):
    page.goto(f"https://www.flipkart.com/search?q={quote_plus(QUERY)}",
              timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    page.mouse.wheel(0, 3000)               # scroll so lazy cards load
    page.wait_for_timeout(1200)
    out, seen = [], set()
    for a in page.locator('a[href*="/p/"]').all():
        try:
            href = a.get_attribute("href") or ""
            text = a.inner_text().strip()
            if href in seen or len(text) < 25:
                continue
            seen.add(href)
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            title = next((l for l in lines if len(l) > 15 and "₹" not in l), lines[0])
            out.append({"site": "Flipkart", "title": title, "text": text,
                        "price": find_price(text),
                        "link": "https://www.flipkart.com" + href})
        except Exception:
            continue
    return out

def scrape_bing(page):
    page.goto(f"https://www.bing.com/search?q={quote_plus(QUERY)}",
              timeout=30000, wait_until="domcontentloaded")
    out = []
    for r in page.locator("li.b_algo").all():
        try:
            title = r.locator("h2").first.inner_text().strip()
            link = r.locator("h2 a").first.get_attribute("href") or ""
            snippet = r.inner_text()
            out.append({"site": "Bing", "title": title, "text": title + " " + snippet,
                        "price": find_price(snippet), "link": link})
        except Exception:
            continue
    return out

def score(item):
    """How many of the 5 specs does this result match?"""
    return sum(bool(re.search(p, item["text"], re.I)) for p in PATTERNS.values())

with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS)
    context = browser.new_context(locale="en-IN")
    context.route("**/*.{png,jpg,jpeg,gif,webp,svg,woff,woff2}", lambda r: r.abort())
    page = context.new_page()

    results = []
    for name, fn in [("Amazon.in", scrape_amazon), ("Flipkart", scrape_flipkart)]:
        print(f"Searching {name} ...")
        try:
            found = fn(page)
        except Exception as e:
            print("  Failed:", str(e).splitlines()[0])
            found = []
        print(f"  {len(found)} products read")
        results += found

    if not results:
        print("Shopping sites gave nothing, trying Bing ...")
        try:
            results = scrape_bing(page)
            print(f"  {len(results)} results read")
        except Exception as e:
            print("  Failed:", str(e).splitlines()[0])

    browser.close()

# ---------- filter and show ----------
for r in results:
    r["score"] = score(r)

exact = [r for r in results if r["score"] == len(PATTERNS)]
near = [r for r in results if r["score"] == len(PATTERNS) - 1]
shown = exact if exact else near
label = "EXACT MATCHES (all 5 specs)" if exact else "CLOSE MATCHES (4 of 5 specs; no exact match found)"

print(f"\n===== {label}: {len(shown)} =====")
for i, r in enumerate(shown, 1):
    print(f"\n{i}. [{r['site']}] {r['title'][:150]}")
    print(f"   Price: {r['price'] or 'n/a'}")
    print(f"   Link:  {r['link'][:120]}")

if shown:
    with open("results.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["site", "title", "price", "link", "score"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(shown)
    print("\nSaved to results.csv")
else:
    print("No matching laptops found.")