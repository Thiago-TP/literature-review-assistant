import { ExternalLink } from 'lucide-react'
import type { PaperDetail } from '../types'
import { Badge } from './ui'

export default function PaperDisplay({ paper }: { paper: PaperDetail }) {
  const metaParts = [paper.authors, paper.year, paper.source_title].filter(Boolean)

  return (
    <div>
      <h2 className="font-serif text-xl leading-snug text-text">{paper.title}</h2>
      {metaParts.length > 0 && (
        <p className="mt-1 text-sm text-text-muted">{metaParts.join(' · ')}</p>
      )}
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
        {paper.abstract || <span className="text-text-muted">No abstract available.</span>}
      </p>
    </div>
  )
}
