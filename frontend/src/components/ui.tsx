import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'

const baseButton =
  'inline-flex items-center justify-center gap-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed'

const variants = {
  primary:
    'tracked-label bg-accent text-accent-fg hover:bg-[var(--color-accent-hover)] px-4 py-2.5 text-xs font-semibold',
  secondary: 'bg-surface text-text border border-border hover:bg-surface-muted px-3.5 py-2',
  ghost: 'text-text-muted hover:text-text hover:bg-surface-muted px-2.5 py-1.5',
  danger: 'tracked-label bg-danger text-danger-fg hover:opacity-90 px-4 py-2.5 text-xs font-semibold',
}

export function Button({
  variant = 'secondary',
  className = '',
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: keyof typeof variants }) {
  return (
    <button className={`${baseButton} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  )
}

/**
 * Note on sizing: `w-full` is baked in, and Tailwind emits `.w-full` after the
 * numeric width utilities, so a `w-*` passed through `className` loses to it no
 * matter which order the classes appear in. Set the width on a wrapper element
 * instead — `className` is still the right place for everything else.
 */
export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={`w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-muted outline-none focus:border-accent ${props.className ?? ''}`}
    />
  )
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={`w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-text placeholder:text-text-muted outline-none focus:border-accent ${props.className ?? ''}`}
    />
  )
}

export function Card({
  children,
  className = '',
  title,
}: {
  children: ReactNode
  className?: string
  /** Native tooltip, for a card whose contents need a word of explanation. */
  title?: string
}) {
  return (
    <div className={`rounded-lg border border-border bg-surface ${className}`} title={title}>
      {children}
    </div>
  )
}

export function Badge({
  children,
  tone = 'default',
}: {
  children: ReactNode
  tone?: 'default' | 'accent' | 'warning'
}) {
  const tones = {
    default: 'bg-surface-muted text-text-muted',
    accent: 'bg-accent/10 text-accent',
    warning: 'bg-danger/10 text-danger',
  }
  const toneClass = tones[tone]
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${toneClass}`}>
      {children}
    </span>
  )
}

export function Spinner({ className = '' }: { className?: string }) {
  return (
    <svg className={`animate-spin ${className}`} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  )
}

export function EmptyState({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border py-16 text-center">
      <p className="font-serif text-lg text-text">{title}</p>
      {description && <p className="max-w-sm text-sm text-text-muted">{description}</p>}
      {action}
    </div>
  )
}

/**
 * Small tracked-uppercase caption: a stat tile's name, an inline label beside
 * a control, a page eyebrow. For the title *of* a section use SectionHeading —
 * the two were previously the same component, which is why identical-looking
 * headings had different weights and spacing.
 */
export function Label({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`tracked-label text-xs text-text-muted ${className}`}>{children}</p>
}

/** Spacing between a section heading and its content, in one place. */
export const SECTION_HEADING_GAP = 'mb-3'

/**
 * The title of a section inside a card. One weight, one colour, one gap below
 * it, everywhere — pass `as` when the heading should also be a landmark for
 * assistive tech rather than plain emphasis.
 */
export function SectionHeading({
  children,
  as: Tag = 'p',
  className = '',
}: {
  children: ReactNode
  // `span` is for headings already wrapped in a heading element or a button.
  as?: 'p' | 'span' | 'h2' | 'h3'
  className?: string
}) {
  return (
    <Tag
      className={`tracked-label flex items-center gap-1.5 text-xs font-semibold text-text ${className}`}
    >
      {children}
    </Tag>
  )
}

/** Numbered circular badge, echoing the pastel step markers in the reference design. */
export function StepBadge({ n, tone = 'a' }: { n: number; tone?: 'a' | 'b' | 'c' }) {
  const tones = {
    a: 'bg-[#c7d3c2] text-[#2f3d2a]',
    b: 'bg-[#c3d0e0] text-[#26364a]',
    c: 'bg-[#e3d5b0] text-[#4a3d1f]',
  }
  return (
    <span
      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${tones[tone]}`}
    >
      {n}
    </span>
  )
}
