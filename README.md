# Takewise

A singing practice app. Upload a track, sing along, and see where your pitch and volume drifted. Then drill the exact passage. Your takes, streak and daily goal are saved automatically on your computer.

## Use it

1. Download `Takewise.html` from this repository.
2. Open it in Chrome or Edge.
3. Allow the microphone when the browser asks.

Nothing is uploaded. Recordings and progress stay in the browser on your computer. Use **Save a backup** under Progress to keep a copy or move to another computer.

## Versions

Each version is a restore point (a Git tag):

| Version | What changed |
| --- | --- |
| `v3` | One app on your computer; the Claude link became a preview with a download button. Backups replace export/import. |
| `v2` | Progress tracking: saved takes, streaks, daily goal, nudges, habits and per-track scores. |
| `v1` | Upload a track, sing takes, pitch and volume feedback, targeted drills, blind mode. |

To go back to a version, ask Claude: “roll Takewise back to v2”. Claude restores that version as a new commit, so nothing later is lost.

## Files

- `Takewise.html` is the app you open. It is built from the source; don't edit it directly.
- `src/takewise.html` is the source.
- `build.sh` rebuilds `Takewise.html` from the source.
- `tests/` has the scripts used to test the app with a simulated singer in a headless browser.
