# Quickstart

## 1. Run it

```bash
git clone https://github.com/deigo-PC/myorbit && cd myorbit
python3 server/server.py
```
Needs Python 3.9+. No dependencies. First run copies the examples to `server/store.json` and
`server/config.json`.

```bash
python3 server/server.py --port 9000 --store ~/orbit.json --config ~/orbit-config.json
python3 server/server.py --host 0.0.0.0        # reachable from other devices on your network
```

## 2. Make it yours

Open `server/config.json`. That file is the whole personality of your instance:

| key | what it decides |
|---|---|
| `areas` + `palette` | the area names in the capture picker, and their colours |
| `work_areas` | which areas count as work (everything else can be filtered out) |
| `focus_projects` | projects that dominate the feed and get the large rows |
| `prime_by_weekday` | which project is expected on which day (`1` = Monday) |
| `project_keywords` | substrings that map a task to a project, for grouping and rings |
| `area_projects` | a project implied by an area, when the title says nothing |
| `personal_areas` | areas that appear in the smaller personal block |
| `name`, `icons` | manifest name and icon URLs |

Then edit `server/store.json`: add a task with `state: "open"`, a `title`, and an `area` that exists
in your config. Reload. It appears.

Project rings come from `children`:

```json
{"id": "t001", "title": "Relaunch — ship the new pricing page", "area": "Website",
 "kind": "project", "state": "active", "children": [{"title": "hero copy", "done": true}]}
```

## 3. Put it on your phone

You need it reachable over HTTPS — an installed web app cannot come from plain `http://`, and
`localhost` is not your phone.

- **Private, easiest:** [Tailscale](https://tailscale.com) on both ends, then
  `tailscale serve --bg 8787` publishes it to your tailnet over HTTPS, no ports opened.
- **Public:** any reverse proxy or tunnel in front of the port.

Then in Chrome: open the URL, log in if you put auth in front, ⋮ → **Install app**.

One gotcha worth knowing: when a web app is installed, Android mints its icon from the manifest
**on Google's servers**, which fetch the icon URLs with no cookies. If your app sits behind a login,
put the icons somewhere genuinely public (a public repo is the cheap trick) and set `icons` in your
config to those URLs. Otherwise the launcher silently uses a default.
