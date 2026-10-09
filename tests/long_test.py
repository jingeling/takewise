# A longer song (many phrases): sing the whole song, drill a phrase twice, then check that
# How it went still lets you switch back to the whole-song breakdown.
# Make the test track first: python3 mksong.py && ffmpeg -stream_loop 3 -i song.wav -t 84 "Long song.mp3"
# Usage: python3 long_test.py /path/to/Takewise.html
import sys, time
from playwright.sync_api import sync_playwright
ARGS=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-audio-capture=voice.wav','--autoplay-policy=no-user-gesture-required']
res=[]
def ok(n,c,d=''): res.append(c); print('PASS' if c else 'FAIL', n, d, flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=ARGS); pg=b.new_page(viewport={'width':1280,'height':1000}); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://'+sys.argv[1]); pg.wait_for_function('window.__takewise && window.__takewise.ref && window.__takewise.takes.length>0', timeout=60000)
    pg.set_input_files('#fileTrack','Long song.mp3'); pg.wait_for_function("__takewise.ref.name==='Long song'", timeout=120000); time.sleep(0.5)
    pg.click('#goSing'); pg.click('#btnTake'); pg.wait_for_function('__takewise.history.length>0', timeout=200000); time.sleep(1)
    n=pg.locator('.phrstrip button').count(); ok('long song shows phrase strip', n>8, f'{n} phrases')
    ok('weakest phrases listed', pg.locator('.phr').count()==3)
    pg.screenshot(path='shots/long_whole.png', full_page=True)
    pg.locator('.phr').first.click(); time.sleep(0.5)
    for k in range(2):
        pg.click('#btnTake'); pg.wait_for_function(f'__takewise.history.length>{k+1}', timeout=60000); time.sleep(0.8)
    pg.click('.steps [data-step="3"]'); time.sleep(0.5)
    labels=pg.locator('.takepick button').all_inner_texts(); ok('picker offers whole song next to passages', any(l.startswith('Whole song') for l in labels) and len(labels)>=2, ' | '.join(labels))
    ok('latest passage take shown first', pg.evaluate('__takewise.selected.id')==3)
    pg.locator('.takepick button', has_text='Whole song').click(); time.sleep(0.6)
    ok('whole-song breakdown back', pg.evaluate('__takewise.selected.id')==1 and pg.locator('.phrstrip button').count()>8)
    pg.screenshot(path='shots/long_back.png', full_page=False)
    pg.set_viewport_size({'width':390,'height':844}); time.sleep(0.3)
    ok('no sideways scroll on phone', pg.evaluate('document.documentElement.scrollWidth')<=390)
    print('errors', errs); b.close()
print('SUMMARY', sum(res), '/', len(res))
