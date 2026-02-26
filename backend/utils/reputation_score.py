"""
Reputation Score — keyword-based company reputation estimator.
"""

# Well-known institution / company keywords mapped to reputation tiers
_TIER_1_KEYWORDS = [
    "iit", "iisc", "isro", "drdo", "google", "microsoft", "apple", "meta",
    "amazon", "nvidia", "openai", "deepmind",
]

_TIER_2_KEYWORDS = [
    "ibm", "oracle", "sap", "intel", "cisco", "adobe", "salesforce",
    "samsung", "sony", "tcs", "infosys", "wipro", "hcl", "accenture",
    "deloitte", "ey", "kpmg", "pwc", "mckinsey", "bcg", "bain",
    "goldman sachs", "morgan stanley", "jpmorgan",
]

_TIER_3_KEYWORDS = [
    "startup", "funded", "ycombinator", "y combinator", "sequoia",
    "series a", "series b", "backed", "venture",
]


def get_reputation_score(company: str) -> float:
    """
    Estimate company reputation score based on name keywords.

    Returns:
        95.0 for Tier-1 (IIT/ISRO/FAANG)
        85.0 for Tier-2 (MNC)
        75.0 for Tier-3 (Funded Startup)
        60.0 for Unknown
    """
    name = company.strip().lower()

    if any(kw in name for kw in _TIER_1_KEYWORDS):
        return 95.0

    if any(kw in name for kw in _TIER_2_KEYWORDS):
        return 85.0

    if any(kw in name for kw in _TIER_3_KEYWORDS):
        return 75.0

    return 60.0
