import type { ReactNode } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Lock } from 'lucide-react'
import ThemeToggle from '../components/ThemeToggle'
import HelpLink from '../components/HelpLink'
import PlanTextBox from '../components/PlanTextBox'
import { Badge, Card, SectionHeading, Spinner } from '../components/ui'
import { useReviewPlan, useUpdateReviewPlan } from '../hooks/useReviewPlan'
import { useFieldMutations } from '../hooks/useTagFields'
import { percentLabel } from '../format'
import { ADHERENCE_FIELD, PLAN_PROMPTS, PLAN_SECTIONS } from '../reviewPlanCopy'
import type { TagField, TagOption } from '../types'

/**
 * The written sections shown before the generated ones. "Anything else" comes
 * last, after the fields and tags, because it is the catch-all.
 */
const LEADING_SECTIONS = PLAN_SECTIONS.filter((key) => key !== 'other')

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} className="scroll-mt-8">
      <h2 className="font-serif text-xl text-text">{title}</h2>
      <div className="mt-3 flex flex-col gap-3 text-sm leading-relaxed text-text">{children}</div>
    </section>
  )
}

/** The weight a tag carries, shown so the reasoning and the number sit together. */
function WeightNote({ weight }: { weight: number }) {
  return <span className="text-xs text-text-muted">weight {weight}</span>
}

/** A tag and its subtopics, indented one step per level, as the tag panel does. */
function TagBoxes({
  option,
  depth,
  onSave,
}: {
  option: TagOption
  depth: number
  onSave: (optionId: number, description: string) => void
}) {
  return (
    <div className="flex flex-col gap-2" style={{ marginLeft: depth * 18 }}>
      <div className="flex items-baseline gap-2">
        <span className="text-sm font-medium text-text">{option.value}</span>
        <WeightNote weight={option.weight} />
      </div>
      <PlanTextBox
        id={`option-${option.id}`}
        value={option.description}
        rows={2}
        placeholder={`What makes a paper "${option.value}"?`}
        onSave={(description) => onSave(option.id, description)}
      />
      {option.children.map((child) => (
        <TagBoxes key={child.id} option={child} depth={depth + 1} onSave={onSave} />
      ))}
    </div>
  )
}

function FieldBlock({
  field,
  onSaveField,
  onSaveOption,
}: {
  field: TagField
  onSaveField: (fieldId: number, description: string) => void
  onSaveOption: (optionId: number, description: string) => void
}) {
  return (
    <Card className="p-5">
      <SectionHeading className="mb-3">
        {field.is_protected && <Lock size={13} className="text-text-muted" />}
        {field.name}
      </SectionHeading>
      <PlanTextBox
        id={`field-${field.id}`}
        value={field.description}
        rows={2}
        placeholder="What does this field ask of a paper?"
        onSave={(description) => onSaveField(field.id, description)}
      />
      {field.options.length > 0 && (
        <div className="mt-4 flex flex-col gap-4 border-t border-border pt-4">
          {field.options.map((option) => (
            <TagBoxes key={option.id} option={option} depth={0} onSave={onSaveOption} />
          ))}
        </div>
      )}
    </Card>
  )
}

export default function ReviewPlanPage() {
  const { projectId: projectIdParam } = useParams()
  const projectId = Number(projectIdParam)
  const { data: plan, isLoading } = useReviewPlan(projectId)
  const updatePlan = useUpdateReviewPlan(projectId)
  const { describeField, updateOption } = useFieldMutations(projectId)

  if (isLoading || !plan) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spinner className="h-6 w-6 text-text-muted" />
      </div>
    )
  }

  const adherence = plan.fields.find((f) => f.name === ADHERENCE_FIELD)
  const otherFields = plan.fields.filter((f) => f.name !== ADHERENCE_FIELD)
  const percent = percentLabel(plan.filled, plan.total)
  const complete = plan.filled >= plan.total

  const saveOption = (optionId: number, description: string) => {
    const field = plan.fields.find((f) => containsOption(f, optionId))
    if (field) updateOption.mutate({ fieldId: field.id, optionId, description })
  }

  const contents: [string, string][] = [
    ...LEADING_SECTIONS.map((key) => [key, PLAN_PROMPTS[key].title] as [string, string]),
    ...(adherence ? ([['adherence', 'What counts as adherent']] as [string, string][]) : []),
    ...(otherFields.length > 0
      ? ([['fields', 'What the fields and tags mean']] as [string, string][])
      : []),
    ['other', PLAN_PROMPTS.other.title],
  ]

  return (
    <div>
      <nav className="flex items-center justify-between border-b border-border px-8 py-4">
        <div className="flex items-center gap-3">
          <Link
            to={`/projects/${projectId}`}
            className="text-text-muted hover:text-text"
            aria-label="Back to the review"
          >
            <ArrowLeft size={18} />
          </Link>
          <span className="font-serif text-lg text-text">{plan.project_name}</span>
        </div>
        <div className="flex items-center gap-2">
          <HelpLink />
          <ThemeToggle />
        </div>
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="font-serif text-3xl leading-tight text-text">Review plan</h1>
        <p className="mt-3 text-text-muted">
          What you are trying to find out, and how you decide. Writing it down once keeps the
          judgements you make on paper 200 the same as the ones you made on paper 1.
        </p>

        <Card className="mt-8 p-5">
          <div className="mb-3 flex items-center justify-between gap-3">
            <span className="text-sm text-text">
              {plan.filled} of {plan.total} written
              {percent !== null && <span className="ml-1.5 font-medium">{percent}</span>}
            </span>
            {complete ? (
              <Badge tone="accent">Complete</Badge>
            ) : (
              <Badge tone="warning">Incomplete</Badge>
            )}
          </div>
          <nav aria-label="Contents">
            <ul className="flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
              {contents.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`} className="text-accent hover:underline">
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
          <p className="mt-3 text-xs text-text-muted">
            Nothing here is required, and everything saves as you leave a box. The count covers the
            five written sections, a note on each field, and what each level of Adherence means.
            Describing individual tags is optional, and shows up beside them while you tag.
          </p>
        </Card>

        <div className="mt-10 flex flex-col gap-10">
          {LEADING_SECTIONS.map((key) => (
            <Section key={key} id={key} title={PLAN_PROMPTS[key].title}>
              <p className="text-text-muted">{PLAN_PROMPTS[key].prompt}</p>
              <PlanTextBox
                id={`section-${key}`}
                value={plan[key]}
                placeholder={PLAN_PROMPTS[key].placeholder}
                onSave={(value) => updatePlan.mutate({ [key]: value })}
              />
            </Section>
          ))}

          {adherence && (
            <Section id="adherence" title="What counts as adherent">
              <p className="text-text-muted">
                Adherence is the field that decides whether a paper survives the review, so it is
                worth being exact about its three levels. This is the judgement that drifts most as
                a long review goes on.
              </p>
              <FieldBlock
                field={adherence}
                onSaveField={(fieldId, description) =>
                  describeField.mutate({ fieldId, description })
                }
                onSaveOption={saveOption}
              />
            </Section>
          )}

          {otherFields.length > 0 && (
            <Section id="fields" title="What the fields and tags mean">
              <p className="text-text-muted">
                One block per field, generated from this review's own fields and tags, so a tag you
                add later turns up here on its own. Each tag's weight is shown beside it; the
                reasoning behind the numbers belongs in the section above.
              </p>
              <div className="flex flex-col gap-4">
                {otherFields.map((field) => (
                  <FieldBlock
                    key={field.id}
                    field={field}
                    onSaveField={(fieldId, description) =>
                      describeField.mutate({ fieldId, description })
                    }
                    onSaveOption={saveOption}
                  />
                ))}
              </div>
            </Section>
          )}

          <Section id="other" title={PLAN_PROMPTS.other.title}>
            <p className="text-text-muted">{PLAN_PROMPTS.other.prompt}</p>
            <PlanTextBox
              id="section-other"
              value={plan.other}
              placeholder={PLAN_PROMPTS.other.placeholder}
              onSave={(value) => updatePlan.mutate({ other: value })}
            />
          </Section>
        </div>
      </div>
    </div>
  )
}

/** Whether a tag with this id sits anywhere in the field's tree. */
function containsOption(field: TagField, optionId: number): boolean {
  const walk = (options: TagOption[]): boolean =>
    options.some((o) => o.id === optionId || walk(o.children))
  return walk(field.options)
}
