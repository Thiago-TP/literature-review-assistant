import { Star } from 'lucide-react'

/** One star, visually 0/half/fully filled, with two overlaid invisible
 * buttons so clicking the left half sets a .5 value and the right half
 * sets the whole number. */
function StarSlot({
  n,
  fillFraction,
  size,
  onPick,
}: {
  n: number
  fillFraction: number
  size: number
  onPick: (value: number) => void
}) {
  return (
    <span className="relative inline-block text-accent" style={{ width: size, height: size }}>
      <Star size={size} strokeWidth={1.5} fill="none" className="pointer-events-none" />
      {fillFraction > 0 && (
        <span
          className="pointer-events-none absolute inset-0 overflow-hidden"
          style={{ width: fillFraction >= 1 ? '100%' : '50%' }}
        >
          <Star size={size} strokeWidth={1.5} fill="currentColor" />
        </span>
      )}
      <button
        type="button"
        aria-label={`${n - 0.5} estrelas`}
        onClick={() => onPick(n - 0.5)}
        className="absolute inset-y-0 left-0 w-1/2"
      />
      <button
        type="button"
        aria-label={`${n} estrelas`}
        onClick={() => onPick(n)}
        className="absolute inset-y-0 right-0 w-1/2"
      />
    </span>
  )
}

export default function StarRating({
  rating,
  onChange,
  size = 18,
}: {
  rating: number | null
  onChange: (rating: number | null) => void
  size?: number
}) {
  const value = rating ?? 0

  function pick(n: number) {
    onChange(rating === n ? null : n)
  }

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <StarSlot
          key={n}
          n={n}
          size={size}
          fillFraction={Math.max(0, Math.min(1, value - (n - 1)))}
          onPick={pick}
        />
      ))}
    </div>
  )
}
