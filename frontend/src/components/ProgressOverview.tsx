import type { ReactNode } from 'react'
import { Check, Pencil, Star } from 'lucide-react'
import type { PaperListItem } from '../types'

const HEADING_ID = 'review-progress-heading'

/**
 * Tiles are painted with a five-step ramp plus a success green, so a corner
 * badge sits on anything from near-white to near-black depending on progress
 * and theme. A thin light halo keeps the badges legible on every one of them
 * without needing a per-background colour.
 */
const BADGE_HALO = 'drop-shadow(0 0 1.2px rgba(255, 255, 255, 0.95))'
const STAR_FILL = '#f5c518'
const STAR_STROKE = '#6b4e00'
const PENCIL_STROKE = '#15161a'

/**
 * Sequential ramp encoding "how many fields are filled in" as magnitude. The
 * steps themselves are palette tokens (see index.css), so each theme gets its
 * own validated ramp and switching theme repaints the tiles through CSS --
 * reading the theme from JavaScript here would leave them on the old ramp
 * until something else happened to re-render the grid.
 *
 * Full completion gets the app's "success" token plus a check icon instead,
 * since "fully reviewed" is a distinct state, not just the top of the scale.
 */
const SEQUENTIAL_STEPS = [
  'var(--color-progress-1)',
  'var(--color-progress-2)',
  'var(--color-progress-3)',
  'var(--color-progress-4)',
  'var(--color-progress-5)',
]

function colorFor(filled: number, total: number): string {
  if (total === 0 || filled === 0) return 'var(--color-border)'
  if (filled === total) return 'var(--color-success)'
  const ratio = filled / total
  const last = SEQUENTIAL_STEPS.length - 1
  const index = Math.min(last, Math.max(0, Math.round(ratio * last)))
  return SEQUENTIAL_STEPS[index]
}

/** One small square in the legend's ramp. */
function Swatch({ color, children }: { color: string; children?: ReactNode }) {
  return (
    <span
      className="relative flex h-3 w-3 shrink-0 items-center justify-center rounded-[2px]"
      style={{ backgroundColor: color }}
    >
      {children}
    </span>
  )
}

/**
 * Colour and badges are the only thing carrying meaning in the grid, so the
 * key that decodes them travels with it.
 */
function Legend() {
  return (
    <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-[11px] text-text-muted">
      <span className="flex items-center gap-1.5">
        no tags
        <span className="flex items-center gap-0.5">
          <Swatch color="var(--color-border)" />
          {SEQUENTIAL_STEPS.map((step) => (
            <Swatch key={step} color={step} />
          ))}
        </span>
        most tags
      </span>
      <span className="flex items-center gap-1.5">
        <Swatch color="var(--color-success)">
          <Check size={8} strokeWidth={3.5} className="text-[var(--color-success-fg)]" />
        </Swatch>
        every field tagged
      </span>
      <span className="flex items-center gap-1.5">
        <Star size={11} fill={STAR_FILL} stroke={STAR_STROKE} strokeWidth={2} className="shrink-0" />
        rated
      </span>
      <span className="flex items-center gap-1.5">
        <Pencil size={11} strokeWidth={2} className="shrink-0" />
        has notes
      </span>
    </div>
  )
}

export default function ProgressOverview({
  papers,
  currentPaperId,
  onSelect,
}: {
  papers: PaperListItem[]
  currentPaperId: number | null
  onSelect: (paperId: number) => void
}) {
  const fullyTagged = papers.filter(
    (paper) => paper.total_field_count > 0 && paper.filled_field_count === paper.total_field_count
  ).length

  return (
    <section aria-labelledby={HEADING_ID}>
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <h2 id={HEADING_ID} className="tracked-label text-xs font-semibold text-text">
          Review progress
        </h2>
        <p className="text-xs text-text-muted">
          {fullyTagged} of {papers.length} fully tagged
        </p>
      </div>
      <div className="flex flex-wrap gap-1.5" role="list">
      {papers.map((paper) => {
        const complete = paper.total_field_count > 0 && paper.filled_field_count === paper.total_field_count
        const isCurrent = paper.id === currentPaperId
        const rated = paper.rating !== null
        const hasNotes = paper.notes.trim().length > 0
        const summary = [
          paper.title,
          `${paper.filled_field_count}/${paper.total_field_count} fields filled`,
          rated ? `rated ${paper.rating}/5` : null,
          hasNotes ? 'has notes' : null,
        ]
          .filter(Boolean)
          .join('\n')
        return (
          <button
            key={paper.id}
            role="listitem"
            title={summary}
            onClick={() => onSelect(paper.id)}
            style={{ backgroundColor: colorFor(paper.filled_field_count, paper.total_field_count) }}
            className={`relative h-7 w-7 rounded transition-transform hover:scale-110 ${
              isCurrent ? 'ring-2 ring-offset-2 ring-accent ring-offset-[var(--color-surface)]' : ''
            }`}
          >
            {rated && (
              <Star
                size={10}
                fill={STAR_FILL}
                stroke={STAR_STROKE}
                strokeWidth={2}
                style={{ filter: BADGE_HALO }}
                className="absolute left-[1px] top-[1px]"
                aria-hidden="true"
              />
            )}
            {hasNotes && (
              <Pencil
                size={9}
                stroke={PENCIL_STROKE}
                strokeWidth={2.5}
                style={{ filter: BADGE_HALO }}
                className="absolute right-[1px] top-[1px]"
                aria-hidden="true"
              />
            )}
            {complete && (
              <Check size={12} strokeWidth={3} className="absolute inset-0 m-auto text-[var(--color-success-fg)]" />
            )}
          </button>
        )
      })}
      </div>
      <Legend />
    </section>
  )
}
