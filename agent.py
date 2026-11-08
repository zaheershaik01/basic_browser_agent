from playwright.sync_api import sync_playwright
import ollama, json

MODEL = "qwen2.5:7b"

# (start URL, goal) - the first site that loads will be used
SITES = [
    ("https://www.bing.com",
     "Search for 'best laptops 2026 with 16GB RAM, 512 SSD, Brand: HP, under 1 lakh rupees' and tell me the title of the top result"),
    ("https://www.google.com",
     "Search for 'best laptops 2026 with 16GB RAM, 512 SSD, Brand: HP, under 1 lakh rupees' and tell me the title of the top result"),
    ("https://en.wikipedia.org",
     "Search for 'Python programming language' and tell me the first sentence of the article"),
]

def get_elements(page):
    """Number every visible input, button, and link (inputs first)."""
    return page.evaluate("""() => {
        const out = [];
        const add = (el) => {
            const r = el.getBoundingClientRect();
            if (r.width > 0 && r.height > 0 && !el.hasAttribute('data-ai-id')) {
                el.setAttribute('data-ai-id', out.length);
                const label = (el.innerText || el.placeholder || el.value
                               || el.ariaLabel || el.name || '').trim().slice(0, 60);
                out.push(out.length + ': <' + el.tagName.toLowerCase() + '> ' + label);
            }
        };
        document.querySelectorAll('input, textarea').forEach(add);
        document.querySelectorAll('button, a').forEach(add);
        return out.slice(0, 60);
    }""")

def ask_model(prompt):
    for _ in range(3):  # retry if the model returns bad JSON
        try:
            reply = ollama.chat(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                format="json",
            )
            return json.loads(reply["message"]["content"])
        except Exception as e:
            print("Model reply problem, retrying:", e)
    return {"action": "done", "answer": "Model failed to give a valid action."}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Find the first site that actually opens
    goal = None
    for url, site_goal in SITES:
        try:
            print("Trying", url, "...")
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            goal = site_goal
            print("Opened", url)
            break
        except Exception as e:
            print("Could not open", url, "-", str(e).splitlines()[0])

    if goal is None:
        print("\nNo site could be opened. Check your internet/VPN/DNS (see notes).")
        browser.close()
        raise SystemExit(1)

    history = []

    for step in range(10):  # step limit for safety
        page.wait_for_timeout(2000)
        elements = get_elements(page)
        page_text = page.inner_text("body")[:2000]

        prompt = f"""You control a web browser. Goal: {goal}

Actions so far: {history}
Current URL: {page.url}

Clickable/typeable elements:
{chr(10).join(elements)}

Visible page text:
{page_text}

Choose ONE next action. Reply ONLY with JSON in one of these forms:
{{"action": "type", "id": 3, "text": "what to type"}}
{{"action": "click", "id": 5}}
{{"action": "done", "answer": "your final answer"}}"""

        act = ask_model(prompt)
        print(f"Step {step + 1}:", act)
        history.append(act)

        try:
            if act["action"] == "done":
                print("\nANSWER:", act["answer"])
                break
            elif act["action"] == "click":
                page.locator(f'[data-ai-id="{act["id"]}"]').first.click(timeout=8000)
            elif act["action"] == "type":
                box = page.locator(f'[data-ai-id="{act["id"]}"]').first
                box.fill(act["text"], timeout=8000)
                box.press("Enter")
        except Exception as e:
            print("Action failed:", str(e).splitlines()[0])
            history.append({"error": "that action failed, try another element"})

    browser.close()