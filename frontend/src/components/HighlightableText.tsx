import { useRef } from 'react'
import type { Highlight, HighlightField } from '../types'

/**
 * Splits `text` into runs, marking the parts covered by a highlight.
 *
 * Offsets come from the server already merged and clamped, but this still
 * guards against overlap and out-of-range values so a stale render can never
 * produce scrambled text.
 */
function runs(text: string, highlights: Highlight[]) {
  const ordered = [...highlights].sort((a, b) => a.start - b.start)
  const out: Array<{ text: string; id?: string }> = []
  let cursor = 0
  for (const highlight of ordered) {
    const start = Math.max(cursor, Math.min(highlight.start, text.length))
    const end = Math.max(start, Math.min(highlight.end, text.length))
    if (start > cursor) out.push({ text: text.slice(cursor, start) })
    if (end > start) out.push({ text: text.slice(start, end), id: highlight.id })
    cursor = Math.max(cursor, end)
  }
  if (cursor < text.length) out.push({ text: text.slice(cursor) })
  return out
}

/**
 * Character offset of a DOM position within `container`'s plain text.
 *
 * The rendered text is broken into several nodes by the marks themselves, so
 * a selection's node-and-offset has to be walked back to an offset into the
 * whole string — which is what the server stores.
 */
function offsetWithin(container: HTMLElement, node: Node, nodeOffset: number): number | null {
  const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT)
  let total = 0
  let current = walker.nextNode()
  while (current) {
    if (current === node) return total + nodeOffset
    total += current.textContent?.length ?? 0
    current = walker.nextNode()
  }
  // The position was a element rather than a text node (an empty container,
  // say); treating it as "no usable selection" is better than guessing.
  return null
}

export default function HighlightableText({
  text,
  field,
  highlights,
  active,
  onAdd,
  onRemove,
  className = '',
}: {
  text: string
  field: HighlightField
  highlights: Highlight[]
  /** Whether selecting text marks it, and clicking a mark removes it. */
  active: boolean
  onAdd: (field: HighlightField, start: number, end: number) => void
  onRemove: (id: string) => void
  className?: string
}) {
  const containerRef = useRef<HTMLSpanElement>(null)

  function handleMouseUp() {
    if (!active) return
    const container = containerRef.current
    const selection = window.getSelection()
    if (!container || !selection || selection.isCollapsed || selection.rangeCount === 0) return

    const range = selection.getRangeAt(0)
    if (!container.contains(range.commonAncestorContainer)) return

    const from = offsetWithin(container, range.startContainer, range.startOffset)
    const to = offsetWithin(container, range.endContainer, range.endOffset)
    if (from === null || to === null) return

    const start = Math.min(from, to)
    const end = Math.max(from, to)
    if (start >= end) return

    // Drop the browser's own selection overlay, so what stays on screen is
    // the highlight rather than both at once.
    selection.removeAllRanges()
    onAdd(field, start, end)
  }

  return (
    <span
      ref={containerRef}
      onMouseUp={handleMouseUp}
      className={`${className} ${active ? 'cursor-text' : ''}`}
    >
      {runs(text, highlights).map((run, index) =>
        run.id === undefined ? (
          <span key={index}>{run.text}</span>
        ) : (
          <mark
            key={index}
            onClick={() => active && onRemove(run.id as string)}
            title={active ? 'Click to remove this highlight' : undefined}
            className={`rounded-[2px] bg-[var(--color-highlight)] text-[var(--color-highlight-fg)] ${
              active ? 'cursor-pointer' : ''
            }`}
          >
            {run.text}
          </mark>
        )
      )}
    </span>
  )
}
