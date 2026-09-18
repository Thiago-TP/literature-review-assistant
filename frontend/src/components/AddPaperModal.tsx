import { useState } from 'react'
import { AlertTriangle, Search } from 'lucide-react'
import Modal from './Modal'
import { Button, Input, Spinner, Textarea } from './ui'
import { importApi } from '../api/importPapers'
import { useCreatePaper } from '../hooks/usePapers'
import type { LookupCandidate } from '../types'
import { ApiError } from '../api/client'

type Tab = 'doi' | 'title' | 'manual'

function CandidateCard({
  candidate,
  onAdd,
  isPending,
}: {
  candidate: LookupCandidate
  onAdd: (force: boolean) => void
  isPending: boolean
}) {
  return (
    <div className="rounded-md border border-border p-3">
      <p className="text-sm font-medium text-text">{candidate.title}</p>
      <p className="mt-0.5 text-xs text-text-muted">
        {[candidate.authors, candidate.year, candidate.source_title].filter(Boolean).join(' · ')}
      </p>
      {!candidate.abstract_available && (
        <p className="mt-1 text-xs text-text-muted">
          No abstract available from CrossRef — you can paste one in manually after adding it.
        </p>
      )}
      {candidate.duplicate.is_duplicate ? (
        <div className="mt-2 flex items-center justify-between gap-2 rounded-md border border-danger/30 bg-danger/10 px-2 py-1.5 text-xs text-danger">
          <span className="flex items-center gap-1.5">
            <AlertTriangle size={13} /> Possible duplicate of "{candidate.duplicate.matched_title}"
          </span>
          <Button variant="ghost" className="!px-2 !py-1 text-danger" onClick={() => onAdd(true)} disabled={isPending}>
            Add anyway
          </Button>
        </div>
      ) : (
        <div className="mt-2 flex justify-end">
          <Button variant="primary" className="!px-3 !py-1.5" onClick={() => onAdd(false)} disabled={isPending}>
            {isPending ? <Spinner className="h-3.5 w-3.5" /> : 'Add'}
          </Button>
        </div>
      )}
    </div>
  )
}

export default function AddPaperModal({ projectId, onClose }: { projectId: number; onClose: () => void }) {
  const [tab, setTab] = useState<Tab>('doi')
  const [doi, setDoi] = useState('')
  const [titleQuery, setTitleQuery] = useState('')
  const [doiCandidate, setDoiCandidate] = useState<LookupCandidate | null>(null)
  const [titleCandidates, setTitleCandidates] = useState<LookupCandidate[] | null>(null)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [searching, setSearching] = useState(false)
  const [manual, setManual] = useState({ title: '', abstract: '', doi: '', authors: '', year: '' })

  const createPaper = useCreatePaper(projectId)

  async function handleDoiSearch(e: React.FormEvent) {
    e.preventDefault()
    setSearchError(null)
    setSearching(true)
    setDoiCandidate(null)
    try {
      const { candidate } = await importApi.lookupByDoi(projectId, doi.trim())
      setDoiCandidate(candidate)
    } catch (error) {
      setSearchError(error instanceof ApiError ? error.message : 'Failed to look up that DOI')
    } finally {
      setSearching(false)
    }
  }

  async function handleTitleSearch(e: React.FormEvent) {
    e.preventDefault()
    setSearchError(null)
    setSearching(true)
    setTitleCandidates(null)
    try {
      const { candidates } = await importApi.lookupByTitle(projectId, titleQuery.trim())
      setTitleCandidates(candidates)
    } catch (error) {
      setSearchError(error instanceof ApiError ? error.message : 'Failed to search by title')
    } finally {
      setSearching(false)
    }
  }

  function addFromCandidate(candidate: LookupCandidate, source: 'crossref_doi' | 'crossref_title', force: boolean) {
    createPaper.mutate(
      {
        title: candidate.title,
        abstract: candidate.abstract,
        doi: candidate.doi,
        authors: candidate.authors,
        year: candidate.year,
        source_title: candidate.source_title,
        source,
        raw_metadata: candidate.raw_metadata,
        force,
      },
      {
        onSuccess: (result) => {
          if (result.paper) onClose()
        },
      }
    )
  }

  function handleManualSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!manual.title.trim()) return
    createPaper.mutate(
      {
        title: manual.title.trim(),
        abstract: manual.abstract.trim() || null,
        doi: manual.doi.trim() || null,
        authors: manual.authors.trim() || null,
        year: manual.year ? parseInt(manual.year, 10) : null,
        source: 'manual',
      },
      {
        onSuccess: (result) => {
          if (result.paper) onClose()
        },
      }
    )
  }

  const manualDuplicate = createPaper.data?.duplicate?.is_duplicate ? createPaper.data.duplicate : null

  return (
    <Modal title="Add paper" onClose={onClose} wide>
      <div className="mb-4 flex gap-4 border-b border-border">
        {(['doi', 'title', 'manual'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`tracked-label -mb-px border-b-2 px-1 pb-2 text-xs font-semibold transition-colors ${
              tab === t ? 'border-accent text-text' : 'border-transparent text-text-muted hover:text-text'
            }`}
          >
            {t === 'doi' ? 'By DOI' : t === 'title' ? 'By title' : 'Manual'}
          </button>
        ))}
      </div>

      {tab === 'doi' && (
        <div>
          <form onSubmit={handleDoiSearch} className="flex gap-2">
            <Input placeholder="10.1000/xyz123" value={doi} onChange={(e) => setDoi(e.target.value)} />
            <Button type="submit" variant="secondary" disabled={!doi.trim() || searching}>
              {searching ? <Spinner className="h-4 w-4" /> : <Search size={15} />}
            </Button>
          </form>
          {searchError && <p className="mt-2 text-sm text-danger">{searchError}</p>}
          {doiCandidate && (
            <div className="mt-3">
              <CandidateCard
                candidate={doiCandidate}
                isPending={createPaper.isPending}
                onAdd={(force) => addFromCandidate(doiCandidate, 'crossref_doi', force)}
              />
            </div>
          )}
        </div>
      )}

      {tab === 'title' && (
        <div>
          <form onSubmit={handleTitleSearch} className="flex gap-2">
            <Input
              placeholder="Paper title"
              value={titleQuery}
              onChange={(e) => setTitleQuery(e.target.value)}
            />
            <Button type="submit" variant="secondary" disabled={!titleQuery.trim() || searching}>
              {searching ? <Spinner className="h-4 w-4" /> : <Search size={15} />}
            </Button>
          </form>
          {searchError && <p className="mt-2 text-sm text-danger">{searchError}</p>}
          {titleCandidates && (
            <div className="mt-3 flex max-h-80 flex-col gap-2 overflow-y-auto">
              {titleCandidates.length === 0 && (
                <p className="text-sm text-text-muted">No results found. Try the "Manual" tab.</p>
              )}
              {titleCandidates.map((candidate, i) => (
                <CandidateCard
                  key={i}
                  candidate={candidate}
                  isPending={createPaper.isPending}
                  onAdd={(force) => addFromCandidate(candidate, 'crossref_title', force)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {tab === 'manual' && (
        <form onSubmit={handleManualSubmit} className="flex flex-col gap-2.5">
          <Input
            placeholder="Title *"
            value={manual.title}
            onChange={(e) => setManual((m) => ({ ...m, title: e.target.value }))}
            required
          />
          <Textarea
            placeholder="Abstract"
            rows={3}
            value={manual.abstract}
            onChange={(e) => setManual((m) => ({ ...m, abstract: e.target.value }))}
          />
          <div className="flex gap-2">
            <Input
              placeholder="DOI"
              value={manual.doi}
              onChange={(e) => setManual((m) => ({ ...m, doi: e.target.value }))}
            />
            <Input
              placeholder="Year"
              type="number"
              value={manual.year}
              onChange={(e) => setManual((m) => ({ ...m, year: e.target.value }))}
              className="w-28"
            />
          </div>
          <Input
            placeholder="Authors"
            value={manual.authors}
            onChange={(e) => setManual((m) => ({ ...m, authors: e.target.value }))}
          />
          {manualDuplicate && (
            <div className="flex items-center justify-between gap-2 rounded-md border border-danger/30 bg-danger/10 px-2 py-1.5 text-xs text-danger">
              <span className="flex items-center gap-1.5">
                <AlertTriangle size={13} /> Possible duplicate of "{manualDuplicate.matched_title}"
              </span>
              <Button
                type="button"
                variant="ghost"
                className="!px-2 !py-1 text-danger"
                onClick={() =>
                  createPaper.mutate(
                    {
                      title: manual.title.trim(),
                      abstract: manual.abstract.trim() || null,
                      doi: manual.doi.trim() || null,
                      authors: manual.authors.trim() || null,
                      year: manual.year ? parseInt(manual.year, 10) : null,
                      source: 'manual',
                      force: true,
                    },
                    { onSuccess: (result) => result.paper && onClose() }
                  )
                }
              >
                Add anyway
              </Button>
            </div>
          )}
          <div className="mt-1 flex justify-end">
            <Button type="submit" variant="primary" disabled={!manual.title.trim() || createPaper.isPending}>
              {createPaper.isPending ? <Spinner className="h-4 w-4" /> : 'Add paper'}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  )
}
