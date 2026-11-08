from playwright.sync_api import sync_playwright
import sys
url=sys.argv[1]; errs=[]
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for name,vp in [('mobile',{'width':390,'height':844}),('desktop',{'width':1280,'height':900})]:
    pg=b.new_page(viewport=vp); pg.on('console',lambda m: m.type=='error' and errs.append(m.text)); pg.on('pageerror',lambda e: errs.append(str(e)))
    pg.on('dialog',lambda d:d.accept())
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload()
    pg.screenshot(path=f'shots/arrow-{name}-welcome.png',full_page=True)
    pg.click('text=Build my first session')
    assert pg.input_value('#po')=='Defense' and pg.input_value('#se')=='In Season'
    pg.fill('#nm','Practice A'); pg.fill('#dt','2026-11-01')
    pg.screenshot(path=f'shots/arrow-{name}-session.png',full_page=True)
    pg.click('text=Next: Ethos'); pg.fill('#e0','Always Try Hard!!')
    pg.screenshot(path=f'shots/arrow-{name}-ethos.png',full_page=True)
    pg.click('nav >> text=2 Customize Session'); assert pg.input_value('#nm')=='Practice A'
    pg.reload(); assert pg.input_value('#nm')=='Practice A'
    pg.click('nav >> text=4 Self Score'); pg.click('#saveBtn'); assert pg.is_visible('#miss')
    def score(n):
      for g in range(3): pg.locator('.sc').nth(g).locator('button').nth(2).click()
      pg.locator('.sc').nth(3).locator('button').nth(n).click()
      for g in range(4,9): pg.locator('.sc').nth(g).locator('button').nth(n).click()
      pg.locator('.sc').nth(12).locator('button').nth(4).click()  # tech N/A
    score(2); assert not pg.is_visible('#miss')
    pg.screenshot(path=f'shots/arrow-{name}-score.png',full_page=True)
    pg.click('#saveBtn'); pg.wait_for_timeout(300)
    assert 'Always Try Hard!!' in pg.content()
    pg.click('nav >> text=2 Customize Session'); pg.click('#repeat')
    pg.click('nav >> text=4 Self Score'); assert pg.locator('.sc button[aria-pressed=true]').count()==0, 'scores not cleared'
    pg.click('nav >> text=2 Customize Session'); pg.fill('#nm','Practice B'); pg.fill('#dt','2026-11-05')
    pg.click('nav >> text=4 Self Score'); score(3); pg.click('#saveBtn'); pg.wait_for_timeout(300)
    pg.click('text=Date range'); pg.fill('#fr','2026-10-01'); pg.locator('#fr').dispatch_event('change')
    assert '2 session(s) selected' in pg.content()
    pg.click('text=Pick sessions'); pg.click('text=Load sample sessions')
    assert '5 session(s) selected' in pg.content()
    pg.screenshot(path=f'shots/arrow-{name}-trends.png',full_page=True)
    pg.click('text=One session'); pg.reload()
    assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions.length")==7
    assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions[0].results.techn")==None
    pg.screenshot(path=f'shots/arrow-{name}-single.png',full_page=True)
    w=pg.evaluate('document.documentElement.scrollWidth'); assert w<=vp['width'],w
    print(name,'ok')
  b.close()
print('errors',errs)
