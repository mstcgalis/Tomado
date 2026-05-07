# Project Hours Tracking — Design Spec
_Tomado · 2026-05-07_

## Overview

Allow users to tag Pomodoro sessions with a named project, then view per-project time breakdowns in the stats menu. The feature is additive: no project is a valid state, and existing records (with `project: ""`) are preserved as-is.

---

## Data Model

### `prefs.json` additions

```json
{
  "current_project": "Tomado",
  "projects": ["Tomado", "Work", "Side Project"]
}
```

- `projects` — ordered list of project name strings. Defaults to `[]` for new/existing installs (handled by `prefs_update`).
- `current_project` — name of the active project, or `""` for none. Already exists.

### `stats.json`

No changes. Each record already has a `project` field (string). Deleting a project removes it from the `projects` list only; historical records retain their original project name string.

### Migration

`prefs_update` in `utilities.py` adds `"projects": []` to default prefs, so existing installs pick it up on first launch after update.

---

## Menu Structure

The top menu item shows the active project with a bullet indicator and updates live:

```
● Tomado                     ← top item; "○ No Project" when none active
  ├── No Project             ← sets current_project = ""
  ├── ────────────
  ├── Tomado                 ← one entry per saved project
  │     ├── Select           ← sets current_project = "Tomado"
  │     ├── Rename…          ← text input; updates projects list + current_project if active
  │     └── Delete           ← removes from projects; clears current_project if active
  ├── Work
  │     ├── Select
  │     ├── Rename…
  │     └── Delete
  └── + New Project…         ← text input dialog; adds to projects list and selects it
```

Behavior:
- **Select** — sets `current_project`, saves prefs, updates top item label.
- **Rename** — rumps text input; updates the name in `projects` and `current_project` if it was the active project.
- **Delete** — removes from `projects`; if it was `current_project`, clears to `""`. Historical stats records are untouched.
- **New Project** — rumps text input; appends to `projects`, sets as `current_project`.
- **No Project** — sets `current_project = ""`.

---

## Stats Display

### `compute_stats` return shape

```python
{
  "today": {
    "pomodoros": 4,
    "pomodoro_time": 7200,
    "breaks": 2,
    "break_time": 600,
    "by_project": {
      "Tomado": {"pomodoros": 3, "pomodoro_time": 5400, "breaks": 1, "break_time": 300},
      "Work":   {"pomodoros": 1, "pomodoro_time": 1800, "breaks": 1, "break_time": 300}
    }
  },
  "week": { "...", "by_project": { "..." } }
}
```

Projects with zero sessions in the period are omitted from `by_project`.

### Stats menu

```
— Daily Stats —
  Today: 4 🍅  2h 00m
  ● Tomado: 3 🍅  1h 30m     ← shown only when a project is active
  By Project ▶
    Tomado: 3 🍅  1h 30m
    Work: 1 🍅  0h 30m
— Weekly Stats —
  This week: 12 🍅  6h 00m
  ● Tomado: 9 🍅  4h 30m
  By Project ▶
    Tomado: 9 🍅  4h 30m
    Work: 3 🍅  1h 30m
```

The highlighted active-project line is omitted entirely when `current_project == ""`.

---

## Implementation Scope

Files to modify:
- `utilities.py` — extend `compute_stats` to populate `by_project`; add `"projects": []` to default prefs
- `tomado.py` — add project selector top item + submenu build/refresh logic; update stats menu to render `by_project` rows

No new files required.
