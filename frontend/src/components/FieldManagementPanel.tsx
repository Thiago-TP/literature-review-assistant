import { useState } from 'react'
import { ChevronDown, ChevronRight, Pencil, Plus, Trash2 } from 'lucide-react'
import type { TagField, TagOption } from '../types'
import { useFieldMutations } from '../hooks/useTagFields'
import { Button, Card, Input, SectionHeading } from './ui'

const MAX_TAG_WEIGHT = 5

function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message)
  }
  return 'Something went wrong'
}

export default function FieldManagementPanel({ projectId, fields }: { projectId: number; fields: TagField[] }) {
  const [open, setOpen] = useState(false)
  const [newFieldName, setNewFieldName] = useState('')
  const [expandedFieldId, setExpandedFieldId] = useState<number | null>(null)
  const [renamingFieldId, setRenamingFieldId] = useState<number | null>(null)
  const [renameValue, setRenameValue] = useState('')

  const [renamingOptionId, setRenamingOptionId] = useState<number | null>(null)
  const [optionRenameValue, setOptionRenameValue] = useState('')
  const [addingChildToOptionId, setAddingChildToOptionId] = useState<number | null>(null)
  const [newChildValue, setNewChildValue] = useState('')
  const [newRootOptionValue, setNewRootOptionValue] = useState('')

  const mutations = useFieldMutations(projectId)

  const customFields = fields.filter((f) => !f.is_protected)

  function saveWeight(fieldId: number, optionId: number, raw: string) {
    const weight = Number(raw)
    if (Number.isNaN(weight)) return
    mutations.updateOption.mutate(
      { fieldId, optionId, weight },
      { onError: (error) => alert(extractErrorMessage(error)) }
    )
  }

  function renderOptionNode(option: TagOption, fieldId: number, isProtected: boolean, depth: number) {
    return (
      <div key={option.id} style={{ marginLeft: depth * 18 }}>
        <div className="flex items-center gap-1 rounded-full bg-surface-muted py-1 pl-2.5 pr-1 text-xs text-text">
          <span>{option.value}</span>
          <input
            type="number"
            step="0.5"
            min={0}
            max={MAX_TAG_WEIGHT}
            defaultValue={option.weight}
            onBlur={(e) => saveWeight(fieldId, option.id, e.target.value)}
            title={`This tag's contribution to the paper score (0 to ${MAX_TAG_WEIGHT}, in steps of 0.5)`}
            aria-label={`Score contribution of ${option.value}`}
            className="ml-1 w-12 rounded border border-border bg-surface px-1 py-0.5 text-right text-xs text-text"
          />
          {!isProtected && (
            <>
              <button
                aria-label={`Add subtopic under ${option.value}`}
                onClick={() => {
                  setAddingChildToOptionId(option.id)
                  setNewChildValue('')
                }}
                className="ml-1 text-text-muted hover:text-accent"
              >
                <Plus size={12} />
              </button>
              <button
                aria-label={`Rename ${option.value}`}
                onClick={() => {
                  setRenamingOptionId(option.id)
                  setOptionRenameValue(option.value)
                }}
                className="text-text-muted hover:text-accent"
              >
                <Pencil size={11} />
              </button>
              <button
                aria-label={`Delete ${option.value}`}
                onClick={() => {
                  mutations.deleteOption.mutate(
                    { fieldId, optionId: option.id },
                    { onError: (error) => alert(extractErrorMessage(error)) }
                  )
                }}
                className="text-text-muted hover:text-danger"
              >
                ×
              </button>
            </>
          )}
        </div>

        {renamingOptionId === option.id && (
          <form
            className="mt-1 flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              const value = optionRenameValue.trim()
              if (!value) return
              mutations.updateOption.mutate(
                { fieldId, optionId: option.id, value },
                {
                  onSuccess: () => setRenamingOptionId(null),
                  onError: (error) => alert(extractErrorMessage(error)),
                }
              )
            }}
          >
            <Input value={optionRenameValue} onChange={(e) => setOptionRenameValue(e.target.value)} autoFocus />
            <Button type="submit" variant="secondary">
              Save
            </Button>
          </form>
        )}

        {addingChildToOptionId === option.id && (
          <form
            className="mt-1 flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              const value = newChildValue.trim()
              if (!value) return
              mutations.addOption.mutate(
                { fieldId, value, parentOptionId: option.id },
                {
                  onSuccess: () => setAddingChildToOptionId(null),
                  onError: (error) => alert(extractErrorMessage(error)),
                }
              )
            }}
          >
            <Input
              placeholder="New subtopic"
              value={newChildValue}
              onChange={(e) => setNewChildValue(e.target.value)}
              autoFocus
            />
            <Button type="submit" variant="secondary">
              Add
            </Button>
          </form>
        )}

        {option.children.length > 0 && (
          <div className="mt-1.5 flex flex-col gap-1.5">
            {option.children.map((child) => renderOptionNode(child, fieldId, isProtected, depth + 1))}
          </div>
        )}
      </div>
    )
  }

  return (
    <Card className="p-5">
      <button
        className="flex w-full items-center justify-between text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <SectionHeading as="p">Manage fields and tags</SectionHeading>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>

      {open && (
        <div className="mt-3 flex flex-col gap-4">
          <form
            className="flex gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              const name = newFieldName.trim()
              if (!name) return
              mutations.addField.mutate(name, { onSuccess: () => setNewFieldName('') })
            }}
          >
            <Input
              placeholder="New field (e.g. Domain)"
              value={newFieldName}
              onChange={(e) => setNewFieldName(e.target.value)}
            />
            <Button type="submit" variant="secondary">
              <Plus size={15} /> Add field
            </Button>
          </form>
          {mutations.addField.isError && (
            <p className="text-xs text-danger">{extractErrorMessage(mutations.addField.error)}</p>
          )}

          {fields.map((field) => (
            <div key={field.id} className="rounded-md border border-border p-3">
              <div className="flex items-center justify-between">
                <button
                  className="flex items-center gap-1.5 text-sm font-medium text-text"
                  onClick={() => setExpandedFieldId((id) => (id === field.id ? null : field.id))}
                >
                  {expandedFieldId === field.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  {field.name}
                  {field.is_protected && <span className="text-xs font-normal text-text-muted">(protected)</span>}
                </button>
                {!field.is_protected && (
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      aria-label="Rename field"
                      onClick={() => {
                        setRenamingFieldId(field.id)
                        setRenameValue(field.name)
                      }}
                    >
                      <Pencil size={14} />
                    </Button>
                    <Button
                      variant="ghost"
                      aria-label="Delete field"
                      onClick={() => {
                        if (confirm(`Delete the field "${field.name}" and all of its tags?`)) {
                          mutations.deleteField.mutate(field.id)
                        }
                      }}
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                )}
              </div>

              {renamingFieldId === field.id && (
                <form
                  className="mt-2 flex gap-2"
                  onSubmit={(e) => {
                    e.preventDefault()
                    const name = renameValue.trim()
                    if (!name) return
                    mutations.renameField.mutate(
                      { fieldId: field.id, name },
                      { onSuccess: () => setRenamingFieldId(null) }
                    )
                  }}
                >
                  <Input value={renameValue} onChange={(e) => setRenameValue(e.target.value)} autoFocus />
                  <Button type="submit" variant="secondary">
                    Save
                  </Button>
                </form>
              )}

              {expandedFieldId === field.id && (
                <div className="mt-3 flex flex-col gap-2 border-t border-border pt-3">
                  {/* Built-in fields have no +, rename or delete controls, so
                      only the weight half of this applies to them -- and that
                      half does, since their tags can still be re-weighted. */}
                  <p className="text-xs text-text-muted">
                    {!field.is_protected && (
                      <>
                        Use the + on each tag to add a subtopic (and inside it, a sub-subtopic, and so
                        on).{' '}
                      </>
                    )}
                    The number next to each tag is how much it contributes to the paper score (0 to{' '}
                    {MAX_TAG_WEIGHT}, in steps of 0.5).
                  </p>
                  <div className="flex flex-col gap-1.5">
                    {field.options.map((option) => renderOptionNode(option, field.id, field.is_protected, 0))}
                  </div>
                  {!field.is_protected && (
                    <form
                      className="mt-1 flex gap-2"
                      onSubmit={(e) => {
                        e.preventDefault()
                        const value = newRootOptionValue.trim()
                        if (!value) return
                        mutations.addOption.mutate(
                          { fieldId: field.id, value },
                          { onSuccess: () => setNewRootOptionValue('') }
                        )
                      }}
                    >
                      <Input
                        placeholder="New topic"
                        value={newRootOptionValue}
                        onChange={(e) => setNewRootOptionValue(e.target.value)}
                      />
                      <Button type="submit" variant="secondary">
                        <Plus size={14} />
                      </Button>
                    </form>
                  )}
                </div>
              )}
            </div>
          ))}

          {customFields.length === 0 && (
            <p className="text-xs text-text-muted">
              The "Adherence" and "Contribution Type" fields are built in. Add your own fields above.
            </p>
          )}
        </div>
      )}
    </Card>
  )
}
