"""The example review the documentation screenshots are taken of.

Everything here is fabricated, the same as in ``examples/``: the titles,
authors and abstracts do not refer to real publications, and the DOIs use the
``10.0000/`` placeholder prefix so nothing in them resolves.

Kept apart from the script that uses it so the pictures can be changed by
editing plain data, without reading any of the browser-driving code.
"""

from __future__ import annotations

from dataclasses import dataclass

PROJECT_NAME = "Automated Screening in Systematic Reviews"

# Field descriptions and tag weights/descriptions. The two protected fields
# already exist on every new project, so for them only the weights and
# descriptions are applied; the custom field is created with its tags.
FIELD_DESCRIPTIONS: dict[str, str] = {
    "Adherence": "How directly the paper answers the review question: automating, or "
    "semi-automating, the title-and-abstract screening stage.",
    "Contribution Type": "What the paper adds: a new technique, an improvement to an existing "
    "one, a survey of others' work, or something else.",
    "Study Domain": "The literature the screening was evaluated on, since performance on "
    "clinical trials rarely transfers to other fields.",
}

# field name -> [(tag, weight, description or None)], in display order.
FIELD_TAGS: dict[str, list[tuple[str, float, str | None]]] = {
    "Adherence": [
        ("Insufficient", 0, "Screening is mentioned, but not evaluated or not automated."),
        ("Partial", 1, "Automates part of screening, or evaluates it without a baseline."),
        ("Sufficient", 2, "Automates screening and reports recall against human screeners."),
    ],
    "Contribution Type": [
        ("Improvement", 1, "Better results from an existing technique."),
        ("New Method", 1.5, "A technique not previously applied to screening."),
        ("Review", 0.5, None),
        ("Other", 0, None),
    ],
    "Study Domain": [
        ("Medicine", 0, None),
        ("Software Engineering", 1, None),
        ("Information Science", 0, None),
    ],
}

# The field that is created by the seeding rather than built in.
CUSTOM_FIELD = "Study Domain"

PLAN: dict[str, str] = {
    "purpose": "Find out how much of title-and-abstract screening can be handed to a machine "
    "without losing relevant papers. Feeds the related-work chapter of the thesis, and decides "
    "whether our own review uses a screening tool at all.",
    "scope": "In: tools and methods that rank or classify candidate papers at the screening "
    "stage, evaluated against human decisions. Out: search-string generation, data "
    "extraction, and anything evaluated only on precision.",
    "search": "Scopus and Web of Science, 2010 onwards, with the string (screening OR "
    '"citation classification") AND ("systematic review" OR "evidence synthesis") AND '
    '(automat* OR "machine learning" OR "active learning"). Deduplicated on import.',
    "weights": "Adherence dominates because it is the review question. A new method outweighs "
    "an improvement, which outweighs a survey. Software engineering gets a point because it is "
    "the domain our own review is in.",
    "other": "Recall matters far more than precision here: a missed paper is a gap in the "
    "review, a spurious one costs a minute of reading.",
}

# The workspace screenshots show this paper (1-based, in import order).
CURRENT_PAPER = 20


@dataclass(frozen=True)
class DemoPaper:
    title: str
    authors: str
    year: int
    venue: str
    abstract: str
    # Tag values by field name. A field left out is untagged on this paper.
    tags: dict[str, str]
    rating: float | None = None
    notes: str = ""
    # (start, end) character ranges of the abstract to highlight.
    highlights: tuple[tuple[int, int], ...] = ()


JRSM = "Journal of Research Synthesis Methods"
ESL = "Evidence Synthesis Letters"
CIJ = "Clinical Informatics Journal"
ESER = "Empirical Software Engineering Review"
IRQ = "Information Retrieval Quarterly"
TMR = "Proceedings of the Workshop on Text Mining for Reviews"

A, C, D = "Adherence", "Contribution Type", "Study Domain"

_CROWD_ABSTRACT = (
    "Paid crowd workers reach expert-level recall when three independent judgements are "
    "aggregated, at roughly a third of the cost."
)

PAPERS: list[DemoPaper] = [
    DemoPaper(
        "Active Learning Halves the Screening Workload",
        "Okafor, N.; Lindqvist, M.",
        2014,
        CIJ,
        "An uncertainty-sampling classifier, retrained after every batch of human decisions, "
        "found 95% of included trials after screening half of the candidates.",
        {A: "Sufficient", C: "New Method", D: "Medicine"},
        4,
        "The 95% recall target is the one everyone else copies. Cite as the baseline.",
    ),
    DemoPaper(
        "Tuning Support Vector Machines for Citation Classification",
        "Brandt, H.",
        2012,
        TMR,
        "Class weighting and feature selection on bag-of-words representations raise recall "
        "on four review datasets by up to eleven points.",
        {A: "Partial", C: "Improvement"},
        3,
        "No human baseline, only other classifiers.",
    ),
    DemoPaper(
        "A Taxonomy of Evidence Synthesis Tasks",
        "Moreau, C.; Adeyemi, T.",
        2016,
        JRSM,
        "Sixteen tasks from question formulation to reporting, with the degree to which each "
        "has been automated to date.",
        {A: "Insufficient"},
    ),
    DemoPaper(
        "Screening Prioritisation in Software Engineering Reviews",
        "Takahashi, R.; Ferreira, L.",
        2019,
        ESER,
        "Re-ranking candidates by predicted relevance lets reviewers stop early; on six "
        "mapping studies the stopping point saved 40% of reads at 97% recall.",
        {A: "Sufficient", C: "Improvement", D: "Software Engineering"},
        3.5,
        "Closest to our own setting. Their stopping rule is worth trying.",
    ),
    DemoPaper(
        "Neural Ranking of Candidate Trials",
        "Hughes, A.; Varga, P.; Sato, K.",
        2021,
        CIJ,
        "A fine-tuned transformer ranks trial reports for inclusion, outperforming classical "
        "classifiers on every one of twenty-three clinical reviews.",
        {A: "Sufficient", C: "New Method", D: "Medicine"},
        4,
        "Strong results, but the model is not released.",
    ),
    DemoPaper(
        "What Reviewers Want From Screening Tools",
        "Nilsen, J.",
        2018,
        ESL,
        "Interviews with thirty review authors on trust, transparency and the workflows "
        "they would accept from a screening assistant.",
        {},
        notes="Background for the discussion section, not the core review.",
    ),
    DemoPaper(
        "Keyword Filters as a First Screening Pass",
        "Castillo, M.",
        2011,
        TMR,
        "Hand-built inclusion and exclusion keyword lists discard a third of candidates with "
        "a small but measurable loss of relevant papers.",
        {A: "Partial"},
        2.5,
    ),
    DemoPaper(
        "Automation in Systematic Reviews: A Survey",
        "Park, S.; Mensah, K.",
        2017,
        JRSM,
        "A survey of forty-four tools across the review pipeline, of which nineteen address "
        "screening.",
        {A: "Insufficient", C: "Review"},
        2,
        "Mostly superseded, but the tool table is a useful checklist.",
    ),
    DemoPaper(
        "Semi-Supervised Screening With Few Labels",
        "Rossi, G.; Achterberg, F.",
        2020,
        CIJ,
        "Self-training from fifty labelled abstracts matches a fully supervised classifier "
        "trained on five hundred.",
        {A: "Sufficient", C: "Improvement", D: "Medicine"},
        3,
        "Useful if we only label a small pilot set.",
    ),
    DemoPaper(
        "Citation Networks as Screening Signals",
        "Dubois, E.",
        2015,
        IRQ,
        "Papers cited by already-included papers are more likely to be included themselves; "
        "adding this signal to a text classifier improves early recall.",
        {A: "Partial", C: "Other", D: "Information Science"},
        2.5,
        "Interesting signal, weak evaluation.",
    ),
    DemoPaper(
        "Deduplicating Records Across Bibliographic Databases",
        "Kowalczyk, B.",
        2013,
        IRQ,
        "A normalisation and fuzzy-matching procedure that finds duplicate records across "
        "three databases with 99% precision.",
        {},
    ),
    DemoPaper(
        "Reporting Standards for Automated Screening",
        "Abara, O.; Whitfield, J.",
        2022,
        JRSM,
        "Proposes a minimum set of items a paper evaluating a screening tool should report, "
        "starting with recall and the stopping criterion.",
        {A: "Insufficient"},
        notes="Use their checklist to judge the others' evaluations.",
    ),
    DemoPaper(
        "Large Language Models as Zero-Shot Screeners",
        "Fischer, L.; Okonkwo, D.",
        2024,
        ESL,
        "Prompted with only the inclusion criteria, a general-purpose language model "
        "screens abstracts at a recall comparable to a trained classifier.",
        {A: "Sufficient", C: "New Method"},
        4,
        "The one everyone will ask about. Check which model version they used.",
    ),
    DemoPaper(
        "Stopping Rules for Prioritised Screening",
        "Lindqvist, M.; Okafor, N.",
        2019,
        CIJ,
        "A statistical stopping rule that bounds the number of relevant papers still unseen, "
        "tested on the CLEF technology-assisted review collections.",
        {A: "Sufficient", C: "Improvement", D: "Medicine"},
        3.5,
        "Pairs with their 2014 paper.",
    ),
    DemoPaper(
        "Screening Diagnostic Accuracy Studies",
        "Novak, I.",
        2016,
        CIJ,
        "Classifiers trained on intervention reviews transfer poorly to diagnostic accuracy "
        "reviews, whose abstracts are structured differently.",
        {A: "Insufficient", C: "Other", D: "Medicine"},
        1.5,
        "A negative result, but a relevant one for domain transfer.",
    ),
    DemoPaper(
        "Ontology-Driven Query Expansion",
        "Haddad, Y.",
        2012,
        IRQ,
        "Expanding search strings with ontology terms improves the recall of the search "
        "itself, before any screening happens.",
        {},
        1,
    ),
    DemoPaper(
        "Feature Engineering for Abstract Classification",
        "Mbeki, S.; Laurent, A.",
        2015,
        TMR,
        "Topic-model features added to bag-of-words improve the ranking of relevant "
        "abstracts on three review datasets.",
        {A: "Partial", C: "Improvement"},
        3,
        "Small gain; mention alongside Brandt 2012.",
    ),
    DemoPaper(
        "The Cost of a Missed Study",
        "Grant, E.",
        2020,
        ESL,
        "Re-running meta-analyses without the studies a screening tool would have missed "
        "changes the pooled estimate in two of fifty reviews.",
        {A: "Insufficient"},
    ),
    DemoPaper(
        "Screening in Qualitative Evidence Syntheses",
        "Ibrahim, H.; Solberg, K.",
        2023,
        JRSM,
        "Qualitative reviews use looser inclusion criteria, which existing screening tools "
        "handle poorly.",
        {},
    ),
    DemoPaper(
        "Crowdsourced Screening: Accuracy and Cost",
        "Yusupova, E.",
        2018,
        JRSM,
        _CROWD_ABSTRACT,
        {A: "Sufficient", C: "New Method", D: "Software Engineering"},
        4.5,
        "A cheaper second screener. Check whether the workers saw the inclusion criteria.",
        ((0, _CROWD_ABSTRACT.index(" when")),),
    ),
    DemoPaper(
        "A Browser Plug-in for Screening",
        "Tanaka, M.",
        2014,
        TMR,
        "A plug-in that shows classifier confidence next to each record in a reference manager.",
        {A: "Insufficient", C: "Other"},
    ),
    DemoPaper(
        "Inter-Rater Agreement Under Automation",
        "Costa, R.; Johansson, P.",
        2021,
        ESER,
        "When one of two screeners is replaced by a classifier, agreement with the remaining "
        "human is comparable to agreement between two humans.",
        {A: "Partial"},
        2,
        "Argument for single-screener-plus-tool.",
    ),
    DemoPaper(
        "Living Reviews and Continuous Screening",
        "Whitaker, D.",
        2022,
        ESL,
        "Keeping a review current means screening a trickle of new records indefinitely, "
        "which changes what a good tool has to do.",
        {},
    ),
    DemoPaper(
        "Screening for Information Science Mapping Studies",
        "Ahmadi, F.; Petrov, V.",
        2020,
        IRQ,
        "Prioritised screening on four bibliometric mapping studies reaches 95% recall after "
        "a third of the candidates.",
        {A: "Sufficient", C: "Improvement", D: "Information Science"},
        3.5,
        "Confirms the medical results carry over outside medicine.",
    ),
]
