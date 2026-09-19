"""Values the rest of the app treats as fixed."""

# The rating scale, in stars. Half stars are allowed, so the step is 0.5.
MAX_RATING: float = 5.0

# Protected tag fields seeded automatically into every new project.
REQUIRED_FIELDS: dict[str, list[str]] = {
    "Adherence": ["Insufficient", "Partial", "Sufficient"],
    "Contribution Type": ["Improvement", "New Method", "Review", "Other"],
}
