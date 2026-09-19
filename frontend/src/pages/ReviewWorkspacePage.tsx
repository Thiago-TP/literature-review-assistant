import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, FilePlus, LayoutDashboard, UploadCloud } from 'lucide-react'
import { useProject, useRememberLastViewed } from '../hooks/useProjects'
import {
  usePaper,
  usePapers,
  usePrefetchAdjacentPapers,
  useRating,
  useToggleTag,
  useUpdatePaper,
} from '../hooks/usePapers'
import { useTagFields } from '../hooks/useTagFields'
import ProgressOverview from '../components/ProgressOverview'
import PaperNav from '../components/PaperNav'
import PaperDisplay from '../components/PaperDisplay'
import TagFieldPanel from '../components/TagFieldPanel'
import NotesPanel from '../components/NotesPanel'
import FieldManagementPanel from '../components/FieldManagementPanel'
import BulkImportModal from '../components/BulkImportModal'
import AddPaperModal from '../components/AddPaperModal'
import StarRating from '../components/StarRating'
import { Button, Card, EmptyState, Label, Spinner, StepBadge } from '../components/ui'
import ThemeToggle from '../components/ThemeToggle'

export default function ReviewWorkspacePage() {
  const { projectId: projectIdParam } = useParams()
  const projectId = Number(projectIdParam)

  const { data: project } = useProject(projectId)
  const { data: papers, isLoading: papersLoading } = usePapers(projectId)
  const { data: fields } = useTagFields(projectId)
  const rememberLastViewed = useRememberLastViewed(projectId)
  const updatePaper = useUpdatePaper(projectId)
  const toggleTag = useToggleTag(projectId)
  const rating = useRating(projectId)

  const [currentPaperId, setCurrentPaperId] = useState<number | null>(null)
  const [showImportModal, setShowImportModal] = useState(false)
  const [showAddPaperModal, setShowAddPaperModal] = useState(false)

  // Settle on a paper whenever there are papers but none open. Deliberately
  // not a run-once-on-mount effect: a project that was empty when the
  // workspace mounted -- a brand new review, which is every review right
  // after it is created -- would otherwise stay on no paper once the import
  // landed, leaving the reviewer to click a tile to start. It also recovers
  // when the open paper is deleted out from under us.
  useEffect(() => {
    if (!project || !papers || papers.length === 0) return
    if (currentPaperId !== null && papers.some((paper) => paper.id === currentPaperId)) return
    const candidate = papers.find((paper) => paper.id === project.last_viewed_paper_id) ?? papers[0]
    setCurrentPaperId(candidate.id)
  }, [project, papers, currentPaperId])

  const { data: paper, isPlaceholderData } = usePaper(projectId, currentPaperId)
  const currentIndex = papers?.findIndex((p) => p.id === currentPaperId) ?? -1

  usePrefetchAdjacentPapers(projectId, papers, currentIndex)

  // While the next paper loads we keep the previous one on screen rather than
  // blanking the workspace. Fade it and lock it so a click can't land a rating
  // or a tag on the paper being navigated away from.
  const staleClass = isPlaceholderData ? 'pointer-events-none opacity-50 transition-opacity' : 'transition-opacity'

  function goToPaperId(paperId: number) {
    setCurrentPaperId(paperId)
    rememberLastViewed(paperId)
  }

  function goToIndex(index: number) {
    if (!papers || index < 0 || index >= papers.length) return
    goToPaperId(papers[index].id)
  }

  // Left/right arrows step through papers, mirroring the "<" and ">" buttons.
  // Skipped while typing, while a modal is open, and for modified presses, so
  // they never steal a keystroke meant for a field or the browser.
  const modalOpen = showImportModal || showAddPaperModal
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return
      if (event.metaKey || event.ctrlKey || event.altKey || modalOpen) return
      const target = event.target as HTMLElement | null
      if (target?.isContentEditable) return
      if (target && ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)) return
      if (!papers || currentIndex < 0) return

      const next = currentIndex + (event.key === 'ArrowRight' ? 1 : -1)
      if (next < 0 || next >= papers.length) return
      event.preventDefault()
      setCurrentPaperId(papers[next].id)
      rememberLastViewed(papers[next].id)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [papers, currentIndex, modalOpen, rememberLastViewed])

  if (!project || papersLoading || !fields) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-6 w-6 text-text-muted" />
      </div>
    )
  }

  return (
    <div>
      <nav className="flex items-center justify-between border-b border-border px-8 py-4">
        <div className="flex items-center gap-3">
          <Link to="/" className="text-text-muted hover:text-text" aria-label="Back to reviews">
            <ArrowLeft size={18} />
          </Link>
          <span className="font-serif text-lg text-text">{project.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <Link to={`/projects/${projectId}/dashboard`}>
            <Button variant="secondary">
              <LayoutDashboard size={15} /> Dashboard
            </Button>
          </Link>
          <Button variant="secondary" onClick={() => setShowImportModal(true)}>
            <UploadCloud size={15} /> Import spreadsheet
          </Button>
          <Button variant="secondary" onClick={() => setShowAddPaperModal(true)}>
            <FilePlus size={15} /> Add paper
          </Button>
          <ThemeToggle />
        </div>
      </nav>

      <div className="mx-auto max-w-5xl px-6 py-8">
      {papers && papers.length === 0 ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[1fr_auto]">
          <EmptyState
            title="No papers in this review yet"
            description="Import a spreadsheet (.xlsx) or add individual papers by DOI, title, or manually."
            action={
              <div className="flex gap-2">
                <Button variant="secondary" onClick={() => setShowImportModal(true)}>
                  <UploadCloud size={15} /> Import spreadsheet
                </Button>
                <Button variant="primary" onClick={() => setShowAddPaperModal(true)}>
                  <FilePlus size={15} /> Add paper
                </Button>
              </div>
            }
          />
          <Card className="w-full p-5 md:w-80">
            <Label>How it works</Label>
            <div className="mt-4 flex flex-col gap-4">
              <div className="flex items-start gap-3">
                <StepBadge n={1} tone="a" />
                <div>
                  <p className="text-sm font-medium text-text">Add papers</p>
                  <p className="text-xs text-text-muted">Import a spreadsheet or search by DOI/title.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <StepBadge n={2} tone="b" />
                <div>
                  <p className="text-sm font-medium text-text">Review one at a time</p>
                  <p className="text-xs text-text-muted">Read the abstract, assign tags, write notes.</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <StepBadge n={3} tone="c" />
                <div>
                  <p className="text-sm font-medium text-text">Progress saved</p>
                  <p className="text-xs text-text-muted">Everything is saved automatically.</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      ) : (
        <div className="flex flex-col gap-6">
          <Card className="p-4">
            <ProgressOverview papers={papers ?? []} currentPaperId={currentPaperId} onSelect={goToPaperId} />
          </Card>

          {paper && (
            <>
              <Card className="p-5">
                <PaperNav currentIndex={currentIndex} total={papers?.length ?? 0} onGoTo={goToIndex} />
                <div className={staleClass}>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-y border-border py-3">
                  <div className="flex items-center gap-2">
                    <Label>Your rating</Label>
                    <StarRating
                      rating={paper.rating}
                      onChange={(value) => rating.mutate({ paperId: paper.id, rating: value })}
                    />
                    {paper.rating !== null && (
                      <span className="text-xs text-text-muted">{paper.rating}/5</span>
                    )}
                  </div>
                  <p className="text-sm text-text-muted">
                    Score: <span className="font-semibold text-text">{paper.score}</span>
                  </p>
                </div>
                <div className="mt-4 grid grid-cols-1 gap-6 md:grid-cols-[2fr_1fr]">
                  <PaperDisplay paper={paper} />
                  <TagFieldPanel
                    fields={fields}
                    paper={paper}
                    onToggle={(_fieldId, optionId, checked) =>
                      toggleTag.mutate({ paperId: paper.id, optionId, assign: checked })
                    }
                  />
                </div>
                </div>
              </Card>

              <Card className={`p-5 ${staleClass}`}>
                <NotesPanel
                  paperId={paper.id}
                  notes={paper.notes}
                  onSave={(notes) => updatePaper.mutate({ paperId: paper.id, payload: { notes } })}
                />
              </Card>
            </>
          )}

          <FieldManagementPanel projectId={projectId} fields={fields} />
        </div>
      )}
      </div>

      {showImportModal && (
        <BulkImportModal projectId={projectId} onClose={() => setShowImportModal(false)} />
      )}
      {showAddPaperModal && (
        <AddPaperModal projectId={projectId} onClose={() => setShowAddPaperModal(false)} />
      )}
    </div>
  )
}
