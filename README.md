# MyOrbit

A phone-first feed for a task store **you** host. One screen, usable with a thumb, so tasks get
updated on the go instead of in a browser tab that never gets opened.

- **Feed, not a board.** Today first, then the week, then the month, then a smaller personal block.
- **Progress you can see.** Every active project gets a ring that fills. Rings are ordered by what is
  closest to done, because proximity to completion is what actually accelerates behaviour.
- **Your data stays yours.** The client holds no state. It talks to a small JSON API you run.

## Quick start

```bash
git clone https://github.com/deigo-PC/myorbit && cd myorbit
python3 server/server.py          # stdlib only, no pip install
# open http://127.0.0.1:8787/
```
It seeds `server/store.json` and `server/config.json` from the examples on first run. Edit those,
hit reload, done.

## Layout

```
client/   the whole client — m.html (vanilla JS, no build step) + the manifest
server/   server.py: reference backend, one file, standard library only
          store.example.json · config.example.json
docs/     QUICKSTART · ARCHITECTURE · ROADMAP
assets/   app icons
```

## How it fits together

```
   phone / browser
        │  GET /api/tasks · PATCH /api/tasks/t001 · POST /api/config…
        ▼
   your server ──────► store.json     (the only state)
        │             config.json     (areas, palette, focus, personal block)
        └── serves the client + manifest
```
The client reads **all** its vocabulary — area names, colours, which projects matter, which areas are
personal — from `GET /api/config` at runtime. That is why the client can be shared publicly while the
thing it runs against stays private.

`server/server.py` is the reference implementation, and this same client also mounts as a plugin tab
in a Hermes dashboard (that is how the original runs). Same contract either way.

## Design principles

- **Colour carries meaning.** The area tints the card, the state paints the left rail. Two different
  things never share a colour by accident.
- **Size encodes priority.** The items that matter most are physically bigger.
- **Heat, not guilt.** A stalled task invites a next step by naming the exact action; it never goes red.
  Red is reserved for real dates.
- **No streaks.** A streak's escalating cost turns a tool into a nag.
- **Nothing is deleted by a tap you did not mean.** Archive is the default exit; delete is confirmed.

## Status

Early and openly evolving — the UI changes as it gets used daily. See `docs/ROADMAP.md`.

## License

MIT. Do what you like with it.
