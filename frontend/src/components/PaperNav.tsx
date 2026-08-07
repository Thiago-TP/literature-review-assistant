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
          aria-label="Artigo anterior"
          disabled={currentIndex <= 0}
          onClick={() => onGoTo(currentIndex - 1)}
        >
          <ChevronLeft size={16} />
        </Button>
        <Button
          variant="secondary"
          aria-label="Próximo artigo"
          disabled={currentIndex >= total - 1}
          onClick={() => onGoTo(currentIndex + 1)}
        >
          <ChevronRight size={16} />
        </Button>
      </div>
      <span className="text-sm font-medium text-text-muted">
        Artigo {currentIndex + 1} de {total}
      </span>
      <form onSubmit={handleGoTo} className="flex items-center gap-1.5">
        <Input
          type="number"
          min={1}
          max={total}
          placeholder="Ir para #"
          value={goToValue}
          onChange={(e) => setGoToValue(e.target.value)}
          className="w-24"
        />
        <Button type="submit" variant="secondary">
          Ir
        </Button>
      </form>
    </div>
  )
}
