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
// The launcher can have the window open before the API is listening, so the
// first ask often cannot be answered. Back off up to a ceiling rather than
// hammering a server that is still starting.
const RETRY_MIN_MS = 500
const RETRY_MAX_MS = 10_000

export function useSessionHeartbeat() {
  useEffect(() => {
    let stopped = false
    let watching = false
    let timer: ReturnType<typeof setInterval> | undefined
    let retry: ReturnType<typeof setTimeout> | undefined

    function beat() {
      if (stopped || !watching) return
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

    /**
     * Whether the server is watching, or null when it could not say.
     *
     * The two are very different: `false` is a backend that answered and is
     * not watching, which is final. `null` is no answer at all -- the dev
     * server proxies /api and replies 502 until the API is up -- which says
     * nothing yet and has to be asked again.
     */
    async function probeWatching(): Promise<boolean | null> {
      try {
        const response = await fetch('/api/session/status')
        if (!response.ok) return null
        const body = (await response.json()) as { watching?: boolean }
        return body.watching === true
      } catch {
        return null
      }
    }

    async function start(retryMs: number) {
      const answer = await probeWatching()
      if (stopped) return
      if (answer === null) {
        // Keep asking. Giving up on one unanswered probe would leave the
        // window unable to ever report itself closed, and the launcher would
        // then run on after the window is gone.
        retry = setTimeout(
          () => void start(Math.min(retryMs * 2, RETRY_MAX_MS)),
          retryMs
        )
        return
      }
      if (!answer) return
      watching = true
      beat()
      timer = setInterval(beat, HEARTBEAT_MS)
      document.addEventListener('visibilitychange', handleVisibility)
      window.addEventListener('pagehide', handlePageHide)
    }

    void start(RETRY_MIN_MS)

    return () => {
      stopped = true
      if (timer !== undefined) clearInterval(timer)
      if (retry !== undefined) clearTimeout(retry)
      document.removeEventListener('visibilitychange', handleVisibility)
      window.removeEventListener('pagehide', handlePageHide)
    }
  }, [])
}
