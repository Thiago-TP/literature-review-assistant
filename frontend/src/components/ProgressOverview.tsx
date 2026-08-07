import { Check } from 'lucide-react'
import type { PaperListItem } from '../types'

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
    <div className="flex flex-wrap gap-1.5" role="list" aria-label="Progresso da revisão">
      {papers.map((paper) => {
        const complete = paper.total_field_count > 0 && paper.filled_field_count === paper.total_field_count
        const isCurrent = paper.id === currentPaperId
        return (
          <button
            key={paper.id}
            role="listitem"
            title={`${paper.title}\n${paper.filled_field_count}/${paper.total_field_count} campos preenchidos`}
            onClick={() => onSelect(paper.id)}
            style={{ backgroundColor: colorFor(paper.filled_field_count, paper.total_field_count) }}
            className={`relative h-6 w-6 transition-transform hover:scale-110 ${
              isCurrent ? 'ring-2 ring-offset-2 ring-accent ring-offset-[var(--color-surface)]' : ''
            }`}
          >
            {complete && (
              <Check size={14} strokeWidth={3} className="absolute inset-0 m-auto text-[var(--color-success-fg)]" />
            )}
          </button>
        )
      })}
    </div>
  )
}
