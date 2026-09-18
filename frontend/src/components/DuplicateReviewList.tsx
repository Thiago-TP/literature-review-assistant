import type { ImportPreviewRow } from '../types'

export default function DuplicateReviewList({
  rows,
  actions,
  onToggle,
}: {
  rows: ImportPreviewRow[]
  actions: Record<number, 'add' | 'skip'>
  onToggle: (rowIndex: number, checked: boolean) => void
}) {
  return (
    <div className="flex max-h-72 flex-col gap-1.5 overflow-y-auto border border-border p-2">
      {rows.map((row) => {
        const checked = (actions[row.row_index] ?? row.default_action) === 'add'
        return (
          <label
            key={row.row_index}
            className={`flex items-start gap-2 px-2 py-1.5 text-sm ${row.is_duplicate ? 'bg-danger/5' : ''}`}
          >
            <input
              type="checkbox"
              className="mt-1"
              checked={checked}
              onChange={(e) => onToggle(row.row_index, e.target.checked)}
            />
            <span>
              <span className="text-text">{row.title}</span>
              {row.is_duplicate && (
                <span className="ml-2 text-xs text-danger">
                  duplicate ({row.duplicate_reason === 'doi' ? 'same DOI' : 'same title'}) of "
                  {row.matched_title}"
                </span>
              )}
            </span>
          </label>
        )
      })}
    </div>
  )
}
