# MyOrbit

A phone-first surface over my Hermes **MyOrbit** panel. Same store, same data — just a screen I can
actually use with a thumb, so tasks get updated on the go instead of in a browser tab I never open.

## What's here

| file | why |
|---|---|
| `m.html` | the mobile page (vanilla JS, no build step) — served by the Hermes dashboard at `/dashboard-plugins/panel/m.html` |
| `app.webmanifest` | manifest the page links to, so the shortcut opens the exact URL in standalone mode |
| `icon-*.png`, `icon.svg` | the app icon. Public URLs are required: Android's WebAPK service fetches manifest icons **without** the site session, so an auth-walled URL resolves to a login page and the launcher falls back to its own default |

## How it actually runs

The page is a *client*. It calls the dashboard plugin API it's served from (`/api/plugins/panel/*`) and
renders whatever comes back. The task data lives in the panel store on the server — **nothing is stored
in this repo, and nothing about the data is public.**

Because it's same-origin with the dashboard, editing works with the normal login session; there are no
tokens, keys or credentials anywhere in this code.

## Design notes worth keeping

- Cards mirror the desktop panel: the **area** tints the card (`color-mix`), the **state** paints the
  left rail, and the domain colours (`Work`, `Dev/Sys`, `deigo`) drive grouping.
- Progress rings are ordered **nearest-to-done first**, with a small deliberate head start. That's the
  goal-gradient effect: proximity to completion is what accelerates behaviour, not raw score.
- No streaks. A streak's escalating cost turns a tool into a nag.
- Feed in the morning, capture bar under the thumb, and a stalled task invites a next step by naming
  the exact command instead of shaming the gap.
