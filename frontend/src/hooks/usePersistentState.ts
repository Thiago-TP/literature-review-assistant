import { useEffect, useState, type Dispatch, type SetStateAction } from 'react'

/**
 * `useState` that survives the component unmounting, by mirroring into
 * localStorage.
 *
 * For display preferences only — which panel is open, which field is
 * expanded. Anything that is part of the review belongs in the backend, where
 * it is shared across browsers and backed up with the database.
 *
 * Every access is guarded: storage can be unavailable in a private window or
 * with site data blocked, and the accessor itself can throw. In that case the
 * state simply behaves like ordinary `useState`.
 */
export function usePersistentState<T>(
  key: string,
  initial: T
): [T, Dispatch<SetStateAction<T>>] {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key)
      return stored === null ? initial : (JSON.parse(stored) as T)
    } catch {
      return initial
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch {
      // Preference just resets on the next visit.
    }
  }, [key, value])

  return [value, setValue]
}
