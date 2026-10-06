# MyOrbit

A phone-first feed client for a task store you run yourself. One screen, usable with a thumb, so tasks
get updated on the go instead of in a browser tab that never gets opened.

It is a **client**. It calls a small JSON API and renders whatever comes back. No database, no state of
its own, no third-party services.

## Files

| file | why |
|---|---|
| `m.html` | the whole client — vanilla JS, no build step |
| `app.webmanifest` | makes "Add to Home screen" pin the exact page and open it standalone |
| `icon-*.png`, `icon.svg` | app icons, hosted here because the URLs must be **public** (see below) |

## Why the icons live in a public repo

Android mints an installed web app's icon from the manifest **on Google's servers**, which fetch the
icon URLs with no cookies and no session. Point those URLs at anything behind a login and the fetch
returns a login page, so the launcher silently draws its own placeholder. A public raw URL is the
simplest honest fix. Icons are the only thing here that has to be public — **no data ever is.**

## The config contract

The client carries no project names, no area names, nothing personal. It fetches its configuration at
runtime from `GET <api>/config` and degrades to a plain feed if that returns nothing:

```json
{
  "areas":            ["…area names shown in the capture picker…"],
  "palette":          { "an area": "#RRGGBB" },
  "work_areas":       ["…areas counted as work…"],
  "focus_projects":   ["…projects that should dominate the feed…"],
  "prime_by_weekday": { "1": "a project" },
  "project_keywords": { "a project": ["substrings that identify it"] },
  "area_projects":    { "an area": "a project" },
  "personal_areas":   ["…areas shown in their own smaller block…"]
}
```
Keeping that server-side means this file can be public while the thing it runs against stays private.

## Design notes worth keeping

- Cards: the **area** tints the card (`color-mix`), the **state** paints the left rail. Colour carries
  meaning, so two different things never share a colour by accident.
- Progress rings are ordered **nearest-to-done first**, each with a small deliberate head start. That is
  the goal-gradient effect: proximity to completion is what accelerates behaviour, not raw score.
- **No streaks.** A streak's escalating cost turns a tool into a nag.
- A stalled task invites a next step by naming the exact action instead of shaming the gap.
