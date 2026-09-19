import { useState } from 'react'
import { Eraser, ExternalLink, Highlighter } from 'lucide-react'
import type { HighlightField, PaperDetail } from '../types'
import HighlightableText from './HighlightableText'
import { Badge, Button } from './ui'

export default function PaperDisplay({
  paper,
  onAddHighlight,
  onRemoveHighlight,
  onClearHighlights,
}: {
  paper: PaperDetail
  onAddHighlight: (field: HighlightField, start: number, end: number) => void
  onRemoveHighlight: (id: string) => void
  onClearHighlights: () => void
}) {
  // Deliberately a mode rather than highlighting every selection: selecting
  // text to copy it is at least as common as marking it up, and silently
  // turning that into a highlight would be worse than one extra click.
  const [marking, setMarking] = useState(false)

  const metaParts = [paper.authors, paper.year, paper.source_title].filter(Boolean)
  const forField = (field: HighlightField) => paper.highlights.filter((h) => h.field === field)

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <Button
          variant={marking ? 'primary' : 'secondary'}
          aria-pressed={marking}
          onClick={() => setMarking((value) => !value)}
          title={
            marking
              ? 'Stop highlighting — selecting text will behave normally again'
              : 'Highlight text by selecting it'
          }
        >
          <Highlighter size={15} /> Highlight
        </Button>
        {paper.highlights.length > 0 && (
          <Button
            variant="ghost"
            onClick={onClearHighlights}
            title="Remove every highlight on this paper"
          >
            <Eraser size={15} /> Clear all
          </Button>
        )}
        {marking && (
          <span className="text-xs text-text-muted">
            Select text to mark it; click a mark to remove it.
          </span>
        )}
      </div>

      <h2 className="font-serif text-xl leading-snug text-text">
        <HighlightableText
          text={paper.title}
          field="title"
          highlights={forField('title')}
          active={marking}
          onAdd={onAddHighlight}
          onRemove={onRemoveHighlight}
        />
      </h2>
      {metaParts.length > 0 && <p className="mt-1 text-sm text-text-muted">{metaParts.join(' · ')}</p>}
      <div className="mt-2 flex items-center gap-2">
        {paper.doi ? (
          <a
            href={`https://doi.org/${paper.doi}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 text-sm text-accent hover:underline"
          >
            {paper.doi} <ExternalLink size={13} />
          </a>
        ) : (
          <Badge>No DOI</Badge>
        )}
      </div>
      <p className="mt-4 whitespace-pre-line text-sm leading-relaxed text-text">
        {paper.abstract ? (
          <HighlightableText
            text={paper.abstract}
            field="abstract"
            highlights={forField('abstract')}
            active={marking}
            onAdd={onAddHighlight}
            onRemove={onRemoveHighlight}
          />
        ) : (
          <span className="text-text-muted">No abstract available.</span>
        )}
      </p>
    </div>
  )
}
