/** Small display helpers shared between the workspace and the dashboard. */

import type { TagField, TagOption } from './types'
import { MAX_RATING } from './constants'

/**
 * A share of a total as a whole percent, or null when there is no total to
 * take a share of.
 *
 * Rounding is nudged at both ends so the percentage can never contradict the
 * figure it sits beside: "199 of 200" must not read 100%, and "1 of 300" must
 * not read 0%. The same applies to an average against its maximum.
 */
export function percentLabel(part: number, total: number): string | null {
  if (total <= 0) return null
  const rounded = Math.round((part / total) * 100)
  if (rounded === 100 && part < total) return '99%'
  if (rounded === 0 && part > 0) return '1%'
  return `${rounded}%`
}

/** Drops a trailing ".0" so a scale reads "/5" rather than "/5.0". */
export function trimScale(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}

/** One named thing adding to a score: a tag and its weight, or the rating. */
export interface ScorePart {
  label: string
  value: number
}

/**
 * What a rating is, for a hover on the stars or on the number beside them.
 *
 * Rating is the one number in the app nobody can derive, so the hover says
 * whose judgement it is as well as how to set it.
 */
export function ratingHint(rating: number | null): string {
  if (rating === null) {
    return [
      'Not rated yet.',
      `Your own judgement of the paper, 0 to ${trimScale(MAX_RATING)} stars. Nothing in the app sets it, and an unrated paper adds 0 to its score.`,
      'Click the left half of a star for a half step, the right half for a whole one.',
    ].join('\n')
  }
  return [
    `Rated ${trimScale(rating)} out of ${trimScale(MAX_RATING)}.`,
    'Your own judgement of the paper, which adds straight onto its score.',
    'Click the left half of a star for a half step, the right half for a whole one, or the same value again to clear it.',
  ].join('\n')
}

/**
 * The arithmetic behind a score, for a hover: "Sufficient 2 + New Method 1.5
 * + your rating 4 = 7.5".
 *
 * Only parts that actually add something are named. A tag weighted 0 is on
 * the paper deliberately -- it describes it without making it more valuable
 * -- so naming it here would pad the hover with terms that change nothing.
 */
export function scoreHint(score: number, parts: ScorePart[]): string {
  const lead = "Score is the weights of a paper's tags plus its rating."
  const contributing = parts.filter((part) => part.value > 0)
  if (contributing.length === 0) {
    return `${lead}\nNothing adds to it yet: no tag on this paper carries a weight above 0, and it is unrated.`
  }
  const sum = contributing.map((part) => `${part.label} ${trimScale(part.value)}`).join(' + ')
  return `${lead}\n${sum} = ${trimScale(score)}`
}

/**
 * A paper's score broken down by name, for the workspace, which has the
 * review's whole tag tree to hand and so can say which tag contributed what.
 */
export function scorePartsForPaper(
  tags: Record<number, number[]>,
  rating: number | null,
  fields: TagField[]
): ScorePart[] {
  const byId = new Map<number, TagOption>()
  const walk = (options: TagOption[]) => {
    for (const option of options) {
      byId.set(option.id, option)
      walk(option.children)
    }
  }
  fields.forEach((field) => walk(field.options))

  const parts: ScorePart[] = []
  for (const optionId of Object.values(tags).flat()) {
    const option = byId.get(optionId)
    if (option) parts.push({ label: option.value, value: option.weight })
  }
  parts.push({ label: 'your rating', value: rating ?? 0 })
  return parts
}

/**
 * The same breakdown where only the totals are known -- the dashboard's lists
 * carry a score and a rating but not the tags behind them. Everything that is
 * not the rating came from tag weights, so the split is still exact, just
 * unnamed.
 */
export function scorePartsFromTotals(score: number, rating: number | null): ScorePart[] {
  const fromRating = rating ?? 0
  return [
    { label: 'tag weights', value: score - fromRating },
    { label: 'your rating', value: fromRating },
  ]
}
