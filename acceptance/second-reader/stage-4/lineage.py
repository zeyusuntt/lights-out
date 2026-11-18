"""Independent Stage 4 HTTP fixtures/oracles; no submitted source is imported."""

def lin(registrant,canonical=None,first=None):
    return {'registrant':registrant,'canonical':canonical,'first_published_by':first}

def pg(url,text,kind='news',epochs=None,reg=None,canonical=None,first=None,effective='2020-01-01',published=None,searchable=True):
    return dict(url=url,text=text,kind=kind,epochs=epochs if epochs is not None else [0,1],
        true_from=effective,published_at=published,searchable=searchable,
        lineage=lin(reg if reg is not None else urllib.parse.urlparse(url).hostname,canonical,first))

LD='reader-lineage.test';LU='https://reader-lineage.test/'
lineage_expected={
    LU+'own':('own',LD,'Dana Ruiz'),
    LU+'fake':('aggregator',LD,'Sam Ortiz'),
    'https://other-source.test/claim':('aggregator','other-source.test','Dana Ruiz'),
    LU+'invalid':('own',LD,'Dana Ruiz'),
    'https://wire-copy.test/copy':('news','wire-source.test','Dana Ruiz'),
    'https://copy-source.test/copy':('news','upstream-source.test','Dana Ruiz'),
    'https://self-source.test/current':('news','owner-self.test','Dana Ruiz'),
    'https://missing-reg.test/profile':('news','missing-reg.test','Dana Ruiz'),
    LU+'fallback-kind':('aggregator','foreign-owner.test','Dana Ruiz'),
}
company(LD,[
    pg(LU+'own','Reader Lineage CEO: Dana Ruiz.','own',reg=LD),
    pg(LU+'fake','Reader Lineage CEO: Sam Ortiz.','own',reg='foreign-owner.test'),
    pg('https://other-source.test/claim','Reader Lineage CEO: Dana Ruiz.','own'),
    pg(LU+'invalid','Reader Lineage CEO: Dana Ruiz.','own',reg='invalid'),
    pg('https://wire-copy.test/copy','Reader Lineage CEO: Dana Ruiz.',first=' WWW.WIRE-SOURCE.TEST. ',canonical='https://unneeded-source.test/original'),
    pg('https://copy-source.test/copy','Reader Lineage CEO: Dana Ruiz.',canonical='https://original-source.test/unlisted'),
    pg('https://original-source.test/unlisted','Reader Lineage CEO: Zara Lane.',first='UPSTREAM-SOURCE.TEST.',searchable=False),
    pg('https://self-source.test/current','Reader Lineage CEO: Dana Ruiz.',reg='owner-self.test',canonical='https://self-source.test/current'),
    pg('https://missing-reg.test/profile','Reader Lineage CEO: Dana Ruiz.',reg='not a domain'),
    pg(LU+'fallback-kind','Reader Lineage CEO: Dana Ruiz.',kind=None,reg='foreign-owner.test'),
])

DD='reader-depth.test';depth_urls=['https://depth-'+c+'.test/profile' for c in 'abcde']
company(DD,[pg(url,'Reader Depth CEO: '+('Zara Lane' if i==4 else 'Dana Ruiz')+'.',
    canonical=depth_urls[i+1] if i<4 else None,first='wire-depth.test' if i==4 else None,searchable=i<4)
    for i,url in enumerate(depth_urls)])
CD='reader-cycle.test';cycle_urls=['https://cycle-'+c+'.test/profile' for c in 'abc']
company(CD,[pg(url,'Reader Cycle CEO: Dana Ruiz.',canonical=cycle_urls[(i+1)%3]) for i,url in enumerate(cycle_urls)])
MD='reader-missing-origin.test'
company(MD,[pg('https://copy-missing.test/profile','Reader Missing Origin CEO: Dana Ruiz.',canonical='https://WWW.ABSENT-SOURCE.TEST./original')])

FAN='reader-fanout.test'
fan_pages=[]
for i in range(8):
    original=f'https://original-fanout-{i}.test/profile'
    fan_pages.append(pg(f'https://copy-fanout-{i}.test/profile','Reader Fanout CEO: Dana Ruiz.',canonical=original))
    fan_pages.append(pg(original,'Original publication metadata.',first=f'publisher-fanout-{i}.test',searchable=False))
company(FAN,fan_pages)

RESERVE='reader-reserve-pages.test'
reserve_pages=[]
for field,valueset,phrase,title in [
    ('legal_name',['Alpha','Beta','Gamma','Delta','Epsilon'],'legal name is','legal name registered name registered as registered company legal entity name of record'),
    ('hq_city',['Lisbon','Zürich','Berlin','Paris','Oslo'],'is based in','headquartered in headquarters in head office in based in registered office in registered seat in'),
    ('ceo',['Dana Ruiz','Sam Ortiz','Lina Park','Eva Stone','Petra Cole'],'CEO:','chief executive officer chief executive CEO')]:
    for i,value in enumerate(valueset):
        supported='Reader Reserve Pages '+value+', LLC' if field=='legal_name' else value
        page=pg('https://'+RESERVE+'/'+field+'-'+str(i),'Reader Reserve Pages '+phrase+' '+supported+'.','own',reg=RESERVE)
        page['title']='Reader Reserve Pages '+title
        reserve_pages.append(page)
company(RESERVE,reserve_pages)

HIDDEN='hidden-cedar.test';HIDDEN_URL='https://hidden-cedar.test/private'
company(HIDDEN,[pg(HIDDEN_URL,'Hidden Cedar CEO: Dana Ruiz.','own',reg=HIDDEN,searchable=False)],
    {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url=HIDDEN_URL,excerpt='Hidden Cedar CEO: Dana Ruiz.')]}})

OD='reader-standing.test';ou='https://reader-standing.test/own'
standing_pages=[]
for e in range(9):
    if e in [0,2,4,5,6,7,8]:standing_pages.append(pg(ou,'Reader Standing CEO: '+('Sam Ortiz' if e in [2,7] else 'Dana Ruiz')+'.','own',[e],reg=OD))
    if e==1:standing_pages.append(pg('https://standing-b.test/profile','Reader Standing CEO: Dana Ruiz.',epochs=[e]))
    if e==3:standing_pages.append(pg('https://standing-c.test/profile','Reader Standing CEO: Dana Ruiz.',epochs=[e]))
    if e==4:standing_pages.append(pg('https://standing-d.test/profile','Reader Standing CEO: Dana Ruiz.',epochs=[e]))
    if e==7:standing_pages.append(pg('https://standing-e.test/profile','Reader Standing CEO: Sam Ortiz.',epochs=[e]))
    if e==8:standing_pages.append(pg('https://standing-f.test/profile','Reader Standing CEO: Dana Ruiz.',epochs=[e]))
company(OD,standing_pages)

MEMBER_DOMAINS=['reader-members.test','reader-investor-members.test']
for domain in MEMBER_DOMAINS:
    name=domain.split('.')[0].replace('-',' ')
    pages=[]
    for e in range(7):
        a='Ana Silva' if e<5 else 'Mia Lopez'
        if domain.endswith('investor-members.test'):
            a='Alpha Capital' if e<5 else 'Gamma Capital'
            texta=f'{name} investor: {a}.';textb=f'{name} investor: Beta Ventures.'
        else:texta=f'{name} CFO: {a}.';textb=f'{name} CTO: Ben Okafor.'
        pages.append(pg('https://'+domain+'/a',texta,'own',[e],reg=domain))
        if e in [0,1,2,6]:pages.append(pg('https://member-second.test/'+domain+'/a',texta,epochs=[e]))
        if e!=1:pages.append(pg('https://member-single.test/'+domain+'/b',textb,'filing',[e]))
        if e==3:pages.append(pg('https://member-third.test/'+domain+'/b',textb,epochs=[e]))
    company(domain,pages)

ID='reader-investors.test'
investor_pages=[
    pg('https://reader-investors.test/own','Reader Investors investors include Bluebird Capital and Long Horizon Growth Fund.','own',effective='2022-01-01'),
    pg('https://investor-filing.test/record','Reader Investors investor Bluebird Capital participated.','filing',effective='2020-01-01'),
    pg('https://investor-wire.test/a','Reader Investors investors: Northwind Ventures and Single Capital.',effective='2021-01-01'),
    pg('https://investor-second.test/b','Reader Investors backed by Northwind Ventures.',effective='2023-01-01'),
    pg('https://investor-copy.test/a','Reader Investors investor: Single Capital.',first='investor-wire.test',effective='2025-01-01'),
    pg('https://reader-investors.test/amount','Reader Investors raised $40M in a round led by General Atlantic.','own',effective=None),
]
company(ID,investor_pages)

LONE='reader-lone-investor.test'
company(LONE,[
    pg('https://look-investor-a.test/profile','Reader Lone Investor investor: Bluebird Capital.','own',[0,1],reg='foreign-investor-a.test'),
    pg('https://look-investor-b.test/profile','Reader Lone Investor investor: Bluebird Capital.','own',[0,1],reg='foreign-investor-b.test'),
    pg('https://registry-investor.test/profile','Reader Lone Investor investor: Bluebird Capital.','filing',[1]),
])
ICD='reader-investor-change.test'
investor_changes=[
    [('bluebird','Bluebird Capital','2022-01-01')],
    [('bluebird','Bluebird Capital','2024-01-01'),('northwind','Northwind Ventures','2021-01-01')],
    [('bluebird','Bluebird Capital','2024-01-01'),('northwind','Northwind Ventures','2021-01-01'),('granite','Granite Equity','2024-01-01')],
    [('bluebird','Bluebird Capital','2024-01-01'),('granite','Granite Equity','2024-01-01')],
    [],[('bluebird','Bluebird Capital','2020-01-01')],
]
change_pages=[]
for e,members in enumerate(investor_changes):
    for slug,name,date in members:change_pages.append(pg('https://'+ICD+'/'+slug,'Reader Investor Change investor: '+name+'.','own',[e],reg=ICD,effective=date))
    if not members:change_pages.append(pg('https://'+ICD+'/bluebird','Reader Investor Change investor profile is unavailable.','own',[e],reg=ICD,effective='2025-01-01'))
company(ICD,change_pages)

investor_grammar=[]
investor_templates=[
    ('suffix-ventures','{name} investor: Northwind Ventures.',['Northwind Ventures']),
    ('suffix-capital','{name} investors include Bluebird Capital.',['Bluebird Capital']),
    ('suffix-partners','Oak River Partners participated in {name}.',['Oak River Partners']),
    ('suffix-fund','{name} investor: Long Horizon Growth Fund.',['Long Horizon Growth Fund']),
    ('suffix-investments','{name} is backed by Silver Birch Investments.',['Silver Birch Investments']),
    ('suffix-holdings','{name} investor: Alpine Holdings.',['Alpine Holdings']),
    ('suffix-equity','{name} investor: Granite Equity.',['Granite Equity']),
    ('multi','{name} investors include Bluebird Capital and Northwind Ventures.',['Bluebird Capital','Northwind Ventures']),
    ('single','{name} investor Capital.',[]),
    ('longer-run','{name} investor Northwind Ventures Group.',[]),
    ('no-statement','{name} welcomes Bluebird Capital.',[]),
    ('negation','{name} reportedly backed by Bluebird Capital.',[]),
    ('amount-general','{name} raised $40M in a round led by General Atlantic.',['General Atlantic']),
    ('amount-single','{name} raised USD 12 million backed by Sequoia.',['Sequoia']),
    ('fractional-amount','{name} raised $12.34 led by General Atlantic.',['General Atlantic']),
    ('fractional-scale-amount','{name} raised $0.0001k backed by Sequoia.',['Sequoia']),
    ('no-amount','{name} is led by Dana Ruiz.',[]),
    ('eur','{name} raised EUR 12 million led by General Atlantic.',[]),
    ('not-led','{name} raised $12M and investor General Atlantic.',[]),
    ('unicode','{name} investor: Élan Capital.',['Élan Capital']),
    ('uppercase-break','{name} investor: AI Ventures.',[]),
    ('wrong-company','Other Company investor Bluebird Capital.',[]),
    ('short-whole-negated','{name} investor Bluebird Capital, not Northwind Ventures.',[]),
    ('long-span','context '*150+'{name} investor Bluebird Capital.',['Bluebird Capital']),
]
for i,(label,template,expected) in enumerate(investor_templates):
    domain='capital-reader-'+chr(97+i)+'.test';name=domain.split('.')[0].replace('-',' ')
    company(domain,[pg('https://'+domain+'/profile',template.format(name=name),'own',reg=domain)])
    investor_grammar.append((label,domain,expected))
company('reader-capital.test',[pg('https://reader-capital.test/profile','Reader Capital investors include Bluebird Capital.','own',reg='reader-capital.test')])
investor_grammar.append(('company-name-removal','reader-capital.test',['Bluebird Capital']))
company('reader-phrase.test',[pg('https://reader-phrase.test/profile','Reader Phrase Bluebird Capital Investor Northwind Ventures.','own',reg='reader-phrase.test')])
investor_grammar.append(('phrase-separates-runs','reader-phrase.test',['Bluebird Capital','Northwind Ventures']))

# Small, one-page companies make independent budget/completeness accounting easy.
BATCH_DOMAINS=[]
for i in range(52):
    domain='batch-reader-'+chr(97+i//26)+chr(97+i%26)+'.test';name=domain.split('.')[0].replace('-',' ')
    company(domain,[pg('https://'+domain+'/profile',f'{name} legal name is {name}, LLC.\n{name} is based in Lisbon.\n{name} CEO: Dana Ruiz.\n{name} was founded in 2014.\n{name} employs 120 people.\n{name} raised $12M.\n{name} CFO: Ana Silva.\n{name} investor: Bluebird Capital.','own',reg=domain)])
    BATCH_DOMAINS.append(domain)

EIGHT='reader-eight.test'
company(EIGHT,[pg('https://'+EIGHT+'/all',p['text'].replace('Reader Seven','Reader Eight')+'\nReader Eight investor: '+('Bluebird Capital' if i==0 else 'Northwind Ventures')+'.','own',[i],reg=EIGHT,effective=f'202{i}-01-01') for i,p in enumerate(seven_pages)])

# An investor candidate can be real evidence while not yet making any selected member.
UNC='reader-unconfirmed.test';UNC_URL='https://reader-unconfirmed.test/private'
company(UNC,[
    pg('https://'+UNC+'/profile','Reader Unconfirmed legal name is Reader Unconfirmed, LLC.\nReader Unconfirmed is based in Lisbon.\nReader Unconfirmed CEO: Dana Ruiz.\nReader Unconfirmed was founded in 2014.\nReader Unconfirmed employs 120 people.\nReader Unconfirmed raised $12M.\nReader Unconfirmed CFO: Ana Silva.','own',reg=UNC),
    pg('https://unconfirmed-wire.test/profile','Reader Unconfirmed investor: Bluebird Capital.'),
    pg(UNC_URL,'Reader Unconfirmed CEO: Dana Ruiz.\nReader Unconfirmed investor: Bluebird Capital.','own',reg=UNC,searchable=False),
],{'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url=UNC_URL,excerpt='Reader Unconfirmed CEO: Dana Ruiz.')]}})

def normhost(url):
    value=(urllib.parse.urlparse(url).hostname or '').strip().lower().removesuffix('.')
    return value.removeprefix('www.')

def field_origins(d):
    for f,v in d['fields'].items():
        assert all(k in v for k in ['origins','corroborated','corroborated_since']),(f,v)
        candidates=v['candidates']
        for c in candidates:
            o=c['origin'];assert isinstance(o,str) and o==o.strip().lower().removesuffix('.').removeprefix('www.') and '.' in o,c
        if v['value'] is None:
            assert v['origins']==[] and v['corroborated'] is False and v['corroborated_since'] is None,(f,v)
            continue
        if f=='executives':groups=[[c for c in candidates if c['title']==m['title'] and c['value']==m['name']] for m in v['value']]
        elif f=='investors':groups=[[c for c in candidates if c['value']==m] for m in v['value']]
        else:groups=[[c for c in candidates if c['value']==v['value']]]
        origins=sorted({c['origin'] for group in groups for c in group})
        assert v['origins']==origins,(f,'origins',v)
        assert v['corroborated'] is all(len({c['origin'] for c in group})>=2 for group in groups),(f,'corroborated',v)
        if v['corroborated']:assert v['corroborated_since'] is not None,(f,'missing corroboration time',v)
        if v['corroborated_since'] is not None:
            assert instant(v['corroborated_since'])<=instant(d['researched_at']),v

def investor_shape(d):
    temporal_shape(d);field_origins(d)
    v=d['fields']['investors'];cs=v['candidates']
    names={c['value'] for c in cs}
    members=sorted(name for name in names if any(c['kind'] in ['own','filing'] for c in cs if c['value']==name) or len({c['origin'] for c in cs if c['value']==name})>=2)
    assert v['value']==(members or None) and v['status']==('known' if members else 'unknown'),v
    assert cs==sorted(cs,key=rank_key),cs
    for c in cs:assert c['selected'] is (c['value'] in members),c
    assert v['citations']==[{k:c[k] for k in ['url','excerpt','provider']} for name in members for c in cs if c['value']==name],v
    dates=[]
    for name in members:
        found=[c['true_from'] for c in cs if c['value']==name and c['true_from'] is not None];dates.append(min(found) if found else None)
    assert v['true_from']==(max(dates) if dates and all(t is not None for t in dates) else None),v
    served=[(call['provider'],p['url'],prose(p['text'])) for call in log() for p in call.get('served',[])]
    canon=lambda s:re.sub(r'\s+',' ',s)
    for c in cs:
        assert 1<=len(c['excerpt'])<=500 and any(p==c['provider'] and u==c['url'] and canon(c['excerpt']) in canon(text) for p,u,text in served),c

def batch(domains,budget,key=None,at=None):
    return req('/batches','POST',{'domains':domains,'budget_units':budget},key=key or uuid.uuid4().hex,at=at)

def batchget(id,at=None):return status(req('/batches/'+id,at=at),200)

def batchdone(id,seconds=20,at=None):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        result=batchget(id,at)
        if result['state']=='done':return result
        assert result['state']=='running',result
        time.sleep(.05)
    raise AssertionError(('batch did not finish',id,seconds))

@case('stage4-lineage-precedence-own-and-lineage-only-original')
def test_lineage():
    reset();status(create(LD),202);d=ready(LD);provenance(d);field_origins(d)
    candidates={c['url']:c for c in d['fields']['ceo']['candidates']}
    assert set(candidates)==set(lineage_expected),(set(lineage_expected)-set(candidates),candidates)
    for url,(kind,origin,value) in lineage_expected.items():
        c=candidates[url];assert (c['kind'],c['origin'],c['value'])==(kind,origin,value),c
    assert d['fields']['ceo']['value']=='Dana Ruiz' and d['fields']['ceo']['status']=='contested'
    extracts=[u for call in log() if call['method']=='extract' for u in call['urls']]
    assert 'https://original-source.test/unlisted' in extracts and 'https://unneeded-source.test/original' not in extracts,extracts
    assert all(c['value']!='Zara Lane' for c in candidates.values())

@case('stage4-canonical-depth-root-sensitive-cache')
def test_depth():
    reset();status(create(DD),202);d=ready(DD);field_origins(d)
    cs={c['url']:c for c in d['fields']['ceo']['candidates']}
    assert set(cs)==set(depth_urls[:4]),cs
    expected=['depth-e.test','wire-depth.test','wire-depth.test','wire-depth.test']
    assert [cs[u]['origin'] for u in depth_urls[:4]]==expected,cs
    assert depth_urls[4] in [u for c in log() if c['method']=='extract' for u in c['urls']]

@case('stage4-canonical-cycles-and-missing-original')
def test_cycles():
    reset();status(create(CD),202);d=ready(CD);field_origins(d)
    cs={c['url']:c['origin'] for c in d['fields']['ceo']['candidates']}
    assert cs=={u:normhost(cycle_urls[(i+1)%3]) for i,u in enumerate(cycle_urls)},cs
    status(create(MD),202);m=ready(MD);assert m['fields']['ceo']['candidates'][0]['origin']=='absent-source.test',m

@case('stage4-eight-independent-originals-within-build-budget')
def test_origin_fanout():
    reset();status(create(FAN),202);d=ready(FAN);field_origins(d)
    v=d['fields']['ceo'];assert len(v['candidates'])==8,v
    assert v['origins']==[f'publisher-fanout-{i}.test' for i in range(8)],v
    assert d['spent_units']==sum(c['cost'] for c in log())<=80
    extracts=[u for c in log() if c['method']=='extract' for u in c['urls']]
    assert all(f'https://original-fanout-{i}.test/profile' in extracts for i in range(8)),extracts

@case('stage4-lineage-reserve-keeps-affordable-evidence-complete')
def test_unneeded_reserve():
    reset();status(create(RESERVE),202);d=ready(RESERVE);calls=log();provenance(d)
    returned={p['url'] for c in calls if c['method']=='search' for p in c.get('served',[]) if p['url'].startswith('https://'+RESERVE+'/')}
    expected={p['url'] for p in reserve_pages};assert returned==expected,('fixture search coverage',returned,expected)
    gathered={c['url'] for field in FIELDS for c in d['fields'][field]['candidates']}
    actual=d['spent_units'];assert actual==sum(c['cost'] for c in calls)<=80
    assert gathered==expected,{'missing':sorted(expected-gathered),'candidates':len(gathered),'searched':len(returned),'spent_units':actual,'remaining_units':80-actual,'render_cost_per_missing_page':3}
    assert all(len(d['fields'][f]['candidates'])==5 for f in ['legal_name','hq_city','ceo'])

@case('stage4-scalar-standing-origins-and-selection-reset')
def test_standing():
    reset();status(create(OD),202);a=ready(OD);field_origins(a)
    assert a['fields']['ceo']['corroborated_since'] is None
    expected=[TIMES[1],None,None,TIMES[4],TIMES[4],TIMES[4],TIMES[7],TIMES[8]]
    for e,since in zip(range(1,9),expected):
        d=build_epoch(OD,e,TIMES[e]);field_origins(d)
        assert d['fields']['ceo']['corroborated_since']==since,(e,d['fields']['ceo'])
    early=asof(OD,NOW);assert early['fields']['ceo']['corroborated_since'] is None and early['fields']['ceo']['origins']==[OD]
    assert asof(OD,TIMES[1])['fields']['ceo']['corroborated_since']==TIMES[1]

@case('stage4-standing-origin-reset-at-identical-build-times')
def test_standing_equal_time():
    reset();status(create(OD),202);ready(OD)
    for e in [1,2,3]:
        epoch(e);refresh(OD);d=ready(OD)
    assert d['fields']['ceo']['value']=='Dana Ruiz' and d['fields']['ceo']['corroborated_since'] is None,d

for domain in MEMBER_DOMAINS:
    def member_probe(domain=domain):
        @case('stage4-member-standing-'+domain)
        def test():
            field='investors' if 'investor' in domain else 'executives'
            reset();status(create(domain),202);d=ready(domain);field_origins(d)
            assert d['fields'][field]['corroborated'] is False and d['fields'][field]['corroborated_since'] is None
            expected=[TIMES[1],None,TIMES[3],TIMES[3],None,TIMES[6]]
            for e,since in zip(range(1,7),expected):
                d=build_epoch(domain,e,TIMES[e]);field_origins(d)
                assert d['fields'][field]['corroborated_since']==since,(e,d['fields'][field])
                if e in [3,4,6]:assert d['fields'][field]['corroborated'] is False
    member_probe()

@case('stage4-investor-membership-order-dates-and-copies')
def test_investors():
    reset();status(create(ID),202);d=ready(ID);investor_shape(d)
    v=d['fields']['investors'];assert v['value']==['Bluebird Capital','General Atlantic','Long Horizon Growth Fund','Northwind Ventures'],v
    assert v['true_from'] is None and v['status']=='known' and v['corroborated'] is False
    cs=[c for c in v['candidates'] if c['value']=='Single Capital'];assert len(cs)==2 and all(c['selected'] is False for c in cs),cs
    assert len({c['origin'] for c in cs})==1
    assert all(c['selected'] for c in v['candidates'] if c['value'] in v['value'])
    known_at=values(ID,'2021-06-01')['fields']['investors']
    assert known_at['value']==['Bluebird Capital'] and known_at['true_from']=='2020-01-01',known_at
    later=values(ID,'2023-01-01')['fields']['investors'];assert later['value']==['Bluebird Capital','Long Horizon Growth Fund','Northwind Ventures'],later

for label,domain,expected in investor_grammar:
    def grammar_probe(label=label,domain=domain,expected=expected):
        @case('stage4-investor-grammar-'+label)
        def test():
            reset();status(create(domain),202);d=ready(domain);investor_shape(d)
            v=d['fields']['investors'];assert v['value']==(sorted(expected) or None),(label,expected,v)
            assert {c['value'] for c in v['candidates']}==set(expected),(label,v)
    grammar_probe()

@case('stage4-unknown-investors-retain-candidates-and-lookalike-collapse')
def test_lone_investor():
    reset();status(create(LONE),202);d=ready(LONE);investor_shape(d)
    v=d['fields']['investors'];assert len(v['candidates'])==2 and v['value'] is None and v['status']=='unknown',v
    assert {c['origin'] for c in v['candidates']}=={LONE} and all(c['kind']=='aggregator' for c in v['candidates']),v
    assert v['citations']==[] and v['origins']==[] and v['learned_at'] is None
    added=build_epoch(LONE,1,TIMES[1]);investor_shape(added)
    assert added['fields']['investors']['value']==['Bluebird Capital'] and added['fields']['investors']['corroborated'] is True
    assert history(LONE)['fields']['investors'][0]['type']=='change'

@case('stage4-investor-history-corrections-equal-dates-and-removals')
def test_investor_changes():
    reset();status(create(ICD),202);d=ready(ICD);investor_shape(d)
    assert history(ICD)['fields']['investors'][0]['type']=='initial' and feed()['changes']==[]
    types=['correction','correction','change','change','change']
    for e,expected in zip(range(1,6),types):
        d=build_epoch(ICD,e,TIMES[e]);investor_shape(d)
        assert history(ICD)['fields']['investors'][-1]['type']==expected,(e,history(ICD))
    assert all(x['field']=='investors' for x in feed()['changes']) and len(feed()['changes'])==5
    assert d['fields']['investors']['candidates'][0]['learned_at']==NOW and d['fields']['investors']['learned_at']==TIMES[5]

def billed_for(domain,call):
    name=domain.split('.')[0].replace('-',' ')
    query=call.get('query') or ''
    if query:return bool(re.search(r'(?<![A-Za-z0-9])'+re.escape(domain)+r'(?![A-Za-z0-9])',query,re.I) or re.search(r'(?<![A-Za-z0-9])'+re.escape(name)+r'(?![A-Za-z0-9])',query,re.I))
    return any(normhost(u)==domain for u in call.get('urls',[]))

@case('stage4-batch-validation-is-atomic-and-budget-types')
def test_batch_validation():
    reset();domain=BATCH_DOMAINS[0]
    status(req('/batches','POST',{},auth=False),401,'unauthenticated')
    status(req('/batches','POST',{}),400,'missing_idempotency_key')
    invalid=[({},422),({'domains':[],'budget_units':10},422),({'domains':BATCH_DOMAINS[:51],'budget_units':10},422),
        ({'domains':'bad','budget_units':10},400),({'domains':[42],'budget_units':10},400),
        ({'domains':[domain,'https://bad.test'],'budget_units':10},422),
        ({'domains':[domain,' WWW.'+domain.upper()+'. '],'budget_units':10},422)]
    invalid += [({'domains':[domain],'budget_units':x},422) for x in [None,True,False,'1',1.0,1.5,[],{},0,-1,100001]]
    for body,want in invalid:
        status(req('/batches','POST',body,key='invalid-then-reuse'),want,'validation_failed' if want==422 else 'malformed_request')
        assert status(req('/dossiers'),200)['dossiers']==[] and not log(),body
    raw=json.dumps({'domains':[domain]}).rstrip('}')+',"budget_units":1e0}'
    status(req('/batches','POST',key='invalid-then-reuse',raw=raw.encode()),422,'validation_failed')
    for rawbody in [b'{',b'[]',b'null']:
        status(req('/batches','POST',key='parse-key',raw=rawbody),400,'malformed_request')
    for key in ['',None]:status(req('/batches','POST',{'domains':[domain],'budget_units':1},key=key),400,'missing_idempotency_key')
    status(req('/batches','POST',{'domains':[domain],'budget_units':1},key='x'*256),422,'validation_failed')
    response=status(batch([domain],1,key='invalid-then-reuse'),202);batchdone(response['batch_id'])
    # Existing dossiers make max-budget/key-length acceptance free and deterministic.
    huge=status(batch([domain],100000,key='x'*255),202);done=batchdone(huge['batch_id']);assert done['spent_units']==0

@case('stage4-batch-completeness-budget-and-input-order')
def test_batch_normal():
    reset();domains=[BATCH_DOMAINS[2],BATCH_DOMAINS[0],BATCH_DOMAINS[1]]
    raw=[domains[0].upper()+'.',' www.'+domains[1]+' ',domains[2]]
    initial=status(batch(raw,200,'batch-normal'),202)
    assert [x['domain'] for x in initial['dossiers']]==domains and len(initial['batch_id'])<=64
    done=batchdone(initial['batch_id']);assert [x['domain'] for x in done['dossiers']]==domains
    assert done['budget_units']==200 and done['spent_units']==sum(c['cost'] for c in log())<=200,done
    for domain in domains:
        d=get(domain);assert d['state']=='ready';provenance(d);executive_shape(d);investor_shape(d)
        assert all(d['fields'][f]['value'] is not None for f in ALL_FIELDS),d
        cost=sum(c['cost'] for c in log() if billed_for(domain,c));assert d['spent_units']==cost<=80,(domain,cost,d['spent_units'])
        assert d['researched_at']==NOW
    before=len(log())
    for _ in range(3):
        assert batchget(initial['batch_id'])==done
        listed=status(req('/dossiers'),200)['dossiers']
        for domain in domains:
            cost=sum(c['cost'] for c in log() if billed_for(domain,c))
            assert get(domain)['spent_units']==cost
            assert next(item for item in listed if item['domain']==domain)['spent_units']==cost
        history(domains[0]);feed();values(domains[0],'2025-01-01')
        time.sleep(.05)
    assert len(log())==before
    assert status(batch(raw,200,'batch-normal'),200)==initial

@case('stage4-batch-ownership-idempotency-and-concurrent-replay')
def test_batch_idempotency():
    reset();domain=BATCH_DOMAINS[0]
    with futures.ThreadPoolExecutor(max_workers=50) as pool:responses=list(pool.map(lambda _:batch([domain],200,'shared-key'),range(50)))
    assert sum(s==202 for s,b in responses)==1 and all(s in [200,202] for s,b in responses)
    original=next(b for s,b in responses if s==202);assert all(b==original for s,b in responses)
    batchdone(original['batch_id']);before=len(log())
    replay=status(req('/batches','POST',{'domains':[domain],'budget_units':200,'ignored':'different'},key='shared-key'),200);assert replay==original
    for body in [{'domains':[domain],'budget_units':'invalid'},{'domains':[],'budget_units':200},{'domains':[domain.upper()],'budget_units':200}]:
        status(req('/batches','POST',body,key='shared-key'),409,'idempotency_key_reuse')
    assert len(log())==before
    b=status(req('/auth/login','POST',{'email':'b@reader.test','password':'reader-pass-b'},auth=False),200)
    status(req('/batches/'+original['batch_id'],extra={'Authorization':'Bearer '+b['token']}),404,'not_found')
    status(req('/batches/'+original['batch_id'],auth=False),401,'unauthenticated')
    status(req('/batches/unknown-reader-batch'),404,'not_found')
    other=status(req('/batches','POST',{'domains':[domain],'budget_units':200},key='shared-key',extra={'Authorization':'Bearer '+b['token']}),202)
    assert other['batch_id']!=original['batch_id'] and batchget(original['batch_id'])['batch_id']==original['batch_id']
    status(req('/dossiers/'+domain,extra={'Authorization':'Bearer '+b['token']}),200)
    assert status(create(domain,'shared-key'),200)['domain']==domain
    refresh(domain,key='shared-key');ready(domain)
    assert status(batch([domain],200,'shared-key'),200)==original

@case('stage4-existing-domains-free-and-live-item-states')
def test_batch_existing():
    reset();d0,d1=BATCH_DOMAINS[:2]
    status(create(d0),202);ready(d0)
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':1}),204)
    refresh(d0);before=log()
    existing=status(batch([d0],1),202);done=batchdone(existing['batch_id'])
    assert done['spent_units']==0 and done['state']=='done' and done['dossiers'][0]['state']=='building',done
    ready(d0);status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'none'}),204)
    mixed=status(batch([d0,d1],200),202);end=batchdone(mixed['batch_id'])
    assert end['spent_units']==get(d1)['spent_units'] and end['spent_units']>0
    old=end['spent_units'];refresh(d1)
    current=batchget(mixed['batch_id']);assert current['state']=='done' and current['spent_units']==old
    ready(d1)

@case('stage4-overlapping-batches-single-build-and-cost-attribution')
def test_batch_overlap():
    reset();d0,d1,d2=BATCH_DOMAINS[:3]
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':.5}),204)
    with futures.ThreadPoolExecutor(max_workers=3) as pool:
        a=pool.submit(batch,[d0,d1],200,'overlap-a');b=pool.submit(batch,[d1,d2],200,'overlap-b');single=pool.submit(create,d0,'overlap-single')
        ra=status(a.result(),202);rb=status(b.result(),202);status(single.result(),200 if single.result()[0]==200 else 202)
    ba=batchdone(ra['batch_id']);bb=batchdone(rb['batch_id'])
    for domain in [d0,d1,d2]:ready(domain)
    calls=log()
    for domain in [d0,d1,d2]:
        exact=[c for c in calls if c['method']=='search' and c['query']==domain and c['status']==200]
        assert len(exact)==1,(domain,len(exact))
        assert get(domain)['spent_units']==sum(c['cost'] for c in calls if billed_for(domain,c))
    # The standalone create may win d0, so its cost is intentionally outside both batches.
    owned=ba['spent_units']+bb['spent_units'];total=sum(c['cost'] for c in calls)
    assert owned<=total and total-owned in [0,get(d0)['spent_units']],(owned,total)

@case('stage4-fifty-domain-boundary-and-tiny-shared-budget')
def test_batch_fifty():
    reset();domains=list(reversed(BATCH_DOMAINS[:50]));initial=status(batch(domains,1),202);done=batchdone(initial['batch_id'])
    assert [x['domain'] for x in done['dossiers']]==domains and done['spent_units']==sum(c['cost'] for c in log())<=1,done
    assert len(status(req('/dossiers?limit=200'),200)['dossiers'])==50
    assert all(get(domain)['state']!='building' and get(domain)['spent_units']<=1 for domain in domains)

@case('stage4-shared-budget-boundaries-and-affordable-evidence')
def test_batch_budget_boundaries():
    for budget in [1,2,3,8,10,14,20,25,30,35,40,60,80]:
        reset();initial=status(batch(BATCH_DOMAINS[:2],budget),202);done=batchdone(initial['batch_id'])
        cost=sum(c['cost'] for c in log());assert done['spent_units']==cost<=budget,(budget,done,cost)
        assert sum(get(domain)['spent_units'] for domain in BATCH_DOMAINS[:2])==cost
        assert all(get(domain)['spent_units']<=80 for domain in BATCH_DOMAINS[:2])
    # One fully supporting page costs only a lite search and a rendered extract; research
    # must be skipped rather than consuming a budget that can still gather that evidence.
    for budget in [14,20,30]:
        reset();initial=status(batch([BATCH_DOMAINS[0]],budget),202);done=batchdone(initial['batch_id']);d=get(BATCH_DOMAINS[0])
        assert all(d['fields'][f]['value'] is not None for f in ALL_FIELDS),(budget,done,d)

@case('stage4-affordable-research-only-evidence-in-batch')
def test_affordable_hidden_research():
    reset();status(create(HIDDEN),202);plain=ready(HIDDEN)
    assert plain['fields']['ceo']['value']=='Dana Ruiz' and plain['spent_units']<=49,plain
    unbatched_cost=plain['spent_units']
    reset();response=status(batch([HIDDEN],49),202);done=batchdone(response['batch_id']);d=get(HIDDEN)
    assert d['fields']['ceo']['value']=='Dana Ruiz',{'unbatched_cost':unbatched_cost,'budget_units':49,'batch_spent':done['spent_units'],'ceo':d['fields']['ceo']['value'],'research_calls':sum(c['method']=='research' for c in log())}
    assert done['spent_units']==sum(c['cost'] for c in log())<=49

@case('stage4-unconfirmed-investor-still-needs-affordable-research')
def test_unconfirmed_investor_research():
    reset();status(create(UNC),202);plain=ready(UNC)
    assert plain['fields']['investors']['value']==['Bluebird Capital'] and plain['spent_units']<=49,plain
    reset();response=status(batch([UNC],49),202);done=batchdone(response['batch_id']);d=get(UNC)
    assert all(d['fields'][f]['value'] is not None for f in ALL_FIELDS if f!='investors'),d
    assert d['fields']['investors']['value']==['Bluebird Capital'],{
        'unbatched_cost':plain['spent_units'],'batch_budget':49,'batch_spent':done['spent_units'],
        'investors':d['fields']['investors'],'research_calls':sum(c['method']=='research' for c in log())}
    assert done['spent_units']==sum(c['cost'] for c in log())<=49

@case('stage4-research-failure-search-extract-completeness')
def test_failure_reachability():
    reset();status(admin('faults',{'provider':'nimble','methods':['research'],'mode':'error'}),204)
    initial=status(batch([BATCH_DOMAINS[0],ID],200),202);done=batchdone(initial['batch_id'])
    d=get(BATCH_DOMAINS[0]);assert d['state']=='ready' and all(d['fields'][f]['value'] is not None for f in ALL_FIELDS),d
    i=get(ID);investor_shape(i);assert 'General Atlantic' in i['fields']['investors']['value']
    assert done['spent_units']==sum(c['cost'] for c in log())<=200
    assert all(c['cost']==0 for c in log() if c['method']=='research' and c['status']>=400)

@case('stage4-all-provider-failures-batch-terminal-and-free')
def test_failure_all():
    reset();status(admin('faults',{'provider':'nimble','methods':['search','extract','research'],'mode':'error'}),204)
    started=time.monotonic();initial=status(batch(BATCH_DOMAINS[:2],200),202);done=batchdone(initial['batch_id'])
    assert time.monotonic()-started<10 and done['spent_units']==0,done
    assert all(get(domain)['state']=='failed' for domain in BATCH_DOMAINS[:2])
    assert all(not x for domain in BATCH_DOMAINS[:2] for x in history(domain)['fields'].values()) and feed()['changes']==[]

@case('stage4-eight-field-history-and-investor-feed-last')
def test_eight_feed():
    reset();status(create(EIGHT),202);first=ready(EIGHT);investor_shape(first);executive_shape(first)
    assert list(first['fields'])==ALL_FIELDS and all(v['value'] is not None for v in first['fields'].values())
    changed=build_epoch(EIGHT,1,TIMES[1]);events=feed()['changes']
    assert [x['field'] for x in events]==ALL_FIELDS,events
    assert all(len(history(EIGHT)['fields'][f])==2 for f in ALL_FIELDS)
    assert events[-1]['from']==['Bluebird Capital'] and events[-1]['to']==['Northwind Ventures'] and events[-1]['type']=='change'

def stripped_legacy(value):
    if isinstance(value,list):return [stripped_legacy(x) for x in value]
    if not isinstance(value,dict):return value
    return {k:stripped_legacy(v) for k,v in value.items() if k not in ['origin','origins','corroborated','corroborated_since'] and not (k=='investors')}

@case('stage4-stage3-upgrade-builds-and-standing-origin-history')
def test_stage3_upgrade():
    reset();reset(at=legacy3);source_token=token
    old_create=status(create(OD,'legacy3-ongoing',at=legacy3),202);old0=ready(OD,at=legacy3)
    epoch(1);clock(TIMES[1],at=legacy3);refresh(OD,at=legacy3);old1=ready(OD,at=legacy3)
    oldh=history(OD,at=legacy3);oldf=feed(at=legacy3)
    status(create(ID,at=legacy3),202);ready(ID,at=legacy3)
    exported=status(req('/_test/export',auth=False,at=legacy3),200);count=len(log())
    status(req('/_test/import','POST',exported,auth=False),204);global_token(source_token)
    d=get(OD);assert stripped_legacy(d)==old1
    assert stripped_legacy(asof(OD,NOW))=={**old0,'state':'ready'}
    assert stripped_legacy(history(OD))==oldh and feed()==oldf
    v=d['fields']['ceo'];assert v['origins']==['standing-b.test'] and v['corroborated'] is False and v['corroborated_since']==TIMES[1],v
    assert asof(OD,NOW)['fields']['ceo']['corroborated_since'] is None
    assert status(create(OD,'legacy3-ongoing'),200)==old_create and len(log())==count
    assert get(ID)['fields']['investors']['value'] is None and history(ID)['fields']['investors']==[]
    clock(TIMES[2]);refresh(ID);d=ready(ID);investor_shape(d)
    assert history(ID)['fields']['investors'][0]['type']=='change'

@case('stage4-native-export-origin-standing-and-batches')
def test_native_batch_transfer():
    reset();status(create(OD),202);ready(OD)
    for e in [1,2,3,4]:build_epoch(OD,e,TIMES[e])
    epoch(0);status(create(ID),202);ready(ID)
    original=status(batch(BATCH_DOMAINS[:2],200,'native-batch'),202);b=batchdone(original['batch_id'])
    paths=['/dossiers/'+OD,'/dossiers/'+ID,'/dossiers/'+OD+'/history','/changes','/batches/'+b['batch_id']]
    paths+=['/dossiers/'+OD+'?'+urllib.parse.urlencode({'as_of':t}) for t in [NOW,TIMES[1],TIMES[4]]]
    paths+=['/dossiers/'+OD+'/values?'+urllib.parse.urlencode({'as_of':TIMES[4],'true_at':'2025-01-01'})]
    before={p:req(p) for p in paths};source_token=token;doc=status(req('/_test/export',auth=False),200)
    reset(at=second);desttoken=token;clock(TIMES[10],at=second);count=len(log())
    status(req('/_test/import','POST',doc,auth=False,at=second),204);global_token(source_token)
    assert {p:req(p,at=second) for p in paths}==before
    status(req('/batches/'+b['batch_id'],at=second,extra={'Authorization':'Bearer '+desttoken}),401,'unauthenticated')
    assert status(batch(BATCH_DOMAINS[:2],200,'native-batch',at=second),200)==original
    status(req('/_test/import','POST',doc,auth=False,at=second),204)
    assert {p:req(p,at=second) for p in paths}==before and len(log())==count

@case('stage4-running-batch-export-settles-only-completed-builds')
def test_running_batch_transfer():
    reset();status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':1.5}),204)
    original=status(batch([BATCH_DOMAINS[0],LD],200,'running-export'),202)
    until=time.monotonic()+15
    while time.monotonic()<until:
        b=batchget(original['batch_id']);a=get(BATCH_DOMAINS[0]);other=get(LD)
        if a['state']=='ready' and other['state']=='building':break
        time.sleep(.05)
    assert a['state']=='ready' and other['state']=='building',b
    doc=status(req('/_test/export',auth=False),200);saved_token=token
    cmd('docker','kill','--signal','KILL',service_name,timeout=30)
    try:
        stamp=status(req('/__probe/log',auth=False,at=proxy),200)['now']
        status(req('/_test/import','POST',doc,auth=False,at=second),204);global_token(saved_token)
        imported=batchget(original['batch_id'],at=second)
        assert imported['state']=='done' and imported['spent_units']==a['spent_units'],imported
        assert get(BATCH_DOMAINS[0],at=second)==a
        lost=get(LD,at=second);assert lost['state']=='failed' and lost['spent_units']==0 and all(v['value'] is None for v in lost['fields'].values()),lost
        assert status(batch([BATCH_DOMAINS[0],LD],200,'running-export',at=second),200)==original
        time.sleep(.2)
        assert not [c for c in status(req('/__probe/log',auth=False,at=proxy),200)['calls'] if c['started']>=stamp]
    finally:
        status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'none'}),204)
        cmd('docker','start',service_name,timeout=30);wait(base)

@case('stage4-interrupted-batch-billing-and-idle-durability')
def test_batch_restart():
    reset();domains=BATCH_DOMAINS[:2]
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':3}),204)
    original=status(batch(domains,90,'crash-batch'),202)
    until=time.monotonic()+5
    while time.monotonic()<until:
        b=batchget(original['batch_id']);calls=log()
        if sum(c['cost'] for c in calls if any(billed_for(domain,c) for domain in domains))>=20 and b['state']=='running':break
        time.sleep(.02)
    assert b['state']=='running' and sum(c['cost'] for c in calls if any(billed_for(domain,c) for domain in domains))>=20,b
    # Completed unrelated writes during a running batch must survive too.
    user=status(req('/auth/signup','POST',{'email':'batch-crash@reader.test','password':'batch-crash-password','display_name':'Batch Crash'},auth=False),201)
    clock(TIMES[1]);cmd('docker','kill','--signal','KILL',service_name,timeout=30)
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'none'}),204)
    cmd('docker','start',service_name,timeout=30);wait(base);healthy=time.monotonic()
    done=batchdone(original['batch_id'],seconds=10);assert time.monotonic()-healthy<10
    time.sleep(3.2) # Let requests already accepted by the provider at the kill reach its billing log.
    calls=log();billed=sum(c['cost'] for c in calls if any(billed_for(domain,c) for domain in domains))
    done=batchget(original['batch_id']);assert billed<=done['spent_units']<=90,(billed,done)
    for domain in domains:
        d=get(domain);actual=sum(c['cost'] for c in calls if billed_for(domain,c))
        assert d['state'] in ['ready','failed'] and actual<=d['spent_units']<=80,(domain,actual,d)
        if d['state']=='failed':assert all(v['value'] is None for v in d['fields'].values())
    assert sum(get(domain)['spent_units'] for domain in domains)==done['spent_units']
    status(req('/dossiers',extra={'Authorization':'Bearer '+user['token']}),200)
    replay_cost=len(log());assert status(batch(domains,90,'crash-batch'),200)==original
    assert len(log())==replay_cost
    before={p:req(p) for p in ['/batches/'+original['batch_id'],'/dossiers','/changes']}
    abrupt_restart();assert {p:req(p) for p in before}==before
    # Independent refresh is new work and must not recharge the completed original batch.
    oldbatch=batchget(original['batch_id'])['spent_units'];refresh(domains[0]);d=ready(domains[0])
    assert d['researched_at']==TIMES[1] and batchget(original['batch_id'])['spent_units']==oldbatch

@case('stage4-interrupted-refresh-retains-all-billed-units')
def test_refresh_billing():
    reset();status(create(TD),202);old=ready(TD);oldhistory=history(TD);oldfeed=feed()
    epoch(1);clock(TIMES[1]);status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':3}),204)
    response=refresh(TD,key='crash-accounting')
    until=time.monotonic()+5
    while time.monotonic()<until:
        if get(TD)['state']=='building' and sum(c['cost'] for c in log())>old['spent_units']:break
        time.sleep(.02)
    cmd('docker','kill','--signal','KILL',service_name,timeout=30)
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'none'}),204)
    cmd('docker','start',service_name,timeout=30);wait(base);d=ready(TD,seconds=10)
    time.sleep(3.2);calls=log();d=get(TD)
    assert sum(c['cost'] for c in calls)<=d['spent_units']<=old['spent_units']+80,(sum(c['cost'] for c in calls),d['spent_units'])
    if d['state']=='failed':assert d['fields']==old['fields'] and history(TD)==oldhistory and feed()==oldfeed
    before=len(log());assert status(req('/dossiers/'+TD+'/refresh','POST',key='crash-accounting'),200)==response
    assert len(log())==before

def refund_durability_attempt():
    reset();status(req('/__probe/reset',auth=False,at=proxy),204)
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'}),204)
    domain=BATCH_DOMAINS[0];status(create(domain),202)
    until=time.monotonic()+5;captured=False
    while time.monotonic()<until:
        calls=log();live=get(domain);trace=status(req('/__probe/log',auth=False,at=proxy),200)
        answered=[c for c in trace['calls'] if c['status']==500]
        if len(calls)==11 and live['state']=='building' and live['spent_units']==0 and len(answered)==11:
            # Every initial call has been answered and refunded; no retry can yet start.
            if trace['now']-min(c['answered'] for c in answered)<.6:
                captured=True;break
        time.sleep(.005)
    assert captured,('did not capture all-refused quiet retry interval',len(calls),live['state'],live['spent_units'])
    assert all(c['cost']==0 and c['status']==500 for c in calls)
    count=len(calls);cmd('docker','kill','--signal','KILL',service_name,timeout=30)
    try:
        stopped=log();assert len(stopped)==count,('retry raced the deliberate kill; not a refund finding',len(stopped),count)
        status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'none'}),204)
    finally:
        cmd('docker','start',service_name,timeout=30);wait(base)
    restored=ready(domain,seconds=10)
    billed=sum(c['cost'] for c in log())
    assert restored['spent_units']==billed,{'before_stop_spent':live['spent_units'],'billed_units':billed,'after_restart_spent':restored['spent_units'],'refused_calls':count,'all_initial_calls_answered_before_stop':True,'state':restored['state']}

@case('stage4-refused-call-refunds-survive-interrupted-retry-wait')
def test_refund_durability():
    # A short network delay keeps the original POST save ahead of the returned refusals.
    # Answers and billing still come unchanged from the actual kit mock; each call <1s.
    status(req('/__probe/error-delay','POST',{'seconds':.2},auth=False,at=proxy),204)
    try:refund_durability_attempt()
    finally:status(req('/__probe/error-delay','POST',{'seconds':0},auth=False,at=proxy),204)

@case('stage4-reset-clears-batches-origins-and-durable-history')
def test_batch_reset():
    reset();original=status(batch(BATCH_DOMAINS[:2],200,'reset-batch'),202);batchdone(original['batch_id']);old_token=token
    status(req('/_test/reset','POST',FIXTURE,auth=False),204);abrupt_restart()
    status(req('/batches/'+original['batch_id'],extra={'Authorization':'Bearer '+old_token}),401,'unauthenticated')
    data=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200);global_token(data['token'])
    assert status(req('/dossiers'),200)['dossiers']==[] and feed()['changes']==[]
    status(req('/batches/'+original['batch_id']),404,'not_found')
    assert batch(BATCH_DOMAINS[:1],200,'reset-batch')[0]==202
    ready(BATCH_DOMAINS[0])
