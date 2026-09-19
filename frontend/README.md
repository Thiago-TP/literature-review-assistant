# Frontend

React 19 + TypeScript on Vite, with React Query for server state, React Router
for the three routes, Tailwind CSS v4 for styling and lucide for icons.

There is no client-side state store. Everything the app shows lives in the
backend, so React Query's cache *is* the state, and the only local state is
transient UI: which paper is open, whether a panel is retracted, the text in a
field before it is saved.

## Running it

```bash
npm install
npm run dev      # http://localhost:5173
```

The dev server proxies `/api` to `http://localhost:8000` (see `vite.config.ts`),
so the app always talks to a same-origin URL and there is no CORS handling in
the client. The backend has to be running separately — or use `python run.py`
from the repository root to start both.

The proxy target is overridable with `LRA_API_PORT`, which is how the launcher
tells Vite where the backend ended up when port 8000 was already taken.

| Script | What it does |
| --- | --- |
| `npm run dev` | Vite dev server with HMR |
| `npm run build` | `tsc --build` then a production bundle into `dist/` |
| `npm run lint` | oxlint |
| `npm run preview` | Serve the built bundle |

`npm run build` type-checks with `noUnusedLocals`/`noUnusedParameters` on, so it
is the real check — `npm run lint` alone will not catch a type error.

## Layout

```
src/
  main.tsx          QueryClientProvider + BrowserRouter
  App.tsx           the three routes
  pages/            one component per route
  components/       presentational pieces, plus ui.tsx (Button, Card, Input, ...)
  hooks/            React Query wrappers, one file per resource
  api/              typed fetch client, one file per resource
  types.ts          the response shapes, mirroring the backend's schemas
  index.css         palette tokens + Tailwind theme wiring
```

| Route | Page | What it is |
| --- | --- | --- |
| `/` | `ProjectListPage` | Create, rename, delete and open reviews |
| `/projects/:projectId` | `ReviewWorkspacePage` | The workspace: overview grid, one paper at a time, tags, notes |
| `/projects/:projectId/dashboard` | `DashboardPage` | Aggregate stats, tag distribution, sortable/searchable paper list |

## Data fetching

Components never call `fetch`. Each resource has a file in `api/` returning
typed promises and a file in `hooks/` wrapping those in `useQuery`/`useMutation`;
components use the hooks.

**Query keys are nested**, which is the one thing to get right:

```
['projects']
['projects', id]
['projects', id, 'papers']
['projects', id, 'papers', paperId]
['projects', id, 'dashboard']
```

React Query matches keys by prefix, so `invalidateQueries({ queryKey:
['projects', id] })` also invalidates every paper and the dashboard for that
project. When you mean only the project itself, pass `exact: true`. Getting this
wrong is not a visible bug — it just quietly refetches everything.

Two deliberate behaviours in `hooks/usePapers.ts` and `hooks/useProjects.ts`:

- Stepping between papers keeps the current one on screen while the next loads
  (`placeholderData: keepPreviousData`) and prefetches both neighbours, so
  holding an arrow key scrolls through papers instead of flashing an empty
  workspace. While placeholder data is showing, the paper body is faded and
  click-locked so a stray click cannot rate the paper you just left.
- The "last viewed paper" bookmark is debounced. It is only read back on the
  next mount, so it does not deserve a request per keypress, and racing writes
  could otherwise bookmark whichever request answered last.

Tag toggles assert one option at a time (`POST`/`DELETE` on a single option)
rather than sending the whole list, so two quick clicks cannot clobber each
other.

`hooks/useSessionHeartbeat.ts` is the exception to "components never call
fetch": it is not server state, it is a liveness signal telling the launcher
this window is still open so that closing it stops both servers. It asks
`/api/session/status` once and stays completely silent when nothing is
watching, which is the case under a plain `npm run dev`.

## Styling and theming

Tailwind v4, configured entirely from `src/index.css` — there is no
`tailwind.config.js`. The palette is CSS custom properties on `:root`,
redeclared for dark mode twice: once under `@media (prefers-color-scheme: dark)`
guarded by `:root:not([data-theme='light'])`, and once under
`:root[data-theme='dark']` so the explicit toggle wins over the system
preference. `@theme inline` re-exports them so Tailwind utilities such as
`bg-surface` and `text-text-muted` resolve to the tokens.

`--color-progress-1` … `-5` is the sequential ramp the review overview paints
its tiles with: one hue, monotone lightness, with a separate set of steps chosen
for each theme rather than an automatic flip.

**Take colour from the tokens, not from JavaScript.** Reading
`prefers-color-scheme` or `data-theme` at render time gives a value that does
not update when the theme changes, which leaves components showing the previous
theme's colours until something else re-renders them.

`index.html` sets `data-theme` in a blocking inline script before the bundle
loads, so there is no flash of the wrong theme on a hard refresh.

Radius scale: `rounded-lg` for surfaces that hold content, `rounded-md` for
controls and inner blocks, `rounded` for small marks, `rounded-full` for pills
and badges.

## Accessibility notes

Worth preserving when editing:

- The overview tiles carry their meaning in colour and two corner badges, so the
  grid ships with a legend, and each tile's `title` spells out its state in
  words.
- The retractable overview panel's toggle carries `aria-expanded` and
  `aria-controls`, and the collapsed region stays in the DOM behind a display
  rule so `aria-controls` keeps pointing at something real.
- Arrow-key paper navigation is skipped while the focus is in an input,
  textarea, select or contenteditable, and for modified key presses.
