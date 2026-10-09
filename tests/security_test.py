# Security check: restores a crafted backup with script payloads in every text field,
# clicks through every screen, and fails if any of the payloads runs.
# Usage: python3 security_test.py /path/to/Takewise.html
import sys, json, time, os, tempfile
from playwright.sync_api import sync_playwright

APP = sys.argv[1]
X = '<img src=x onerror="window.__pwned=(window.__pwned||[]).concat(\'%s\')">'
now = int(time.time() * 1000)
def rec(i):
    return {"v": 1, "uid": "u%d" % i, "trackId": "sample", "trackName": X % 'trackName', "createdAt": now - i * 1000, "day": X % 'day',
            "a": 0, "b": 5, "mode": X % 'mode', "source": X % 'source', "t0Track": 0, "offset": 0, "tol": 50, "octFree": True,
            "onPitch": 0.5, "vol": X % 'vol', "bias": X % 'bias', "sung": X % 'sung',
            "phrases": [{"a": X % 'pa', "b": 2, "onPitch": X % 'pon', "vol": 0.5}, {"a": 2, "b": 4, "onPitch": 0.6, "vol": 0.5}],
            "hints": [{"key": X % 'key', "tone": X % 'tone', "title": X % 'title', "ev": X % 'ev', "tip": X % 'tip', "drill": {"a": X % 'da', "b": 3}}],
            "guess": {"pitch": X % 'guessP', "vol": X % 'guessV'}, "hasAudio": False, "events": [X % 'event']}
doc = {"app": "takewise", "version": 1, "profile": {"goal": X % 'goal'},
       "tracks": [{"id": "trk-evil", "name": X % 'tname', "dur": X % 'dur', "mLo": X % 'mlo', "mHi": 60, "file": "../../x", "sample": False, "addedAt": now}],
       "takes": [rec(i) for i in range(3)]}
path = os.path.join(tempfile.mkdtemp(), 'evil-backup.json')
json.dump(doc, open(path, 'w'))

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 900}); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + APP)
    pg.wait_for_function('window.__takewise && window.__takewise.ref && window.__takewise.takes.length>0', timeout=60000); time.sleep(0.5)
    pg.set_input_files('#fileImport', path); time.sleep(1.5)
    for n in [1, 2, 3]:
        pg.click(f'.steps [data-step="{n}"]'); time.sleep(0.3)
    pg.click('#takesBox summary'); time.sleep(0.3)
    for i in range(pg.locator('[data-show]').count()):
        pg.locator('[data-show]').nth(i).click(); time.sleep(0.3)
    if pg.locator('.more summary').count(): pg.click('.more summary')
    if pg.locator('[data-drill]').count(): pg.locator('[data-drill]').first.click(); time.sleep(0.5)
    pg.click('#btnProgress'); time.sleep(0.5); pg.keyboard.press('Escape')
    pg.click('.steps [data-step="1"]'); time.sleep(0.3)
    pw = pg.evaluate('window.__pwned||[]')
    print('PASS no injected code ran' if not pw else 'FAIL injected code ran: ' + str(pw))
    print('page errors:', errs[:5])
    b.close()
    sys.exit(1 if pw else 0)
