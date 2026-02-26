"""
Confidence Calculator — weighted composite confidence score.
"""


def calculate_confidence(
    skill_match: float, domain_match: float, experience_match: float
) -> float:
    """
    Compute composite confidence score.

    Formula:
        0.5 * skill_match + 0.3 * domain_match + 0.2 * experience_match

    All inputs should be on a 0–100 scale.

    Returns:
        Confidence score (0–100).
    """
    return 0.5 * skill_match + 0.3 * domain_match + 0.2 * experience_match
