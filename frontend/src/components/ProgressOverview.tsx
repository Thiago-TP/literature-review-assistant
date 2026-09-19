import { useEffect, useState, type ReactNode } from 'react'
import { Check, ChevronDown, ChevronRight, Pencil, Star } from 'lucide-react'
import type { PaperListItem } from '../types'

const HEADING_ID = 'review-progress-heading'
const GRID_ID = 'review-progress-grid'

/**
 * Whether the panel is retracted, remembered per browser. It is a display
 * preference, not review data, so it belongs in localStorage rather than on
 * the project -- and a browser that refuses storage just gets the open
 * default rather than an error.
 */
const COLLAPSED_KEY = 'progressOverviewCollapsed'

function readCollapsed(): boolean {
  try {
    return localStorage.getItem(COLLAPSED_KEY) === 'true'
  } catch {
    return false
  }
}

/**
 * Tiles are painted with a five-step ramp plus a success green, so a corner
 * badge sits on anything from near-white to near-black depending on progress
 * and theme. A thin light halo keeps the badges legible on every one of them
 * without needing a per-background colour.
 */
const BADGE_HALO = 'drop-shadow(0 0 1.2px rgba(255, 255, 255, 0.95))'
const STAR_FILL = '#f5c518'
const STAR_STROKE = '#6b4e00'

/**
 * The notes pencil rides on a filled chip rather than a bare outline. A stroke
 * alone had to be dark to read on the pale end of the ramp and light to read
 * on the deep end, which no single colour satisfies; a light chip with a dark
 * rim carries its own contrast onto every tile colour in both themes.
 */
const NOTE_CHIP_BG = '#f7f4ea'
const NOTE_CHIP_RIM = 'rgba(0, 0, 0, 0.55)'
const NOTE_CHIP_FG = '#15161a'

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
        <span
          className="flex h-3 w-3 shrink-0 items-center justify-center rounded-[3px]"
          style={{ backgroundColor: NOTE_CHIP_BG, boxShadow: `0 0 0 0.5px ${NOTE_CHIP_RIM}` }}
        >
          <Pencil size={8} stroke={NOTE_CHIP_FG} strokeWidth={2.75} />
        </span>
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
  const [collapsed, setCollapsed] = useState(readCollapsed)

  useEffect(() => {
    try {
      localStorage.setItem(COLLAPSED_KEY, String(collapsed))
    } catch {
      // Storage unavailable (private browsing, blocked site data); the panel
      // still works, it just reopens on the next visit.
    }
  }, [collapsed])

  const fullyTagged = papers.filter(
    (paper) => paper.total_field_count > 0 && paper.filled_field_count === paper.total_field_count
  ).length

  return (
    <section aria-labelledby={HEADING_ID}>
      <h2 id={HEADING_ID}>
        <button
          type="button"
          onClick={() => setCollapsed((value) => !value)}
          aria-expanded={!collapsed}
          aria-controls={GRID_ID}
          className="flex w-full flex-wrap items-center justify-between gap-x-4 gap-y-1 text-left"
        >
          <span className="flex items-center gap-1.5 text-text">
            {collapsed ? <ChevronRight size={16} /> : <ChevronDown size={16} />}
            <span className="tracked-label text-xs font-semibold">Review progress</span>
          </span>
          <span className="text-xs font-normal text-text-muted">
            {fullyTagged} of {papers.length} fully tagged
          </span>
        </button>
      </h2>

      <div id={GRID_ID} className={collapsed ? 'hidden' : 'mt-3'}>
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
              <span
                className="absolute bottom-[1px] right-[1px] flex h-3 w-3 items-center justify-center rounded-[3px]"
                style={{ backgroundColor: NOTE_CHIP_BG, boxShadow: `0 0 0 0.5px ${NOTE_CHIP_RIM}` }}
                aria-hidden="true"
              >
                <Pencil size={8} stroke={NOTE_CHIP_FG} strokeWidth={2.75} />
              </span>
            )}
            {/* Top-right rather than centred: the notes chip now occupies the
                bottom-right, and a centred check overlapped it. Completion is
                still carried mainly by the tile turning the success colour --
                the check is the redundant, non-colour encoding of it. */}
            {complete && (
              <Check
                size={11}
                strokeWidth={3.25}
                className="absolute right-[1px] top-[1px] text-[var(--color-success-fg)]"
                aria-hidden="true"
              />
            )}
          </button>
        )
      })}
      </div>
        <Legend />
      </div>
    </section>
  )
}
