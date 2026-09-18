import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, FilePlus, LayoutDashboard, UploadCloud } from 'lucide-react'
import { useProject, useSetLastViewed } from '../hooks/useProjects'
import { usePaper, usePapers, useRating, useToggleTag, useUpdatePaper } from '../hooks/usePapers'
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
  const setLastViewed = useSetLastViewed(projectId)
  const updatePaper = useUpdatePaper(projectId)
  const toggleTag = useToggleTag(projectId)
  const rating = useRating(projectId)

  const [currentPaperId, setCurrentPaperId] = useState<number | null>(null)
  const [initialized, setInitialized] = useState(false)
  const [showImportModal, setShowImportModal] = useState(false)
  const [showAddPaperModal, setShowAddPaperModal] = useState(false)

  useEffect(() => {
    if (initialized || !project || !papers) return
    if (papers.length === 0) {
      setInitialized(true)
      return
    }
    const candidate = papers.find((p) => p.id === project.last_viewed_paper_id) ?? papers[0]
    setCurrentPaperId(candidate.id)
    setInitialized(true)
  }, [initialized, project, papers])

  const { data: paper } = usePaper(projectId, currentPaperId)

  function goToPaperId(paperId: number) {
    setCurrentPaperId(paperId)
    setLastViewed.mutate(paperId)
  }

  function goToIndex(index: number) {
    if (!papers || index < 0 || index >= papers.length) return
    goToPaperId(papers[index].id)
  }

  if (!project || papersLoading || !fields) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-6 w-6 text-text-muted" />
      </div>
    )
  }

  const currentIndex = papers?.findIndex((p) => p.id === currentPaperId) ?? -1

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
              </Card>

              <Card className="p-5">
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
