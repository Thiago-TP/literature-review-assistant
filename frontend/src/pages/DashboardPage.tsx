import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Search, Star } from 'lucide-react'
import { useProject, useSetLastViewed } from '../hooks/useProjects'
import { useDashboard } from '../hooks/useDashboard'
import { usePapers } from '../hooks/usePapers'
import { Card, EmptyState, Input, Label, Spinner } from '../components/ui'
import ThemeToggle from '../components/ThemeToggle'

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <Card className="p-4">
      <Label>{label}</Label>
      <p className="mt-1.5 font-serif text-2xl text-text">{value}</p>
    </Card>
  )
}

function truncate(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max)}…` : text
}

export default function DashboardPage() {
  const { projectId: projectIdParam } = useParams()
  const projectId = Number(projectIdParam)
  const navigate = useNavigate()

  const { data: project } = useProject(projectId)
  const { data: stats, isLoading } = useDashboard(projectId)
  const { data: papers } = usePapers(projectId)
  const setLastViewed = useSetLastViewed(projectId)
  const [query, setQuery] = useState('')

  function openPaper(paperId: number) {
    setLastViewed.mutate(paperId, {
      onSuccess: () => navigate(`/projects/${projectId}`),
    })
  }

  const filteredPapers = useMemo(() => {
    const sorted = (papers ?? []).slice().sort((a, b) => b.score - a.score)
    const q = query.trim().toLowerCase()
    if (!q) return sorted
    return sorted.filter(
      (p) => p.title.toLowerCase().includes(q) || p.notes.toLowerCase().includes(q)
    )
  }, [papers, query])

  if (!project || isLoading || !stats) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-6 w-6 text-text-muted" />
      </div>
    )
  }

  const maxCount = Math.max(1, ...stats.tag_distribution.map((e) => e.count))

  return (
    <div>
      <nav className="flex items-center justify-between border-b border-border px-8 py-4">
        <div className="flex items-center gap-3">
          <Link to={`/projects/${projectId}`} className="text-text-muted hover:text-text" aria-label="Back to the review">
            <ArrowLeft size={18} />
          </Link>
          <span className="font-serif text-lg text-text">{project.name} — Dashboard</span>
        </div>
        <ThemeToggle />
      </nav>

      <div className="mx-auto max-w-5xl px-6 py-8">
        {stats.total_papers === 0 ? (
          <EmptyState
            title="Nothing to analyse yet"
            description="Import or add papers, then assign tags and write notes to see the data here."
          />
        ) : (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
              <StatTile label="Papers" value={String(stats.total_papers)} />
              <StatTile
                label="Fully tagged"
                value={`${stats.fully_tagged_count}/${stats.total_papers}`}
              />
              <StatTile label="Rated" value={`${stats.rated_count}/${stats.total_papers}`} />
              <StatTile label="With notes" value={`${stats.with_notes_count}/${stats.total_papers}`} />
              <StatTile
                label="Average rating"
                value={stats.average_rating !== null ? stats.average_rating.toFixed(1) : '—'}
              />
              <StatTile label="Average score" value={stats.average_score.toFixed(1)} />
            </div>

            <Card className="p-5">
              <Label>Tag distribution</Label>
              {stats.tag_distribution.length === 0 ? (
                <p className="mt-3 text-sm text-text-muted">No tags assigned yet.</p>
              ) : (
                <div className="mt-4 flex flex-col gap-2.5">
                  {stats.tag_distribution.map((entry) => (
                    <div key={entry.option_id} className="flex items-center gap-3">
                      <div className="w-56 shrink-0 truncate text-xs text-text-muted" title={entry.option_path}>
                        <span className="text-text">{entry.field_name}</span>
                        {' · '}
                        {entry.option_path}
                      </div>
                      <div className="flex-1 bg-surface-muted">
                        <div
                          className="flex h-3.5 items-center justify-end rounded-r bg-accent pr-1.5"
                          style={{ width: `${(entry.count / maxCount) * 100}%` }}
                        >
                          <span className="text-[10px] font-medium text-accent-fg">{entry.count}</span>
                        </div>
                      </div>
                      {entry.weight !== 0 && (
                        <span className="w-14 shrink-0 text-right text-xs text-text-muted">
                          weight {entry.weight}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </Card>

            <Card className="p-5">
              <Label>Top papers by score</Label>
              <div className="mt-3 flex flex-col divide-y divide-border">
                {stats.top_papers.map((p, i) => (
                  <button
                    key={p.id}
                    onClick={() => openPaper(p.id)}
                    className="flex items-center gap-3 py-2.5 text-left hover:bg-surface-muted"
                  >
                    <span className="w-5 shrink-0 text-xs text-text-muted">{i + 1}</span>
                    <span className="flex-1 truncate text-sm text-text">{p.title}</span>
                    {p.rating !== null && (
                      <span className="flex items-center gap-0.5 text-xs text-text-muted">
                        <Star size={12} fill="currentColor" /> {p.rating}
                      </span>
                    )}
                    <span className="w-16 shrink-0 text-right text-sm font-semibold text-text">{p.score}</span>
                  </button>
                ))}
              </div>
            </Card>

            <Card className="p-5">
              <div className="flex items-center justify-between gap-3">
                <Label>All papers</Label>
                <div className="relative w-64">
                  <Search size={14} className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-text-muted" />
                  <Input
                    placeholder="Search by title or notes..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
              <div className="mt-3 flex flex-col divide-y divide-border">
                <div className="flex items-center gap-3 pb-2 text-xs text-text-muted">
                  <span className="flex-1">Title</span>
                  <span className="w-20 text-right">Tags</span>
                  <span className="w-16 text-right">Rating</span>
                  <span className="w-16 text-right">Score</span>
                </div>
                {filteredPapers.length === 0 && (
                  <p className="py-4 text-sm text-text-muted">No papers found for "{query}".</p>
                )}
                {filteredPapers.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => openPaper(p.id)}
                    className="flex items-center gap-3 py-2 text-left hover:bg-surface-muted"
                  >
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm text-text">{p.title}</span>
                      {p.notes.trim() && (
                        <span className="block truncate text-xs text-text-muted">{truncate(p.notes, 100)}</span>
                      )}
                    </span>
                    <span className="w-20 shrink-0 text-right text-xs text-text-muted">
                      {p.filled_field_count}/{p.total_field_count}
                    </span>
                    <span className="w-16 shrink-0 text-right text-xs text-text-muted">{p.rating ?? '—'}</span>
                    <span className="w-16 shrink-0 text-right text-sm font-medium text-text">{p.score}</span>
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
