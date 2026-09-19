import { useMemo, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Search, Star } from 'lucide-react'
import { useProject, useSetLastViewed } from '../hooks/useProjects'
import { useDashboard } from '../hooks/useDashboard'
import { usePapers } from '../hooks/usePapers'
import { Card, EmptyState, Input, Label, SECTION_HEADING_GAP, SectionHeading, Spinner } from '../components/ui'
import ThemeToggle from '../components/ThemeToggle'
import HelpLink from '../components/HelpLink'
import {
  percentLabel,
  ratingHint,
  scoreHint,
  scorePartsFromTotals,
  trimScale,
} from '../format'

function StatTile({
  label,
  value,
  percent,
  hint,
}: {
  label: string
  value: string
  /** Only for tiles whose value is a share of something. */
  percent?: string | null
  hint?: string
}) {
  return (
    // h-full + justify-between so the numbers line up across the row even
    // where a longer label wraps to two lines.
    <Card className="flex h-full flex-col justify-between p-5" title={hint}>
      <Label>{label}</Label>
      <p className="mt-1.5 flex items-baseline gap-1.5 font-serif text-2xl text-text">
        {value}
        {percent && <span className="font-sans text-sm font-medium text-text-muted">{percent}</span>}
      </p>
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
        <div className="flex items-center gap-2">
          <HelpLink />
          <ThemeToggle />
        </div>
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
                percent={percentLabel(stats.fully_tagged_count, stats.total_papers)}
              />
              <StatTile
                label="Rated"
                value={`${stats.rated_count}/${stats.total_papers}`}
                percent={percentLabel(stats.rated_count, stats.total_papers)}
              />
              <StatTile
                label="With notes"
                value={`${stats.with_notes_count}/${stats.total_papers}`}
                percent={percentLabel(stats.with_notes_count, stats.total_papers)}
              />
              <StatTile
                label="Average rating"
                value={
                  stats.average_rating !== null
                    ? `${stats.average_rating.toFixed(1)}/${trimScale(stats.max_rating)}`
                    : '—'
                }
                percent={
                  stats.average_rating !== null
                    ? percentLabel(stats.average_rating, stats.max_rating)
                    : null
                }
                hint={
                  stats.average_rating !== null
                    ? `Out of a fixed scale of ${trimScale(stats.max_rating)}, averaged over the ${stats.rated_count} rated ${stats.rated_count === 1 ? 'paper' : 'papers'} only. Rating is your own judgement; nothing in the app sets it.`
                    : 'No paper has been rated yet. Rating is your own judgement of a paper, zero to five stars.'
                }
              />
              <StatTile
                label="Average score"
                value={
                  stats.max_score > 0
                    ? `${stats.average_score.toFixed(1)}/${trimScale(stats.max_score)}`
                    : stats.average_score.toFixed(1)
                }
                percent={percentLabel(stats.average_score, stats.max_score)}
                hint={
                  stats.max_score > 0
                    ? 'Out of the highest score in this review. A paper scores the weights of its tags plus its rating.'
                    : undefined
                }
              />
            </div>

            <Card className="p-5">
              <SectionHeading as="h2" className={SECTION_HEADING_GAP}>
                Tag distribution
              </SectionHeading>
              {stats.tag_distribution.length === 0 ? (
                <p className="text-sm text-text-muted">No tags assigned yet.</p>
              ) : (
                <div className="flex flex-col gap-2.5">
                  {stats.tag_distribution.map((entry) => (
                    <div key={entry.option_id} className="flex items-center gap-3">
                      <div className="w-56 shrink-0 truncate text-xs text-text-muted" title={entry.option_path}>
                        <span className="text-text">{entry.field_name}</span>
                        {' · '}
                        {entry.option_path}
                      </div>
                      <div className="flex-1 rounded bg-surface-muted">
                        <div
                          className="flex h-3.5 items-center justify-end rounded-r bg-accent pr-1.5"
                          style={{ width: `${(entry.count / maxCount) * 100}%` }}
                        >
                          <span className="text-[10px] font-medium text-accent-fg">{entry.count}</span>
                        </div>
                      </div>
                      {entry.weight !== 0 && (
                        <span className="w-20 shrink-0 whitespace-nowrap text-right text-xs text-text-muted">
                          weight {entry.weight}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </Card>

            <Card className="p-5">
              <SectionHeading as="h2" className={SECTION_HEADING_GAP}>
                Top papers by score
              </SectionHeading>
              <div className="flex flex-col divide-y divide-border">
                {stats.top_papers.map((p, i) => (
                  <button
                    key={p.id}
                    onClick={() => openPaper(p.id)}
                    className="flex items-center gap-3 py-2.5 text-left hover:bg-surface-muted"
                  >
                    <span className="w-5 shrink-0 text-xs text-text-muted">{i + 1}</span>
                    <span className="flex-1 truncate text-sm text-text">{p.title}</span>
                    {p.rating !== null && (
                      <span
                        className="flex items-center gap-0.5 text-xs text-text-muted"
                        title={ratingHint(p.rating)}
                      >
                        <Star size={12} fill="currentColor" /> {p.rating}
                      </span>
                    )}
                    <span
                      className="w-16 shrink-0 text-right text-sm font-semibold text-text"
                      title={scoreHint(p.score, scorePartsFromTotals(p.score, p.rating))}
                    >
                      {p.score}
                    </span>
                  </button>
                ))}
              </div>
            </Card>

            <Card className="p-5">
              <div className={`flex items-center justify-between gap-3 ${SECTION_HEADING_GAP}`}>
                <SectionHeading as="h2">All papers</SectionHeading>
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
              <div className="flex flex-col divide-y divide-border">
                <div className="flex items-center gap-3 pb-2 text-xs text-text-muted">
                  <span className="flex-1">Title</span>
                  <span className="w-20 text-right">Tags</span>
                  <span
                    className="w-16 text-right"
                    title="Your own judgement of a paper, zero to five stars. A dash means it is not rated yet."
                  >
                    Rating
                  </span>
                  <span
                    className="w-16 text-right"
                    title="Score is the weights of a paper's tags plus its rating. Hover a number to see the split."
                  >
                    Score
                  </span>
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
                    <span
                      className="w-16 shrink-0 text-right text-xs text-text-muted"
                      title={ratingHint(p.rating)}
                    >
                      {p.rating ?? '—'}
                    </span>
                    <span
                      className="w-16 shrink-0 text-right text-sm font-medium text-text"
                      title={scoreHint(p.score, scorePartsFromTotals(p.score, p.rating))}
                    >
                      {p.score}
                    </span>
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
