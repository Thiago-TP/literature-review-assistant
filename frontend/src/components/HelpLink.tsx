import { Link, useLocation } from 'react-router-dom'
import { CircleHelp } from 'lucide-react'

/** The "?" in every nav bar, styled to match the theme toggle beside it. */
export default function HelpLink() {
  const location = useLocation()
  // Where the reader was, so the help page can send them back there rather
  // than to the project list. Carried in history state instead of the URL so
  // it survives a theme toggle or a jump to a section, and is simply absent
  // when /help is opened directly.
  const from = `${location.pathname}${location.search}${location.hash}`

  return (
    <Link
      to="/help"
      state={{ from }}
      aria-label="Help"
      title="How this app works"
      className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-surface text-text transition-colors hover:border-accent hover:text-accent"
    >
      <CircleHelp size={16} />
    </Link>
  )
}
