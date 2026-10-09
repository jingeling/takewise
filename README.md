# Takewise

A singing practice app. Upload a track, sing along, and see where your pitch and volume drifted. Then drill the exact passage. Your takes, streak and daily goal are saved automatically on your computer.

## Use it

1. Download `Takewise.html` from this repository.
2. Open it in Chrome or Edge.
3. Allow the microphone when the browser asks.

Nothing is uploaded. The first time, press **Choose folder** and pick a folder on your computer (for example the folder `Takewise.html` is in). Takewise then keeps everything in a `Takewise data` folder there:

- `takewise-progress.json`: every take's scores, your streak, goal and learning curve
- `recordings/`: your takes
- `tracks/`: the MP3s you uploaded

Clearing cookies and site data in the browser doesn't touch that folder. Afterwards, press **Choose folder**, pick the same folder, and your history comes back. Folder saving works in Chrome and Edge; other browsers keep progress in the browser only.

## Versions

Each version is its own commit on `main`, so you can return to any of them:

| Version | Commit | What changed |
| --- | --- | --- |
| v6.1 | `9a39f60` | How it went gets a row to switch between your recent takes, so the whole-song breakdown stays one tap away after practising a passage. Long songs show their phrases as one compact strip plus the three weakest phrases. |
| v6 | `f7c2bf5` | Calmer step-by-step layout: Pick a song → Sing → How it went → Fix one thing. Progress and settings open from the header. Backups and the progress file are checked field by field before use, closing a hole where a tampered backup could run code. Uses your computer's own fonts, so the app makes no outside requests. |
| v5 | `97fd04b` | Progress is saved to a folder on your computer and survives clearing browser data. |
| v4 | `5425f1b` | Review fixes: short drill passages, friendlier wording, uploaded recordings line up automatically, all tracks listed. |
| v3 | `bad08fb` | One app on your computer; the Claude link became a preview with a download button. Backups replace export/import. |
| v2 | `b1fb452` | Progress tracking: saved takes, streaks, daily goal, nudges, habits and per-track scores. |
| v1 | `c1413f0` | Upload a track, sing takes, pitch and volume feedback, targeted drills, blind mode. |

On GitHub, open **Commits** and click a commit to see that version, or open `Takewise.html` in it to download that version of the app.

To go back to a version, ask Claude: “roll Takewise back to v2”. Claude restores that version as a new commit, so nothing later is lost.

## Files

- `Takewise.html` is the app you open. It is built from the source; don't edit it directly.
- `src/takewise.html` is the source.
- `build.sh` rebuilds `Takewise.html` from the source.
- `tests/` has the scripts used to test the app with a simulated singer in a headless browser. `journey.py` runs 37 checks through the main things a user does. `long_test.py` checks a longer song and switching back to the whole-song take. `security_test.py` restores a tampered backup and checks that nothing in it can run as code.
