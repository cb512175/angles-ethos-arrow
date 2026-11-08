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
      for g in range(9,14): pg.locator('.sc').nth(g).locator('button').nth(n).click()
      pg.locator('.sc').nth(8).locator('button').nth(4).click()  # tech N/A
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
    assert 'Teammate Value' in pg.content() and 'formula v3' in pg.content()
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
    assert 'I was an arrow once too.' in t and 'football' not in t
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
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload(); pg.evaluate('document.fonts.ready')
    assert pg.evaluate("document.fonts.check('16px \"Patrick Hand\"')"), 'font'
    assert 'Patrick' in pg.evaluate("getComputedStyle(document.querySelector('#eq')).fontFamily")
    assert 'Patrick' not in pg.evaluate("getComputedStyle(document.querySelector('main p')).fontFamily")
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    if vp['width']==390: pg.screenshot(path='shots/arrow-chalk-font.png',clip={'x':0,'y':0,'width':390,'height':700})
    pg.click('text=Build my first session'); assert 'Patrick' not in pg.evaluate("getComputedStyle(document.querySelector('#nm')).fontFamily")
    print('font ok'); pg.close()
T='The AchievementEquation bought time for my body to catch up with the conviction the other 3 parts of the human performance system (body+brain+mind+spirit) already had. Time matters, because most of winning is just lasting.'
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); e=[]; pg.on('pageerror',lambda x:e.append(str(x)))
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload(); t=pg.inner_text('main')
    assert t.count(T)==1 and t.index('a belief and a mission. '+T)>0
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    print('conv ok',e); pg.close()

import json,tempfile,os
with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
  for vp in [{'width':390,'height':844},{'width':1280,'height':900}]:
    pg=b.new_page(viewport=vp); e=[]; pg.on('pageerror',lambda x:e.append(str(x))); pg.on('console',lambda m: m.type=='error' and 'favicon' not in m.text and '404' not in m.text and e.append(m.text)); pg.on('dialog',lambda d:d.accept())
    pg.goto(url); pg.evaluate('localStorage.clear()'); pg.reload()
    li=[x.split(' ')[0] for x in pg.locator('main ol li').all_inner_texts()][:5]; assert li==['Tactics','Techniques','Teammate','Tools','Tech'],li
    pg.click('text=Build my first session'); pg.fill('#nm','V3 test'); pg.fill('#dt','2026-11-07')
    h=[x.split(' (')[0] for x in pg.locator('main h3').all_inner_texts()]; assert h==['1 · Tactics','2 · Techniques','3 · Teammate','4 · Tools','5 · Tech'],h
    pg.click('nav >> text=4 Self Score')
    assert 'pending' in pg.inner_text('#tacticsCard')
    sc=lambda g,i: pg.locator('.sc').nth(g).locator('button').nth(i).click()
    sc(0,2);sc(1,2);sc(2,3); sc(3,2); assert 'pending' in pg.inner_text('#tacticsCard'), 'value missing must stay pending'
    sc(4,1); sc(5,3); sc(6,4); sc(8,4)
    t=pg.inner_text('#tacticsCard'); assert '+1.28' in t and 'average of 3 active Angles' in t, t
    pg.click('#saveBtn'); assert 'Ethos 1' in pg.inner_text('#miss')
    for g in range(9,14): sc(g,2)
    o=pg.evaluate("[...document.querySelectorAll('#app h3')].map(h=>h.innerText)"); idx=lambda k:[i for i,x in enumerate(o) if x.startswith(k)][0]
    assert idx('Tactics Score')<idx('2 · Techniques')<idx('3 · Teammate')<idx('4 · Tools')<idx('5 · Tech')<idx('Ethos')<idx('Additional Factors'),o
    ft=pg.inner_text('#factors'); assert ft.index('How we handle sleep')<ft.index('1 to 5, higher is better')<ft.index('Sleep hours')
    pg.locator('#factors').screenshot(path=f'shots/arrow-factors-{vp["width"]}.png'); pg.locator('#tacticsCard').screenshot(path=f'shots/arrow-tactics-card-{vp["width"]}.png')
    pg.fill('#slh','8'); sc(14,3); pg.fill('#mn','pasta'); pg.reload()
    assert pg.input_value('#mn')=='pasta' and pg.input_value('#slh')=='8'
    pg.click('#saveBtn'); pg.wait_for_timeout(200)
    r=pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions[0]"); R=r['results']
    assert r['fv']==3 and abs(R['tactics']-(4/3+.5+2)/3)<1e-9 and R['techn'] is None and R['tools']==2 and R['teammate']==.5 and R['denom']==3 and R['combined']==R['tactics']+1 and r['factors']['sleep']==4 and r['factors']['meals'] is None, R
    assert 'Sleep 8 h' in pg.content() and 'Meal note: pasta' in pg.content()
    pg.click('nav >> text=2 Customize Session'); pg.click('#repeat'); pg.click('nav >> text=4 Self Score')
    assert pg.locator('.sc button[aria-pressed=true]').count()==0 and pg.input_value('#slh')=='' and pg.input_value('#mn')==''
    # import mixed v2 + v3
    d={'v':1,'sessions':[{'id':'imp2','savedAt':5,'name':'Imported v2','date':'2026-09-01','fv':2,'plan':{'type':'Practice','sport':'Hockey','position':'Defense','season':'In Season','tactic':'T','techniques':['a'],'tools':[],'techn':[]},'ethos':['1','2','3','4','5'],'scores':{'tech':[1],'perf':1,'val':2,'ethos':[1,1,1,1,1],'tools':[],'techn':[]},'gear':{'tools':[],'techn':[]},'notes':''}]}
    fn=tempfile.mktemp(suffix='.json'); open(fn,'w').write(json.dumps(d))
    pg.click('nav >> text=5 Past'); pg.set_input_files('input[type=file]',fn); pg.wait_for_timeout(300)
    s2=pg.evaluate("JSON.parse(localStorage.ae_arrow_v1).sessions.find(s=>s.id=='imp2')"); assert s2['fv']==2 and abs(s2['results']['player']-4/3)<1e-9
    pg.click('text=Load sample sessions'); pg.click('text=Pick sessions')
    for c in pg.locator('.sess input[type=checkbox]').all():
      if not c.is_checked(): c.check()
    assert 'Older sessions (formula v1/v2' in pg.content()
    btn=pg.locator('.lgb[data-hl=techniques]').first; btn.focus(); pg.keyboard.press('Enter')
    assert pg.locator('g[data-k=techniques]').first.get_attribute('opacity')=='1' and pg.locator('g[data-k=tactics]').first.get_attribute('opacity')=='0.18'
    assert pg.locator('.lgb[data-hl=techniques]').first.get_attribute('aria-pressed')=='true'
    pg.locator('svg[aria-label^="The 5 Angles"]').scroll_into_view_if_needed()
    pg.screenshot(path=f'shots/arrow-trend-highlight-{vp["width"]}.png')
    pg.locator('.lgb[data-hl=techniques]').first.focus(); pg.keyboard.press('Enter')
    assert pg.locator('g[data-k=tactics]').first.get_attribute('opacity')=='1'
    pg.locator('.lgb[data-hl=sleep]').first.click(); assert pg.locator('g[data-k=meals]').first.get_attribute('opacity')=='0.18'
    assert pg.evaluate('document.documentElement.scrollWidth')<=vp['width']
    print('v3 ok',e); pg.close()
