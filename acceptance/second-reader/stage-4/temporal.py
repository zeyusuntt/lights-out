"""Independent Stage 3 fixtures and HTTP-only temporal/crash probes.

Executed in the runner's namespace so its inherited service lifecycle is reused.
No submitted source, product tests or other seats' probes are imported.
"""
import http.client

STAGE3_FIELDS = FIELDS + ['executives']
ALL_FIELDS = STAGE3_FIELDS + ['investors']
TITLES = ['cfo','coo','cto']
TIMES = [f'2026-03-{i+1:02d}T09:00:00+00:00' for i in range(15)]
TD = 'reader-temporal.test'
TU = 'https://reader-temporal.test/profile'
temporal_pages = []
for epoch, person, effective in [
    (0,'Dana Ruiz','2020-01-01'), (1,'Sam Ortiz','2021-01-01'),
    (2,'Lina Park','2020-06-01'), (3,'Lina Park','2020-07-01'),
    (4,None,'2022-01-01'), (5,'Dana Ruiz',None), (6,'Dana Ruiz','2019-01-01')]:
    temporal_pages.append(dict(url=TU,epochs=[epoch],true_from=effective,
        published_at=None,text=f'Reader Temporal CEO: {person}.' if person else 'Reader Temporal CEO profile is currently unavailable.'))
# An absent URL does not supply a new empty version of it.
temporal_pages.append(dict(url='https://reader-temporal.test/other',epochs=[7],
    kind='news',true_from='2023-01-01',text='Reader Temporal CEO: Eva Stone.'))
company(TD,temporal_pages)

ED='reader-executives.test'
EU='https://reader-executives.test/'
executive_pages=[]
exec_states=[
    [('cfo','Ana Silva','2022-01-01'),('coo','Lee Park',None),('cto','Ben Okafor','2021-01-01')],
    [('cfo','Mia Lopez','2021-01-01'),('coo','Lee Park','2030-01-01'),('cto','Ben Okafor','2021-01-01')],
    [('cfo','Mia Lopez','2021-01-01'),('cto','Ben Okafor','2021-01-01')],
    [], [('cfo','Mia Lopez','2020-01-01')],
]
for epoch,members in enumerate(exec_states):
    for title,name,effective in members:
        executive_pages.append(dict(url=EU+title,epochs=[epoch],true_from=effective,
            text=f'Reader Executives {title.upper()}: {name}.'))
    if not members:
        executive_pages.append(dict(url=EU+'cfo',epochs=[epoch],true_from='2031-01-01',text='Reader Executives company overview.'))
    if epoch==0:
        executive_pages.append(dict(url='https://reader-news.test/cfo',epochs=[epoch],kind='news',
            published_at='2090-01-01T00:00:00+00:00',true_from='2025-01-01',text='Reader Executives chief financial officer: Eva Stone.'))
company(ED,executive_pages)

SD='reader-seven.test'
seven_pages=[]
for epoch in [0,1]:
    vals=[('Reader Seven legal name is Reader Seven, '+('LLC' if epoch==0 else 'Inc.')+'.'),
          'Reader Seven is based in '+('Lisbon' if epoch==0 else 'Zürich')+'.',
          'Reader Seven CEO: '+('Dana Ruiz' if epoch==0 else 'Sam Ortiz')+'.',
          'Reader Seven was founded in '+('2014' if epoch==0 else '2015')+'.',
          'Reader Seven employs '+('120' if epoch==0 else '600')+' people.',
          'Reader Seven raised '+('$12M' if epoch==0 else '$13M')+'.',
          'Reader Seven CFO: '+('Ana Silva' if epoch==0 else 'Mia Lopez')+'.',
          'Reader Seven COO: Lee Park.', 'Reader Seven CTO: Ben Okafor.']
    seven_pages.append(dict(url='https://reader-seven.test/all',epochs=[epoch],true_from=f'202{epoch}-01-01',text='\n'.join(vals)))
company(SD,seven_pages)

FD='reader-effective.test'
effective_cases=[
    ('valid','Dana Ruiz','2024-02-29','2030-01-01T00:00:00+00:00','2024-02-29'),
    ('invalid','Sam Ortiz','2025-02-30','2026-01-01T00:30:00+02:00','2025-12-31'),
    ('fallback','Lina Park',None,'2025-12-31T23:30:00-02:00','2026-01-01'),
    ('undated','Eva Stone',None,None,None),
    ('format','Petra Cole','2024-2-9','2025-01-01T00:00:00+00:00','2025-01-01'),
    ('prose','Zara Lane',None,None,None)]
company(FD,[dict(url='https://reader-effective.test/'+label,true_from=effective,published_at=published,
    text=('Effective: 2020-01-01\n' if label=='prose' else '')+'Reader Effective CEO: '+person+'.') for label,person,effective,published,expected in effective_cases])

company('reader-date-shift.test',[
    dict(url='https://reader-date-shift.test/profile',epochs=[e],true_from=effective,text='Reader Date Shift CEO: '+name+'.')
    for e,name,effective in [(0,'Dana Ruiz','2020-01-01'),(1,'Dana Ruiz','2022-01-01'),(2,'Sam Ortiz','2021-01-01'),(3,'Lina Park','2021-01-01')]])
company('reader-appears.test',[
    dict(url='https://reader-appears.test/profile',epochs=[0],true_from='2020-01-01',text='Reader Appears CEO profile is unavailable.'),
    dict(url='https://reader-appears.test/profile',epochs=[1],true_from='2021-01-01',text='Reader Appears CEO: Dana Ruiz.\nReader Appears CFO: Ana Silva.')])

executive_grammar=[]
for i,(title,phrase,sentence,expected) in enumerate([
    ('cfo','chief financial officer','{name} chief financial officer: Élodie Müller.','Élodie Müller'),
    ('cfo','CFO','{name} CFO: Ana Silva.','Ana Silva'),
    ('coo','chief operating officer','{name} chief operating officer: Lee Maria Park.','Lee Maria Park'),
    ('coo','COO','{name} COO: Sam Ortiz.','Sam Ortiz'),
    ('cto','chief technology officer','{name} chief technology officer: Ben Okafor.','Ben Okafor'),
    ('cto','CTO','{name} CTO: Dana Ruiz.','Dana Ruiz'),
    ('cto','CTO','{name} reportedly appoints CTO Dana Ruiz.',None),
    ('cfo','CFO','{name} CFO: Dana Maria Elena Ruiz.',None),
    ('coo','COO','{name} CEO: Dana Ruiz.',None),
    ('cfo','CFO','{name} CFOnly: Dana Ruiz.',None),
    ('cto','CTO','{name} company profile. Its CTO is Dana Ruiz.',None),
    ('cfo','CFO','context '*150+'{name} CFO: Ana Silva.','Ana Silva'),
]):
    domain='reader-exec-'+chr(97+i)+'.test';name=domain.split('.')[0].replace('-',' ')
    company(domain,[dict(text=sentence.format(name=name),true_from='2025-01-01')])
    executive_grammar.append((domain,title,expected))

def clock(value,at=None):
    status(req('/_test/clock','POST',{'now':value},auth=False,at=at),204)

def epoch(value):
    status(admin('epoch',{'epoch':value}),204)

def refresh(domain,at=None,key=None):
    return status(req('/dossiers/'+domain+'/refresh','POST',key=key or uuid.uuid4().hex,at=at),202)

def asof(domain,value,at=None,want=200):
    return status(req('/dossiers/'+domain+'?'+urllib.parse.urlencode({'as_of':value}),at=at),want,'not_found' if want==404 else None)

def values(domain,date,learned=None,at=None,want=200):
    query={'true_at':date}
    if learned is not None:query['as_of']=learned
    return status(req('/dossiers/'+domain+'/values?'+urllib.parse.urlencode(query),at=at),want,'not_found' if want==404 else None)

def history(domain,at=None):
    return status(req('/dossiers/'+domain+'/history',at=at),200)

def feed(query='',at=None):
    return status(req('/changes'+('?' + query if query else ''),at=at),200)

def build_epoch(domain,e,t):
    epoch(e);clock(t);refresh(domain);return ready(domain)

def temporal_shape(d):
    assert list(d['fields'])==ALL_FIELDS,('field order',list(d['fields']))
    for field,value in d['fields'].items():
        assert 'true_from' in value and 'learned_at' in value,(field,value)
        if value['value'] is None:
            assert value['true_from'] is None and value['learned_at'] is None,(field,value)
        elif field not in ['executives','investors']:
            assert value['true_from']==next(c['true_from'] for c in value['candidates'] if c['selected']),value
            assert value['learned_at'] is not None,value
        for c in value['candidates']:
            assert 'true_from' in c and c['learned_at'] is not None,c
            assert instant(c['learned_at'])<=instant(c['retrieved_at']),c

def executive_shape(d):
    temporal_shape(d)
    ex=d['fields']['executives'];cands=ex['candidates'];members=[];cites=[];dates=[]
    assert len({(c['title'],c['value'],c['url']) for c in cands})==len(cands),cands
    ordered=[];contested=False
    for title in TITLES:
        group=sorted([c for c in cands if c['title']==title],key=rank_key)
        ordered+=group
        assert sum(c['selected'] is True for c in group)==bool(group),group
        if group:
            assert group[0]['selected'] is True,group
            winner=group[0]['value'];members.append({'title':title,'name':winner});dates.append(group[0]['true_from'])
            cites.extend({k:c[k] for k in ['url','excerpt','provider']} for c in group if c['value']==winner)
            contested|=len({c['value'] for c in group})>1
    assert cands==ordered,cands
    assert ex['value']==(members or None),ex
    assert ex['citations']==cites,ex
    assert ex['status']==('unknown' if not members else 'contested' if contested else 'known'),ex
    assert ex['true_from']==(max(dates) if dates and all(x is not None for x in dates) else None),ex
    served=[(c['provider'],p['url'],p['text']) for c in log() for p in c.get('served',[])]
    for c in cands:
        assert 1<=len(c['excerpt'])<=500,c
        canon=lambda s:re.sub(r'\s+',' ',s)
        assert any(provider==c['provider'] and url==c['url'] and canon(c['excerpt']) in canon(prose(text)) for provider,url,text in served),c

@case('stage3-effective-header-and-utc-fallback')
def test_effective():
    reset();status(create(FD),202);d=ready(FD);temporal_shape(d);provenance(d)
    cs={c['url'].rsplit('/',1)[-1]:c for c in d['fields']['ceo']['candidates']}
    assert set(cs)=={x[0] for x in effective_cases},cs
    for label,person,effective,published,expected in effective_cases:
        c=cs[label];assert c['value']==person and c['true_from']==expected,c
        assert c['learned_at']==NOW and c['retrieved_at']==NOW,c
    for f in ALL_FIELDS:
        if f!='ceo':assert d['fields'][f]['value'] is None,d['fields'][f]

@case('stage3-selected-and-candidate-learned-times')
def test_learned():
    reset();status(create(TD),202);a=ready(TD);temporal_shape(a)
    b=build_epoch(TD,1,TIMES[1]);c=build_epoch(TD,2,TIMES[2]);same=build_epoch(TD,3,TIMES[3])
    for d,person,t in [(a,'Dana Ruiz',NOW),(b,'Sam Ortiz',TIMES[1]),(c,'Lina Park',TIMES[2])]:
        known(d,'ceo',person);assert d['fields']['ceo']['learned_at']==t,d['fields']['ceo']
    cv=same['fields']['ceo'];assert cv['learned_at']==TIMES[2] and cv['true_from']=='2020-07-01',cv
    assert cv['candidates'][0]['learned_at']==TIMES[2] and cv['candidates'][0]['retrieved_at']==TIMES[3],cv
    h=history(TD)['fields']['ceo'];assert [e['type'] for e in h]==['initial','change','correction'],h
    assert h[-1]['true_from']=='2020-06-01' and h[-1]['learned_at']==TIMES[2],h
    removed=build_epoch(TD,4,TIMES[4]);assert removed['fields']['ceo']['learned_at'] is None
    row=history(TD)['fields']['ceo'][-1]
    assert row=={'type':'change','value':None,'true_from':None,'learned_at':TIMES[4],'citations':[]},row
    back=build_epoch(TD,5,TIMES[5]);c=back['fields']['ceo']['candidates'][0]
    assert c['learned_at']==NOW and c['retrieved_at']==TIMES[5],c
    assert back['fields']['ceo']['learned_at']==TIMES[5] and back['fields']['ceo']['true_from'] is None
    entries=feed()['changes'];assert len(entries)==4,entries
    assert [(x['from'],x['to'],x['type']) for x in entries]==[('Dana Ruiz','Sam Ortiz','change'),('Sam Ortiz','Lina Park','correction'),('Lina Park',None,'change'),(None,'Dana Ruiz','change')],entries
    old=asof(TD,TIMES[2]);assert old['fields']['ceo']['true_from']=='2020-06-01' and old['fields']['ceo']['learned_at']==TIMES[2],old

@case('stage3-unchanged-value-date-shift-then-correction')
def test_date_shift():
    domain='reader-date-shift.test';reset();status(create(domain),202);first=ready(domain)
    same=build_epoch(domain,1,TIMES[1]);assert same['fields']['ceo']['true_from']=='2022-01-01'
    assert same['fields']['ceo']['learned_at']==NOW and len(history(domain)['fields']['ceo'])==1 and feed()['changes']==[]
    changed=build_epoch(domain,2,TIMES[2]);assert changed['fields']['ceo']['value']=='Sam Ortiz'
    assert history(domain)['fields']['ceo'][-1]['type']=='correction' and feed()['changes'][-1]['type']=='correction'
    assert asof(domain,NOW)['fields']==first['fields'] and asof(domain,TIMES[1])['fields']==same['fields']
    equal=build_epoch(domain,3,TIMES[3]);assert equal['fields']['ceo']['value']=='Lina Park'
    assert history(domain)['fields']['ceo'][-1]['type']=='correction'
    assert values(domain,'2021-01-01',TIMES[3])['fields']['ceo']['value']=='Lina Park'

@case('stage3-first-value-after-ready-unknown-is-change')
def test_first_appearance():
    domain='reader-appears.test';reset();status(create(domain),202);first=ready(domain)
    assert all(v['value'] is None for v in first['fields'].values()) and all(not x for x in history(domain)['fields'].values())
    new=build_epoch(domain,1,TIMES[1]);assert new['fields']['ceo']['value']=='Dana Ruiz'
    for field in ['ceo','executives']:
        h=history(domain)['fields'][field];assert len(h)==1 and h[0]['type']=='change' and h[0]['learned_at']==TIMES[1],h
    events=feed()['changes'];assert [x['field'] for x in events]==['ceo','executives'] and all(x['from'] is None for x in events),events

@case('stage3-version-corrections-empty-null-and-absence')
def test_versions():
    reset();status(create(TD),202);ready(TD)
    snapshots={0:NOW}
    for e in range(1,8):
        build_epoch(TD,e,TIMES[e]);snapshots[e]=TIMES[e]
    # Independent expected CEO timeline after every knowledge epoch.
    expected={
        0:[('2019-12-31',None),('2020-01-01','Dana Ruiz'),('2021-01-01','Dana Ruiz')],
        1:[('2020-12-31','Dana Ruiz'),('2021-01-01','Sam Ortiz')],
        2:[('2020-05-31','Dana Ruiz'),('2020-06-01','Lina Park'),('2021-01-01','Lina Park')],
        3:[('2020-05-31','Dana Ruiz'),('2020-06-01','Lina Park'),('2020-07-01','Lina Park')],
        4:[('2021-12-31','Lina Park'),('2022-01-01',None),('2099-01-01',None)],
        5:[('1900-01-01',None),('2020-01-01',None),('2099-01-01',None)],
        6:[('2018-12-31',None),('2019-01-01','Dana Ruiz'),('2099-01-01','Dana Ruiz')],
        7:[('2020-01-01','Dana Ruiz'),('2023-01-01','Dana Ruiz'),('2099-01-01','Dana Ruiz')],
    }
    for e,pairs in expected.items():
        for date,person in pairs:
            value=values(TD,date,snapshots[e]);assert list(value['fields'])==ALL_FIELDS,value
            actual=value['fields']['ceo'];assert actual['value']==person,(e,date,person,actual)
            if person is None:assert {k:actual[k] for k in ['value','true_from','citations']}=={'value':None,'true_from':None,'citations':[]},actual
            else:assert actual['citations'] and actual['true_from'] is not None,actual
    # Current candidates are only the last build, but the old own URL still holds historically.
    assert get(TD)['fields']['ceo']['value']=='Eva Stone'
    assert values(TD,'2099-01-01')['fields']['ceo']['value']=='Dana Ruiz'
    before=values(TD,'2021-02-01',TIMES[1]);after=values(TD,'2021-02-01',TIMES[2])
    assert before['fields']['ceo']['value']=='Sam Ortiz' and after['fields']['ceo']['value']=='Lina Park'

@case('stage3-as-of-ties-offsets-and-failed-cost')
def test_asof_ties():
    reset();status(create(TD),202);a=ready(TD)
    epoch(1);refresh(TD);b=ready(TD)
    clock('2026-03-01T11:00:00+02:00');epoch(2);refresh(TD);c=ready(TD)
    for timestamp in [NOW,'2026-03-01T11:00:00+02:00','2026-03-01T04:00:00-05:00']:
        snap=asof(TD,timestamp);assert snap['fields']==c['fields'] and snap['researched_at']==c['researched_at'],snap
        assert snap['state']=='ready' and snap['spent_units']==c['spent_units'],snap
    asof(TD,'2026-03-01T08:59:59+00:00',want=404)
    # Some searches incur units before research/extract are refused, so the failed/partial
    # outcome is independently reconciled by the current and snapshot spending totals.
    clock(TIMES[1]);status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'}),204)
    refresh(TD);failed=ready(TD);assert failed['state']=='failed'
    snap=asof(TD,TIMES[1]);assert snap['state']=='ready' and snap['fields']==c['fields']
    assert snap['spent_units']==failed['spent_units']
    assert len(history(TD)['fields']['ceo'])==3 and len(feed()['changes'])==2

@case('stage3-in-flight-snapshot-spending-and-build-time')
def test_inflight():
    reset();status(create(TD),202);a=ready(TD);old_h=history(TD);old_feed=feed()
    epoch(1);clock(TIMES[1]);status(admin('faults',{'provider':'nimble','methods':['research'],'mode':'delay','seconds':2}),204)
    refresh(TD);until=time.monotonic()+3
    while time.monotonic()<until:
        current=get(TD)
        if current['state']=='building' and current['spent_units']>a['spent_units']:break
        time.sleep(.02)
    assert current['state']=='building' and current['spent_units']>a['spent_units'],current
    snap=asof(TD,TIMES[1]);assert snap['fields']==a['fields'] and snap['state']=='ready'
    latest=get(TD);assert a['spent_units']<snap['spent_units']<=latest['spent_units'],(a['spent_units'],snap['spent_units'],latest['spent_units'])
    assert history(TD)==old_h and feed()==old_feed
    clock(TIMES[2]);new=ready(TD);assert new['researched_at']==TIMES[1]
    assert new['fields']['ceo']['learned_at']==TIMES[1]
    assert feed()['changes'][-1]['learned_at']==TIMES[1]
    assert asof(TD,NOW)['fields']==a['fields'] and asof(TD,NOW)['spent_units']==a['spent_units']

@case('stage3-executives-selection-dates-and-corrections')
def test_executives():
    reset();status(create(ED),202);a=ready(ED);executive_shape(a)
    ex=a['fields']['executives'];assert ex['value']==[{'title':'cfo','name':'Ana Silva'},{'title':'coo','name':'Lee Park'},{'title':'cto','name':'Ben Okafor'}],ex
    assert ex['status']=='contested' and ex['true_from'] is None
    assert history(ED)['fields']['executives'][0]['type']=='initial' and feed()['changes']==[]
    b=build_epoch(ED,1,TIMES[1]);executive_shape(b)
    assert b['fields']['executives']['status']=='known' and b['fields']['executives']['true_from']=='2030-01-01'
    h=history(ED)['fields']['executives'];assert h[-1]['type']=='correction',h
    for e in [2,3,4]:
        d=build_epoch(ED,e,TIMES[e]);executive_shape(d)
        assert history(ED)['fields']['executives'][-1]['type']=='change'
    ex=d['fields']['executives'];assert ex['value']==[{'title':'cfo','name':'Mia Lopez'}]
    assert ex['learned_at']==TIMES[4] and ex['candidates'][0]['learned_at']==TIMES[1],ex
    assert len(history(ED)['fields']['executives'])==5 and len(feed()['changes'])==4
    for c in log():
        if c['method']=='research':assert c['fields']==sorted(FIELDS),c['fields']

for domain,title,expected in executive_grammar:
    def make_exec_grammar(domain=domain,title=title,expected=expected):
        @case('stage3-executive-support-'+domain)
        def probe():
            reset();status(create(domain),202);d=ready(domain);executive_shape(d)
            actual=d['fields']['executives']['value']
            assert actual==([{'title':title,'name':expected}] if expected else None),(domain,expected,actual)
    make_exec_grammar()

@case('stage3-executive-values-at-valid-time')
def test_exec_values():
    reset();status(create(ED),202);ready(ED);build_epoch(ED,1,TIMES[1])
    early=values(ED,'2021-06-01',NOW)['fields']['executives']
    # Initial undated COO never holds, CFO own starts2022 but dated news starts2025.
    assert early['value']==[{'title':'cto','name':'Ben Okafor'}],early
    later=values(ED,'2021-06-01',TIMES[1])['fields']['executives']
    assert later['value']==[{'title':'cfo','name':'Mia Lopez'},{'title':'cto','name':'Ben Okafor'}],later
    assert later['true_from']=='2021-01-01' and len(later['citations'])==2,later
    future=values(ED,'2030-01-01',TIMES[1])['fields']['executives']
    assert [x['title'] for x in future['value']]==TITLES and future['true_from']=='2030-01-01',future

@case('stage3-seven-field-history-feed-order-and-replay')
def test_seven_feed():
    reset();original=status(create(SD,'seven-create'),202);a=ready(SD);executive_shape(a)
    assert all(len(x)==1 and x[0]['type']=='initial' for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)),history(SD)
    assert feed()=={'changes':[],'has_more':False}
    epoch(1);clock(TIMES[1]);reply=refresh(SD,key='seven-refresh');b=ready(SD)
    events=feed()['changes'];assert [x['field'] for x in events]==STAGE3_FIELDS,events
    for f,e in zip(STAGE3_FIELDS,events):
        assert e['domain']==SD and e['type']=='change' and type(e['seq']) is int and e['seq']>0,e
        assert e['from']==a['fields'][f]['value'] and e['to']==b['fields'][f]['value'],e
        assert e['learned_at']==TIMES[1] and e['true_from']=='2021-01-01',e
    before=len(log());h=history(SD);epoch(0)
    assert status(req('/dossiers/'+SD+'/refresh','POST',key='seven-refresh'),200)==reply
    assert status(create(SD,'seven-create'),200)==original
    assert history(SD)==h and len(log())==before and feed()['changes']==events

@case('stage3-new-endpoint-auth-and-query-boundaries')
def test_temporal_errors():
    reset();status(create(TD),202);ready(TD)
    for path in ['/changes','/dossiers/'+TD+'/history','/dossiers/'+TD+'/values?true_at=2020-01-01','/dossiers/'+TD+'?as_of='+urllib.parse.quote(NOW)]:
        status(req(path,auth=False),401,'unauthenticated')
    for val in ['', '2026-03-01','2026-03-01T09:00:00','bogus','2026-02-30T09:00:00+00:00']:
        for stem in ['/dossiers/'+TD+'?','/dossiers/'+TD+'/values?true_at=2020-01-01&']:
            status(req(stem+urllib.parse.urlencode({'as_of':val})),422,'validation_failed')
    for val in ['', '2026-2-01','2026-02-30','2025-02-29','2026-03-01T00:00:00Z','bogus']:
        status(req('/dossiers/'+TD+'/values?'+urllib.parse.urlencode({'true_at':val})),422,'validation_failed')
    status(req('/dossiers/'+TD+'/values'),422,'validation_failed')
    for date in ['2024-02-29','2020-01-01']:values(TD,date)
    for key,bads in [('since',['-1','+1','1e2','1.0','','letters']),('limit',['0','201','-1','+1','1e2','1.0',''])]:
        for val in bads:status(req('/changes?'+urllib.parse.urlencode({key:val})),422,'validation_failed')
    for path in ['/dossiers/missing-reader.test/history','/dossiers/missing-reader.test/values?true_at=2020-01-01','/dossiers/missing-reader.test?as_of='+urllib.parse.quote(NOW)]:
        status(req(path),404,'not_found')
    count=len(log())
    for suffix in ['/history','/values?true_at=2020-01-01','?as_of='+urllib.parse.quote(NOW)]:
        path='/dossiers/'+urllib.parse.quote(' WWW.READER-TEMPORAL.TEST. ',safe='')+suffix
        assert status(req(path),200)['domain']==TD
    assert len(log())==count
    # A ready but undated page has no active valid-time candidates, not404.
    status(create('reader-blank.test'),202);ready('reader-blank.test')
    blank=values('reader-blank.test','2020-01-01')
    assert all(v['value'] is None and v['true_from'] is None and not v['citations'] for v in blank['fields'].values()),blank

def query_matrix(domain,at=None):
    paths=['/dossiers','/dossiers/'+domain,'/dossiers/'+domain+'/history','/changes','/changes?since=1&limit=1']
    paths+=['/dossiers/'+domain+'?'+urllib.parse.urlencode({'as_of':t}) for t in [NOW,TIMES[1],TIMES[3],TIMES[6]]]
    paths+=['/dossiers/'+domain+'/values?'+urllib.parse.urlencode({'true_at':date,'as_of':t})
        for t in [NOW,TIMES[1],TIMES[3],TIMES[6]] for date in ['2019-12-31','2020-06-01','2021-01-01','2099-01-01']]
    return {p:req(p,at=at) for p in paths}

@case('stage3-native-transfer-preserves-builds-versions-and-feed')
def test_native_temporal_transfer():
    reset();original=status(create(TD,'native-create'),202);ready(TD)
    for e in [1,2,3,4,5,6]:build_epoch(TD,e,TIMES[e])
    before=query_matrix(TD);source_token=token;exported=status(req('/_test/export',auth=False),200)
    count=len(log());reset(at=second);destination_token=token;clock(TIMES[10],at=second)
    status(req('/_test/import','POST',exported,auth=False,at=second),204);global_token(source_token)
    assert query_matrix(TD,at=second)==before
    status(req('/dossiers',at=second,extra={'Authorization':'Bearer '+destination_token}),401,'unauthenticated')
    assert status(create(TD,'native-create',at=second),200)==original
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    assert query_matrix(TD,at=second)==before and len(log())==count
    # Import does not move the destination clock, and seq continues beyond saved entries.
    epoch(1);refresh(TD,at=second);new=ready(TD,at=second)
    assert new['researched_at']==TIMES[10]
    oldseq=max(x['seq'] for x in before['/changes'][1]['changes'])
    assert feed(at=second)['changes'][-1]['seq']>oldseq
    status(req('/_test/reset','POST',FIXTURE,auth=False,at=second),204)
    status(req('/changes',at=second,extra={'Authorization':'Bearer '+source_token}),401,'unauthenticated')

@case('stage3-legacy-stage1-synthetic-time-and-first-executives')
def test_upgrade_stage1():
    reset();reset(at=legacy);old_token=token
    original=status(create(SD,'s1-source',at=legacy),202);old=ready(SD,at=legacy)
    exported=status(req('/_test/export',auth=False,at=legacy),200);before=len(log())
    status(req('/_test/import','POST',exported,auth=False),204);global_token(old_token)
    current=get(SD);assert current['dossier_id']==old['dossier_id']
    assert asof(SD,NOW)['fields']==current['fields'];asof(SD,'2026-03-01T08:59:59+00:00',want=404)
    assert current['fields']['executives']['value'] is None and history(SD)['fields']['executives']==[]
    assert feed()['changes']==[]
    for f in FIELDS:
        v=current['fields'][f]
        if v['value'] is not None:
            assert v['true_from'] is None and v['learned_at']==NOW
            assert len(history(SD)['fields'][f])==1 and history(SD)['fields'][f][0]['type']=='initial'
        for c in v['candidates']:assert c['true_from'] is None and c['learned_at']==c['retrieved_at']
    assert all(v['value'] is None for v in values(SD,'2099-01-01')['fields'].values())
    assert status(create(SD,'s1-source'),200)==original and len(log())==before
    clock(TIMES[1]);refresh(SD);d=ready(SD);executive_shape(d)
    row=history(SD)['fields']['executives'][0];assert row['type']=='change' and row['learned_at']==TIMES[1],row

@case('stage3-legacy-stage2-current-view-and-publication-fallback')
def test_upgrade_stage2():
    reset();reset(at=legacy2);old_token=token
    status(create(FD,'s2-source',at=legacy2),202);old=ready(FD,at=legacy2)
    exported=status(req('/_test/export',auth=False,at=legacy2),200)
    count=len(log());status(req('/_test/import','POST',exported,auth=False),204);global_token(old_token)
    new=get(FD);assert new['spent_units']==old['spent_units'] and new['dossier_id']==old['dossier_id']
    cs={c['url'].rsplit('/',1)[-1]:c for c in new['fields']['ceo']['candidates']}
    expected={'valid':'2030-01-01','invalid':'2025-12-31','fallback':'2026-01-01','undated':None,'format':'2025-01-01','prose':None}
    assert {k:c['true_from'] for k,c in cs.items()}==expected,cs
    assert all(c['learned_at']==c['retrieved_at']==NOW for c in cs.values())
    assert new['fields']['ceo']['true_from']=='2030-01-01' and new['fields']['ceo']['learned_at']==NOW
    assert history(FD)['fields']['ceo'][0]['type']=='initial' and feed()['changes']==[]
    assert asof(FD,NOW)['fields']==new['fields'];asof(FD,'2026-03-01T08:59:59+00:00',want=404)
    # Effective2024 was not exported by Stage2. Publication2030 determines upgraded support.
    assert values(FD,'2024-03-01')['fields']['ceo']['value'] is None
    assert values(FD,'2030-01-01')['fields']['ceo']['value']=='Dana Ruiz'
    assert len(log())==count

@case('stage3-legacy-stage2-collapsed-builds-and-executives')
def test_upgrade_stage2_builds():
    reset();reset(at=legacy2);old_token=token
    original=status(create(SD,'s2-seven',at=legacy2),202);first=ready(SD,at=legacy2)
    epoch(1);clock(TIMES[1],at=legacy2);refresh(SD,at=legacy2);old=ready(SD,at=legacy2)
    exported=status(req('/_test/export',auth=False,at=legacy2),200);count=len(log())
    status(req('/_test/import','POST',exported,auth=False),204);global_token(old_token);clock(TIMES[2])
    new=get(SD);assert new['spent_units']==old['spent_units'] and new['spent_units']>first['spent_units']
    assert asof(SD,TIMES[1])['spent_units']==old['spent_units'];asof(SD,NOW,want=404)
    assert new['fields']['executives']['value'] is None and history(SD)['fields']['executives']==[]
    assert all(len(history(SD)['fields'][f])==1 for f in FIELDS)
    assert feed()['changes']==[] and len(log())==count
    assert status(create(SD,'s2-seven'),200)==original
    refresh(SD);ready(SD);assert history(SD)['fields']['executives'][0]['type']=='change'
    # Same scalar values and no imported Effective date => only executives changed.
    assert [x['field'] for x in feed()['changes']]==['executives']

@case('stage3-upgrade-through-both-legacy-generations')
def test_legacy_chain():
    reset();reset(at=legacy);old_token=token
    original=status(create(legacy_domain,'chain-create',at=legacy),202);ready(legacy_domain,at=legacy)
    first_export=status(req('/_test/export',auth=False,at=legacy),200)
    status(req('/_test/import','POST',first_export,auth=False,at=legacy2),204)
    clock(TIMES[1],at=legacy2);refresh(legacy_domain,at=legacy2);old=ready(legacy_domain,at=legacy2)
    second_export=status(req('/_test/export',auth=False,at=legacy2),200);count=len(log())
    status(req('/_test/import','POST',second_export,auth=False),204);global_token(old_token)
    new=get(legacy_domain);assert new['dossier_id']==old['dossier_id'] and new['fields']['ceo']['value']=='Zara Lane'
    assert asof(legacy_domain,TIMES[1])['fields']==new['fields'];asof(legacy_domain,NOW,want=404)
    assert status(create(legacy_domain,'chain-create'),200)==original and feed()['changes']==[] and len(log())==count

@case('stage3-never-ready-upgrades-and-initial-after-failure')
def test_never_ready():
    reset();status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'}),204)
    status(create(SD),202);failed=ready(SD);assert failed['state']=='failed'
    for t in [NOW,TIMES[-1]]:asof(SD,t,want=404);values(SD,'2020-01-01',t,want=404)
    assert all(not x for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)) and feed()['changes']==[]
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'none'}),204)
    refresh(SD);ready(SD)
    assert all(x and x[0]['type']=='initial' for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)) and feed()['changes']==[]
    for old_at in [legacy,legacy2]:
        reset(at=old_at);old_token=token
        status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'}),204)
        status(create(SD,at=old_at),202);ready(SD,at=old_at)
        exported=status(req('/_test/export',auth=False,at=old_at),200)
        status(req('/_test/import','POST',exported,auth=False),204);global_token(old_token)
        asof(SD,TIMES[-1],want=404);values(SD,'2020-01-01',TIMES[-1],want=404)
        status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'none'}),204)
        refresh(SD);ready(SD)
        assert history(SD)['fields']['executives'][0]['type']=='initial' and feed()['changes']==[]

@case('stage3-feed-pagination-concurrent-builds-and-atomic-reads')
def test_feed_pagination():
    reset()
    for domain in [TD,ED,SD]:status(create(domain),202);ready(domain)
    epoch(1);clock(TIMES[1]);status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':.4}),204)
    with futures.ThreadPoolExecutor(max_workers=50) as pool:
        replies=list(pool.map(lambda i:refresh([TD,ED,SD][i%3],key='concurrent-history-'+str(i)),range(50)))
    for domain in [TD,ED,SD]:ready(domain)
    entries=feed()['changes'];assert len(entries)==9,(len(entries),entries)
    seqs=[e['seq'] for e in entries];assert seqs==sorted(set(seqs)) and all(type(n)is int and n>0 for n in seqs),seqs
    for domain in [TD,ED,SD]:
        expected=[f for f in ALL_FIELDS if len(history(domain)['fields'][f])>1]
        assert [e['field'] for e in entries if e['domain']==domain]==expected,entries
    pages=[];since=0
    while True:
        page=feed(urllib.parse.urlencode({'since':since,'limit':2}));pages+=page['changes']
        assert page['has_more']==(len(pages)<len(entries)),page
        if not page['has_more']:break
        since=page['changes'][-1]['seq']
    assert pages==entries
    assert feed('since='+str(seqs[-1]))=={'changes':[],'has_more':False}
    assert feed('limit=200')['changes']==entries
    # Every identical-key replay leaves the event set fixed.
    before=len(log())
    with futures.ThreadPoolExecutor(max_workers=50) as pool:
        result=list(pool.map(lambda i:req('/dossiers/'+[TD,ED,SD][i%3]+'/refresh','POST',key='concurrent-history-'+str(i)),range(50)))
    assert all(x[0]==200 for x in result) and feed()['changes']==entries and len(log())==before

@case('stage3-feed-default-limit-and-exclusive-cursor')
def test_feed_default_limit():
    reset();status(create(SD),202);ready(SD)
    for i in range(9):
        clock(TIMES[i+1]);epoch((i+1)%2);refresh(SD);ready(SD)
    all_entries=feed('limit=200')['changes'];assert len(all_entries)==63,len(all_entries)
    first=feed();assert len(first['changes'])==50 and first['has_more'] is True,first
    assert first['changes']==all_entries[:50]
    remaining=feed('since='+str(first['changes'][-1]['seq']))
    assert remaining['changes']==all_entries[50:] and remaining['has_more'] is False
    assert feed('since='+str(all_entries[-1]['seq'])+'&limit=1')=={'changes':[],'has_more':False}

@case('stage3-failed-build-incurred-spending-in-as-of')
def test_failed_spending():
    reset();status(create(TD),202);old=ready(TD);h=history(TD);f=feed();clock(TIMES[1])
    try:
        cmd('docker','stop',PREFIX+'-web',timeout=30)
        refresh(TD);failed=ready(TD,seconds=20)
        assert failed['state']=='failed' and old['spent_units']<failed['spent_units']<=old['spent_units']+80,failed
        assert asof(TD,NOW)['spent_units']==old['spent_units']
        snap=asof(TD,TIMES[1]);assert snap['spent_units']==failed['spent_units'] and snap['fields']==old['fields'] and snap['state']=='ready',snap
        assert history(TD)==h and feed()==f
    finally:
        cmd('docker','start',PREFIX+'-web',timeout=30);wait(mock,'/_mock/health')

def abrupt_restart(name= None,at=None):
    name=name or service_name
    cmd('docker','kill','--signal','KILL',name,timeout=30)
    cmd('docker','start',name,timeout=30);wait(at or base)

@case('stage3-idle-abrupt-restart-all-state-and-seq')
def test_idle_restart():
    reset();original=status(create(TD,'restart-create'),202);ready(TD)
    for e in [1,2,4,5,6]:build_epoch(TD,e,TIMES[e])
    saved_token=token;before=query_matrix(TD)
    abrupt_restart()
    assert token==saved_token and query_matrix(TD)==before
    count=len(log());assert status(create(TD,'restart-create'),200)==original and len(log())==count
    login=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200)
    assert login['user_id']=='reader_a'
    oldseq=feed()['changes'][-1]['seq'];epoch(1);clock(TIMES[7]);refresh(TD);ready(TD)
    assert feed()['changes'][-1]['seq']>oldseq
    assert get(TD)['researched_at']==TIMES[7]

@case('stage3-interrupted-refresh-rollback-and-replay')
def test_interrupted_refresh():
    reset();status(create(TD),202);old=ready(TD);h=history(TD);events=feed()
    epoch(1);clock(TIMES[1]);status(admin('faults',{'provider':'nimble','methods':['research','extract'],'mode':'delay','seconds':3}),204)
    response=refresh(TD,key='interrupt-refresh')
    signup=status(req('/auth/signup','POST',{'email':'interrupt@reader.test','password':'interrupt-password','display_name':'During build'},auth=False),201)
    current=get(TD);assert current['state']=='building'
    abrupt_restart();now=get(TD)
    assert now['state'] in ['ready','failed']
    if now['state']=='failed':
        assert now['fields']==old['fields'] and now['researched_at']==old['researched_at'],now
    assert old['spent_units']<=now['spent_units']<=old['spent_units']+80
    if now['state']=='failed':assert history(TD)==h and feed()==events
    status(req('/dossiers',extra={'Authorization':'Bearer '+signup['token']}),200)
    status(req('/auth/login','POST',{'email':'interrupt@reader.test','password':'interrupt-password'},auth=False),200)
    count=len(log());assert status(req('/dossiers/'+TD+'/refresh','POST',key='interrupt-refresh'),200)==response
    assert len(log())==count
    status(admin('faults',{'provider':'nimble','methods':['research','extract'],'mode':'none'}),204)
    refresh(TD);new=ready(TD);assert new['fields']['ceo']['value']=='Sam Ortiz' and new['researched_at']==TIMES[1]
    assert len(feed()['changes'])==1 and len(history(TD)['fields']['ceo'])==2

@case('stage3-interrupted-first-build-failed-then-initial')
def test_interrupted_first():
    reset();status(admin('faults',{'provider':'nimble','methods':['research','extract'],'mode':'delay','seconds':3}),204)
    original=status(create(SD,'interrupt-first'),202);assert get(SD)['state']=='building'
    abrupt_restart();d=ready(SD,seconds=10)
    assert d['state'] in ['ready','failed'],d
    if d['state']=='failed':
        assert d['researched_at'] is None and all(v['value'] is None for v in d['fields'].values()),d
        assert all(not x for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)) and feed()['changes']==[]
        asof(SD,NOW,want=404)
    else:
        assert all(d['fields'][f]['value'] is not None for f in STAGE3_FIELDS)
        assert all(x and x[0]['type']=='initial' for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)) and feed()['changes']==[]
    assert status(create(SD,'interrupt-first'),200)==original
    status(admin('faults',{'provider':'nimble','methods':['research','extract'],'mode':'none'}),204)
    refresh(SD);ready(SD)
    assert all(x[0]['type']=='initial' for x in (history(SD)['fields'][f] for f in STAGE3_FIELDS)) and feed()['changes']==[]

@case('stage3-fifty-concurrent-durable-writes')
def test_fifty_writes():
    reset()
    def signup(i):
        body={'email':f'parallel-{i}@reader.test','password':'parallel-password','display_name':f'Parallel {i}'}
        started=time.monotonic();response=status(req('/auth/signup','POST',body,auth=False),201)
        return (i,response,time.monotonic()-started)
    with futures.ThreadPoolExecutor(max_workers=50) as pool:created=list(pool.map(signup,range(50)))
    assert max(x[2] for x in created)<5
    abrupt_restart()
    for i,user,elapsed in created:
        data=status(req('/auth/login','POST',{'email':f'parallel-{i}@reader.test','password':'parallel-password'},auth=False),200)
        assert data['user_id']==user['user_id']
        status(req('/dossiers',extra={'Authorization':'Bearer '+user['token']}),200)
    print('DURABLE_WRITE_LATENCY',round(max(x[2] for x in created),3),'seconds,50 writes',flush=True)

@case('stage3-every-completed-write-is-durable')
def test_response_durability():
    reset()
    user=status(req('/auth/signup','POST',{'email':'durable@reader.test','password':'durable-password','display_name':'Durable'},auth=False),201)
    abrupt_restart();status(req('/dossiers',extra={'Authorization':'Bearer '+user['token']}),200)
    session=status(req('/auth/login','POST',{'email':'durable@reader.test','password':'durable-password'},auth=False),200)
    abrupt_restart();status(req('/dossiers',extra={'Authorization':'Bearer '+session['token']}),200)
    clock(TIMES[4]);abrupt_restart()
    status(create(TD),202);d=ready(TD);assert d['researched_at']==TIMES[4]
    exported=status(req('/_test/export',auth=False),200);old_token=token
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    abrupt_restart(PREFIX+'-second',second)
    assert get(TD,at=second)==d
    status(req('/_test/reset','POST',FIXTURE,auth=False),204)
    abrupt_restart()
    status(req('/dossiers',extra={'Authorization':'Bearer '+old_token}),401,'unauthenticated')
    reset_login=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200)
    global_token(reset_login['token']);assert status(req('/dossiers'),200)['dossiers']==[] and feed()['changes']==[]
    status(req('/auth/login','POST',{'email':'durable@reader.test','password':'durable-password'},auth=False),401,'unauthenticated')
    status(create(TD),202);new=ready(TD);assert new['researched_at']==NOW

@case('stage3-crash-atomic-concurrent-signups')
def test_crash_atomic():
    reset();completed=[]
    def writer(i):
        try:
            response=status(req('/auth/signup','POST',{'email':f'crash-{i}@reader.test','password':'crash-password','display_name':f'Crash {i}'},auth=False),201)
            completed.append((i,response))
        except (OSError,http.client.HTTPException,json.JSONDecodeError):pass # A deliberately cut response is unacknowledged.
    killed=False
    try:
        with futures.ThreadPoolExecutor(max_workers=50) as pool:
            jobs=[pool.submit(writer,i) for i in range(50)]
            until=time.monotonic()+4
            while not completed and time.monotonic()<until:time.sleep(.005)
            assert completed,'no completed write before deliberate crash'
            cmd('docker','kill','--signal','KILL',service_name,timeout=30);killed=True
            for job in jobs:job.result()
    finally:
        if killed:cmd('docker','start',service_name,timeout=30);wait(base)
    acknowledged=list(completed)
    status(req('/dossiers'),200)
    for i,user in acknowledged:
        login=status(req('/auth/login','POST',{'email':f'crash-{i}@reader.test','password':'crash-password'},auth=False),200)
        assert login['user_id']==user['user_id']
        status(req('/dossiers',extra={'Authorization':'Bearer '+user['token']}),200)
    print('CRASH_ACKNOWLEDGED_WRITES',len(acknowledged),flush=True)

@case('stage3-pre-reset-system-clock-mode-survives-restart')
def test_system_clock_restart():
    # R3-5: this intentionally never calls reset or clock on this fresh service.
    saved_token=token;name=PREFIX+'-system-clock'
    at=run_container(name,PREFIX+'-service',network,8097,env);wait(at)
    try:
        auth=status(req('/auth/signup','POST',{'email':'system-mode@reader.test','password':'system-mode-password','display_name':'System Mode'},auth=False,at=at),201)
        global_token(auth['token'])
        status(create('reader-blank.test',at=at),202);first=ready('reader-blank.test',at=at)
        time.sleep(.15)
        status(create('reader-full.test',at=at),202);second_build=ready('reader-full.test',at=at)
        assert instant(second_build['researched_at'])>instant(first['researched_at'])
        abrupt_restart(name,at);assert get('reader-full.test',at=at)==second_build
        status(create('reader-long.test',at=at),202);last=ready('reader-long.test',at=at)
        assert instant(last['researched_at'])>instant(second_build['researched_at'])
        assert abs(time.time()-float(instant(last['researched_at'])))<10
    finally:global_token(saved_token)
