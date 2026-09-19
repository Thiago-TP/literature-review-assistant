/**
 * Values the app treats as fixed, mirroring `backend/app/constants.py`.
 *
 * These are constants of the app rather than per-review data, so the frontend
 * holds its own copy instead of asking for them. Keep the two files in step:
 * the backend validates against its copy, so a change made on only one side
 * shows up as a request the server rejects, not as a wrong number on screen.
 */

/** The rating scale, in stars. Half stars are allowed, so the step is 0.5. */
export const MAX_RATING = 5

/** The range a tag's weight may take, in the same half-point steps. */
export const MAX_TAG_WEIGHT = 5
