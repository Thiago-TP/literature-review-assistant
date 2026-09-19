import type { PlanSection } from './types'

/**
 * The review plan's written sections and the words that introduce them.
 *
 * Kept apart from the page so the wording can be read and revised on its own;
 * it is the part of this feature most likely to change. The order matches
 * `PLAN_SECTIONS` in the backend service of the same name.
 */
export const PLAN_SECTIONS: PlanSection[] = ['purpose', 'scope', 'search', 'weights', 'other']

/** The field whose tags decide whether a paper is in or out. Protected, so it always exists. */
export const ADHERENCE_FIELD = 'Adherence'

export const PLAN_PROMPTS: Record<
  PlanSection,
  { title: string; prompt: string; placeholder: string }
> = {
  purpose: {
    title: 'Why this review exists',
    prompt:
      'The question this review is meant to answer, and what you will do with the answer: a thesis chapter, a paper, a decision. Everything else on this page is downstream of it, since a paper is only relevant relative to a question.',
    placeholder: 'Write it for yourself in six months...',
  },
  scope: {
    title: 'What is in scope, and what is not',
    prompt:
      'The rules that decide whether a paper belongs in this review at all: subject matter, years, venues, languages, study types. The ones you keep re-deciding are the ones worth writing down.',
    placeholder: 'Include... Exclude...',
  },
  search: {
    title: 'How you found these papers',
    prompt:
      'Which databases you searched, the exact query strings, and on what date. The app keeps your papers but not where they came from, and this is the part that cannot be reconstructed later.',
    placeholder: 'Scopus, 19 Sep 2026: TITLE-ABS-KEY(...)',
  },
  weights: {
    title: 'Why the weights are what they are',
    prompt:
      "Score is the weights of a paper's tags plus its rating. Explain the balance you chose: which tags you deliberately set high, which you left at 0, and what a five-star rating means in this review. The app cannot define that last one for you.",
    placeholder: 'A five-star paper is one that...',
  },
  other: {
    title: 'Anything else worth remembering',
    prompt:
      'Conventions, caveats, decisions you made mid-way and want to keep applying. Anything you would tell someone taking over this review.',
    placeholder: 'Notes to your future self...',
  },
}
