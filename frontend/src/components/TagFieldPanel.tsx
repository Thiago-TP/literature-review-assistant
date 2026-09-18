import { Lock, Pencil } from 'lucide-react'
import type { PaperDetail, TagField, TagOption } from '../types'

function OptionPill({
  option,
  isSelected,
  onClick,
}: {
  option: TagOption
  isSelected: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
        isSelected
          ? 'border-accent bg-accent text-accent-fg'
          : 'border-border bg-surface text-text-muted hover:border-accent hover:text-text'
      }`}
    >
      {option.value}
    </button>
  )
}

/** Recursive row for one option + its subtopics, indented one step per depth. */
function OptionTreeRow({
  option,
  depth,
  selected,
  onToggle,
}: {
  option: TagOption
  depth: number
  selected: Set<number>
  onToggle: (optionId: number) => void
}) {
  return (
    <div className="flex flex-col gap-1" style={{ marginLeft: depth * 18 }}>
      <OptionPill option={option} isSelected={selected.has(option.id)} onClick={() => onToggle(option.id)} />
      {option.children.map((child) => (
        <OptionTreeRow key={child.id} option={child} depth={depth + 1} selected={selected} onToggle={onToggle} />
      ))}
    </div>
  )
}

export default function TagFieldPanel({
  fields,
  paper,
  onToggle,
}: {
  fields: TagField[]
  paper: PaperDetail
  onToggle: (fieldId: number, optionId: number, checked: boolean) => void
}) {
  return (
    <div className="flex flex-col gap-4">
      {fields.map((field) => {
        const selected = new Set(paper.tags[field.id] ?? [])
        const hasNesting = field.options.some((o) => o.children.length > 0)
        return (
          <div key={field.id}>
            <p className="tracked-label mb-1.5 flex items-center gap-1.5 text-xs font-semibold text-text">
              {field.is_protected ? <Lock size={13} className="text-text-muted" /> : <Pencil size={13} className="text-text-muted" />}
              {field.name}
            </p>
            {field.options.length === 0 && (
              <p className="text-xs text-text-muted">No tags defined yet.</p>
            )}
            {hasNesting ? (
              <div className="flex flex-col gap-1.5">
                {field.options.map((option) => (
                  <OptionTreeRow
                    key={option.id}
                    option={option}
                    depth={0}
                    selected={selected}
                    onToggle={(optionId) => onToggle(field.id, optionId, !selected.has(optionId))}
                  />
                ))}
              </div>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {field.options.map((option) => (
                  <OptionPill
                    key={option.id}
                    option={option}
                    isSelected={selected.has(option.id)}
                    onClick={() => onToggle(field.id, option.id, !selected.has(option.id))}
                  />
                ))}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
