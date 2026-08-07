import { useEffect, useRef, useState } from 'react'
import { Label, Textarea } from './ui'

export default function NotesPanel({
  paperId,
  notes,
  onSave,
}: {
  paperId: number
  notes: string
  onSave: (value: string) => void
}) {
  const [value, setValue] = useState(notes)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Reset local draft when navigating to a different paper.
  useEffect(() => {
    setValue(notes)
  }, [paperId, notes])

  function handleChange(next: string) {
    setValue(next)
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => onSave(next), 400)
  }

  return (
    <div>
      <Label className="mb-1.5">Suas notas</Label>
      <Textarea
        rows={4}
        placeholder="Escreva suas notas sobre este artigo..."
        value={value}
        onChange={(e) => handleChange(e.target.value)}
      />
    </div>
  )
}
