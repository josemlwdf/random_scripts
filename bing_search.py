#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import re
from html import unescape
from html.parser import HTMLParser
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

REQUEST_TIMEOUT = 10.0
NUM_RESULTS = 5
DEBUG_LOGGING = True
BING_LANGUAGE = "en"
BING_COUNTRY = "us"
BING_MARKET = "en-US"
BING_SAFESEARCH = "strict"

LOGGER = logging.getLogger("bing_search")

ENGLISH_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "best", "browse", "by", "for", "from",
    "gear", "in", "is", "it", "latest", "men", "new", "of", "on", "or", "our", "shop",
    "shoes", "sport", "style", "styles", "the", "to", "training", "us", "wear", "with",
    "women", "your",
}


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._ignored_tag_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        _ = attrs
        if tag in {"script", "style", "noscript"}:
            self._ignored_tag_stack.append(tag)
        elif tag in {"br", "p", "div", "li", "section", "article", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._ignored_tag_stack and tag == self._ignored_tag_stack[-1]:
            self._ignored_tag_stack.pop()
        elif tag in {"p", "div", "li", "section", "article", "h1", "h2", "h3"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignored_tag_stack:
            return
        text = " ".join(data.split())
        if text:
            self._chunks.append(text)

    def get_text(self) -> str:
        lines: list[str] = []
        for raw_line in "".join(self._chunks).splitlines():
            line = normalize_whitespace(raw_line)
            if line:
                lines.append(line)
        return "\n".join(lines)


def normalize_whitespace(value: str) -> str:
    return " ".join(unescape(value).split())


def configure_logging() -> None:
    level = logging.DEBUG if DEBUG_LOGGING else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        force=True,
    )


def log_http_error(exc: HTTPError, label: str) -> None:
    LOGGER.error("%s failed with HTTP %s %s", label, exc.code, exc.reason)
    LOGGER.debug("%s error URL: %s", label, exc.url)
    LOGGER.debug("%s error headers: %s", label, dict(exc.headers.items()))

    try:
        body_bytes = exc.read()
    except Exception as read_error:  # pragma: no cover - defensive logging
        LOGGER.exception("%s error body could not be read: %s", label, read_error)
        return

    if not body_bytes:
        LOGGER.debug("%s error body: <empty>", label)
        return

    charset = exc.headers.get_content_charset() or "utf-8"
    body_text = body_bytes.decode(charset, errors="replace")
    LOGGER.debug("%s error body (%s bytes): %s", label, len(body_bytes), body_text)

    try:
        parsed = json.loads(body_text)
    except json.JSONDecodeError:
        LOGGER.debug("%s error body is not JSON.", label)
        return

    LOGGER.error("%s parsed error JSON: %s", label, json.dumps(parsed, indent=2))


def build_bing_search_url(query: str, num_results: int = NUM_RESULTS) -> str:
    params = {
        "q": f"{query}",
        "count": max(1, min(num_results, 50)),
        "format": "rss",
        "setlang": BING_LANGUAGE,
        "cc": BING_COUNTRY,
        "mkt": BING_MARKET,
        "adlt": BING_SAFESEARCH,
    }
    return f"https://www.bing.com/search?{urlencode(params)}"


def strip_html_to_text(html: str) -> str:
    LOGGER.debug("Stripping HTML to text. Input size=%s bytes", len(html))
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    extractor.close()
    text = extractor.get_text()
    LOGGER.debug(
        "HTML stripped successfully. Output size=%s chars, lines=%s",
        len(text),
        len(text.splitlines()),
    )
    return text


def parse_bing_rss(xml_text: str, max_results: int = NUM_RESULTS) -> list[dict[str, str]]:
    LOGGER.debug("Parsing Bing RSS response. Input size=%s bytes", len(xml_text))
    root = ET.fromstring(xml_text)
    results: list[dict[str, str]] = []

    for item in root.findall("./channel/item")[:max_results]:
        title = normalize_whitespace(item.findtext("title", default=""))
        snippet = strip_html_to_text(item.findtext("description", default=""))
        link = normalize_whitespace(item.findtext("link", default=""))
        if title or snippet or link:
            results.append(
                {
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                }
            )

    LOGGER.debug("Bing RSS items parsed=%s", len(results))
    return results


def is_likely_english(text: str) -> bool:
    normalized = normalize_whitespace(text)
    if not normalized:
        return False

    non_latin_chars = sum(
        1
        for char in normalized
        if (
            "\u4e00" <= char <= "\u9fff"
            or "\u3040" <= char <= "\u30ff"
            or "\uac00" <= char <= "\ud7af"
            or "\u0400" <= char <= "\u04ff"
            or "\u0600" <= char <= "\u06ff"
        )
    )
    if non_latin_chars:
        return False

    words = re.findall(r"[A-Za-z']+", normalized.lower())
    if not words:
        return False

    stopword_hits = sum(1 for word in words if word in ENGLISH_STOPWORDS)
    ascii_letters = sum(1 for char in normalized if char.isascii() and char.isalpha())
    all_letters = sum(1 for char in normalized if char.isalpha())
    ascii_ratio = ascii_letters / all_letters if all_letters else 0.0
    stopword_ratio = stopword_hits / len(words)
    return ascii_ratio >= 0.85 and (stopword_hits >= 2 or stopword_ratio >= 0.08)


def filter_english_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    english_results: list[dict[str, str]] = []
    for index, result in enumerate(results, start=1):
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        keep = is_likely_english(text)
        LOGGER.debug("Result %s english_match=%s title=%r", index, keep, result.get("title", ""))
        if keep:
            english_results.append(result)
    LOGGER.debug("English results kept=%s of %s", len(english_results), len(results))
    return english_results


def format_bing_results(results: list[dict[str, str]]) -> str:
    LOGGER.debug("Formatting %s Bing results into plain text", len(results))
    lines = ["Bing English search results", ""]
    for index, result in enumerate(results, start=1):
        lines.append(f"Result {index}")
        if result.get("title"):
            lines.append(f"Title: {result['title']}")
        if result.get("snippet"):
            lines.append(f"Snippet: {result['snippet']}")
        if result.get("link"):
            lines.append(f"Link: {result['link']}")
        lines.append("")
    return "\n".join(lines).strip()


def fetch_bing_search_text(query: str, timeout: float = REQUEST_TIMEOUT) -> str:
    url = build_bing_search_url(query, num_results=NUM_RESULTS)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    LOGGER.debug("Preparing Bing search request.")
    LOGGER.debug("Bing URL: %s", url)
    LOGGER.debug("Bing headers: %s", headers)
    LOGGER.debug("Bing timeout: %ss", timeout)
    request = Request(url, headers=headers)

    with urlopen(request, timeout=timeout) as response:
        LOGGER.debug("Bing response status: %s", getattr(response, "status", "unknown"))
        LOGGER.debug("Bing response URL: %s", response.geturl())
        LOGGER.debug("Bing response headers: %s", dict(response.headers.items()))
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read()
        LOGGER.debug("Bing raw response size: %s bytes", len(body))
        xml_text = body.decode(charset, errors="replace")
        LOGGER.debug("Bing decoded charset: %s", charset)

    results = parse_bing_rss(xml_text, max_results=NUM_RESULTS)
    english_results = filter_english_results(results)
    if english_results:
        return format_bing_results(english_results)
    if results:
        LOGGER.warning("Bing returned results, but none looked English after filtering.")
        return "No English Bing results were found for this query."

    LOGGER.warning("No Bing RSS items were parsed. Falling back to visible text extraction.")
    return strip_html_to_text(xml_text)


def main() -> int:
    configure_logging()
    query = " ".join(sys.argv[1:]).strip()
    LOGGER.debug("Script started. argv=%s", sys.argv)

    if not query:
        LOGGER.error("No query provided.")
        print("Usage: python3 bing_search.py your search query", file=sys.stderr)
        return 1

    LOGGER.debug("Query received: %r", query)
    LOGGER.debug(
        "Current config: timeout=%ss num_results=%s language=%s country=%s market=%s safesearch=%s",
        REQUEST_TIMEOUT,
        NUM_RESULTS,
        BING_LANGUAGE,
        BING_COUNTRY,
        BING_MARKET,
        BING_SAFESEARCH,
    )

    try:
        text = fetch_bing_search_text(query, timeout=REQUEST_TIMEOUT)
    except HTTPError as exc:
        log_http_error(exc, "Bing request")
        print(f"Bing returned HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        return 1
    except URLError as exc:
        LOGGER.exception("Network error while querying Bing.")
        print(f"Network error while querying Bing: {exc.reason}", file=sys.stderr)
        return 1
    except Exception:
        LOGGER.exception("Unexpected failure while running the search script.")
        raise

    if not text:
        LOGGER.error("The script completed but produced no text.")
        print("No visible text was extracted from the Bing response.", file=sys.stderr)
        return 1

    LOGGER.debug("Search completed successfully. Output length=%s chars", len(text))
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
