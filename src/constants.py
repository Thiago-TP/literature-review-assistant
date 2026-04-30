# Standard Scopus columns that are expected to come
# in the Excel and can be ignored when looking for user defined tags

SCOPUS_COLUMNS = [
    "Abbreviated Source Title",
    "Abstract",
    "Affiliations",
    "Art. No.",
    "Authors",
    "Author(s) ID",
    "Author full names",
    "Authors with affiliations",
    "Author Keywords",
    "Cited by",
    "CODEN",
    "Correspondence Address",
    "Document Type",
    "DOI",
    "Editors",
    "EID",
    "Index Keywords",
    "ISBN",
    "Issue",
    "ISSN",
    "Language of Original Document",
    "Link",
    "Open Access",
    "Page count",
    "Page end",
    "Page start",
    "Publication Stage",
    "Publisher",
    "PubMed ID",
    "Source",
    "Source title",
    "Title",
    "Unnamed: 0",
    "Volume",
    "Year",
]

ADHERENCE_OPTIONS = ["Insufficient", "Partial", "Sufficient"]
CONTRIBUTION_OPTIONS = ["Improvement", "New Method", "Review", "Other"]
REQUIRED_FIELDS = {
    "Adherence": ADHERENCE_OPTIONS,
    "Contribution Type": CONTRIBUTION_OPTIONS,
}
ABSTRACT_COLUMN = "Abstract"
TITLE_COLUMN = "Title"
DOI_COLUMN = "DOI"
NOTE_COLUMN = "Notes"
