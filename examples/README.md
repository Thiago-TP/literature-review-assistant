# Example import spreadsheets

Two small `.xlsx` files you can import to see how the bulk import works before
pointing the app at your own export.

| File | What it is |
| --- | --- |
| [`example-scopus-export.xlsx`](example-scopus-export.xlsx) | A five-row export, shaped like a Scopus download |
| [`example-second-source.xlsx`](example-second-source.xlsx) | A three-row export from a "second database", overlapping the first |

The rows are fabricated. The titles, authors and abstracts do not refer to real
publications, and the DOIs use the `10.0000/` placeholder prefix so nothing in
them resolves.

## Try them

1. Start the app and create a review.
2. **Import spreadsheet** → `example-scopus-export.xlsx` → **Confirm import**.
   All five papers are added.
3. **Import spreadsheet** again → `example-second-source.xlsx`. The preview now
   reports **1 new** and **2 possible duplicates**:
   - *Active learning reduces screening burden in evidence synthesis* — matched
     by **DOI**, even though the author formatting and abstract differ.
   - *Reproducibility of search strategies in published reviews* — this copy has
     no DOI, so it is matched by **title** instead.

   Both duplicates are unchecked by default; the one new paper is checked. Nothing
   is written until you confirm, so you can tick a duplicate back on if the match
   is wrong.

## The format

The first row is the header. Column names are matched exactly, and only two
columns are required:

| Column | Required | Notes |
| --- | --- | --- |
| `Title` | **yes** | Rows with a blank title are skipped |
| `Abstract` | **yes** | The column must exist; individual cells may be blank |
| `DOI` | no | Used for duplicate detection when present |
| `Authors` | no | Free text, however your database formats it |
| `Year` | no | Read as a number; unparseable values become blank |
| `Source title` | no | Journal or conference name |

Any **other** column is kept as-is against the paper rather than discarded —
`Document Type` in these examples. That way a re-export of your data does not
silently lose the fields this app does not have a UI for.

Both Scopus and Web of Science exports already use these column names, so in
practice an unmodified download usually imports without editing. A hand-built
sheet works too: a `Title` column and an `Abstract` column are enough.

## Duplicate detection

When importing into a review that already has papers, each incoming row is
checked against them:

1. **By DOI** — matched after normalisation, so `10.0000/Example.0001`,
   `doi:10.0000/example.0001` and `https://doi.org/10.0000/example.0001` all
   count as the same DOI.
2. **By title** — for rows with no DOI or no DOI match, compared with case,
   punctuation and spacing normalised.

Rows are also checked against *earlier rows in the same file*, so a single
export containing the same paper twice is flagged on the second occurrence.

Matches are flagged and unchecked in the preview, never dropped silently.
