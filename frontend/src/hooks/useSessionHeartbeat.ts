import { useEffect } from 'react'

/**
 * Tells the backend this window is still open, so the launcher can stop both
 * servers once it is closed.
 *
 * The server is asked first whether anyone is listening: under `npm run dev`,
 * or against a backend someone started by hand, nothing is watching and this
 * hook stays completely silent rather than posting into the void every few
 * seconds.
 *
 * The unload beacon is what makes closing the window feel immediate; the
 * interval is the backstop for a browser that was force-quit or crashed and
 * never got to send one.
 */
const HEARTBEAT_MS = 10_000

export function useSessionHeartbeat() {
  useEffect(() => {
    let stopped = false
    let timer: ReturnType<typeof setInterval> | undefined

    function beat() {
      if (stopped) return
      // keepalive so a beat already in flight survives the page going away.
      void fetch('/api/session/heartbeat', { method: 'POST', keepalive: true }).catch(
        () => undefined
      )
    }

    function handleVisibility() {
      // Browsers throttle timers in hidden tabs, so check in promptly on the
      // way back rather than waiting out the next tick.
      if (document.visibilityState === 'visible') beat()
    }

    function handlePageHide(event: PageTransitionEvent) {
      // A bfcache-persisted page can come straight back; that is not a close.
      if (event.persisted) return
      navigator.sendBeacon?.('/api/session/closed')
    }

    async function start() {
      try {
        const response = await fetch('/api/session/status')
        if (!response.ok) return
        const { watching } = (await response.json()) as { watching?: boolean }
        if (!watching || stopped) return
      } catch {
        return
      }
      beat()
      timer = setInterval(beat, HEARTBEAT_MS)
      document.addEventListener('visibilitychange', handleVisibility)
      window.addEventListener('pagehide', handlePageHide)
    }

    void start()

    return () => {
      stopped = true
      if (timer !== undefined) clearInterval(timer)
      document.removeEventListener('visibilitychange', handleVisibility)
      window.removeEventListener('pagehide', handlePageHide)
    }
  }, [])
}
