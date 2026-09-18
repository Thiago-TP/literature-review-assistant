import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { useCreateProject, useDeleteProject, useProjects, useRenameProject } from '../hooks/useProjects'
import { Button, Card, EmptyState, Input, Label, Spinner } from '../components/ui'
import ThemeToggle from '../components/ThemeToggle'
import type { Project } from '../types'

function ProjectRow({ project, onOpen }: { project: Project; onOpen: () => void }) {
  const [renaming, setRenaming] = useState(false)
  const [name, setName] = useState(project.name)
  const renameProject = useRenameProject(project.id)
  const deleteProject = useDeleteProject()

  if (renaming) {
    return (
      <Card className="p-4">
        <form
          className="flex gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            const trimmed = name.trim()
            if (!trimmed) return
            renameProject.mutate(trimmed, { onSuccess: () => setRenaming(false) })
          }}
        >
          <Input value={name} onChange={(e) => setName(e.target.value)} autoFocus />
          <Button type="submit" variant="primary">
            Save
          </Button>
          <Button type="button" variant="secondary" onClick={() => setRenaming(false)}>
            Cancel
          </Button>
        </form>
      </Card>
    )
  }

  return (
    <Card className="flex items-center justify-between p-4">
      <button className="flex-1 text-left" onClick={onOpen}>
        <p className="font-serif text-base text-text">{project.name}</p>
        <p className="mt-0.5 text-sm text-text-muted">
          {project.paper_count} {project.paper_count === 1 ? 'paper' : 'papers'} · updated{' '}
          {new Date(project.updated_at).toLocaleDateString()}
        </p>
      </button>
      <div className="flex gap-1">
        <Button variant="ghost" aria-label="Rename review" onClick={() => setRenaming(true)}>
          <Pencil size={16} />
        </Button>
        <Button
          variant="ghost"
          aria-label="Delete review"
          onClick={() => {
            if (confirm(`Delete the review "${project.name}"? This cannot be undone.`)) {
              deleteProject.mutate(project.id)
            }
          }}
        >
          <Trash2 size={16} />
        </Button>
      </div>
    </Card>
  )
}

export default function ProjectListPage() {
  const { data: projects, isLoading } = useProjects()
  const createProject = useCreateProject()
  const [newName, setNewName] = useState('')
  const navigate = useNavigate()

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    const name = newName.trim()
    if (!name) return
    createProject.mutate(name, {
      onSuccess: (project) => {
        setNewName('')
        navigate(`/projects/${project.id}`)
      },
    })
  }

  return (
    <div>
      <nav className="flex items-center justify-between border-b border-border px-8 py-4">
        <span className="font-serif text-lg text-text">Literature Review Assistant</span>
        <ThemeToggle />
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-16">
        <Label>Literature Review Assistant</Label>
        <h1 className="mt-3 font-serif text-4xl leading-tight text-text sm:text-5xl">
          Your reviews, <span className="italic text-accent">always saved</span>.
        </h1>
        <p className="mt-4 max-w-xl text-text-muted">
          Create a review, import papers, and assess them one at a time. Everything is saved automatically —
          close the app and pick up where you left off.
        </p>

        <Card className="mt-10 p-4">
          <form onSubmit={handleCreate} className="flex gap-2">
            <Input
              placeholder="Name of the new review (e.g. Review on XYZ)"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
            <Button type="submit" variant="primary" disabled={!newName.trim() || createProject.isPending}>
              <Plus size={14} />
              Create
            </Button>
          </form>
        </Card>

        {isLoading && (
          <div className="flex justify-center py-12 text-text-muted">
            <Spinner className="h-6 w-6" />
          </div>
        )}

        {!isLoading && projects && projects.length === 0 && (
          <div className="mt-6">
            <EmptyState
              title="No reviews yet"
              description="Create a review above to start importing and assessing papers."
            />
          </div>
        )}

        <div className="mt-6 flex flex-col gap-3">
          {projects?.map((project) => (
            <ProjectRow key={project.id} project={project} onOpen={() => navigate(`/projects/${project.id}`)} />
          ))}
        </div>
      </div>
    </div>
  )
}
