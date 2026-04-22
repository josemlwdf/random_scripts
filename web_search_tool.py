#!/usr/bin/env python3
"""Web search tool using DuckDuckGo Lite HTML with robust attribute parsing."""

import html
import json
import re
import ssl
import sys
import time
from urllib.parse import quote_plus, unquote
from urllib.request import Request, urlopen

REQUEST_TIMEOUT = 15.0
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── Subject-aware query optimization ──────────────────────────────────

SUBJECT_MODIFIERS = [
    ({"recipe", "cooking", "bake", "food", "pasta", "soup", "cake", "salad", "grill",
      "roast", "ingredient", "dish", "cuisine", "cook", "meal", "dinner", "lunch",
      "breakfast", "appetizer", "dessert"}, "recipe"),
    ({"github", "repo", "repository", "boilerplate", "template", "open source",
      "framework", "npm package", "pip install"}, "site:github.com"),
    ({"zero day", "cve", "vulnerability", "exploit", "malware", "ransomware",
      "penetration test", "pentest", "cybersecurity", "infosec", "firewall", "patch",
      "security advisory", "breach"}, "cybersecurity"),
    ({"python", "pypi", "pip install", "django", "flask", "fastapi", "numpy", "pandas",
      "python3", "conda"}, "python"),
    ({"album", "song", "band", "artist", "music", "lyrics", "discography", "single",
      "track", "vinyl", "spotify", "concert", "genre"}, "music"),
    ({"things to do", "visit", "travel", "tourism", "hotel", "flight", "itinerary",
      "attractions", "sightseeing", "vacation", "trip", "destination", "landmark",
      "museum", "guide"}, "travel guide"),
    ({"theorem", "proof", "equation", "formula", "eigenvalue", "matrix", "calculus",
      "algebra", "topology", "integral", "derivative", "mathematics", "math",
      "linear algebra", "statistics", "probability", "geometry"}, "mathematics"),
    ({"rtx", "gtx", "gpu", "cpu", "benchmark", "review", "specs", "ram", "ssd",
      "motherboard", "processor", "graphics card", "hardware", "laptop review",
      "phone review", "performance"}, "review benchmarks"),
    ({"treatment", "symptoms", "diagnosis", "medical", "health", "disease", "therapy",
      "drug", "medication", "clinical", "patient", "hypertension", "diabetes",
      "cancer", "vaccine", "prescription"}, "health medical"),
]


def optimize_query(query: str) -> str:
    ql = query.lower()
    for keywords, modifier in SUBJECT_MODIFIERS:
        if any(kw in ql for kw in keywords):
            # Avoid appending if the modifier is already in the query
            if modifier not in ql:
                return f"{query} {modifier}"
    return query

# ── DDG Lite HTML scraping ────────────────────────────────────────────

def _fetch(url: str) -> str:
    ctx = ssl._create_unverified_context()
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=REQUEST_TIMEOUT, context=ctx) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")

def parse_results(page: str) -> list:
    results = []
    
    # 1. Extract result blocks. In DDG Lite, results are often in <tr> or specific <table> rows.
    # We look for the <a> tag with class "result-link" specifically.
    # This regex finds the entire <a> tag regardless of attribute order.
    link_tags = re.findall(r'<a[^>]+class=["\']result-link["\'][^>]*>.*?</a>', page, re.DOTALL)
    
    # 2. Extract snippets. Snippets follow the link in a <td> with class "result-snippet".
    snippets = re.findall(r'<td[^>]+class=["\']result-snippet["\'][^>]*>(.*?)</td>', page, re.DOTALL)
    
    for i, tag in enumerate(link_tags[:10]):
        # Extract href
        href_match = re.search(r'href=["\']([^"\']+)["\']', tag)
        link = href_match.group(1) if href_match else ""
        
        # Extract Title (text inside the <a> tag)
        title = re.sub(r'<[^>]+>', '', tag).strip()
        title = html.unescape(title)
        
        # Clean DDG internal redirects
        if "uddg=" in link:
            link = link.split("uddg=")[1].split("&")[0]
            link = unquote(link)
        elif link.startswith("/"):
            link = f"https://duckduckgo.com{link}"

        snippet = ""
        if i < len(snippets):
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            snippet = html.unescape(snippet)
        
        if title:
            results.append({"title": title, "snippet": snippet, "link": link})
    
    return results

def search(query: str) -> list:
    if not query.strip():
        return []
    
    optimized = optimize_query(query)
    # Using the 'lite' endpoint specifically as requested
    url = f"https://lite.duckduckgo.com/lite/?q={quote_plus(optimized)}"
    
    try:
        page = _fetch(url)
        # Check if we got hit by a bot detection page
        if "ddg-captcha" in page or "Action Forbidden" in page:
            return [{"error": "Rate limited or bot detection triggered by DuckDuckGo."}]
            
        results = parse_results(page)
        for r in results:
            r["_optimized_query"] = optimized
        return results
    except Exception as e:
        return [{"error": f"Request failed: {str(e)}"}]

def main():
    if len(sys.argv) < 2:
        print("Usage: python web_search_tool.py 'your query'")
        sys.exit(1)

    raw_input = " ".join(sys.argv[1:])
    try:
        queries = json.loads(raw_input) if raw_input.startswith("[") else [raw_input]
    except (json.JSONDecodeError, ValueError):
        queries = [raw_input]

    all_data = {}
    for q in queries[:10]:
        all_data[q] = search(q)
        if len(queries) > 1:
            time.sleep(2.0) # Increased delay to be safer

    for q, results in all_data.items():
        print(f"\n🔍 {q}")
        print("─" * 60)
        if not results:
            print("  No results found. (The structure might have changed or query was blocked)")
            continue
            
        for i, r in enumerate(results, 1):
            if "error" in r:
                print(f"  ❌ Error: {r['error']}")
                continue
            print(f"  {i}. {r.get('title', 'No title')}")
            if r.get("snippet"):
                print(f"     {r['snippet'][:200]}")
            print(f"     🔗 {r.get('link', 'No link')}")
            print()

if __name__ == "__main__":
    main()
