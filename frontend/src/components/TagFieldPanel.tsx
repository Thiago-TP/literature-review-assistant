import { Lock, Pencil } from 'lucide-react'
import type { PaperDetail, TagField, TagOption } from '../types'
import { SECTION_HEADING_GAP, SectionHeading } from './ui'

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
      // The tag's meaning from the review plan, on hover. A native title
      // rather than a popover: it costs no markup, works on a button that is
      // already here, and matches how the progress tiles carry their meaning.
      title={option.description ?? undefined}
      className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
        isSelected
          ? 'border-accent bg-accent text-accent-fg'
          : 'border-border bg-surface text-text-muted hover:border-accent hover:text-text'
      } ${option.description ? 'underline decoration-dotted underline-offset-2' : ''}`}
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
            <SectionHeading className={SECTION_HEADING_GAP}>
              {field.is_protected ? (
                <Lock size={13} className="text-text-muted" />
              ) : (
                <Pencil size={13} className="text-text-muted" />
              )}
              <span title={field.description ?? undefined}>{field.name}</span>
            </SectionHeading>
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
