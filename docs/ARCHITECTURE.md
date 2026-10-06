# Architecture

Two pieces: a **client** with no state, and a **server** you own.

## The store

One JSON file. `{"rows": [ ...tasks ]}`. There is no database and no migration step — the shape below
is the contract.

| field | notes |
|---|---|
| `id` | `t001`, `t002`, … assigned on create |
| `title` | the one required field |
| `area` | must match an entry in `config.areas` to get a colour |
| `domain` | a coarse grouping (`Work`, `Personal`, …) |
| `state` | `open` · `active` · `waiting` · `verify` · `parked` · `later` · `done` |
| `kind` | `task` · `project` · `meeting` |
| `next_action` | the physical next step. Absent = stalled, and the client says so |
| `due` | `YYYY-MM-DD` |
| `priority` | 1–3, the 3-level flag the client writes |
| `blocker`, `waits_on` | whats in the way, and who |
| `children` | `[{"title": "...", "done": true}]` — drives the project rings |
| `moved` | last touched. Used for "stalled" and recency |
| `pinned` | flag, shown in its own strip |

Anything else in a row is preserved untouched, so you can carry your own fields.

## API

| method | path | purpose |
|---|---|---|
| GET | `/api/tasks` | `{"rows": [...], "count": n}` |
| POST | `/api/tasks` | create; server assigns `id` |
| PATCH | `/api/tasks/{id}` | partial update; unknown fields ignored |
| DELETE | `/api/tasks/{id}` | hard delete |
| POST | `/api/tasks/bulk` | `{"ids": [...], "patch": {...}}` or `{"ids": [...], "delete": true}` |
| GET | `/api/config` | the runtime config the client renders from |

Writes that only set `priority` are fine — but note this contract is written by us, so if you extend
the editable set, extend it in **both** the server's allow-list and the client.

## The client

`client/m.html`, one file, no build step. It works in two homes and detects which:

```js
const API = location.pathname.startsWith("/dashboard-plugins") ? "/api/plugins/panel" : "/api";
```
Everything else is the same code path: fetch config → fetch tasks → render → PATCH on edit.

Rendering rules worth not breaking:

- **Rings** are sorted by percentage complete descending, and each is given a small floor so nothing
  renders empty. That is deliberate: the goal-gradient effect says *proximity* to completion drives
  effort, so an all-empty ring row is demotivating by construction.
- **Cards**: `background: color-mix(in srgb, <area> 13%, panel)`, `border-left: 3px solid <state>`.
- **Stalled items** invite a next step in the row itself (`next t117: ...`) rather than being hidden.
