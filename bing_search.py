#!/usr/bin/env python3
"""Improved Bing search script with query rewriting, English filtering, and smarter ranking."""

import html
from html.parser import HTMLParser
from itertools import combinations
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

REQUEST_TIMEOUT = 10.0
NUM_RESULTS = 10
MAX_FETCH_MULTIPLIER = 4  # fetch extra results to allow filtering/reranking

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

ENGLISH_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "is", "are", "was", "were", "be", "been", "have", "has",
    "by", "from", "as", "if", "will", "can", "that", "this", "it", "not",
    "no", "yes", "how", "what", "when", "where", "why", "which", "do", "does",
    "did", "about", "after", "before", "more", "most", "new", "one", "two",
    "first", "last", "other", "some", "any", "many", "much", "only", "also",
    "very", "today", "yesterday", "tomorrow", "who", "whom", "whose", "there",
    "here", "up", "down", "out", "off", "over", "under", "between", "through",
    "during", "while", "since", "until", "than", "because", "so", "into",
    "via",
}

DOC_SIGNAL_WORDS = {
    "documentation", "docs", "doc", "readme", "guide", "reference", "manual",
    "api", "wiki", "help", "examples", "tutorial"
}

DOC_SIGNAL_DOMAINS = {
    "github.com",
    "gitlab.com",
    "hexdocs.pm",
    "learn.microsoft.com",
    "npmjs.com",
    "nuget.org",
    "pkg.go.dev",
    "pypi.org",
    "rdoc.info",
    "readthedocs.io",
    "rubydoc.info",
    "docs.python.org",
    "developer.mozilla.org",
}

DOC_SIGNAL_DOMAIN_PREFIXES = (
    "api.",
    "developer.",
    "docs.",
    "learn.",
)

QUERY_TERM_RE = re.compile(
    r"\.?[a-z0-9]+(?:[.+#:/_-][a-z0-9]+)*(?:[+#]+)?",
    flags=re.IGNORECASE,
)
SEARCH_OPERATOR_PREFIX_RE = re.compile(
    r"^(?:intitle|intext|inbody|inurl|site|filetype|ext):",
    flags=re.IGNORECASE,
)
SEARCH_OPERATOR_TERMS = {
    "ext",
    "filetype",
    "inbody",
    "intitle",
    "intext",
    "inurl",
    "site",
}

SMART_PUNCT_TRANSLATION = str.maketrans({
    "\u00a0": " ",
    "\u2013": "-",
    "\u2014": "-",
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2212": "-",
})

SPECIAL_SHORT_QUERY_TERMS = {"c", "r"}

LOW_SIGNAL_VARIANT_TERMS = {
    "api",
    "apis",
    "cli",
    "command",
    "commands",
    "config",
    "configuration",
    "code",
    "documentation",
    "example",
    "examples",
    "flag",
    "flags",
    "guide",
    "help",
    "install",
    "issue",
    "issues",
    "manual",
    "option",
    "options",
    "problem",
    "problems",
    "readme",
    "reference",
    "setup",
    "syntax",
    "tutorial",
    "usage",
}

BROAD_TECH_TERMS = {
    "ruby",
    "python",
    "javascript",
    "typescript",
    "node",
    "nodejs",
    "node.js",
    "java",
    "go",
    "golang",
    "rust",
    "php",
    "perl",
    "elixir",
    "erlang",
    "clojure",
    "scala",
    "kotlin",
    "swift",
    "dotnet",
    ".net",
    "c",
    "c++",
    "c#",
}

ACTION_CONTEXT_TERMS = {
    "boot",
    "exec",
    "execute",
    "fork",
    "launch",
    "load",
    "run",
    "spawn",
    "start",
    "worker",
    "workers",
}

DOC_QUERY_TERMS = DOC_SIGNAL_WORDS | {
    "cli",
    "command",
    "commands",
    "config",
    "configuration",
    "flag",
    "flags",
    "install",
    "option",
    "options",
    "setup",
    "spawn",
    "usage",
    "worker",
    "workers",
}

ECOSYSTEM_DOC_SITE_HINTS = {
    "ruby": ["site:github.com", "site:rubydoc.info", "site:rdoc.info", "site:rubygems.org"],
    "python": ["site:github.com", "site:docs.python.org", "site:pypi.org", "site:readthedocs.io"],
    "javascript": ["site:github.com", "site:developer.mozilla.org", "site:npmjs.com"],
    "typescript": ["site:github.com", "site:developer.mozilla.org", "site:npmjs.com"],
    "node": ["site:github.com", "site:nodejs.org", "site:npmjs.com"],
    "nodejs": ["site:github.com", "site:nodejs.org", "site:npmjs.com"],
    "node.js": ["site:github.com", "site:nodejs.org", "site:npmjs.com"],
    "java": ["site:github.com", "site:mvnrepository.com"],
    "go": ["site:github.com", "site:pkg.go.dev"],
    "golang": ["site:github.com", "site:pkg.go.dev"],
    "c#": ["site:github.com", "site:learn.microsoft.com", "site:nuget.org"],
    ".net": ["site:github.com", "site:learn.microsoft.com", "site:nuget.org"],
    "dotnet": ["site:github.com", "site:learn.microsoft.com", "site:nuget.org"],
    "php": ["site:github.com", "site:php.net", "site:packagist.org"],
}

ECOSYSTEM_DIRECT_DOC_URL_PATTERNS = {
    "ruby": [
        "https://{subject}.io/",
        "https://github.com/{subject}/{subject}",
        "https://www.rubydoc.info/gems/{subject}",
        "https://rubygems.org/gems/{subject}",
    ],
    "python": [
        "https://{subject}.readthedocs.io/en/latest/",
        "https://pypi.org/project/{subject}/",
        "https://github.com/{subject}/{subject}",
    ],
    "javascript": [
        "https://www.npmjs.com/package/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "typescript": [
        "https://www.npmjs.com/package/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "node": [
        "https://www.npmjs.com/package/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "nodejs": [
        "https://www.npmjs.com/package/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "node.js": [
        "https://www.npmjs.com/package/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "php": [
        "https://packagist.org/packages/{subject}/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    ".net": [
        "https://www.nuget.org/packages/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "dotnet": [
        "https://www.nuget.org/packages/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
    "c#": [
        "https://www.nuget.org/packages/{subject}",
        "https://github.com/{subject}/{subject}",
    ],
}

GENERIC_DIRECT_DOC_URL_PATTERNS = (
    "https://{subject}.io/",
    "https://{subject}.org/",
    "https://github.com/{subject}/{subject}",
)

TARGET_QUERY_VARIANTS = 10
MAX_COMBINATION_TERMS = 6
SIMILAR_RESULT_CONTAINMENT_THRESHOLD = 0.40
MIN_ACCEPTABLE_RESULT_SCORE = 0.0
DIRECT_DOC_FETCH_TIMEOUT = 5.0
MIN_DIRECT_DOC_RESULTS = 3
MAX_DIRECT_DOC_CANDIDATES = 8


def _fetch_text_response(url: str, timeout: float = REQUEST_TIMEOUT) -> tuple[str, str]:
    """Fetch text content from a URL."""
    request = Request(url, headers=DEFAULT_REQUEST_HEADERS)
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        body = response.read()
        content_type = response.headers.get("Content-Type", "")
        return body.decode(charset, errors="replace"), content_type


def build_bing_search_url(query: str, num_results: int = NUM_RESULTS) -> str:
    """Build Bing search RSS URL."""
    params = {
        "q": query,
        "count": max(1, min(num_results, 50)),
        "format": "rss",
        "setlang": "en",
        "cc": "us",
        "mkt": "en-US",
        "adlt": "strict",
    }
    return f"https://www.bing.com/search?{urlencode(params)}"


def clean_text(text: str) -> str:
    """Normalize RSS text before filtering and scoring."""
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


class HTMLMetadataParser(HTMLParser):
    """Extract a page title and common description metadata from HTML."""

    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self._title_parts: list[str] = []
        self.description = ""
        self.og_description = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered_tag = tag.lower()
        attr_map = {key.lower(): (value or "") for key, value in attrs}

        if lowered_tag == "title":
            self._in_title = True
            return

        if lowered_tag != "meta":
            return

        content = clean_text(attr_map.get("content", ""))
        if not content:
            return

        if attr_map.get("name", "").lower() == "description" and not self.description:
            self.description = content
        elif (
            attr_map.get("property", "").lower() == "og:description"
            and not self.og_description
        ):
            self.og_description = content

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)

    @property
    def title(self) -> str:
        return clean_text(" ".join(self._title_parts))


def extract_html_metadata(html_text: str) -> tuple[str, str]:
    """Extract a concise title/snippet pair from a fetched HTML page."""
    parser = HTMLMetadataParser()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    return parser.title, parser.description or parser.og_description


def english_confidence(text: str) -> float:
    """Return a rough English-likeness score from 0.0 to 1.0."""
    text = clean_text(text)
    if not text:
        return 0.0

    words = re.findall(r"[a-z]+", text.lower())
    if not words:
        return 0.0

    ascii_ratio = sum(1 for ch in text if ord(ch) < 128) / max(len(text), 1)
    stopword_hits = sum(1 for w in words if w in ENGLISH_STOPWORDS)
    stopword_ratio = stopword_hits / len(words)

    if len(words) < 5:
        return 0.75 * ascii_ratio + 0.25 * stopword_ratio

    return 0.45 * ascii_ratio + 0.55 * stopword_ratio


def is_english(text: str) -> bool:
    """Check if text is likely in English."""
    return english_confidence(text) >= 0.42


def _split_attached_version_tokens(query: str) -> str:
    """Separate attached technology/version tokens like python3.11 or node.js18."""
    query = re.sub(
        r"\b([a-z][a-z0-9.+#_/-]{1,})[-/](\d+(?:\.\d+)+)\b",
        r"\1 \2",
        query,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"\b([a-z][a-z0-9.+#_-]{1,})(\d+(?:\.\d+)+)\b",
        r"\1 \2",
        query,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"\b([a-z][a-z0-9.+#_-]*[a-z.+#_-])(\d{1,2})\b",
        r"\1 \2",
        query,
        flags=re.IGNORECASE,
    )
    return query


def _simplify_common_executable_paths(query: str) -> str:
    """Map common absolute binary paths to their executable name for search intent."""
    query = re.sub(
        r"(?<!\S)/(?:usr/)?(?:local/)?(?:s)?bin/([a-z0-9._+-]+)\b",
        r"\1",
        query,
        flags=re.IGNORECASE,
    )
    query = re.sub(
        r"(?<!\S)/(?:opt|app|home)/(?:[a-z0-9._+-]+/){1,4}bin/([a-z0-9._+-]+)\b",
        r"\1",
        query,
        flags=re.IGNORECASE,
    )
    return query


def rewrite_query(query: str) -> str:
    """
    Normalize common query noise while preserving intent.
    This is intentionally conservative.
    """
    q = (query or "").strip()
    q = q.translate(SMART_PUNCT_TRANSLATION)
    q = re.sub(r"^\s*[-–—]+\s*", "", q)  # strip accidental leading hyphen-like noise
    q = html.unescape(q)
    q = _split_attached_version_tokens(q)
    q = _simplify_common_executable_paths(q)
    q = re.sub(r"^\s*how\s+to\s+", "", q, flags=re.IGNORECASE)
    q = re.sub(r"\bvia\b", " ", q, flags=re.IGNORECASE)

    # Make docs intent a little more explicit, but do not overforce it.
    q = re.sub(r"\bdocs?\b", "documentation", q, flags=re.IGNORECASE)
    q = re.sub(
        r"\bdocumentation(?:\s+documentation)+\b",
        "documentation",
        q,
        flags=re.IGNORECASE,
    )

    q = re.sub(r"\s+", " ", q).strip()
    return q


def sanitize_query(query: str) -> str:
    """Keep useful search characters while removing obvious noise."""
    query = query.strip()
    query = re.sub(r"[^\w\s\-\.:\"/#\+]", " ", query)
    query = re.sub(r"\s+", " ", query)
    return query.strip()


def normalize_query(query: str) -> list[str]:
    """Extract meaningful query terms, filtering out stopwords."""
    words = QUERY_TERM_RE.findall(query.lower())
    terms = []
    for w in words:
        operator_free = SEARCH_OPERATOR_PREFIX_RE.sub("", w)
        bare = re.sub(r"^[^\w]+|[^\w]+$", "", operator_free)
        if not operator_free:
            continue
        if bare in ENGLISH_STOPWORDS or bare in SEARCH_OPERATOR_TERMS:
            continue
        if len(bare) <= 1 and bare not in SPECIAL_SHORT_QUERY_TERMS:
            continue
        terms.append(operator_free)
    return terms


def build_scoring_query_terms(query: str) -> list[str]:
    """Build clean query terms for final result ranking."""
    rewritten = sanitize_query(rewrite_query(query))
    return dedupe_strings(normalize_query(rewritten))


def dedupe_strings(values: list[str]) -> list[str]:
    """De-duplicate strings while preserving order."""
    out = []
    seen = set()
    for value in values:
        key = value.lower().strip()
        if not key or key in seen:
            continue
        out.append(value)
        seen.add(key)
    return out


def is_subject_candidate(term: str) -> bool:
    """Detect query terms that likely name the primary subject/package."""
    return (
        bool(term)
        and term not in BROAD_TECH_TERMS
        and term not in ACTION_CONTEXT_TERMS
        and term not in LOW_SIGNAL_VARIANT_TERMS
        and not is_version_like_term(term)
    )


def extract_subject_terms(terms: list[str], limit: int = 2) -> list[str]:
    """Select likely subject terms to drive official-doc fallback URLs."""
    unique_terms = dedupe_strings(terms)
    subjects = [term for term in unique_terms if is_subject_candidate(term)]
    if subjects:
        return subjects[:limit]

    fallback_subjects = [
        term for term in choose_variant_focus_terms(unique_terms)
        if is_subject_candidate(term)
    ]
    return dedupe_strings(fallback_subjects)[:limit]


def build_direct_doc_candidate_urls(query_terms: list[str]) -> list[str]:
    """Guess a few likely official/package URLs when search results are poor."""
    subject_terms = extract_subject_terms(query_terms)
    if not subject_terms:
        return []

    ecosystem_term = next(
        (term for term in dedupe_strings(query_terms) if term in ECOSYSTEM_DIRECT_DOC_URL_PATTERNS),
        "",
    )
    url_patterns = list(ECOSYSTEM_DIRECT_DOC_URL_PATTERNS.get(ecosystem_term, []))
    url_patterns.extend(GENERIC_DIRECT_DOC_URL_PATTERNS)

    candidate_urls = []
    for subject in subject_terms:
        for pattern in url_patterns:
            candidate_urls.append(pattern.format(subject=subject))

    return dedupe_strings(candidate_urls)[:MAX_DIRECT_DOC_CANDIDATES]


def is_version_like_term(term: str) -> bool:
    """Detect version-ish tokens that are useful to relax in fallback variants."""
    return bool(
        re.fullmatch(r"v?\d+(?:\.\d+)+", term, flags=re.IGNORECASE)
        or re.fullmatch(r"\d+(?:\.\d+)*\.x", term, flags=re.IGNORECASE)
        or re.fullmatch(r"\d+x", term, flags=re.IGNORECASE)
        or re.fullmatch(r"\d{1,2}", term)
    )


def has_documentation_intent(terms: list[str]) -> bool:
    """Detect whether the query likely wants docs, usage, or command references."""
    return any(term in DOC_QUERY_TERMS for term in terms)


def query_term_priority(term: str) -> float:
    """Estimate how useful a query term is for subset search variants."""
    score = 0.0
    if term not in LOW_SIGNAL_VARIANT_TERMS:
        score += 2.0
    if not is_version_like_term(term):
        score += 1.2
    else:
        score -= 1.0
    if term in BROAD_TECH_TERMS:
        score -= 0.6
    if len(term) >= 4:
        score += 0.2
    if any(ch in term for ch in ".#+"):
        score += 0.2
    return score


def choose_variant_focus_terms(terms: list[str]) -> list[str]:
    """Choose a compact pair of high-signal terms for fallback variants."""
    unique_terms = dedupe_strings(terms)

    def choose_from(candidates: list[str], count: int = 2) -> list[str]:
        if len(candidates) < count:
            return []
        indexed = list(enumerate(candidates))
        ranked = sorted(
            indexed,
            key=lambda item: (-query_term_priority(item[1]), item[0]),
        )
        selected_indexes = sorted(index for index, _ in ranked[:count])
        return [candidates[index] for index in selected_indexes]

    meaningful_terms = [
        term for term in unique_terms
        if not is_version_like_term(term) and term not in LOW_SIGNAL_VARIANT_TERMS
    ]
    subject_terms = [
        term for term in meaningful_terms
        if term not in BROAD_TECH_TERMS and term not in ACTION_CONTEXT_TERMS
    ]
    action_terms = [term for term in meaningful_terms if term in ACTION_CONTEXT_TERMS]

    selected_subject = choose_from(subject_terms, count=1)
    selected_action = choose_from(action_terms, count=1)
    if selected_subject and selected_action:
        return [selected_subject[0], selected_action[0]]

    selected = choose_from(meaningful_terms)
    if selected:
        return selected

    non_version_terms = [term for term in unique_terms if not is_version_like_term(term)]
    selected = choose_from(non_version_terms)
    if selected:
        return selected

    return choose_from(unique_terms) or unique_terms[:2]


def select_combination_terms(terms: list[str]) -> list[str]:
    """Choose a bounded set of terms to use for combinatorial search variants."""
    unique_terms = dedupe_strings(terms)
    if len(unique_terms) <= MAX_COMBINATION_TERMS:
        return unique_terms

    ranked = sorted(
        enumerate(unique_terms),
        key=lambda item: (-query_term_priority(item[1]), item[0]),
    )
    selected_indexes = sorted(index for index, _ in ranked[:MAX_COMBINATION_TERMS])
    return [unique_terms[index] for index in selected_indexes]


def split_terms_by_selection(terms: list[str], selected_terms: list[str]) -> tuple[list[str], list[str]]:
    """Remove one occurrence of each selected term, preserving remaining order."""
    remaining_counts: dict[str, int] = {}
    for term in selected_terms:
        remaining_counts[term] = remaining_counts.get(term, 0) + 1

    selected: list[str] = []
    remainder: list[str] = []
    for term in terms:
        if remaining_counts.get(term, 0) > 0:
            selected.append(term)
            remaining_counts[term] -= 1
            continue
        remainder.append(term)
    return selected, remainder


def build_quoted_pair_variant(terms: list[str]) -> str:
    """Build a query variant that enforces a useful 2-term phrase."""
    pair = choose_variant_focus_terms(terms)
    if len(pair) < 2:
        return ""

    _selected_pair_terms, remainder = split_terms_by_selection(terms, pair)
    variant_parts = [f'"{" ".join(pair)}"']
    if remainder:
        variant_parts.extend(remainder[:4])
    return " ".join(variant_parts).strip()


def build_operator_variants(terms: list[str]) -> list[str]:
    """Generate operator-style query variants like intitle: and intext:."""
    combination_terms = select_combination_terms(terms)
    focus_terms = choose_variant_focus_terms(combination_terms)
    if len(focus_terms) < 2:
        return []

    _selected_focus_terms, remainder = split_terms_by_selection(combination_terms, focus_terms)
    variants: list[str] = []
    intext_remainder = [f"intext:{term}" for term in remainder[:3]]

    phrase_variant_parts = [f'intitle:"{" ".join(focus_terms)}"']
    phrase_variant_parts.extend(intext_remainder)
    variants.append(" ".join(phrase_variant_parts).strip())

    title_first_parts = [
        f"intitle:{focus_terms[0]}",
        f"intext:{focus_terms[1]}",
    ]
    title_first_parts.extend(intext_remainder[:2])
    variants.append(" ".join(title_first_parts).strip())

    title_second_parts = [
        f"intitle:{focus_terms[1]}",
        f"intext:{focus_terms[0]}",
    ]
    title_second_parts.extend(intext_remainder[:2])
    variants.append(" ".join(title_second_parts).strip())

    inbody_targets = remainder[:3] or [focus_terms[1]]
    inbody_parts = [f'intitle:"{" ".join(focus_terms)}"']
    inbody_parts.extend(f"inbody:{term}" for term in inbody_targets)
    variants.append(" ".join(inbody_parts).strip())

    return dedupe_strings(variants)


def build_site_variants(terms: list[str]) -> list[str]:
    """Generate targeted site: queries when the query smells like docs/help intent."""
    if not has_documentation_intent(terms):
        return []

    combination_terms = select_combination_terms(terms)
    focus_terms = choose_variant_focus_terms(combination_terms)
    if not focus_terms:
        return []

    subject_terms = [
        term for term in combination_terms
        if (
            term not in BROAD_TECH_TERMS
            and term not in ACTION_CONTEXT_TERMS
            and not is_version_like_term(term)
            and term not in LOW_SIGNAL_VARIANT_TERMS
        )
    ]
    subject = subject_terms[0] if subject_terms else focus_terms[0]

    ecosystem_term = next((term for term in combination_terms if term in ECOSYSTEM_DOC_SITE_HINTS), "")
    site_prefixes = ECOSYSTEM_DOC_SITE_HINTS.get(
        ecosystem_term,
        ["site:github.com", "site:readthedocs.io"],
    )

    context_terms = []
    for term in combination_terms:
        if term == subject:
            continue
        if is_version_like_term(term):
            continue
        context_terms.append(term)

    variants = []
    for site_prefix in site_prefixes[:4]:
        parts = [site_prefix, subject]
        parts.extend(context_terms[:3])
        variants.append(" ".join(parts).strip())

    return dedupe_strings(variants)


def build_quoted_combination_variants(terms: list[str]) -> list[str]:
    """Generate extra quoted-pair queries using different term pairings."""
    combination_terms = select_combination_terms(terms)
    if len(combination_terms) < 2:
        return []

    focus_terms = set(choose_variant_focus_terms(combination_terms))
    scored_variants: list[tuple[tuple[float, ...], str]] = []

    for indexes in combinations(range(len(combination_terms)), 2):
        pair_terms = [combination_terms[index] for index in indexes]
        pair_term_set = set(pair_terms)
        remainder = [
            term for idx, term in enumerate(combination_terms)
            if idx not in indexes
        ]
        variant_parts = [f'"{" ".join(pair_terms)}"']
        if remainder:
            variant_parts.extend(remainder[:4])
        variant = " ".join(variant_parts).strip()
        if not variant:
            continue

        rank = (
            float(sum(1 for term in focus_terms if term in pair_term_set)),
            sum(query_term_priority(term) for term in pair_terms),
            -float(sum(indexes)),
            -sum(query_term_priority(term) for term in remainder),
        )
        scored_variants.append((rank, variant))

    scored_variants.sort(key=lambda item: item[0], reverse=True)
    return dedupe_strings([variant for _, variant in scored_variants])


def build_term_combination_variants(terms: list[str]) -> list[str]:
    """Generate ranked subset queries so Bing sees more than one term mix."""
    combination_terms = select_combination_terms(terms)
    if len(combination_terms) < 3:
        return []

    focus_terms = set(choose_variant_focus_terms(combination_terms))
    scored_variants: list[tuple[tuple[float, ...], str]] = []

    def rank_indexes(indexes: tuple[int, ...]) -> tuple[float, ...]:
        kept_terms = [combination_terms[index] for index in indexes]
        kept_term_set = set(kept_terms)
        dropped_terms = [
            term for idx, term in enumerate(combination_terms)
            if idx not in indexes
        ]
        return (
            float(len(kept_terms)),
            float(sum(1 for term in focus_terms if term in kept_term_set)),
            sum(query_term_priority(term) for term in kept_terms),
            -sum(query_term_priority(term) for term in dropped_terms),
            -float(sum(indexes)),
        )

    for size in range(len(combination_terms) - 1, 1, -1):
        for indexes in combinations(range(len(combination_terms)), size):
            variant = " ".join(combination_terms[index] for index in indexes).strip()
            if variant:
                scored_variants.append((rank_indexes(indexes), variant))

    scored_variants.sort(key=lambda item: item[0], reverse=True)
    return dedupe_strings([variant for _, variant in scored_variants])


def build_single_term_variants(terms: list[str]) -> list[str]:
    """Fallback broad queries used only when we still lack search attempts."""
    combination_terms = select_combination_terms(terms)
    ranked_terms = sorted(
        enumerate(combination_terms),
        key=lambda item: (-query_term_priority(item[1]), item[0]),
    )
    return [term for _, term in ranked_terms]


def build_query_variants(original_query: str) -> list[str]:
    """
    Build a small set of query variants for retrieval.
    This improves recall without flooding Bing with noisy OR expressions.
    """
    rewritten = sanitize_query(rewrite_query(original_query))
    variants = []

    if rewritten:
        variants.append(rewritten)

    terms = dedupe_strings(normalize_query(rewritten))
    if len(terms) >= 2:
        quoted_pair = build_quoted_pair_variant(terms)
        if quoted_pair and quoted_pair not in variants:
            variants.append(quoted_pair)

        compact_focus = " ".join(choose_variant_focus_terms(terms))
        if compact_focus and compact_focus not in variants:
            variants.append(compact_focus)

    variants.extend(build_operator_variants(terms))
    variants.extend(build_site_variants(terms))
    variants.extend(build_term_combination_variants(terms))
    variants.extend(build_quoted_combination_variants(terms))
    variants = dedupe_strings(variants)
    if len(variants) < TARGET_QUERY_VARIANTS:
        variants.extend(build_single_term_variants(terms))
    return dedupe_strings(variants)[:TARGET_QUERY_VARIANTS]


def parse_bing_rss(xml_text: str, max_results: int = NUM_RESULTS) -> list[dict[str, str]]:
    """Parse Bing RSS search results."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    results: list[dict[str, str]] = []

    for item in root.findall("./channel/item")[:max_results * MAX_FETCH_MULTIPLIER]:
        title = clean_text(item.findtext("title", "") or "")
        snippet = clean_text(item.findtext("description", "") or "")
        link = clean_text(item.findtext("link", "") or "")

        if not (title or snippet):
            continue

        combined = f"{title} {snippet}".strip()
        title_conf = english_confidence(title)
        snippet_conf = english_confidence(snippet)
        combined_conf = english_confidence(combined)

        # Keep useful English results, but be stricter when the text is long enough
        # to provide a real language signal.
        if len(combined) > 60:
            if combined_conf < 0.42 and title_conf < 0.50 and snippet_conf < 0.35:
                continue
        else:
            if combined_conf < 0.35 and title_conf < 0.45:
                continue

        results.append({
            "title": title,
            "snippet": snippet,
            "link": link,
        })

        if len(results) >= max_results:
            break

    return results[:max_results]


def domain_from_url(url: str) -> str:
    """Extract a crude hostname from a URL for domain-based scoring."""
    if not url:
        return ""
    m = re.match(r"^[a-z]+://([^/]+)/?", url.lower())
    return m.group(1) if m else ""


def contains_query_term(term: str, text: str) -> bool:
    """Match query terms with light boundaries while preserving tech punctuation."""
    if not term or not text:
        return False

    pattern = re.escape(term)
    if term[0].isalnum():
        pattern = rf"(?<![a-z0-9]){pattern}"
    if term[-1].isalnum():
        pattern = rf"{pattern}(?![a-z0-9])"
    return re.search(pattern, text) is not None


def has_doc_signal_domain(domain: str) -> bool:
    """Heuristic documentation-domain check that is not tied to one ecosystem."""
    if not domain:
        return False
    if any(domain == hint or domain.endswith(f".{hint}") for hint in DOC_SIGNAL_DOMAINS):
        return True
    return any(domain.startswith(prefix) or f".{prefix}" in domain for prefix in DOC_SIGNAL_DOMAIN_PREFIXES)


def matches_ecosystem_context(query_terms: list[str], text: str, link: str) -> bool:
    """Check whether a result still reflects the ecosystem in the query."""
    ecosystem_term = next(
        (term for term in dedupe_strings(query_terms) if term in ECOSYSTEM_DOC_SITE_HINTS),
        "",
    )
    if not ecosystem_term:
        return True

    combined_text = f"{text} {link}".lower()
    if contains_query_term(ecosystem_term, combined_text):
        return True

    domain = domain_from_url(link)
    for site_hint in ECOSYSTEM_DOC_SITE_HINTS.get(ecosystem_term, []):
        hinted_domain = site_hint.removeprefix("site:")
        if domain == hinted_domain or domain.endswith(f".{hinted_domain}"):
            return True
    return False


def relevance_score(query_terms: list[str], title: str, snippet: str, link: str = "") -> float:
    """Score a result by query match quality, English quality, and doc signal."""
    title = clean_text(title)
    snippet = clean_text(snippet)
    link = clean_text(link)
    text = f"{title} {snippet}".lower()
    title_lower = title.lower()
    snippet_lower = snippet.lower()
    domain = domain_from_url(link)

    unique_query_terms = dedupe_strings(query_terms)
    if not unique_query_terms:
        return english_confidence(f"{title} {snippet}") * 2.0

    score = 0.0
    matched_terms = set()
    matched_title_terms = set()

    for term in unique_query_terms:
        in_title = contains_query_term(term, title_lower)
        in_snippet = contains_query_term(term, snippet_lower)
        exact = contains_query_term(term, text)

        if in_title:
            score += 4.0
            matched_terms.add(term)
            matched_title_terms.add(term)
        elif in_snippet:
            score += 1.5
            matched_terms.add(term)

        if exact:
            score += 0.6

    # Reward coverage strongly. A page matching only one ambiguous term
    # (like "puma") should not outrank actual documentation results.
    coverage = len(matched_terms) / max(len(unique_query_terms), 1)
    title_coverage = len(matched_title_terms) / max(len(unique_query_terms), 1)
    unique_hits = len(matched_terms)
    score += coverage * 5.5
    score += title_coverage * 3.0
    score += unique_hits * 1.2
    score += unique_hits * max(unique_hits - 1, 0) * 1.0

    # Penalize results that only match one term when the query has several terms.
    if len(unique_query_terms) >= 3 and unique_hits < 2:
        score -= 5.0
    elif len(unique_query_terms) >= 2 and unique_hits < 2:
        score -= 2.5
    if len(unique_query_terms) >= 5 and unique_hits < 3:
        score -= 3.5

    subject_terms = extract_subject_terms(unique_query_terms, limit=2)
    combined_text = f"{text} {link.lower()}"
    subject_match = any(contains_query_term(term, combined_text) for term in subject_terms)
    ecosystem_match = matches_ecosystem_context(unique_query_terms, text, link)

    if subject_terms and not subject_match:
        score -= 6.0
    elif subject_terms and not ecosystem_match:
        score -= 4.5
    elif subject_terms and ecosystem_match:
        score += 2.0

    # Documentation intent bonus.
    if any(term in {"documentation", "docs", "doc", "readme", "guide", "api"} for term in unique_query_terms):
        if any(word in text for word in DOC_SIGNAL_WORDS):
            score += 2.0
        if has_doc_signal_domain(domain):
            score += 2.5

    # Stronger preference for English-clean results.
    score += english_confidence(f"{title} {snippet}") * 1.5

    return score


def dedupe_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicates by normalized title + link."""
    seen = set()
    deduped = []

    for r in results:
        key = (
            (r.get("title", "").lower().strip(),),
            (r.get("link", "").lower().strip(),)
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)

    return deduped


def result_similarity_containment(first: dict[str, str], second: dict[str, str]) -> float:
    """Measure overlap relative to the smaller result text footprint."""
    first_text = clean_text(f"{first.get('title', '')} {first.get('snippet', '')}")
    second_text = clean_text(f"{second.get('title', '')} {second.get('snippet', '')}")
    first_terms = set(normalize_query(first_text))
    second_terms = set(normalize_query(second_text))

    if not first_terms or not second_terms:
        return 0.0

    overlap = len(first_terms & second_terms)
    return overlap / max(min(len(first_terms), len(second_terms)), 1)


def collapse_similar_results(
    results: list[dict[str, str]],
    threshold: float = SIMILAR_RESULT_CONTAINMENT_THRESHOLD,
) -> list[dict[str, str]]:
    """Keep the highest-scored result from groups of strongly overlapping results."""
    kept_results: list[dict[str, str]] = []

    for result in results:
        if any(result_similarity_containment(result, kept) >= threshold for kept in kept_results):
            continue
        kept_results.append(result)

    return kept_results


def keep_acceptable_results(
    results: list[dict[str, str]],
    minimum_score: float = MIN_ACCEPTABLE_RESULT_SCORE,
) -> list[dict[str, str]]:
    """Discard results whose relevance score marks them as unusable."""
    kept_results: list[dict[str, str]] = []
    for result in results:
        if float(result.get("score", float("-inf"))) < minimum_score:
            continue
        kept_results.append(result)
    return kept_results


def rank_results(results: list[dict[str, str]], query_terms: list[str]) -> list[dict[str, str]]:
    """Apply final scoring, de-duplication, overlap collapse, and score filtering."""
    ranked_results = dedupe_results(results)
    for result in ranked_results:
        result["score"] = relevance_score(
            query_terms,
            result.get("title", ""),
            result.get("snippet", ""),
            result.get("link", ""),
        )

    ranked_results.sort(key=lambda result: result.get("score", 0), reverse=True)
    ranked_results = collapse_similar_results(ranked_results)
    return keep_acceptable_results(ranked_results)


def result_matches_subject_context(result: dict[str, str], query_terms: list[str]) -> bool:
    """Check whether a result reflects both the package/project and its ecosystem."""
    subject_terms = extract_subject_terms(query_terms, limit=2)
    if not subject_terms:
        return False

    combined_text = clean_text(
        f"{result.get('title', '')} {result.get('snippet', '')} {result.get('link', '')}"
    ).lower()
    if not any(contains_query_term(term, combined_text) for term in subject_terms):
        return False

    ecosystem_terms = [
        term for term in dedupe_strings(query_terms)
        if term in BROAD_TECH_TERMS or term in ECOSYSTEM_DOC_SITE_HINTS
    ]
    if not ecosystem_terms:
        return True

    return any(contains_query_term(term, combined_text) for term in ecosystem_terms[:3])


def should_fetch_direct_doc_candidates(
    results: list[dict[str, str]],
    query_terms: list[str],
) -> bool:
    """Decide whether generic search results are weak enough to warrant a docs fallback."""
    if not build_direct_doc_candidate_urls(query_terms):
        return False

    if len(results) < min(MIN_DIRECT_DOC_RESULTS, NUM_RESULTS):
        return True

    top_results = results[: min(len(results), 5)]
    return not any(result_matches_subject_context(result, query_terms) for result in top_results)


def fetch_direct_doc_candidate_results(
    query_terms: list[str],
    timeout: float = REQUEST_TIMEOUT,
) -> list[dict[str, str]]:
    """Probe likely official/package pages when Bing returns too little signal."""
    candidate_urls = build_direct_doc_candidate_urls(query_terms)
    if not candidate_urls:
        return []

    results: list[dict[str, str]] = []
    candidate_timeout = min(timeout, DIRECT_DOC_FETCH_TIMEOUT)

    for url in candidate_urls:
        try:
            html_text, content_type = _fetch_text_response(url, timeout=candidate_timeout)
        except (HTTPError, URLError, ValueError):
            continue

        if "html" not in content_type.lower():
            continue

        title, snippet = extract_html_metadata(html_text)
        if not (title or snippet):
            continue

        results.append({
            "title": title,
            "snippet": snippet,
            "link": url,
        })

    return rank_results(results, query_terms)


def fetch_bing_search_results(query: str, timeout: float = REQUEST_TIMEOUT) -> list[dict[str, str]]:
    """Fetch search results from Bing and rank by relevance."""
    original_query = query
    query_variants = build_query_variants(original_query)
    scoring_terms = build_scoring_query_terms(original_query)

    if not query_variants:
        return []

    all_results: list[dict[str, str]] = []
    candidate_results_per_variant = min(NUM_RESULTS * MAX_FETCH_MULTIPLIER, 50)

    for variant in query_variants:
        query_terms = normalize_query(variant)
        url = build_bing_search_url(variant, num_results=candidate_results_per_variant)

        print(f"Searching Bing for: {variant}", file=sys.stderr)

        try:
            xml_text, _ = _fetch_text_response(url, timeout=timeout)
            results = parse_bing_rss(xml_text, max_results=candidate_results_per_variant)

            for result in results:
                result["score"] = relevance_score(
                    query_terms,
                    result.get("title", ""),
                    result.get("snippet", ""),
                    result.get("link", "")
                )

            all_results.extend(results)

        except HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        except URLError as e:
            print(f"Network Error: {e.reason}", file=sys.stderr)

    all_results = dedupe_results(all_results)
    ranked_results = rank_results(all_results, scoring_terms)

    if should_fetch_direct_doc_candidates(ranked_results, scoring_terms):
        direct_results = fetch_direct_doc_candidate_results(scoring_terms, timeout=timeout)
        ranked_results = rank_results(ranked_results + direct_results, scoring_terms)

    # Keep only the best ranked results.
    return ranked_results[:NUM_RESULTS]


def print_results(results: list[dict[str, str]]) -> None:
    """Print search results."""
    if not results:
        print("No results found.")
        return

    print(f"\nBing Search Results ({len(results)} results)\n")

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        if result.get("title"):
            print(f"  Title: {result['title']}")
        if result.get("score") is not None:
            print(f"  Score: {result.get('score', 0):.2f}")
        if result.get("snippet"):
            print(f"  Snippet: {result['snippet']}")
        print()


def main() -> int:
    """Main entry point."""
    query = " ".join(sys.argv[1:]).strip()

    if not query:
        print("Usage: python3 lib/bing_search.py <search_query>", file=sys.stderr)
        return 1

    results = fetch_bing_search_results(query)
    print_results(results)

    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())
