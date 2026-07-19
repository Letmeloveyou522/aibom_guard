"""
license_checker.py
-----------------------------------
Decides whether a package's license complies with the competition rules
(Article 8: only OSI-approved open source licenses are allowed).

- ALLOWED: safe to use, OSI-approved and commercially usable
- REVIEW: usable but needs a human check (e.g. GPL-family licenses have
  copyleft conditions that may or may not be a problem)
- BLOCKED: has a Non-Commercial restriction, which likely violates the
  competition rules
"""

ALLOWED_LICENSES = {
    "mit", "mit license",
    "apache-2.0","apache 2.0", "apache software license", "apache license 2.0",
    "bsd-3-clause", "bsd-2-clause", "bsd license", "new bsd license",
    "isc license", "isc",
    "zlib", "0bsd", "cc0-1.0",
}

REVIEW_LICENSES = {
    "gpl-2.0", "gpl-3.0", "gnu general public license",
    "lgpl", "lgpl-2.1", "lgpl-3.0",
    "mpl-2.0", "mozilla public license 2.0",
}

BLOCKED_KEYWORDS = {
    "non-commercial", "noncommercial", "nc", "cc-by-nc",
    "proprietary", "commercial license required",
}


def classify_license(license_string: str) -> str:
    """
    Classify a single license string as ALLOWED / REVIEW / BLOCKED / UNKNOWN.

    License strings from tools like pip-licenses come in many different
    formats (e.g. "BSD-3-Clause AND MIT"), so we lowercase everything and
    do keyword matching instead of exact matching.
    """
    if not license_string:
        return "UNKNOWN"

    normalized = license_string.lower().strip()

    # If any non-commercial keyword shows up, block immediately
    for keyword in BLOCKED_KEYWORDS:
        if keyword in normalized:
            return "BLOCKED"

    # Multiple licenses can be combined with AND/OR, so split on those
    parts = normalized.replace(" and ", "|").replace(" or ", "|").split("|")

    statuses = set()
    for part in parts:
        part = part.strip()
        if part in ALLOWED_LICENSES:
            statuses.add("ALLOWED")
        elif part in REVIEW_LICENSES:
            statuses.add("REVIEW")
        else:
            statuses.add("UNKNOWN")

    # If REVIEW and UNKNOWN are mixed, lean toward the stricter verdict
    if "REVIEW" in statuses and "UNKNOWN" not in statuses:
        return "REVIEW"
    if statuses == {"ALLOWED"}:
        return "ALLOWED"
    if "UNKNOWN" in statuses:
        return "UNKNOWN"

    return "REVIEW"


if __name__ == "__main__":
    tests = [
        "MIT License",
        "BSD-3-Clause AND MIT",
        "GNU General Public License v3",
        "CC-BY-NC-4.0",
        "",
    ]
    for t in tests:
        print(f"{t!r:40} -> {classify_license(t)}")
