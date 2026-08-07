"""Protected tag fields seeded automatically into every new project."""

REQUIRED_FIELDS: dict[str, list[str]] = {
    "Adherence": ["Insufficient", "Partial", "Sufficient"],
    "Contribution Type": ["Improvement", "New Method", "Review", "Other"],
}
