import { useState } from 'react'
import { ChevronDown, ChevronRight, Pencil, Plus, Trash2 } from 'lucide-react'
import type { TagField, TagOption } from '../types'
import { useFieldMutations } from '../hooks/useTagFields'
import { Button, Card, Input } from './ui'

function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'message' in error) {
    return String((error as { message: unknown }).message)
  }
  return 'Algo deu errado'
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

  function renderOptionNode(option: TagOption, fieldId: number, isProtected: boolean, depth: number) {
    return (
      <div key={option.id} style={{ marginLeft: depth * 18 }}>
        <div className="flex items-center gap-1 rounded-full bg-surface-muted py-1 pl-2.5 pr-1 text-xs text-text">
          <span>{option.value}</span>
          {!isProtected && (
            <>
              <button
                aria-label={`Adicionar subtópico em ${option.value}`}
                onClick={() => {
                  setAddingChildToOptionId(option.id)
                  setNewChildValue('')
                }}
                className="ml-1 text-text-muted hover:text-accent"
              >
                <Plus size={12} />
              </button>
              <button
                aria-label={`Renomear ${option.value}`}
                onClick={() => {
                  setRenamingOptionId(option.id)
                  setOptionRenameValue(option.value)
                }}
                className="text-text-muted hover:text-accent"
              >
                <Pencil size={11} />
              </button>
              <button
                aria-label={`Apagar ${option.value}`}
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
              mutations.renameOption.mutate(
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
              Salvar
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
              placeholder="Novo subtópico"
              value={newChildValue}
              onChange={(e) => setNewChildValue(e.target.value)}
              autoFocus
            />
            <Button type="submit" variant="secondary">
              Adicionar
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
    <Card className="p-4">
      <button
        className="flex w-full items-center justify-between text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <span className="tracked-label text-xs font-semibold text-text">Gerenciar campos e tags</span>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </button>

      {open && (
        <div className="mt-4 flex flex-col gap-4">
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
              placeholder="Novo campo (ex: Domínio)"
              value={newFieldName}
              onChange={(e) => setNewFieldName(e.target.value)}
            />
            <Button type="submit" variant="secondary">
              <Plus size={15} /> Adicionar campo
            </Button>
          </form>
          {mutations.addField.isError && (
            <p className="text-xs text-danger">{extractErrorMessage(mutations.addField.error)}</p>
          )}

          {fields.map((field) => (
            <div key={field.id} className="border border-border p-3">
              <div className="flex items-center justify-between">
                <button
                  className="flex items-center gap-1.5 text-sm font-medium text-text"
                  onClick={() => setExpandedFieldId((id) => (id === field.id ? null : field.id))}
                >
                  {expandedFieldId === field.id ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  {field.name}
                  {field.is_protected && <span className="text-xs font-normal text-text-muted">(protegido)</span>}
                </button>
                {!field.is_protected && (
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      aria-label="Renomear campo"
                      onClick={() => {
                        setRenamingFieldId(field.id)
                        setRenameValue(field.name)
                      }}
                    >
                      <Pencil size={14} />
                    </Button>
                    <Button
                      variant="ghost"
                      aria-label="Apagar campo"
                      onClick={() => {
                        if (confirm(`Apagar o campo "${field.name}" e todas as suas tags?`)) {
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
                    Salvar
                  </Button>
                </form>
              )}

              {expandedFieldId === field.id && (
                <div className="mt-3 flex flex-col gap-2 border-t border-border pt-3">
                  <p className="text-xs text-text-muted">
                    Use o + em cada tag para adicionar um subtópico (e dentro dele, um subsubtópico, e assim por
                    diante).
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
                        placeholder="Novo tópico"
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
              Os campos "Adherence" e "Contribution Type" são fixos. Adicione campos próprios acima.
            </p>
          )}
        </div>
      )}
    </Card>
  )
}
