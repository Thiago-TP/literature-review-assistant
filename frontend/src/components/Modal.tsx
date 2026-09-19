import { X } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button } from './ui'

export default function Modal({
  title,
  onClose,
  children,
  wide = false,
}: {
  title: string
  onClose: () => void
  children: ReactNode
  wide?: boolean
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/40 p-4 pt-16">
      <div
        className={`w-full ${wide ? 'max-w-2xl' : 'max-w-md'} rounded-lg border border-border bg-surface p-5 shadow-xl`}
      >
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-serif text-lg text-text">{title}</h3>
          <Button variant="ghost" aria-label="Close" onClick={onClose}>
            <X size={18} />
          </Button>
        </div>
        {children}
      </div>
    </div>
  )
}
