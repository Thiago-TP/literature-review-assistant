#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = ["httpx>=0.28", "playwright>=1.50"]
# ///
"""Retake the screenshots in the documentation, offscreen.

Starts the backend and frontend against a throwaway database, fills it with
the example review in ``screenshot_data.py``, and photographs the app in a
headless browser, once in each theme. Nothing opens on screen, and neither
your own database nor anything already running on the default ports is
touched.

The images it writes, in place:

    docs/screenshots/workspace.png                  the root README: both themes,
                                                    sliced diagonally into one
    docs/screenshots/workspace-{light,dark}.png     ...and each theme in full
    frontend/public/help/*-{light,dark}.png         the in-app help page

It drives the Google Chrome (or Edge) already installed on the machine, so
there is no browser to download. Without either, install Playwright's own:
``uv run --with playwright playwright install chromium``.

Usage, from the repository root (uv installs the two dependencies on the fly):
    uv run scripts/take_screenshots.py                  all of them, in place
    uv run scripts/take_screenshots.py --only plan      just the ones named
    uv run scripts/take_screenshots.py --out /tmp/shots write there, to compare first
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

# Playwright is imported where it is used, not here, so the backend's test
# suite can import `seed` to check the example review against the API without
# having Playwright installed.
if TYPE_CHECKING:
    from playwright.sync_api import Browser, Locator, Page, Playwright

# The launcher already knows how to find the servers, pick free ports and tear
# a process tree down on every platform; reuse it rather than keep a copy.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import main as launcher  # noqa: E402
import screenshot_data as demo  # noqa: E402

THEMES = ("light", "dark")

# Tall enough that every element the help figures crop to is on screen without
# scrolling, so element boxes and screenshot clips share one coordinate space.
# Nothing in the app sizes itself by the viewport height, so the extra room
# changes no layout.
HELP_VIEWPORT = (1280, 2000)

# Where the cut between the themes in a composite crosses the top and bottom
# edges, as fractions of the width. Light is left of it, dark right of it.
# Slanted rather than corner to corner: on a wide picture a true diagonal is
# so shallow that it splits the page into a light top and a dark bottom.
SLICE_TOP = 0.6
SLICE_BOTTOM = 0.4


@dataclass(frozen=True)
class Seeded:
    """The ids the seeding produced, which routes and preferences refer to."""

    project_id: int
    custom_field_id: int


@dataclass(frozen=True)
class Shot:
    name: str
    route: str
    # Repository-relative, with ``{theme}`` for light or dark.
    output: str
    viewport: tuple[int, int]
    # Device pixel ratio. The README image is shown large on GitHub, so it is
    # taken at 2x; the help figures are shown narrower than they are taken.
    scale: int = 1
    # Elements the image is cropped to (their combined box, plus padding).
    # None photographs the viewport as it stands.
    crop: Callable[[Page], list[Locator]] | None = None
    padding: int = 14
    # Elements that have to be visible before the page counts as rendered.
    # Defaults to the crop elements.
    ready: Callable[[Page], list[Locator]] | None = None
    # localStorage display preferences, beyond the theme.
    prefs: Callable[[Seeded], dict[str, object]] = field(default=lambda _seeded: {})
    # Also join the two themes into one picture, sliced diagonally, here.
    composite: str | None = None


# ---- Locating things on the page ----------------------------------------


def card_of(locator: Locator) -> Locator:
    """The card (``ui.tsx`` ``Card``) a piece of text sits in."""
    return locator.locator(
        "xpath=ancestor::div[contains(concat(' ', @class, ' '), ' rounded-lg ')"
        " and contains(concat(' ', @class, ' '), ' bg-surface ')][1]"
    )


def overview_card(page: Page) -> Locator:
    return card_of(page.locator("#review-progress-heading"))


def notes_card(page: Page) -> Locator:
    return card_of(page.get_by_text("Your notes", exact=True))


def fields_card(page: Page) -> Locator:
    return card_of(page.get_by_text("Manage fields and tags", exact=True))


def current_paper_title(page: Page) -> Locator:
    return page.get_by_text(demo.PAPERS[demo.CURRENT_PAPER - 1].title).first


def stat_tiles(page: Page) -> Locator:
    # The first tile's card, then the grid holding all six.
    return card_of(page.get_by_text("Papers", exact=True)).locator("xpath=..")


def tag_distribution_card(page: Page) -> Locator:
    return card_of(page.get_by_text("Tag distribution", exact=True))


def workspace_ready(page: Page) -> list[Locator]:
    # The overview renders before the paper does, and a crop taken in between
    # would catch the previous paper still fading out.
    return [overview_card(page), current_paper_title(page)]


SHOTS: list[Shot] = [
    Shot(
        name="readme",
        route="/projects/{project}",
        output="docs/screenshots/workspace-{theme}.png",
        viewport=(1280, 810),
        scale=2,
        ready=workspace_ready,
        composite="docs/screenshots/workspace.png",
    ),
    Shot(
        name="workspace",
        route="/projects/{project}",
        output="frontend/public/help/workspace-{theme}.png",
        viewport=HELP_VIEWPORT,
        # Overview down to the notes: the paper card sits between the two.
        crop=lambda page: [overview_card(page), notes_card(page)],
        padding=24,
        ready=workspace_ready,
    ),
    Shot(
        name="overview",
        route="/projects/{project}",
        output="frontend/public/help/overview-{theme}.png",
        viewport=HELP_VIEWPORT,
        crop=lambda page: [overview_card(page)],
        ready=workspace_ready,
    ),
    Shot(
        name="fields",
        route="/projects/{project}",
        output="frontend/public/help/fields-{theme}.png",
        viewport=HELP_VIEWPORT,
        crop=lambda page: [fields_card(page)],
        # Open, with the custom field expanded to show its tags and weights.
        prefs=lambda seeded: {
            "fieldPanelOpen": True,
            "fieldPanelExpandedField": seeded.custom_field_id,
        },
    ),
    Shot(
        name="dashboard",
        route="/projects/{project}/dashboard",
        output="frontend/public/help/dashboard-{theme}.png",
        viewport=HELP_VIEWPORT,
        crop=lambda page: [stat_tiles(page), tag_distribution_card(page)],
    ),
    Shot(
        name="plan",
        route="/projects/{project}/plan",
        output="frontend/public/help/plan-{theme}.png",
        viewport=(1004, 716),
        ready=lambda page: [page.get_by_role("heading", name="Review plan", exact=True)],
    ),
]


# ---- Seeding the example review -----------------------------------------


def seed(api: httpx.Client) -> Seeded:
    """Build the example review through the public API, the same way the app
    would, so the pictures show exactly what a real review looks like."""

    def call(method: str, url: str, **kwargs) -> dict | list | None:
        response = api.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else None

    project_id = call("POST", "/api/projects", json={"name": demo.PROJECT_NAME})["id"]
    base = f"/api/projects/{project_id}"

    fields = {f["name"]: f for f in call("GET", f"{base}/fields")}
    fields[demo.CUSTOM_FIELD] = call("POST", f"{base}/fields", json={"name": demo.CUSTOM_FIELD})

    option_ids: dict[tuple[str, str], int] = {}
    for field_name, tags in demo.FIELD_TAGS.items():
        field_id = fields[field_name]["id"]
        existing = {option["value"]: option["id"] for option in fields[field_name]["options"]}
        for value, weight, description in tags:
            option_id = existing.get(value)
            if option_id is None:
                created = call("POST", f"{base}/fields/{field_id}/options", json={"value": value})
                option_id = created["id"]
            update: dict[str, object] = {"weight": weight}
            if description is not None:
                update["description"] = description
            call("PATCH", f"{base}/fields/{field_id}/options/{option_id}", json=update)
            option_ids[field_name, value] = option_id
        call(
            "PATCH",
            f"{base}/fields/{field_id}",
            json={"description": demo.FIELD_DESCRIPTIONS[field_name]},
        )

    paper_ids: list[int] = []
    for number, paper in enumerate(demo.PAPERS, start=1):
        created = call(
            "POST",
            f"{base}/papers",
            json={
                "title": paper.title,
                "abstract": paper.abstract,
                "doi": f"10.0000/demo.{number:04d}",
                "authors": paper.authors,
                "year": paper.year,
                "source_title": paper.venue,
            },
        )
        if created["paper"] is None:
            raise SystemExit(f"Example paper {number} was taken for a duplicate: {paper.title}")
        paper_id = created["paper"]["id"]
        paper_ids.append(paper_id)

        for field_name, value in paper.tags.items():
            call("POST", f"{base}/papers/{paper_id}/tags/{option_ids[field_name, value]}")
        if paper.rating is not None:
            call("PUT", f"{base}/papers/{paper_id}/rating", json={"rating": paper.rating})
        if paper.notes:
            call("PATCH", f"{base}/papers/{paper_id}", json={"notes": paper.notes})
        for start, end in paper.highlights:
            call(
                "POST",
                f"{base}/papers/{paper_id}/highlights",
                json={"field": "abstract", "start": start, "end": end},
            )

    call("PATCH", f"{base}/plan", json=demo.PLAN)
    # The workspace opens on the last paper viewed, which is how the pictures
    # land on a tagged, rated, highlighted paper rather than the first one.
    call(
        "PATCH",
        f"{base}/last-viewed",
        json={"paper_id": paper_ids[demo.CURRENT_PAPER - 1]},
    )

    return Seeded(project_id=project_id, custom_field_id=fields[demo.CUSTOM_FIELD]["id"])


# ---- Taking the pictures ------------------------------------------------


def launch_browser(playwright: Playwright) -> Browser:
    """An installed Chrome or Edge first, falling back to Playwright's own
    Chromium if `playwright install chromium` has been run."""
    from playwright.sync_api import Error

    for channel in ("chrome", "msedge", None):
        try:
            return playwright.chromium.launch(channel=channel)
        except Error:
            continue
    launcher.fail(
        "No browser found. Install Google Chrome, or Playwright's Chromium with:\n"
        "  uv run --with playwright playwright install chromium"
    )


def clip_around(locators: list[Locator], padding: int) -> dict[str, float]:
    boxes = [locator.bounding_box() for locator in locators]
    if any(box is None for box in boxes):
        raise RuntimeError("An element to crop to is not on the page")
    left = max(0, min(box["x"] for box in boxes) - padding)
    top = max(0, min(box["y"] for box in boxes) - padding)
    right = max(box["x"] + box["width"] for box in boxes) + padding
    bottom = max(box["y"] + box["height"] for box in boxes) + padding
    return {"x": left, "y": top, "width": right - left, "height": bottom - top}


def take(browser: Browser, frontend_url: str, shot: Shot, theme: str, seeded: Seeded, path: Path):
    width, height = shot.viewport
    context = browser.new_context(
        viewport={"width": width, "height": height},
        device_scale_factor=shot.scale,
        color_scheme=theme,
    )
    try:
        # Preferences go in before the app's first script runs, so it starts
        # in them rather than rendering once and then switching.
        prefs = {"progressOverviewCollapsed": False, "fieldPanelOpen": False}
        prefs.update(shot.prefs(seeded))
        storage = {key: json.dumps(value) for key, value in prefs.items()}
        # ThemeToggle stores the bare word, not JSON.
        storage["theme"] = theme
        context.add_init_script(
            f"for (const [k, v] of Object.entries({json.dumps(storage)})) "
            "localStorage.setItem(k, v)"
        )

        page = context.new_page()
        page.goto(frontend_url + shot.route.format(project=seeded.project_id))
        page.wait_for_load_state("networkidle")
        ready = shot.ready or shot.crop
        if ready is not None:
            for locator in ready(page):
                locator.wait_for(state="visible")
        page.evaluate("document.fonts.ready")

        clip = clip_around(shot.crop(page), shot.padding) if shot.crop else None
        path.parent.mkdir(parents=True, exist_ok=True)
        # "disabled" finishes transitions rather than catching them halfway,
        # e.g. the fade a paper does as it loads.
        page.screenshot(path=path, clip=clip, animations="disabled")
    finally:
        context.close()


def compose_diagonal(browser: Browser, shot: Shot, light: Path, dark: Path, path: Path):
    """Both themes as one picture: light on one side of a slanted cut, dark on
    the other.

    Done in the browser, like the screenshots themselves: the dark one is laid
    over the light one and clipped with CSS, which anti-aliases the cut, and
    means no imaging library to install.
    """
    width, height = shot.viewport
    top, bottom = f"{SLICE_TOP:.0%}", f"{SLICE_BOTTOM:.0%}"

    def data_url(image: Path) -> str:
        return "data:image/png;base64," + base64.b64encode(image.read_bytes()).decode()

    context = browser.new_context(
        viewport={"width": width, "height": height}, device_scale_factor=shot.scale
    )
    try:
        page = context.new_page()
        # set_content waits for the load event, so both images have decoded.
        page.set_content(
            f"""
            <style>
              body {{ margin: 0; }}
              img {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
              .dark {{ clip-path: polygon({top} 0, 100% 0, 100% 100%, {bottom} 100%); }}
            </style>
            <img src="{data_url(light)}">
            <img class="dark" src="{data_url(dark)}">
            """
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=path)
    finally:
        context.close()


# ---- Running it all -----------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    names = [shot.name for shot in SHOTS]
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--only",
        nargs="+",
        choices=names,
        metavar="NAME",
        help=f"retake only these ({', '.join(names)})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="write under this directory (same relative paths) instead of in place",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    launcher.install_shutdown_handler()
    shots = [shot for shot in SHOTS if args.only is None or shot.name in args.only]
    out_root = args.out.resolve() if args.out else ROOT

    uvicorn = launcher.venv_executable("uvicorn")
    if not uvicorn.exists():
        launcher.fail(launcher.SETUP_BACKEND)
    if not (launcher.FRONTEND_DIR / "node_modules").is_dir():
        launcher.fail(launcher.SETUP_FRONTEND)
    npm = launcher.npm_executable()
    if npm is None:
        launcher.fail("npm not found on PATH. Install Node.js 20+ from https://nodejs.org/.")

    backend_port = launcher.pick_port(launcher.DEFAULT_BACKEND_PORT, taken=set())
    frontend_port = launcher.pick_port(launcher.DEFAULT_FRONTEND_PORT, taken={backend_port})
    backend_url = f"http://127.0.0.1:{backend_port}"
    frontend_url = f"http://localhost:{frontend_port}"

    # ignore_cleanup_errors: on Windows the database can still be held open
    # for a moment after uvicorn is told to stop.
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as scratch:
        # Quietened: a request log per screenshot buries the list of files.
        backend_command = [str(uvicorn), "app.main:app", "--port", str(backend_port)]
        backend_command += ["--log-level", "warning"]
        frontend_command = [npm, "run", "--silent", "dev", "--", "--port", str(frontend_port)]
        frontend_command += ["--strictPort", "--logLevel", "warn"]

        processes = []
        count = 0
        try:
            processes.append(
                launcher.spawn(
                    backend_command,
                    launcher.BACKEND_DIR,
                    env={
                        "LRA_DB_PATH": str(Path(scratch) / "screenshots.db"),
                        # No window of ours to watch; stay up until stopped.
                        "LRA_SESSION_WATCH": "0",
                    },
                )
            )
            processes.append(
                launcher.spawn(
                    frontend_command,
                    launcher.FRONTEND_DIR,
                    env={"LRA_API_PORT": str(backend_port)},
                )
            )
            if not launcher.wait_for_servers(
                [f"{backend_url}/api/health", frontend_url], processes
            ):
                launcher.fail("The servers did not come up; see their output above.")

            with httpx.Client(base_url=backend_url, timeout=30) as api:
                seeded = seed(api)

            from playwright.sync_api import sync_playwright

            with sync_playwright() as playwright:
                browser = launch_browser(playwright)
                for shot in shots:
                    written = {}
                    for theme in THEMES:
                        relative = shot.output.format(theme=theme)
                        written[theme] = out_root / relative
                        take(browser, frontend_url, shot, theme, seeded, written[theme])
                        print(f"  {relative}", flush=True)
                    if shot.composite:
                        compose_diagonal(
                            browser,
                            shot,
                            written["light"],
                            written["dark"],
                            out_root / shot.composite,
                        )
                        print(f"  {shot.composite}", flush=True)
                        count += 1
                    count += len(THEMES)
                browser.close()
        except KeyboardInterrupt:
            return 130
        finally:
            for process in processes:
                launcher.stop(process)

    where = "" if out_root == ROOT else f" under {out_root}"
    print(f"Wrote {count} screenshots{where}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
