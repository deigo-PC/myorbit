# Roadmap

The UI is still moving — this is a tool that gets changed by using it. Current thinking, nearest first.

## Next

- **Search and a full list.** The feed deliberately shows a selection (~15 rows). Everything else needs
  a way in: a search field plus "all tasks" grouped by area.
- **Momentum strip.** A small bar row of what moved in the last 7 days, so a week that felt wasted can
  be seen to have moved.
- **Weekly charts.** Progress over time per area, on the Sunday view.
- **A real screenshot in the README**, rendered from fake data so the repo stays data-free.

## Later

- **Offline read.** A service worker caching the last payload so the feed opens with no signal.
- **Reminders** for items that actually have a `due`, and nothing else.
- **Multiple stores** (work + personal separate files, one client).
- **Themes.** Light mode exists in the reference panel; the client is dark-first today.

## Not planned

- Streaks. Deliberately absent — study-level evidence links them to anxiety-driven use, and the
  escalating cost of breaking one is the mechanism.
- Accounts, sync, and any server-side copy of your data. It runs where you run it.
