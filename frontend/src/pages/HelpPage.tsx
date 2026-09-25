import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ArrowLeft, Check, Pencil, Star } from 'lucide-react'
import ThemeToggle from '../components/ThemeToggle'
import { Card } from '../components/ui'

function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <section id={id} className="scroll-mt-8">
      <h2 className="font-serif text-xl text-text">{title}</h2>
      <div className="mt-3 flex flex-col gap-3 text-sm leading-relaxed text-text">{children}</div>
    </section>
  )
}

/**
 * A screenshot, in whichever theme the reader is using. Both variants are in
 * the markup and CSS picks one (see index.css) — reading the theme in
 * JavaScript would leave the figure on the old one after a toggle.
 */
function Figure({ name, alt, caption }: { name: string; alt: string; caption: string }) {
  const className = 'w-full rounded-lg border border-border'
  return (
    <figure className="mt-1 flex flex-col gap-2">
      <img src={`/help/${name}-light.png`} alt={alt} className={`${className} figure-light`} loading="lazy" />
      <img src={`/help/${name}-dark.png`} alt={alt} className={`${className} figure-dark`} loading="lazy" />
      <figcaption className="text-xs text-text-muted">{caption}</figcaption>
    </figure>
  )
}

/** A term and its definition, for the pieces of vocabulary the app invents. */
function Term({ name, children }: { name: string; children: ReactNode }) {
  return (
    <div>
      <p className="text-sm font-semibold text-text">{name}</p>
      <p className="text-sm leading-relaxed text-text">{children}</p>
    </div>
  )
}

const CONTENTS = [
  ['what-it-is', 'What this is for'],
  ['getting-started', 'Getting started'],
  ['reviewing', 'Reviewing a paper'],
  ['fields-and-tags', 'Fields and tags'],
  ['review-plan', 'The review plan'],
  ['rating-and-score', 'Rating and score'],
  ['overview', 'The progress overview'],
  ['dashboard', 'The dashboard'],
  ['your-data', 'Where your data lives'],
  ['shortcuts', 'Keyboard shortcuts'],
] as const

export default function HelpPage() {
  // The page the "?" was clicked on, put there by HelpLink. Leaving help
  // should drop the reader back where they were -- on the paper they were
  // reviewing, not at the start of the app. A direct visit to /help carries
  // no such state, so the project list is the fallback.
  const { state } = useLocation()
  const backTo = (state as { from?: string } | null)?.from ?? '/'

  return (
    <div>
      <nav className="flex items-center justify-between border-b border-border px-8 py-4">
        <div className="flex items-center gap-3">
          <Link
            to={backTo}
            replace
            className="text-text-muted hover:text-text"
            aria-label={backTo === '/' ? 'Back to reviews' : 'Back'}
          >
            <ArrowLeft size={18} />
          </Link>
          <span className="font-serif text-lg text-text">Help</span>
        </div>
        <ThemeToggle />
      </nav>

      <div className="mx-auto max-w-3xl px-6 py-10">
        <h1 className="font-serif text-3xl leading-tight text-text">
          How the Literature Review Assistant works
        </h1>
        <p className="mt-3 text-text-muted">
          A short tour of the app: what it is for, how a review runs, and what the numbers mean.
        </p>

        <Card className="mt-8 p-5">
          <nav aria-label="Contents">
            <ul className="flex flex-wrap gap-x-5 gap-y-1.5 text-sm">
              {CONTENTS.map(([id, label]) => (
                <li key={id}>
                  <a href={`#${id}`} className="text-accent hover:underline">
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>
        </Card>

        <div className="mt-10 flex flex-col gap-10">
          <Section id="what-it-is" title="What this is for">
            <p>
              A systematic literature review means going through a long list of papers and making
              the same handful of judgements about each one: is it relevant, what kind of
              contribution is it, what did I think of it, what do I want to remember about it.
            </p>
            <p>
              This app is a place to do that one paper at a time without losing your place. You
              import a list of papers once, then work through them assigning tags, giving a rating
              and writing notes. Everything is saved as you go, to a database (db) file on your own
              machine.
            </p>
            <Figure
              name="workspace"
              alt="The review workspace, showing the progress overview above a single paper with its tags and notes"
              caption="The workspace: progress across the whole review at the top, the paper you are on below it. (Example data.)"
            />
          </Section>

          <Section id="getting-started" title="Getting started">
            <p>
              <strong>1. Create a review.</strong> On the home page, give it a name. Each review is
              independent, i.e., it has its own papers, its own tags, its own progress, so you can keep
              several going at once.
            </p>
            <p>
              <strong>2. Add papers.</strong> Two ways, and you can mix them:
            </p>
            <ul className="ml-5 list-disc marker:text-text-muted">
              <li>
                <strong>Import a spreadsheet</strong> <br />Upload/drag-and-drop an <code>.xlsx</code> export from Scopus,
                Web of Science, or any sheet with <code>Title</code> and <code>Abstract</code>{' '}
                columns. You get a preview before anything is saved, with likely duplicates flagged
                and unchecked so re-importing or combining two databases will not double up your
                list.
              </li>
              <li>
                <strong>Add one paper</strong> <br />Search by DOI or by title and the details are
                fetched from CrossRef, or type them in yourself.
              </li>
            </ul>
            <p>
              <strong>3. Work through them.</strong> The very first time you open a database, the app opens on the first paper. 
              Afterwards, it continues from where you left off and remembers
              where you stopped, so closing it and coming back tomorrow picks up where you were.
            </p>
          </Section>

          <Section id="reviewing" title="Reviewing a paper">
            <p>
              For each paper you read the abstract and do three things, in whatever order suits
              you: assign tags, give it a star rating, and write notes. All three save
              automatically. There is no save button to forget and nothing to export to avoid
              losing work.
            </p>
            <p>
              Move between papers with the <strong>&lt;</strong> and <strong>&gt;</strong> buttons,
              the left and right arrow keys, the <strong>Go to #</strong> box, or by clicking any
              tile in the progress overview.
            </p>
            <p>
              <strong>Highlighting.</strong> Press <strong>Highlight</strong> above the title to
              turn the highlighter on, then select any part of the title or abstract to mark it.
              Marks are saved with the paper and are still there when you come back to it. Click a
              mark while the highlighter is on to remove it, or <strong>Clear all</strong> to
              remove every mark on the paper. With the highlighter off, selecting text behaves
              normally so copying a sentence does not leave a mark behind.
            </p>
          </Section>

          <Section id="fields-and-tags" title="Fields and tags">
            <p>
              A <strong>field</strong> is a question you are asking of every paper. A{' '}
              <strong>tag</strong> is one possible answer. Every new review starts with two
              built-in fields:
            </p>
            <ul className="ml-5 list-disc marker:text-text-muted">
              <li>
                <strong>Adherence</strong> is one of: Insufficient, Partial, or Sufficient
              </li>
              <li>
                <strong>Contribution Type</strong> is one of: Improvement, New Method, Review, or Other
              </li>
            </ul>
            <p>
              These two cannot be renamed or deleted, but everything else is yours: 
              add your own fields in{' '}
              <strong>Manage fields and tags</strong>, and give each one whatever tags your review
              needs.
            </p>
            <p>
              Tags can nest. Use the <strong>+</strong> beside a tag to add a subtopic underneath
              it, and a subtopic under that, as deep as you like. A paper can carry any number of
              tags from any field, at any depth.
            </p>
            <Figure
              name="fields"
              alt="The manage fields and tags panel, with a field expanded to show its tags and their weight boxes"
              caption="Each tag carries a weight (the number beside it) which is what feeds the paper's score."
            />
          </Section>

          <Section id="review-plan" title="The review plan">
            <p>
              A review runs on judgements you have to make the same way every time: what you are
              looking for, what makes a paper relevant, what a tag means, why a weight is what it
              is. The <strong>Review plan</strong> is where you write those down, once, instead of
              carrying them in your head from one session to the next.
            </p>
            <p>
              Open it from the clipboard button beside any review on the home page, or from{' '}
              <strong>Review plan</strong> in the top right while you are working. It holds five
              written sections, a note on what each field asks, and what each level of{' '}
              <strong>Adherence</strong> means. Nothing in it is required, and every box saves by
              itself when you click away.
            </p>
            <p>
              Anything you write about a tag comes back to you where you need it: hover a tag while
              tagging a paper and its definition appears. Tags that have one are marked with a
              dotted underline.
            </p>
            <p>
              A review whose plan is unfinished is marked <strong>Plan incomplete</strong> on the
              home page and with a dot beside the button. That is a nudge, never a block: the count
              covers the five sections, a note on each field, and the three Adherence levels, so
              describing individual tags is optional.
            </p>
            <Figure
              name="plan"
              alt="The review plan page, showing its progress count, contents, and the first written section"
              caption="The plan page: what is written so far at the top, then a box per section. (Example data.)"
            />
          </Section>

          <Section id="rating-and-score" title="Rating and score">
            <div className="flex flex-col gap-4">
              <Term name="Rating is what you thought of it">
                Your own judgement, zero stars to five stars. It is subjective and entirely up to
                you; nothing in the app sets it. Click the left half of a star for a half step, the
                right half for a whole one, and click the same value again to clear the rating.
              </Term>
              <Term name="Weight is what a tag is worth">
                Every tag has a weight from 0 to 5, in steps of half a point, set in{' '}
                <strong>Manage fields and tags</strong>. New tags start at 0, which means "this tag
                describes the paper but does not make it more valuable to me". Raise the weight of
                the tags that mark a paper as worth your time.
              </Term>
              <Term name="Score is the two combined">
                A single number for how promising a paper is, so a long list can be sorted.
              </Term>
            </div>
            <Card className="p-5">
              <p className="text-center font-serif text-lg text-text">
                score = sum of the weights of the paper's tags + its rating
              </p>
            </Card>
            <p>
              So a paper tagged <em>Sufficient</em> (weight 2) and <em>New Method</em> (weight 1.5)
              and rated four stars scores 2 + 1.5 + 4 = <strong>7.5</strong>. Tags at every depth
              count, so a subtopic's weight adds on top of its parent's if both are assigned. An
              unrated paper contributes 0 from the rating.
            </p>
            <p>
              The score is worked out fresh every time it is shown, never stored. Change a tag's
              weight and every paper carrying that tag is re-scored at once. This means you can adjust the
              weights as your sense of the literature develops, without redoing any tagging.
            </p>
            <p>
              <strong>Hover any score or rating to see what it is made of.</strong> On a paper, the
              score spells out the sum tag by tag, so you can see which weight put it where it is.
              In the dashboard's lists, where the tags are not to hand, it splits the total into
              what came from tag weights and what came from your rating.
            </p>
          </Section>

          <Section id="overview" title="The progress overview">
            <p>
              One tile per paper, in order. Colour shows how many fields that paper has at least
              one tag in, so at a glance you can see how much of the review is left. Click any tile
              to jump to that paper; the one you are on is outlined.
            </p>
            <div className="flex flex-col gap-2">
              <p className="flex items-center gap-2">
                <span
                  className="inline-block h-4 w-4 shrink-0 rounded"
                  style={{ backgroundColor: 'var(--color-border)' }}
                  aria-hidden="true"
                />
                No tags yet.
              </p>
              <p className="flex items-center gap-2">
                <span className="flex shrink-0 items-center gap-0.5" aria-hidden="true">
                  {[1, 2, 3, 4, 5].map((step) => (
                    <span
                      key={step}
                      className="inline-block h-4 w-4 rounded"
                      style={{ backgroundColor: `var(--color-progress-${step})` }}
                    />
                  ))}
                </span>
                Partly tagged. Darker means more fields covered.
              </p>
              <p className="flex items-center gap-2">
                <span
                  className="flex h-4 w-4 shrink-0 items-center justify-center rounded"
                  style={{ backgroundColor: 'var(--color-success)' }}
                  aria-hidden="true"
                >
                  <Check size={11} strokeWidth={3} className="text-[var(--color-success-fg)]" />
                </span>
                Every field has at least one tag. The paper is fully tagged.
              </p>
              <p className="flex items-center gap-2">
                <Star
                  size={15}
                  fill="#f5c518"
                  stroke="#6b4e00"
                  strokeWidth={2}
                  className="shrink-0"
                  aria-hidden="true"
                />
                A gold star in the top-left corner means you have rated it.
              </p>
              <p className="flex items-center gap-2">
                <span
                  className="flex h-4 w-4 shrink-0 items-center justify-center rounded-[3px]"
                  style={{ backgroundColor: '#f7f4ea', boxShadow: '0 0 0 0.5px rgba(0,0,0,0.55)' }}
                  aria-hidden="true"
                >
                  <Pencil size={10} stroke="#15161a" strokeWidth={2.75} />
                </span>
                A pencil in the bottom-right corner means you have written notes.
              </p>
            </div>
            <p>
              Hovering a tile spells all of that out in words. The heading shows how many papers
              are fully tagged and what share of the review that is, and clicking the heading folds
              the panel away when you want the room.
            </p>
            <Figure
              name="overview"
              alt="The progress overview: a row of coloured tiles with corner badges, above a legend"
              caption="Colour for progress, corners for rated and noted."
            />
          </Section>

          <Section id="dashboard" title="The dashboard">
            <p>
              <strong>Dashboard</strong> in the top right of a review summarises the whole thing:
              how many papers are fully tagged, rated and annotated, which tags you have used most,
              and your highest-scoring papers. Click any paper in either list to jump straight to
              it.
            </p>
            <p>
              The averages are shown against the scale they are read on. Rating is out of five.
              Score has no fixed maximum, it grows with the weights you set, so it is shown
              against the highest score in that review, which is the most useful comparison
              available: how the typical paper compares with the best one in the spreadsheet.
            </p>
            <Figure
              name="dashboard"
              alt="The dashboard, showing summary tiles above a tag distribution chart"
              caption="Summary tiles and tag distribution for a review in progress."
            />
          </Section>

          <Section id="your-data" title="Where your data lives">
            <p>
              Everything is stored in a single SQLite database file on your own computer, at{' '}
              <code>backend/data/app.db</code>. Nothing is uploaded anywhere, and there is no
              account. Copy that file to back your work up, the same way you would back up a
              document.
            </p>
            <p>
              The only thing that leaves your machine is a CrossRef lookup, and only when you
              search for a paper by DOI or title.
            </p>
          </Section>

          <Section id="shortcuts" title="Keyboard shortcuts">
            <ul className="ml-5 list-disc marker:text-text-muted">
              <li>
                <strong>Left arrow</strong> / <strong>right arrow</strong> <br />
                Navigate to the previous and next paper, respectively.
                Ignored while you are typing in a box, so they will not interrupt a note.
              </li>
            </ul>
          </Section>
        </div>
      </div>
    </div>
  )
}
