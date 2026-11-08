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
      pg.click('#saveBtn'); assert 'Teammate Value' in pg.inner_text('#miss')
      pg.locator('.sc').nth(4).locator('button').nth(n).click()
      for g in range(5,10): pg.locator('.sc').nth(g).locator('button').nth(n).click()
      pg.locator('.sc').nth(13).locator('button').nth(4).click()  # tech N/A
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
    assert 'Teammate Value' in pg.content() and 'formula v2' in pg.content()
    pg.click('text=One session'); pg.reload()
    assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions.length")==7
    assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions[0].results.techn")==None
    pg.screenshot(path=f'shots/arrow-{name}-single.png',full_page=True)
    w=pg.evaluate('document.documentElement.scrollWidth'); assert w<=vp['width'],w
    print(name,'ok')
  b.close()
print('errors',errs)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  pg=b.new_page(viewport={'width':390,'height':844}); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
  pg.goto(url); pg.click('text=Navy & Gold'); pg.locator('#ca').evaluate("el=>{el.value='#222222';el.dispatchEvent(new Event('change'))}")
  pg.locator('#colors').screenshot(path='shots/arrow-mobile-colors.png')
  au=pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--au')"); print('accent adjusted',au)
  assert au!='#222222'
  pg.click('nav >> text=3 Ethos'); pg.reload()
  assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).theme.a")=='#222222'
  assert pg.evaluate("document.documentElement.style.getPropertyValue('--g')")=='#1f3f8a'
  pg.screenshot(path='shots/arrow-mobile-ethos-themed.png',full_page=True)
  assert pg.evaluate('document.documentElement.scrollWidth')<=390
  print('theme ok',e)

with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  pg=b.new_page(); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
  pg.goto(url); pg.click('text=Build my first session')
  pg.evaluate("""()=>{const d=JSON.parse(localStorage.ae_arrow_v1);d.sessions=[{id:'old1',savedAt:1,name:'Old log',date:'2026-10-01',plan:{type:'Practice',sport:'Hockey',position:'Defense',season:'In Season',tactic:'T',techniques:['a'],tools:[],techn:[]},ethos:['e1','e2','e3','e4','e5'],scores:{tech:[1],perf:1,ethos:[0,0,0,0,0],tools:[],techn:[]},gear:{tools:[],techn:[]},notes:'',results:{tactics:1,perf:1,value:0,player:1,combined:1}}];d.sel={mode:'single',ids:['old1']};d.tab='past';localStorage.ae_arrow_v1=JSON.stringify(d)}""")
  pg.reload(); c=pg.content()
  assert 'legacy v1 formula' in c and 'n/a (legacy)' in c, 'legacy label'
  assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions[0].scores.val")==None
  pg.screenshot(path='shots/arrow-legacy.png',full_page=True)
  print('legacy ok',e)
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload()
    assert pg.evaluate("document.body.classList.contains('chalk')")
    t=pg.inner_text('main')
    assert 'I’m Clint Bruce, I was an arrow once too.' in t and 'football' not in t
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    if vp['width']==390:
      pg.screenshot(path='shots/arrow-chalk-welcome.png',full_page=True); pg.locator('#colors').screenshot(path='shots/arrow-chalk-colors.png')
    pg.click('text=Purple & Gold'); pg.reload(); assert not pg.evaluate("document.body.classList.contains('chalk')")
    assert pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).theme.p")=='#5b2a9e'
    # legacy user with no theme keeps classic green
    pg.evaluate("()=>{const d=JSON.parse(localStorage.ae_arrow_v1);delete d.theme;localStorage.ae_arrow_v1=JSON.stringify(d)}"); pg.reload()
    assert pg.evaluate("document.documentElement.style.getPropertyValue('--g')")=='#1e6b42'
    print('chalk ok',e); pg.close()
B=['5th string fullback in 8th grade','Naval Academy Hall of Fame Linebacker, Team Captain and MVP','NFL player with Baltimore Ravens and New Orleans Saints','Navy SEAL Officer','Husband of a beautiful Bride','Father of 3 BraveBruceBeauties.']
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload()
    assert pg.locator('#bio li').all_inner_texts()==B
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    if vp['width']==390: pg.screenshot(path='shots/arrow-welcome-bio.png',clip={'x':0,'y':0,'width':390,'height':760})
    print('bio ok',e); pg.close()
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload()
    assert pg.locator('.eq').count()==1 and pg.is_visible('#eq')
    assert pg.inner_text('#eq').replace('\u200b','')=='Angles + Allies + Advantages = Achievements'
    o=pg.evaluate("""()=>{const t=document.querySelector('main').innerHTML;return [t.indexOf('called the AchievementEquation.'),t.indexOf('id="eq"'),t.indexOf('sharing it with you here')]}""")
    assert o[0]<o[1]<o[2],o
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    if vp['width']==390: pg.screenshot(path='shots/arrow-welcome-equation.png',clip={'x':0,'y':0,'width':390,'height':640})
    print('eq ok',e); pg.close()
