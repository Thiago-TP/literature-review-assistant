/** Small display helpers shared between the workspace and the dashboard. */

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
