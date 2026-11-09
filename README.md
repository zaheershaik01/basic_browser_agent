# Basic Browser Agent

A beginner-friendly Python project that demonstrates browser automation using local LLMs and Playwright. The repository includes a simple browser agent that can navigate websites, interact with page elements, and a laptop search script that filters results from shopping sites and saves them as CSV.

## Project overview

This repository was built to explore how a browser can be controlled by a local language model such as Ollama-hosted Llama 3.2 or Qwen 2.5. It is intentionally simple and educational, with scripts designed for experimentation and learning rather than production use.

## Included scripts

### 1. `agent.py`
This script uses Playwright to open a website and then asks a local Ollama model to decide the next browser action.

Features:
- Opens a supported site such as Bing or Google
- Finds visible page elements like buttons, links, and inputs
- Sends the current page text and element list to a local model
- Chooses one of:
  - click
  - type
  - done
- Uses `ollama.chat()` with `qwen2.5:7b`

Example action flow:
- Browser opens a page
- Script extracts visible elements
- Model decides what to click or type
- Script performs the action
- Loop continues until the model decides the task is complete

### 2. `laptop_finder.py`
This script searches for a laptop based on a hardcoded specification and checks products from Amazon, Flipkart, and Bing.

It:
- Searches for "HP laptop 12th Gen Intel Core i5 16GB RAM 512GB SSD"
- Scrapes product cards from Amazon and Flipkart
- Tries Bing when the shopping sites yield little or no data
- Scores results against key specs such as:
  - brand
  - RAM
  - CPU generation
  - storage
- Saves the best matches to `results.csv`

### 3. `bu_agent (1).py`
This is a simpler browser-use example using the `browser_use` package and `ChatOllama`.

It:
- Connects to Ollama with `llama3.2`
- Uses a browser agent to search Bing for a laptop query
- Reads the first 5 non-sponsored results
- Prints the product name, price (if shown), and link

## Quick start

### Prerequisites
- Python 3.9+
- Ollama installed and running locally
- A browser supported by Playwright

### Install dependencies

```bash
pip install browser-use playwright ollama
python -m playwright install chromium
```

### Pull a local model

```bash
ollama pull llama3.2
ollama pull qwen2.5:7b
```

### Run the browser agent

```bash
python agent.py
```

### Run the laptop search script

```bash
python laptop_finder.py
```

### Run the browser-use example

```bash
python "bu_agent (1).py"
```

## Notes

- Several scripts open a real browser window (`headless=False`) so the actions can be watched live.
- The scripts depend heavily on internet access and current website HTML structure.
- Web pages can change over time, so selectors and scraping logic may need adjustments.
- This project is best suited for learning and experimentation rather than production-grade automation.

## Example outputs

The script `laptop_finder.py` writes matched results to `results.csv`, which contains columns like:

- site
- title
- price
- link
- score

## Repository structure

```text
basic_browser_agent/
├── agent.py
├── bu_agent (1).py
├── laptop_finder.py
├── results.csv
└── README.md
```

## License

No explicit license file is included in this repository. If you plan to reuse or share the code, confirm the licensing terms before publishing or distributing it.

## Summary

This repository is a practical introduction to AI-assisted browser automation with local models. It combines Playwright-based browser control, Ollama model inference, and basic web scraping to create an approachable project for learning how browser agents and automated product search workflows can work together.
