import sys, time, json, shutil, os, subprocess
from playwright.sync_api import sync_playwright
ARGS=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-audio-capture=voice.wav','--autoplay-policy=no-user-gesture-required']
URL='http://127.0.0.1:8765/Takewise.html'
srv=subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1','-d','www'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); time.sleep(1)
MOCK="""
window.showDirectoryPicker = async () => { const r = await navigator.storage.getDirectory(); return r.getDirectoryHandle('Takewise', {create:true}); };
FileSystemHandle.prototype.queryPermission = async function(){ return localStorage.getItem('__perm') || 'granted'; };
FileSystemHandle.prototype.requestPermission = async function(){ window.__asked=(window.__asked||0)+1; return 'granted'; };
"""
LIST="""(async()=>{ const out=[]; async function w(d,p){ for await (const [n,h] of d.entries()){ if(h.kind==='file'){ const f=await h.getFile(); out.push(p+n+' '+f.size); } else await w(h,p+n+'/'); } }
  const r=await navigator.storage.getDirectory(); try{ await w(await r.getDirectoryHandle('Takewise'),'Takewise/'); }catch(e){} return out; })()"""
res=[]; errs=[]
def ok(n,c,d=''): res.append(c); print('PASS' if c else 'FAIL', n, d, flush=True)
def hook(pg):
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'fonts' not in m.text and 'ERR_' not in m.text else None)
def ready(pg): pg.wait_for_function('window.__takewise && window.__takewise.ref && !window.__takewise.busy', timeout=90000); time.sleep(1)
prof='fprofile'; shutil.rmtree(prof, ignore_errors=True)
try:
  with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(prof,args=ARGS,viewport={'width':1280,'height':1400}); ctx.add_init_script(MOCK)
    pg=ctx.pages[0]; hook(pg); pg.goto(URL); ready(pg)
    ok('fresh: asks to choose a folder', 'Choose a folder' in pg.inner_text('#storeStatus'), pg.inner_text('#storeStatus'))
    pg.click('#storeStatus button'); time.sleep(1.5)
    ok('folder connected', 'Saved to your folder “Takewise”' in pg.inner_text('#storeStatus'), pg.inner_text('#storeStatus'))
    pg.set_input_files('#fileTrack', 'Twinkle guide vocal.mp3'); pg.wait_for_function("__takewise.ref.name==='Twinkle guide vocal'", timeout=90000); time.sleep(1)
    for k in range(2):
        pg.click('#btnTake'); pg.wait_for_function(f'__takewise.history.length>{k}', timeout=60000); time.sleep(0.5)
    pg.click('#goalUp'); time.sleep(2)
    files=pg.evaluate(LIST); print('   folder:', files)
    prog=[f for f in files if f.startswith('Takewise/Takewise data/takewise-progress.json')]
    ok('progress file written', len(prog)==1)
    ok('2 recordings in folder', len([f for f in files if '/recordings/' in f])==2)
    ok('uploaded MP3 in folder', any('/tracks/Twinkle guide vocal' in f and f.split()[-1]!='0' for f in files))
    txt=pg.evaluate("""(async()=>{const r=await navigator.storage.getDirectory(); const d=await (await r.getDirectoryHandle('Takewise')).getDirectoryHandle('Takewise data'); return await (await (await d.getFileHandle('takewise-progress.json')).getFile()).text();})()""")
    doc=json.loads(txt); ok('progress file has takes + goal', len(doc['takes'])==2 and doc['profile']['goal']==4, f"{len(doc['takes'])} takes, goal {doc['profile']['goal']}")
    before=pg.evaluate("[document.querySelector('#tStreak').textContent, document.querySelector('#tGoalTxt').textContent, __takewise.history.map(r=>Math.round(r.onPitch*100))]")
    ctx.close()
    # ---- clear cookies and site data (browser storage wiped; the folder on disk stays) ----
    ctx=p.chromium.launch_persistent_context(prof,args=ARGS,viewport={'width':1280,'height':1400}); ctx.add_init_script(MOCK)
    pg=ctx.pages[0]; pg.goto('http://127.0.0.1:8765/blank.html')
    pg.evaluate("new Promise(r=>{localStorage.clear(); const q=indexedDB.deleteDatabase('takewise'); q.onsuccess=q.onerror=q.onblocked=()=>r(1);})"); time.sleep(0.5)
    hook(pg); pg.goto(URL); ready(pg)
    ok('after clearing: history empty in browser', pg.evaluate('__takewise.history.length')==0)
    ok('after clearing: offers to bring history back', 'bring your history back' in pg.inner_text('#storeStatus'), pg.inner_text('#storeStatus'))
    pg.click('#storeStatus button'); pg.wait_for_function("__takewise.history.length===2", timeout=30000); time.sleep(3)
    after=pg.evaluate("[document.querySelector('#tStreak').textContent, document.querySelector('#tGoalTxt').textContent, __takewise.history.map(r=>Math.round(r.onPitch*100))]")
    ok('history, streak and goal restored', after==before, f'before {before} after {after}')
    ok('restore message', 'Brought back 2 takes' in pg.inner_text('#dataMsg'), pg.inner_text('#dataMsg'))
    ok('track reopened from folder', pg.evaluate('__takewise.ref.name')=='Twinkle guide vocal', pg.evaluate('__takewise.ref.name'))
    pg.locator('[data-show]').first.click(); pg.wait_for_function('__takewise.selected && __takewise.selected.light===false', timeout=30000)
    ok('old recording plays back from folder', pg.evaluate('!!__takewise.selected.play && !!__takewise.selected.um'))
    pg.screenshot(path='folder_restored.png', full_page=False)
    ctx.close()
    # ---- next visit: Chrome asks for permission again ----
    ctx=p.chromium.launch_persistent_context(prof,args=ARGS,viewport={'width':1280,'height':1400}); ctx.add_init_script(MOCK)
    pg=ctx.pages[0]; pg.goto('http://127.0.0.1:8765/blank.html'); pg.evaluate("localStorage.setItem('__perm','prompt')")
    hook(pg); pg.goto(URL); ready(pg)
    ok('next visit: asks for OK', 'needs your OK' in pg.inner_text('#storeStatus'), pg.inner_text('#storeStatus'))
    pg.evaluate("localStorage.setItem('__perm','granted')")
    pg.click('#btnTake'); pg.wait_for_function('__takewise.history.length>2', timeout=60000); time.sleep(2)
    ok('Sing a take re-allows the folder', 'Saved to your folder' in pg.inner_text('#storeStatus') and pg.evaluate('window.__asked')==1, pg.inner_text('#storeStatus'))
    files=pg.evaluate(LIST); ok('3rd take written to folder', len([f for f in files if '/recordings/' in f])==3)
    # ---- delete all clears the folder too ----
    pg.click('#btnDelete'); ok('delete warns about the folder', 'your folder “Takewise”' in pg.inner_text('#delWrap'), pg.inner_text('#delWrap')); pg.click('#delYes'); time.sleep(2)
    files=pg.evaluate(LIST); doc=json.loads(pg.evaluate("""(async()=>{const r=await navigator.storage.getDirectory(); const d=await (await r.getDirectoryHandle('Takewise')).getDirectoryHandle('Takewise data'); return await (await (await d.getFileHandle('takewise-progress.json')).getFile()).text();})()"""))
    ok('delete empties folder', len(doc['takes'])==0 and not any('/recordings/' in f for f in files), str(files))
    ok('still connected after delete', 'Saved to your folder' in pg.inner_text('#storeStatus'))
    ctx.close()
finally:
    srv.terminate()
print('ERRORS', errs[:10]); print('SUMMARY', sum(res), '/', len(res))
