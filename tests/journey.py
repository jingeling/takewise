import sys, time, json, shutil, os
from playwright.sync_api import sync_playwright
APP=sys.argv[1]; OUT=sys.argv[2] if len(sys.argv)>2 else '.'
ARGS=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-audio-capture=voice.wav','--autoplay-policy=no-user-gesture-required']
errs=[]; results=[]
def ok(name, cond, detail=''):
    results.append(('PASS' if cond else 'FAIL', name, detail)); print(('PASS' if cond else 'FAIL'), name, detail, flush=True)
def hook(pg):
    pg.on('pageerror', lambda e: errs.append('PAGEERROR '+str(e)))
    pg.on('console', lambda m: errs.append('CONSOLE '+m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text and 'fonts.g' not in m.text else None)
def ready(pg): pg.wait_for_function('window.__takewise && window.__takewise.ref && !window.__takewise.busy', timeout=90000); time.sleep(0.5)
def take(pg, n_before, wait=25):
    pg.click('#btnTake'); pg.wait_for_function(f'window.__takewise.history.length>{n_before}', timeout=wait*1000+30000); time.sleep(0.5)
prof=os.path.join(OUT,'profile'); shutil.rmtree(prof, ignore_errors=True)
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(prof, args=ARGS, viewport={'width':1280,'height':1500}, accept_downloads=True)
    pg=ctx.pages[0]; hook(pg); pg.goto('file://'+APP); ready(pg)
    pg.screenshot(path=f'{OUT}/01_first_run.png', full_page=True)
    ok('first run shows example take', pg.evaluate("window.__takewise.selected && window.__takewise.selected.source==='example'"))
    ok('first run nudge', 'start here' in pg.inner_text('#tNudge').lower(), pg.inner_text('#tNudge'))
    # J2 upload MP3
    pg.set_input_files('#fileTrack', 'Twinkle guide vocal.mp3'); pg.wait_for_function("window.__takewise.ref && window.__takewise.ref.name==='Twinkle guide vocal'", timeout=90000); time.sleep(1)
    R=pg.evaluate("({dur:__takewise.ref.dur, clar:__takewise.ref.clarity, notes:__takewise.ref.notes.length, lo:document.querySelector('#trackMeta').textContent, takes:__takewise.takes.length})")
    ok('mp3 decoded and analysed', R['dur']>20 and R['notes']>=20, json.dumps(R))
    ok('mp3 melody range C4-A4', 'C4' in R['lo'] and 'A4' in R['lo'], R['lo'])
    ok('new track starts with no takes', R['takes']==0)
    ph=pg.evaluate("__takewise.ref.phrases.map(p=>+((p.i1-p.i0)*256/11025).toFixed(1))"); ok('song split into short phrases', len(ph)>=3 and max(ph)<=8.5, str(ph))
    ok('new track listed before singing', 'Twinkle guide vocal' in pg.inner_text('#tracksList') and 'No takes yet' in pg.inner_text('#tracksList'), pg.inner_text('#tracksList').replace('\n',' | '))
    ok('tolerance explained in plain words', 'piano-key' in pg.inner_text('#tolHint'), pg.inner_text('#tolHint'))
    pg.screenshot(path=f'{OUT}/02_uploaded.png', full_page=True)
    # J7 range test
    pg.click('#btnLow'); time.sleep(4.2)
    ok('range low recorded', pg.evaluate('__takewise.range.low')!=None, pg.inner_text('#rangeOut'))
    # J4 drill via phrase: select region by drag on overview
    box=pg.locator('#overview').bounding_box()
    pg.mouse.move(box['x']+box['width']*0.05, box['y']+20); pg.mouse.down(); pg.mouse.move(box['x']+box['width']*0.3, box['y']+20, steps=8); pg.mouse.up(); time.sleep(0.3)
    reg=pg.evaluate('__takewise.region'); ok('drag selects a passage', reg is not None and reg['b']-reg['a']>3, json.dumps(reg)+' | '+pg.inner_text('#regionText'))
    # J3 guided take on passage
    take(pg, 0, 10)
    t=pg.evaluate("({a:__takewise.selected.a,b:__takewise.selected.b,src:__takewise.selected.source,ev:__takewise.selected.events, on:__takewise.selected.stats.onPitch})")
    ok('passage take recorded within passage', abs(t['a']-reg['a'])<0.01 and t['b']<=reg['b']+0.01, json.dumps(t))
    ok('first take event', any('First take' in e for e in t['ev']), json.dumps(t['ev']))
    # J12 stop mid take
    pg.click('#btnClearRegion'); time.sleep(0.2)
    pg.click('#btnTake'); time.sleep(5); pg.click('#btnStop'); pg.wait_for_function('__takewise.history.length>1', timeout=30000); time.sleep(0.5)
    s=pg.evaluate("({a:__takewise.selected.a,b:__takewise.selected.b})"); ok('stopped take length ~3.5s', 2.5 < s['b']-s['a'] < 4.2, json.dumps(s))
    # J5 blind
    pg.click('#segMode button[data-v=blind]'); 
    box=pg.locator('#overview').bounding_box(); pg.mouse.move(box['x']+box['width']*0.05, box['y']+20); pg.mouse.down(); pg.mouse.move(box['x']+box['width']*0.3, box['y']+20, steps=8); pg.mouse.up()
    take(pg, 2, 10)
    ok('blind take hides scores', pg.is_visible('#btnReveal') and '?' in pg.inner_text('#takeRows'))
    pg.click('[data-g=pitch] button[data-v=on]'); pg.click('[data-g=vol] button[data-v=follow]'); pg.click('#btnReveal'); time.sleep(0.3)
    ok('reveal shows guess check', 'guess' in pg.inner_text('#resBody').lower(), pg.inner_text('#resBody')[:160].replace('\n',' | '))
    pg.click('#segMode button[data-v=guided]')
    # J8 settings
    pg.click('#segTol button[data-v="25"]'); pg.click('#chkOct'); pg.click('#chkOct'); time.sleep(0.3)
    ok('settings change no crash', True)
    # drill button
    if pg.locator('[data-drill]').count():
        pg.locator('[data-drill]').first.click(); time.sleep(0.4); r=pg.evaluate('__takewise.region'); ok('drill passage is short', r and r['b']-r['a']<=9, pg.inner_text('#regionText'))
    ok('phrase-by-phrase shown', pg.locator('.phr').count()>=2, str(pg.locator('.phr').count()))
    ok('friendly times (no tenths) in labels', '.' not in pg.inner_text('#regionText') and '.' not in pg.inner_text('#resMeta'), pg.inner_text('#regionText')+' / '+pg.inner_text('#resMeta'))
    # J13 keyboard listen
    pg.click('h1'); pg.keyboard.press('Space'); time.sleep(0.6); ok('space starts listening', pg.inner_text('#livePill')=='Listening to the track', pg.inner_text('#livePill')); pg.keyboard.press('Space'); time.sleep(0.3)
    # backup
    with pg.expect_download() as d: pg.click('#btnExport')
    bpath=os.path.join(OUT,'backup.json'); d.value.save_as(bpath); bk=json.load(open(bpath))
    ok('backup has takes and tracks', len(bk['takes'])==3 and any(t['id'].startswith('trk-') for t in bk['tracks']), f"{len(bk['takes'])} takes")
    pg.screenshot(path=f'{OUT}/03_after_takes.png', full_page=True)
    hist=pg.evaluate('__takewise.history.length')
    ctx.close()
    # J reopen: same profile
    ctx=p.chromium.launch_persistent_context(prof, args=ARGS, viewport={'width':1280,'height':1500}); pg=ctx.pages[0]; hook(pg); pg.goto('file://'+APP); ready(pg)
    ok('reopen restores last track', pg.evaluate('__takewise.ref.name')=='Twinkle guide vocal', pg.evaluate('__takewise.ref.name'))
    ok('reopen restores takes', pg.evaluate('__takewise.takes.length')==hist, str(pg.evaluate('__takewise.takes.length')))
    ok('reopen today goal', pg.inner_text('#tGoalTxt')=='3 / 3 takes', pg.inner_text('#tGoalTxt'))
    ok('reopen remembers settings', pg.evaluate('__takewise.set.tol')==25)
    # J14 load recording of saved take
    pg.locator('[data-show]').first.click(); pg.wait_for_function('__takewise.selected && __takewise.selected.light===false', timeout=30000)
    ok('saved take recording loads', pg.evaluate('!!__takewise.selected.um'))
    # J11 switch to sample via tracks list
    btn=pg.locator('#tracksList [data-open="sample"]')
    if btn.count(): btn.click(); pg.wait_for_function("__takewise.ref.id==='sample'", timeout=60000); time.sleep(0.5); ok('switch track to sample', True)
    else: ok('switch track to sample', False, pg.inner_text('#tracksList'))
    # J10 delete all
    pg.click('#btnDelete'); pg.click('#delYes'); time.sleep(1)
    ok('delete clears progress', pg.evaluate('__takewise.history.length')==0 and pg.inner_text('#tStreak')=='0')
    ctx.close()
    ctx=p.chromium.launch_persistent_context(prof, args=ARGS, viewport={'width':1280,'height':1500}); pg=ctx.pages[0]; hook(pg); pg.goto('file://'+APP); ready(pg)
    ok('delete persists after reopen', pg.evaluate('__takewise.history.length')==0)
    # J9 restore
    pg.set_input_files('#fileImport', bpath); time.sleep(1)
    ok('restore backup', pg.evaluate('__takewise.history.length')==3, pg.inner_text('#dataMsg'))
    # J6 upload a recording of a take
    pg.evaluate("document.querySelector('#micHelp').hidden=false")
    pg.set_input_files('#fileTake', 'voice.wav'); pg.wait_for_function('__takewise.history.length>3', timeout=60000)
    ok('uploaded recording scored', pg.evaluate("__takewise.selected.source==='file'"), str(round(pg.evaluate('__takewise.selected.stats.onPitch')*100))+'% on pitch')
    ok('uploaded recording auto-aligned', abs(abs(pg.evaluate('__takewise.selected.offset'))-1.5)<0.15 and pg.evaluate('__takewise.selected.stats.onPitch')>0.8, 'offset '+str(round(pg.evaluate('__takewise.selected.offset'),2))+' s · '+json.dumps(pg.evaluate('__takewise.selected.stats.hints.map(h=>h.title)')))
    # phone + dark
    pg.set_viewport_size({'width':390,'height':900}); pg.emulate_media(color_scheme='dark'); time.sleep(0.5)
    ow=pg.evaluate('document.documentElement.scrollWidth'); ok('no sideways scroll on phone', ow<=390, str(ow))
    pg.screenshot(path=f'{OUT}/04_phone_dark.png', full_page=True)
    ctx.close()
print('\nERRORS:', json.dumps(errs, indent=1)[:3000])
print('SUMMARY', sum(r[0]=='PASS' for r in results), 'pass /', len(results))
