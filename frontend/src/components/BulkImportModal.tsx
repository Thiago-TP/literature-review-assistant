import { useRef, useState } from 'react'
import { UploadCloud } from 'lucide-react'
import Modal from './Modal'
import DuplicateReviewList from './DuplicateReviewList'
import { Button, Spinner } from './ui'
import { importApi } from '../api/importPapers'
import { useQueryClient } from '@tanstack/react-query'
import type { ImportPreviewResponse } from '../types'
import { ApiError } from '../api/client'

export default function BulkImportModal({ projectId, onClose }: { projectId: number; onClose: () => void }) {
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null)
  const [actions, setActions] = useState<Record<number, 'add' | 'skip'>>({})
  const [loading, setLoading] = useState(false)
  const [committing, setCommitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<{ added: number; skipped: number } | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setError(null)
    setLoading(true)
    try {
      const response = await importApi.preview(projectId, file)
      setPreview(response)
      setActions(Object.fromEntries(response.rows.map((r) => [r.row_index, r.default_action])))
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to read the file')
    } finally {
      setLoading(false)
    }
  }

  async function handleCommit() {
    if (!preview) return
    setCommitting(true)
    try {
      const response = await importApi.commit(projectId, preview.rows, actions)
      setResult({ added: response.added_count, skipped: response.skipped_count })
      queryClient.invalidateQueries({ queryKey: ['projects', projectId, 'papers'] })
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to import')
    } finally {
      setCommitting(false)
    }
  }

  return (
    <Modal title="Import spreadsheet (.xlsx or .csv)" onClose={onClose} wide>
      {!preview && !result && (
        <div>
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex w-full flex-col items-center gap-2 rounded-lg border-2 border-dashed border-border py-10 text-text-muted hover:border-accent hover:text-accent"
          >
            <UploadCloud size={28} />
            <span className="text-sm">
              {loading ? 'Processing...' : 'Click to choose an .xlsx or .csv file (Scopus, WoS, etc.)'}
            </span>
            {loading && <Spinner className="h-5 w-5" />}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.csv"
            className="hidden"
            onChange={handleFileChange}
          />
          {error && <p className="mt-3 text-sm text-danger">{error}</p>}
        </div>
      )}

      {preview && !result && (
        <div>
          <p className="mb-3 text-sm text-text-muted">
            <strong className="text-text">{preview.new_count}</strong> new ·{' '}
            <strong className="text-text">{preview.duplicate_count}</strong> possible duplicate(s) — unchecked by
            default, review before confirming.
          </p>
          <DuplicateReviewList
            rows={preview.rows}
            actions={actions}
            onToggle={(rowIndex, checked) =>
              setActions((prev) => ({ ...prev, [rowIndex]: checked ? 'add' : 'skip' }))
            }
          />
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
          <div className="mt-4 flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setPreview(null)} disabled={committing}>
              Choose another file
            </Button>
            <Button variant="primary" onClick={handleCommit} disabled={committing}>
              {committing ? <Spinner className="h-4 w-4" /> : 'Confirm import'}
            </Button>
          </div>
        </div>
      )}

      {result && (
        <div className="text-center">
          <p className="text-sm text-text">
            <strong>{result.added}</strong> paper(s) added, <strong>{result.skipped}</strong> skipped.
          </p>
          <Button variant="primary" className="mt-4" onClick={onClose}>
            Close
          </Button>
        </div>
      )}
    </Modal>
  )
}
