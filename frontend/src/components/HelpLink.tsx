import { Link } from 'react-router-dom'
import { CircleHelp } from 'lucide-react'

/** The "?" in every nav bar, styled to match the theme toggle beside it. */
export default function HelpLink() {
  return (
    <Link
      to="/help"
      aria-label="Help"
      title="How this app works"
      className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-surface text-text transition-colors hover:border-accent hover:text-accent"
    >
      <CircleHelp size={16} />
    </Link>
  )
}
