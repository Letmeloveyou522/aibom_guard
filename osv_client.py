"""
osv_client.py
-----------------------------------
Queries the OSV (Open Source Vulnerabilities) API with a package name
and version to check for known vulnerabilities (CVEs, etc.).

OSV is a free, open vulnerability database run by Google.
No API key is needed - just send an HTTP POST request.
Docs: https://osv.dev/docs/
"""

import requests

OSV_API_URL = "https://api.osv.dev/v1/query"


def query_vulnerabilities(package_name: str, version: str, ecosystem: str = "PyPI") -> list:
    """
    Query the OSV API for known vulnerabilities affecting a specific
    package name + version.

    Args:
        package_name: Package name (e.g. "requests")
        version: Package version (e.g. "2.28.0")
        ecosystem: Package ecosystem (PyPI, npm, crates.io, etc.)

    Returns:
        A list of vulnerability dicts: {id, summary, severity}.
        Returns an empty list if no vulnerabilities are found.
    """
    payload = {
        "package": {
            "name": package_name,
            "ecosystem": ecosystem,
        },
        "version": version,
    }

    try:
        response = requests.post(OSV_API_URL, json=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Don't crash the whole scan if the network call fails
        print(f"[WARNING] Failed to query vulnerabilities for {package_name}: {e}")
        return []

    data = response.json()
    vulns = data.get("vulns", [])

    results = []
    for vuln in vulns:
        # Many entries don't have a clean severity field, so we
        # try a couple of fallbacks before giving up.
        severity = "UNKNOWN"
        if vuln.get("severity"):
            severity = vuln["severity"][0].get("score", "UNKNOWN")
        elif vuln.get("database_specific", {}).get("severity"):
            severity = vuln["database_specific"]["severity"]

        results.append({
            "id": vuln.get("id", "UNKNOWN-ID"),
            "summary": vuln.get("summary", "No description"),
            "severity": severity,
        })

    return results


if __name__ == "__main__":
    # Quick manual test: requests 2.28.0 has known CVEs
    import json
    result = query_vulnerabilities("requests", "2.28.0")
    print(json.dumps(result, indent=2, ensure_ascii=False))
