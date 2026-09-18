import { Check, Pencil, Star } from 'lucide-react'
import type { PaperListItem } from '../types'

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
 * Sequential blue ramp (validated for CVD/contrast, light->dark) used to encode
 * "how many fields are filled in" as magnitude. Full completion gets the
 * app's "success" token + a check icon instead, since "fully reviewed" is a
 * distinct state, not just the top of the magnitude scale.
 */
const SEQUENTIAL_STEPS_LIGHT = ['#cde2fb', '#9ec5f4', '#6da7ec', '#3987e5', '#1c5cab']
const SEQUENTIAL_STEPS_DARK = ['#184f95', '#1c5cab', '#256abf', '#3987e5', '#6da7ec']

function isDarkMode(): boolean {
  if (typeof document === 'undefined') return false
  const explicit = document.documentElement.getAttribute('data-theme')
  if (explicit === 'dark') return true
  if (explicit === 'light') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function colorFor(filled: number, total: number): string {
  if (total === 0 || filled === 0) return 'var(--color-border)'
  if (filled === total) return 'var(--color-success)'
  const steps = isDarkMode() ? SEQUENTIAL_STEPS_DARK : SEQUENTIAL_STEPS_LIGHT
  const ratio = filled / total
  const index = Math.min(steps.length - 1, Math.max(0, Math.round(ratio * (steps.length - 1))))
  return steps[index]
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
  return (
    <div className="flex flex-wrap gap-1.5" role="list" aria-label="Review progress">
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
            className={`relative h-7 w-7 transition-transform hover:scale-110 ${
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
  )
}
