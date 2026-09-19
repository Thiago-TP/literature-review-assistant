import { useEffect, useRef, useState } from 'react'
import { Check } from 'lucide-react'
import { Textarea } from './ui'

/**
 * One box of the review plan: always editable, saved when it loses focus.
 *
 * Not the Edit/OK toggle of `NotesPanel` — a plan page holds ten or more of
 * these, and two extra clicks each turns writing it into a chore. Saving on
 * blur also keeps the promise the rest of the app makes, that nothing needs
 * saving by hand.
 */
export default function PlanTextBox({
  id,
  value,
  placeholder,
  rows = 4,
  onSave,
}: {
  /** Identifies what is being edited. Changing it reloads the draft. */
  id: string
  value: string | null
  placeholder: string
  rows?: number
  onSave: (value: string) => void
}) {
  const [draft, setDraft] = useState(value ?? '')
  const [justSaved, setJustSaved] = useState(false)
  const saved = useRef(value ?? '')

  // Reset only when the box is pointed at something else -- never on `value`,
  // which also updates right after our own save, once the query refetches,
  // and would otherwise stomp on text as it is being typed. Same reasoning as
  // NotesPanel.
  useEffect(() => {
    setDraft(value ?? '')
    saved.current = value ?? ''
    setJustSaved(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  useEffect(() => {
    if (!justSaved) return
    const timer = setTimeout(() => setJustSaved(false), 2000)
    return () => clearTimeout(timer)
  }, [justSaved])

  function handleBlur() {
    // Nothing typed since the last save: no request, and no "Saved" flash
    // for a click that passed through.
    if (draft === saved.current) return
    saved.current = draft
    onSave(draft)
    setJustSaved(true)
  }

  return (
    <div className="relative">
      <Textarea
        rows={rows}
        placeholder={placeholder}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={handleBlur}
      />
      {justSaved && (
        <span
          className="pointer-events-none absolute bottom-2 right-2 flex items-center gap-1 text-xs text-text-muted"
          role="status"
        >
          <Check size={12} /> Saved
        </span>
      )}
    </div>
  )
}
