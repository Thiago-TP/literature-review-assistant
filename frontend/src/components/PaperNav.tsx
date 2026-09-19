import { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button, Input } from './ui'

export default function PaperNav({
  currentIndex,
  total,
  onGoTo,
}: {
  currentIndex: number
  total: number
  onGoTo: (index: number) => void
}) {
  const [goToValue, setGoToValue] = useState('')

  function handleGoTo(e: React.FormEvent) {
    e.preventDefault()
    const n = parseInt(goToValue, 10)
    if (!Number.isNaN(n) && n >= 1 && n <= total) {
      onGoTo(n - 1)
      setGoToValue('')
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-1">
        <Button
          variant="secondary"
          aria-label="Previous paper"
          title="Previous paper (left arrow)"
          disabled={currentIndex <= 0}
          onClick={() => onGoTo(currentIndex - 1)}
        >
          <ChevronLeft size={16} />
        </Button>
        <Button
          variant="secondary"
          aria-label="Next paper"
          title="Next paper (right arrow)"
          disabled={currentIndex >= total - 1}
          onClick={() => onGoTo(currentIndex + 1)}
        >
          <ChevronRight size={16} />
        </Button>
      </div>
      <span className="text-sm font-medium text-text-muted">
        Paper {currentIndex + 1} of {total}
      </span>
      <form onSubmit={handleGoTo} className="flex items-center gap-1.5">
        {/* Width goes on the wrapper, not the Input: see the note in ui.tsx.
            32 leaves room for the placeholder beside a number input's spinner
            arrows, which eat into the field on top of the padding. */}
        <div className="w-32">
          <Input
            type="number"
            min={1}
            max={total}
            placeholder="Go to #"
            aria-label="Go to paper number"
            value={goToValue}
            onChange={(e) => setGoToValue(e.target.value)}
          />
        </div>
        <Button type="submit" variant="secondary">
          Go
        </Button>
      </form>
    </div>
  )
}
