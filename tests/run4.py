import sys, time
from playwright.sync_api import sync_playwright
app=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream','--use-file-for-fake-audio-capture=voice.wav','--autoplay-policy=no-user-gesture-required'])
    # ---- app on the computer ----
    ctx=b.new_context(viewport={'width':1280,'height':1800}, accept_downloads=True); pg=ctx.new_page(); errs=[]
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://'+app)
    pg.wait_for_function('window.__takewise && window.__takewise.ref && window.__takewise.takes.length>0', timeout=60000)
    print('APP status:', pg.inner_text('#storeStatus'))
    print('APP card hidden:', pg.evaluate("document.querySelector('#getApp').hidden"), '| today shown:', pg.evaluate("!document.querySelector('#todayPanel').hidden"))
    pg.click('#btnTake'); time.sleep(21); pg.wait_for_function('window.__takewise.history.length>0', timeout=30000)
    pg.reload(); pg.wait_for_function('window.__takewise && window.__takewise.ref && window.__takewise.history.length>0', timeout=60000)
    print('APP after reload: takes', pg.evaluate('window.__takewise.history.length'), '| goal', pg.inner_text('#tGoalTxt'), '| streak', pg.inner_text('#tStreak'))
    print('APP backup info:', pg.inner_text('#backupInfo'))
    with pg.expect_download() as d: pg.click('#btnExport')
    print('APP backup file:', d.value.suggested_filename, '| msg:', pg.inner_text('#dataMsg'))
    print('APP backup info after:', pg.inner_text('#backupInfo'))
    pg.screenshot(path='app.png', full_page=True)
    ctx.close()
    # ---- Claude preview ----
    ctx=b.new_context(viewport={'width':1280,'height':1400}); 
    ctx.add_init_script("""window.__forceHosted=true; window.__saved=null;
      window.claude={use: async n => n==='downloads' ? {save: async r => { window.__saved={name:r.filename, size:r.data.size}; return {status:'saved'}; }} : null};
      const of=window.fetch; window.fetch = async u => String(u)==='Takewise.html' ? new Response('<html>app</html>') : of(u);""")
    pg=ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://'+app)
    pg.wait_for_function('window.__takewise && window.__takewise.ref && window.__takewise.takes.length>0', timeout=60000)
    print('PREVIEW card shown:', pg.evaluate("!document.querySelector('#getApp').hidden"), '| today hidden:', pg.evaluate("document.querySelector('#todayPanel').hidden"), '| progress hidden:', pg.evaluate("document.querySelector('#progress').hidden"))
    pg.click('#btnTake'); time.sleep(0.6)
    print('PREVIEW sing ->', pg.inner_text('#livePill'), '|', pg.inner_text('#liveText'))
    pg.click('#btnGetApp'); time.sleep(0.5)
    print('PREVIEW download:', pg.evaluate('JSON.stringify(window.__saved)'), '|', pg.inner_text('#getAppMsg'))
    pg.evaluate('window.scrollTo(0,0)'); pg.screenshot(path='preview.png')
    print('errors:', errs)
    b.close()
