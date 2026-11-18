"""Independent browser/API journeys; does not read implementation or other tests."""
import asyncio,json,os,re,time,traceback,urllib.error,urllib.request
from pathlib import Path
from playwright.async_api import async_playwright

CONFIG=json.loads(Path('/work/config.json').read_text())
BASE=CONFIG['base'];MOCK=CONFIG['mock'];LEGACY=CONFIG['legacy']
FIELDS=['legal_name','hq_city','ceo','founded_year','headcount_range','funding_total']
NOW='2026-03-01T09:00:00+02:00'
FIXTURE={'now':NOW,'users':[{'id':'reader_a','email':'a@reader.test','password':'reader-pass-a','display_name':'Reader A'},{'id':'reader_b','email':'b@reader.test','password':'reader-pass-b','display_name':'Reader B'}]}
OUT=Path('/work/browser-results.json');SHOTS=Path('/work/browser-shots');SHOTS.mkdir(exist_ok=True)
results=[];secret_values=[]

def request(path,method='GET',body=None,token=None,at=BASE,key=None):
    headers={'Content-Type':'application/json; charset=utf-8'}
    if token:headers['Authorization']='Bearer '+token
    if key:headers['Idempotency-Key']=key
    if path.startswith('/_mock/'):headers['X-Mock-Admin']='reader-local-admin'
    data=json.dumps(body).encode() if body is not None else None
    try:r=urllib.request.urlopen(urllib.request.Request(at+path,data=data,headers=headers,method=method),timeout=12)
    except urllib.error.HTTPError as exc:r=exc
    raw=r.read();value=json.loads(raw) if raw else None
    return r.status,value

async def api(path,method='GET',body=None,token=None,at=BASE,key=None,want=200):
    status,value=await asyncio.to_thread(request,path,method,body,token,at,key)
    assert status==want,(method,path,'expected',want,'actual',status,'error',value.get('error',{}).get('code') if isinstance(value,dict) else None)
    if isinstance(value,dict) and isinstance(value.get('token'),str):secret_values.append(value['token'])
    return value

async def admin(path,body=None):
    return await api('/_mock/'+path,'POST' if body is not None else 'GET',body,at=MOCK,want=204 if body is not None else 200)

async def setup(domains=()):
    await api('/_test/reset','POST',FIXTURE,want=204)
    await admin('reset',{'epoch':0})
    login=await api('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'})
    token=login['token']
    for domain in domains:
        await api('/dossiers','POST',{'domain':domain},token,key='browser-seed-'+domain,want=202)
        await terminal(domain,token)
    return token

async def terminal(domain,token,at=BASE,seconds=20):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        d=await api('/dossiers/'+domain,token=token,at=at)
        if d['state']!='building':return d
        await asyncio.sleep(.1)
    raise AssertionError(('build did not finish',domain))

async def wait_text(locator,text,timeout=10000):
    until=time.monotonic()+timeout/1000
    while time.monotonic()<until:
        if await locator.count() and text in await locator.inner_text():return
        await asyncio.sleep(.05)
    raise AssertionError(('missing expected visible text',text))

async def login(page,expected='/'):
    await page.goto(BASE+'/login')
    await page.get_by_test_id('login-email').fill('a@reader.test')
    await page.get_by_test_id('login-password').fill('reader-pass-a')
    await page.get_by_test_id('login-submit').click()
    await wait_text(page.get_by_test_id('current-user'),'Reader A')
    await page.wait_for_url(BASE+expected)

async def shot(page,name):
    await page.screenshot(path=str(SHOTS/(name+'.png')),full_page=True)

async def no_overflow(page):
    assert await page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),('horizontal overflow',page.url)

async def labels(page,ids):
    for name in ids:
        element=page.get_by_test_id(name)
        assert await element.count()==1 and await element.is_visible(),name
        assert await element.evaluate('(el) => Array.from(el.labels || []).some(l => l.innerText.trim() && getComputedStyle(l).display !== "none" && getComputedStyle(l).visibility !== "hidden")'),('missing visible label',name)

async def field_view(page,d):
    await wait_text(page.get_by_test_id('dossier-domain'),d['domain'])
    await wait_text(page.get_by_test_id('dossier-state'),d['state'])
    assert (await page.get_by_test_id('dossier-domain').inner_text()).strip()==d['domain']
    assert (await page.get_by_test_id('dossier-state').inner_text()).strip()==d['state']
    assert await page.get_by_test_id('dossier-spent').get_attribute('data-units')==str(d['spent_units'])
    order=await page.locator('[data-testid]').evaluate_all('(els) => els.map(e=>e.dataset.testid).filter(x=>/^field-(legal_name|hq_city|ceo|founded_year|headcount_range|funding_total)$/.test(x))')
    assert order==['field-'+f for f in FIELDS],order
    for field in FIELDS:
        v=d['fields'][field];container=page.get_by_test_id('field-'+field)
        assert await container.get_attribute('data-status')==v['status']
        val=page.get_by_test_id('field-value-'+field)
        assert await val.count()==(v['value'] is not None)
        if v['value'] is not None:
            assert await val.get_attribute('data-value')==str(v['value'])
            assert (await val.inner_text()).strip()
        assert await page.get_by_test_id('field-contested-'+field).count()==(v['status']=='contested')
        assert await page.get_by_test_id('field-citations-'+field).count()==1
        for i,c in enumerate(v['citations'],1):
            el=page.get_by_test_id(f'citation-{field}-{i}')
            assert re.sub(r'\s+',' ',c['excerpt']) in re.sub(r'\s+',' ',await el.inner_text())
            assert await el.get_attribute('data-provider')==c['provider']
            assert await el.locator('a').first.get_attribute('href')==c['url']
    timestamp=page.get_by_test_id('dossier-researched-at')
    if d['researched_at'] is None:assert await timestamp.count()==0
    else:
        text=await timestamp.inner_text();assert d['researched_at'] in text
        values=[await timestamp.get_attribute('datetime'),await timestamp.get_attribute('data-value')]
        for node in await timestamp.locator('[datetime],[data-value]').all():
            values.extend([await node.get_attribute('datetime'),await node.get_attribute('data-value')])
        assert d['researched_at'] in values,('missing machine-readable timestamp',await timestamp.evaluate('(e)=>e.outerHTML'))
        human=text.replace(d['researched_at'],'').strip()
        assert human and re.search(r'\b0?9:00\b',human),('people-first original-offset time',human)

async def evidence_view(page,d):
    await page.get_by_test_id('evidence-'+FIELDS[0]).wait_for()
    nonempty=next((field for field in FIELDS if d['fields'][field]['candidates']),None)
    if nonempty:await page.get_by_test_id('candidate-'+nonempty+'-1').wait_for()
    for field in FIELDS:
        group=page.get_by_test_id('evidence-'+field);assert await group.count()==1
        cands=d['fields'][field]['candidates']
        assert await page.get_by_test_id('evidence-empty-'+field).count()==(not cands)
        for i,c in enumerate(cands,1):
            el=page.get_by_test_id(f'candidate-{field}-{i}')
            assert await el.get_attribute('data-value')==str(c['value'])
            for attr,key in [('data-provider','provider'),('data-url','url')]:assert await el.get_attribute(attr)==c[key]
            assert await el.get_attribute('data-kind') is not None
            if c['kind'] is not None:assert await el.get_attribute('data-kind')==c['kind']
            assert await el.get_attribute('data-published-at')==(c['published_at'] or '')
            assert await el.get_attribute('data-selected')==str(c['selected']).lower()
            text=await el.inner_text()
            assert re.sub(r'\s+',' ',c['excerpt']) in re.sub(r'\s+',' ',text)
            assert c['retrieved_at'] in text
            if c['published_at'] is not None:assert c['published_at'] in text

async def new_page(browser,width=1280):
    context=await browser.new_context(viewport={'width':width,'height':900},timezone_id='America/Los_Angeles')
    page=await context.new_page()
    page.set_default_timeout(8000)
    return context,page

async def test_auth(browser):
    await setup(['amber-rank.test'])
    context,page=await new_page(browser)
    try:
        await page.goto(BASE+'/signup')
        await labels(page,['signup-email','signup-password','signup-display-name'])
        await page.get_by_test_id('signup-email').fill('new@browser.test')
        await page.get_by_test_id('signup-password').fill('browser-password')
        await page.get_by_test_id('signup-display-name').fill('Browser Reader')
        await page.get_by_test_id('signup-submit').click()
        await wait_text(page.get_by_test_id('current-user'),'Browser Reader')
        assert await page.get_by_test_id('auth-error').count()==0
        await page.get_by_test_id('logout-button').click()
        await page.goto(BASE+'/dossiers/amber-rank.test/evidence')
        await page.wait_for_url(re.compile(r'/login'))
        await labels(page,['login-email','login-password'])
        await page.get_by_test_id('login-email').fill('a@reader.test')
        await page.get_by_test_id('login-password').fill('wrong-password')
        await page.get_by_test_id('login-submit').click()
        await page.get_by_test_id('auth-error').wait_for(state='visible')
        assert (await page.get_by_test_id('auth-error').inner_text()).strip()
        await page.get_by_test_id('login-password').fill('reader-pass-a')
        await page.get_by_test_id('login-submit').click()
        await page.wait_for_url(BASE+'/dossiers/amber-rank.test/evidence')
        await wait_text(page.get_by_test_id('current-user'),'Reader A')
        assert await page.get_by_test_id('auth-error').count()==0
        await shot(page,'desktop-auth-return')
    finally:await context.close()

async def test_routes(browser,width):
    token=await setup(['silver-value.test','maple-complete.test','amber-rank.test'])
    context,page=await new_page(browser,width)
    try:
        await login(page)
        await labels(page,['research-domain','dossier-search'])
        items=page.locator('[data-testid^="dossier-item-"]')
        await items.first.wait_for()
        ids=await items.evaluate_all('(els)=>els.map(e=>e.dataset.testid)')
        assert ids==['dossier-item-amber-rank.test','dossier-item-maple-complete.test','dossier-item-silver-value.test']
        await page.get_by_test_id('dossier-search').fill('Maple Complete, LLC')
        await page.wait_for_function('''() => document.querySelectorAll('[data-testid^="dossier-item-"]').length === 1 && !!document.querySelector('[data-testid="dossier-item-maple-complete.test"]')''')
        await page.get_by_test_id('dossier-search').fill('no-such-company')
        await page.get_by_test_id('empty-dossiers').wait_for()
        assert await page.get_by_test_id('dossier-list').count()==0
        await page.get_by_test_id('dossier-search').fill('')
        await page.get_by_test_id('dossier-item-amber-rank.test').wait_for()
        await no_overflow(page);await shot(page,f'{width}-list')
        for domain in ['amber-rank.test','silver-value.test','maple-complete.test']:
            await page.goto(BASE+'/dossiers/'+domain)
            d=await api('/dossiers/'+domain,token=token)
            await field_view(page,d);await no_overflow(page)
            await shot(page,f'{width}-dossier-{domain}')
            await page.get_by_test_id('dossier-evidence-link').click()
            await page.get_by_test_id('evidence-ceo').wait_for()
            await evidence_view(page,d);await no_overflow(page)
            await shot(page,f'{width}-evidence-{domain}')
        nav=page.locator('a[href="/contested"]:visible').first
        if await nav.count()==0:
            menu=page.get_by_role('button',name=re.compile('menu|navigation',re.I))
            if await menu.count():await menu.first.click()
            nav=page.locator('a[href="/contested"]:visible').first
        assert await nav.count()>0
        await nav.click();await page.get_by_test_id('contested-list').wait_for()
        ids=await page.locator('[data-testid^="contested-item-"]').evaluate_all('(els)=>els.map(e=>e.dataset.testid)')
        assert ids==['contested-item-amber-rank.test-ceo','contested-item-maple-complete.test-ceo','contested-item-silver-value.test-funding_total'],ids
        zero=page.get_by_test_id('contested-item-silver-value.test-funding_total')
        assert await zero.get_attribute('data-value')=='0'
        assert re.search(r'(?<![0-9])0(?![0-9])',await zero.inner_text())
        assert await zero.locator('a').first.get_attribute('href')=='/dossiers/silver-value.test/evidence'
        await no_overflow(page);await shot(page,f'{width}-contested')
        await page.goto(BASE+'/dossiers/absent-browser.test')
        await page.get_by_test_id('dossier-not-found').wait_for()
        assert await page.get_by_test_id('field-ceo').count()==0
        await no_overflow(page)
        await page.goto(BASE+'/')
        field=page.get_by_test_id('research-domain')
        await page.locator('body').click(position={'x':2,'y':2})
        before=await field.evaluate('(e)=>{let s=getComputedStyle(e);return [s.outline,s.boxShadow,s.borderColor,s.backgroundColor].join("|")}')
        await field.focus()
        after=await field.evaluate('(e)=>{let s=getComputedStyle(e);return [s.outline,s.boxShadow,s.borderColor,s.backgroundColor].join("|")}')
        assert before!=after,('keyboard focus not visually apparent',before,after)
    finally:await context.close()

async def test_research_poll(browser):
    token=await setup()
    context,page=await new_page(browser)
    try:
        await login(page)
        await page.get_by_test_id('empty-dossiers').wait_for()
        await page.get_by_test_id('research-domain').fill('https://invalid.test/path')
        await page.get_by_test_id('research-submit').click()
        await page.get_by_test_id('research-error').wait_for()
        assert await page.get_by_test_id('research-uncertain').count()==0
        await admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':.6})
        reads=[]
        page.on('request',lambda r:reads.append(time.monotonic()) if r.method=='GET' and r.url==BASE+'/dossiers/maple-complete.test' and 'text/html' not in r.headers.get('accept','') else None)
        await page.get_by_test_id('research-domain').fill(' WWW.MAPLE-COMPLETE.TEST. ')
        await page.get_by_test_id('research-submit').click()
        await page.wait_for_url(BASE+'/dossiers/maple-complete.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready',timeout=20000)
        assert await page.get_by_test_id('field-value-ceo').get_attribute('data-value')=='Bob Stone'
        assert len(reads)>=2 and max(b-a for a,b in zip(reads,reads[1:]))<=2.1,('building poll cadence',reads)
        count=len(reads);await asyncio.sleep(2.2);assert len(reads)==count
        await page.goto(BASE+'/')
        await page.get_by_test_id('dossier-item-maple-complete.test').wait_for()
        # Another client has the domain before the stale form's create is submitted.
        await api('/dossiers','POST',{'domain':'amber-rank.test'},token,key='other-client-create',want=202)
        await terminal('amber-rank.test',token)
        before=len((await admin('log'))['calls'])
        await page.get_by_test_id('research-domain').fill('WWW.AMBER-RANK.TEST.')
        await page.get_by_test_id('research-submit').click()
        await page.wait_for_url(BASE+'/dossiers/amber-rank.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        assert len((await admin('log'))['calls'])==before
        await page.get_by_test_id('dossier-reload').click()
        await asyncio.sleep(.2);assert len((await admin('log'))['calls'])==before
    finally:await context.close()

async def test_latest_read(browser):
    token=await setup(['reader-full.test'])
    context,page=await new_page(browser)
    gate=asyncio.Event();captured=asyncio.Event();count=0
    try:
        await login(page);await page.goto(BASE+'/dossiers/reader-full.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        async def hold(route):
            nonlocal count
            if route.request.method!='GET' or 'text/html' in route.request.headers.get('accept',''):
                await route.continue_();return
            count+=1;number=count
            response=await route.fetch()
            if number==1:
                captured.set();await asyncio.wait_for(gate.wait(),15)
            await route.fulfill(response=response)
        await page.route('**/dossiers/reader-full.test',hold)
        await page.get_by_test_id('dossier-reload').click()
        await asyncio.wait_for(captured.wait(),5)
        await shot(page,'desktop-loading-read')
        await admin('epoch',{'epoch':1})
        await api('/dossiers/reader-full.test/refresh','POST',token=token,key='newer-read',want=202)
        new=await terminal('reader-full.test',token)
        assert new['fields']['hq_city']['value']=='Zürich'
        await page.get_by_test_id('dossier-reload').click(timeout=3000)
        await page.wait_for_function('document.querySelector("[data-testid=field-value-hq_city]")?.dataset.value === "Zürich"')
        gate.set();await asyncio.sleep(.5)
        assert await page.get_by_test_id('field-value-hq_city').get_attribute('data-value')=='Zürich'
        assert count>=2
    finally:gate.set();await context.close()

async def test_poll_read_order(browser):
    token=await setup()
    await admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':1.2})
    await api('/dossiers','POST',{'domain':'reader-full.test'},token,key='poll-order',want=202)
    context,page=await new_page(browser);gate=asyncio.Event();captured=asyncio.Event();count=0
    try:
        await login(page)
        async def hold(route):
            nonlocal count
            if route.request.method!='GET' or 'text/html' in route.request.headers.get('accept',''):
                await route.continue_();return
            count+=1;number=count;response=await route.fetch()
            if number==2:
                captured.set();await asyncio.wait_for(gate.wait(),15)
            await route.fulfill(response=response)
        await page.route('**/dossiers/reader-full.test',hold)
        await page.goto(BASE+'/dossiers/reader-full.test')
        await asyncio.wait_for(captured.wait(),8)
        await wait_text(page.get_by_test_id('dossier-state'),'ready',timeout=15000)
        assert count>=3
        gate.set();await asyncio.sleep(.5)
        assert (await page.get_by_test_id('dossier-state').inner_text()).strip()=='ready'
    finally:gate.set();await context.close()

async def test_lost_write(browser,refresh=False):
    token=await setup(['amber-rank.test'] if refresh else [])
    context,page=await new_page(browser);seen=[];first=True
    domain='amber-rank.test' if refresh else 'maple-complete.test'
    path='/dossiers/'+domain+'/refresh' if refresh else '/dossiers'
    prefix='refresh' if refresh else 'research'
    try:
        await login(page)
        if refresh:
            await page.goto(BASE+'/dossiers/'+domain);await wait_text(page.get_by_test_id('dossier-state'),'ready')
        else:await page.get_by_test_id('research-domain').fill(domain)
        async def lose(route):
            nonlocal first
            if route.request.method!='POST':await route.continue_();return
            seen.append((route.request.headers.get('idempotency-key'),route.request.post_data))
            response=await route.fetch()
            if first:first=False;await route.abort('failed')
            else:await route.fulfill(response=response)
        await page.route('**'+path,lose)
        button=page.get_by_test_id('dossier-refresh' if refresh else 'research-submit')
        await button.click()
        await page.get_by_test_id(prefix+'-uncertain').wait_for()
        assert (await page.get_by_test_id(prefix+'-uncertain').inner_text()).strip()
        assert await page.get_by_test_id(prefix+'-error').count()==0
        await terminal(domain,token)
        before=len((await admin('log'))['calls'])
        async with page.expect_response(lambda r:r.request.method=='POST' and r.url==BASE+path) as response_event:
            await button.click()
        retry_response=await response_event.value
        assert retry_response.status==200,('retry status',retry_response.status)
        await page.wait_for_url(BASE+'/dossiers/'+domain)
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        assert len(seen)==2 and seen[0]==seen[1] and seen[0][0],('retry did not preserve key/body',len(seen),seen[0][1] if seen else None)
        await page.get_by_test_id(prefix+'-uncertain').wait_for(state='detached')
        assert await page.get_by_test_id(prefix+'-error').count()==0
        assert len((await admin('log'))['calls'])==before
    finally:await context.close()

async def test_upgrade_pending(browser):
    await setup()
    await api('/_test/reset','POST',FIXTURE,at=LEGACY,want=204)
    old_login=await api('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},at=LEGACY)
    old_token=old_login['token']
    initial=await api('/_test/export',at=LEGACY)
    await api('/_test/import','POST',initial,want=204)
    context,page=await new_page(browser);seen=[];first=True;original=None
    try:
        async def old_auth(route):await route.fulfill(status=200,content_type='application/json; charset=utf-8',body=json.dumps(old_login))
        await page.route('**/auth/login',old_auth)
        await login(page);await page.unroute('**/auth/login',old_auth)
        await page.get_by_test_id('research-domain').fill('legacy-amber.test')
        async def old_write(route):
            nonlocal first,original
            if route.request.method!='POST':await route.continue_();return
            seen.append((route.request.headers.get('idempotency-key'),route.request.post_data))
            if first:
                first=False
                response=await route.fetch(url=LEGACY+'/dossiers')
                original=await response.json();assert response.status==202
                await route.abort('failed')
            else:await route.continue_()
        await page.route('**/dossiers',old_write)
        await page.get_by_test_id('research-submit').click()
        await page.get_by_test_id('research-uncertain').wait_for()
        await terminal('legacy-amber.test',old_token,at=LEGACY)
        exported=await api('/_test/export',at=LEGACY)
        before=len((await admin('log'))['calls'])
        await api('/_test/import','POST',exported,want=204)
        assert len((await admin('log'))['calls'])==before
        await page.get_by_test_id('research-submit').click()
        await page.wait_for_url(BASE+'/dossiers/legacy-amber.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        await wait_text(page.get_by_test_id('current-user'),'Reader A')
        assert len(seen)>=2 and seen[0]==seen[-1] and seen[0][0]
        assert len((await admin('log'))['calls'])==before
        assert await page.get_by_test_id('research-uncertain').count()==0
        d=await api('/dossiers/legacy-amber.test',token=old_token)
        assert all(c['kind'] is None for f in FIELDS for c in d['fields'][f]['candidates'])
        assert original['dossier_id']==d['dossier_id']
        await page.get_by_test_id('dossier-evidence-link').click()
        await evidence_view(page,d)
        await page.goto(BASE+'/')
        await page.get_by_test_id('dossier-item-legacy-amber.test').wait_for()
        await wait_text(page.get_by_test_id('current-user'),'Reader A')
    finally:await context.close()

async def test_refresh_refusal_and_other_client(browser):
    token=await setup(['reader-full.test'])
    context,page=await new_page(browser)
    try:
        await login(page);await page.goto(BASE+'/dossiers/reader-full.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        async def refuse(route):
            await route.fulfill(status=404,content_type='application/json; charset=utf-8',body=json.dumps({'error':{'code':'not_found','message':'The dossier was removed by another client.'}}))
        await page.route('**/dossiers/reader-full.test/refresh',refuse)
        await page.get_by_test_id('dossier-refresh').click()
        await page.get_by_test_id('refresh-error').wait_for()
        assert (await page.get_by_test_id('refresh-error').inner_text()).strip()
        assert await page.get_by_test_id('refresh-uncertain').count()==0
        await shot(page,'desktop-refresh-refusal')
        await page.unroute('**/dossiers/reader-full.test/refresh',refuse)
        await admin('epoch',{'epoch':1})
        await admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':.6})
        await api('/dossiers/reader-full.test/refresh','POST',token=token,key='other-client-refresh',want=202)
        await page.get_by_test_id('dossier-refresh').click()
        await page.get_by_test_id('refresh-error').wait_for(state='detached')
        await wait_text(page.get_by_test_id('dossier-state'),'ready',timeout=20000)
        await page.wait_for_function('document.querySelector("[data-testid=field-value-hq_city]")?.dataset.value === "Zürich"')
        calls=(await admin('log'))['calls']
        exact=[c for c in calls if c['method']=='search' and c['query']=='reader-full.test' and c['status']==200]
        assert len(exact)==2,('browser refresh started a second concurrent build',len(exact))
        assert await page.get_by_test_id('refresh-uncertain').count()==0
    finally:await context.close()

async def test_failed_build_feedback(browser):
    token=await setup()
    context,page=await new_page(browser,375)
    try:
        await login(page)
        await admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'})
        await page.get_by_test_id('research-domain').fill('maple-complete.test')
        await page.get_by_test_id('research-submit').click()
        await page.wait_for_url(BASE+'/dossiers/maple-complete.test')
        await wait_text(page.get_by_test_id('dossier-state'),'building')
        await shot(page,'375-building-feedback')
        await wait_text(page.get_by_test_id('dossier-state'),'failed',timeout=15000)
        d=await api('/dossiers/maple-complete.test',token=token)
        await field_view(page,d);await no_overflow(page)
        await shot(page,'375-failed-feedback')
        await admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'none'})
        await page.get_by_test_id('dossier-refresh').click()
        await page.wait_for_function('document.querySelector("[data-testid=field-value-ceo]")?.dataset.value === "Bob Stone"',timeout=15000)
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        await shot(page,'375-recovered-feedback')
    finally:await context.close()

async def test_initial_loading_feedback(browser):
    await setup(['reader-full.test'])
    context,page=await new_page(browser);gate=asyncio.Event();captured=asyncio.Event()
    try:
        await login(page)
        async def hold(route):
            if route.request.method!='GET' or 'text/html' in route.request.headers.get('accept',''):
                await route.continue_();return
            response=await route.fetch();captured.set()
            await asyncio.wait_for(gate.wait(),10)
            await route.fulfill(response=response)
        await page.route('**/dossiers/reader-full.test',hold)
        await page.goto(BASE+'/dossiers/reader-full.test')
        await asyncio.wait_for(captured.wait(),5)
        assert re.search('loading|reading',await page.locator('body').inner_text(),re.I) or await page.locator('[aria-busy="true"],[role="progressbar"]').count()>0, 'no visible loading feedback'
        await shot(page,'desktop-initial-loading')
        gate.set();await wait_text(page.get_by_test_id('dossier-state'),'ready')
    finally:gate.set();await context.close()

async def test_executive_screens(browser,width):
    token=await setup(['reader-executives.test'])
    context,page=await new_page(browser,width)
    try:
        await login(page);await page.goto(BASE+'/dossiers/reader-executives.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        d=await api('/dossiers/reader-executives.test',token=token)
        await field_view(page,d);await no_overflow(page)
        text=await page.locator('body').inner_text()
        # Executive display uses its own markup; the inherited test IDs still name six fields.
        assert await page.get_by_test_id('field-executives').count()==0
        if 'Ana Silva' in text:
            assert 'Lee Park' in text and 'Ben Okafor' in text,text
            assert re.search(r'holds from|effective|start date not stated',text,re.I) and re.search(r'learned',text,re.I),text
        await shot(page,str(width)+'-executives-dossier')
        await page.get_by_test_id('dossier-evidence-link').click();await evidence_view(page,d)
        assert await page.get_by_test_id('evidence-executives').count()==0
        await no_overflow(page);await shot(page,str(width)+'-executives-evidence')
        await page.goto(BASE+'/contested')
        await page.get_by_test_id('empty-contested').wait_for()
        assert await page.get_by_test_id('contested-list').count()==0
        await no_overflow(page)
        await page.goto(BASE+'/dossiers/reader-executives.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        await admin('epoch',{'epoch':1})
        await page.get_by_test_id('dossier-refresh').click()
        await page.wait_for_function('document.body.innerText.includes("Mia Lopez")')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        dated=await page.locator('body').inner_text()
        assert re.search(r'holds from|effective',dated,re.I) and '2030' in dated and 'Learned' in dated,dated
        await no_overflow(page);await shot(page,str(width)+'-executives-dated')
    finally:await context.close()

async def test_investor_screens(browser,width):
    token=await setup(['reader-investors.test','reader-lone-investor.test'])
    context,page=await new_page(browser,width)
    try:
        await login(page);await page.goto(BASE+'/dossiers/reader-investors.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready')
        d=await api('/dossiers/reader-investors.test',token=token);await field_view(page,d)
        assert await page.get_by_test_id('field-investors').count()==0
        text=await page.locator('body').inner_text()
        if 'Bluebird Capital' in text:
            for value in d['fields']['investors']['value']:assert value in text,(value,text)
        await no_overflow(page);await shot(page,str(width)+'-investors-dossier')
        await page.get_by_test_id('dossier-evidence-link').click();await evidence_view(page,d)
        assert await page.get_by_test_id('evidence-investors').count()==0
        await no_overflow(page);await shot(page,str(width)+'-investors-evidence')
        await page.goto(BASE+'/dossiers/reader-lone-investor.test')
        await wait_text(page.get_by_test_id('dossier-state'),'ready');await no_overflow(page)
        await shot(page,str(width)+'-investors-unconfirmed')
        await page.goto(BASE+'/contested');await page.get_by_test_id('empty-contested').wait_for()
        assert await page.get_by_test_id('contested-list').count()==0
    finally:await context.close()

async def main():
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        cases=[('auth-labels-and-return-navigation',lambda:test_auth(browser)),('desktop-routes-fields-evidence-contested',lambda:test_routes(browser,1280)),('mobile-375-routes-fields-evidence-contested',lambda:test_routes(browser,375)),('research-refusal-poll-existing-client',lambda:test_research_poll(browser)),('latest-manual-read-wins',lambda:test_latest_read(browser)),('latest-building-poll-wins',lambda:test_poll_read_order(browser)),('lost-research-response-retry',lambda:test_lost_write(browser,False)),('lost-refresh-response-retry',lambda:test_lost_write(browser,True)),('legacy-token-and-pending-retry-upgrade',lambda:test_upgrade_pending(browser)),('refresh-refusal-and-other-client-build',lambda:test_refresh_refusal_and_other_client(browser)),('failed-build-and-recovery-feedback',lambda:test_failed_build_feedback(browser)),('initial-loading-feedback',lambda:test_initial_loading_feedback(browser))]
        cases.extend([('executives-and-six-field-ui-1280',lambda:test_executive_screens(browser,1280)),('executives-and-six-field-ui-375',lambda:test_executive_screens(browser,375))])
        cases.extend([('investors-and-origins-ui-1280',lambda:test_investor_screens(browser,1280)),('investors-and-origins-ui-375',lambda:test_investor_screens(browser,375))])
        if CONFIG.get('only'):cases=[(name,fn) for name,fn in cases if name in CONFIG['only'].split(',')]
        for name,fn in cases:
            start=time.monotonic()
            try:
                await asyncio.wait_for(fn(),timeout=90)
                results.append({'case':'browser-'+name,'result':'pass','seconds':round(time.monotonic()-start,3)})
                print('PASS browser-'+name,flush=True)
            except Exception as exc:
                detail=str(exc);trace=traceback.format_exc()
                for value in secret_values:
                    detail=detail.replace(value,'<redacted>');trace=trace.replace(value,'<redacted>')
                detail=re.sub(r'(?i)Bearer\s+[A-Za-z0-9._~-]+','Bearer <redacted>',detail)
                trace=re.sub(r'(?i)Bearer\s+[A-Za-z0-9._~-]+','Bearer <redacted>',trace)
                results.append({'case':'browser-'+name,'result':'fail','seconds':round(time.monotonic()-start,3),'detail':detail,'traceback':trace})
                print('FAIL browser-'+name,detail[:1200],flush=True)
        await browser.close()
    OUT.write_text(json.dumps({'results':results},ensure_ascii=False,indent=2))
    print('BROWSER COUNTS',sum(r['result']=='pass' for r in results),'passed',sum(r['result']=='fail' for r in results),'failed',flush=True)
    return any(r['result']=='fail' for r in results)

if __name__=='__main__':raise SystemExit(asyncio.run(main()))
