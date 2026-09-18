import { useEffect, useState } from 'react'
import { Check, Pencil } from 'lucide-react'
import { Button, Label, Textarea } from './ui'

export default function NotesPanel({
  paperId,
  notes,
  onSave,
}: {
  paperId: number
  notes: string
  onSave: (value: string) => void
}) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(notes)

  // Reset only when navigating to a different paper -- NOT on every `notes`
  // change, since that prop also updates right after our own save (once the
  // query refetches), which would otherwise stomp on text as it's typed.
  useEffect(() => {
    setDraft(notes)
    setEditing(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [paperId])

  function startEditing() {
    setDraft(notes)
    setEditing(true)
  }

  function handleSave() {
    onSave(draft)
    setEditing(false)
  }

  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between">
        <Label>Your notes</Label>
        {editing ? (
          <Button variant="secondary" onClick={handleSave}>
            <Check size={14} /> OK
          </Button>
        ) : (
          <Button variant="ghost" onClick={startEditing}>
            <Pencil size={14} /> Edit
          </Button>
        )}
      </div>

      {editing ? (
        <Textarea
          rows={4}
          autoFocus
          placeholder="Write your notes about this paper..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
      ) : (
        <p className="min-h-[2.5rem] whitespace-pre-line border border-border bg-surface-muted px-3 py-2 text-sm text-text">
          {notes ? notes : <span className="text-text-muted">No notes yet.</span>}
        </p>
      )}
    </div>
  )
}
