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

export function Card({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-lg border border-border bg-surface ${className}`}>{children}</div>
}

export function Badge({ children, tone = 'default' }: { children: ReactNode; tone?: 'default' | 'accent' }) {
  const toneClass = tone === 'accent' ? 'bg-accent/10 text-accent' : 'bg-surface-muted text-text-muted'
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

/** Small tracked-uppercase caption, used for section eyebrows and step labels. */
export function Label({ children, className = '' }: { children: ReactNode; className?: string }) {
  return <p className={`tracked-label text-xs text-text-muted ${className}`}>{children}</p>
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
