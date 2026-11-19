#!/usr/bin/env python3
"""Independent black-box probes. No product modules or shipped checks are imported."""
import concurrent.futures as futures
import datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent
STAGE = Path(sys.argv[1]).resolve()
KIT = Path(os.environ.get('DOSSIER_KIT', '/Users/[REDACTED]/dev/band-factory/vendor/sf-buildathon-2026'))
PREFIX = 'second-reader-audit-' + uuid.uuid4().hex[:8]
RUN_ROOT=ROOT.parent/'runs-stage-3'
RUN_ROOT.mkdir(exist_ok=True)
WORK = Path(tempfile.mkdtemp(prefix=PREFIX + '-',dir=RUN_ROOT))
(WORK/'buildx').mkdir()
os.environ['BUILDX_CONFIG'] = str(WORK/'buildx')
FIELDS = ['legal_name', 'hq_city', 'ceo', 'founded_year', 'headcount_range', 'funding_total']
NOW = '2026-03-01T09:00:00+00:00'
LATER = '2026-03-02T11:30:00+02:00'
FIXTURE = {'now': NOW, 'users': [dict(id='reader_a', email='a@reader.test', password='reader-pass-a', display_name='Reader A'), dict(id='reader_b', email='b@reader.test', password='reader-pass-b', display_name='Reader B')]}
results = []
containers = []
networks = []
sample_base = None
base = None
mock = None
second = None
legacy = None
legacy2 = None
proxy = None
token = None

def cmd(*args, timeout=240, check=True):
    p = subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=timeout)
    if check and p.returncode:
        raise RuntimeError('command failed: ' + ' '.join(args[:5]) + '\n' + p.stdout[-5000:])
    return p.stdout.strip()

def req(path, method='GET', body=None, key=None, auth=True, at=None, raw=None, extra=None):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    if auth and token:
        headers['Authorization'] = 'Bearer ' + token
    if key is not None:
        headers['Idempotency-Key'] = key
    headers.update(extra or {})
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    request = urllib.request.Request((at or base) + path, data=data, headers=headers, method=method)
    t = time.monotonic()
    try:
        response = urllib.request.urlopen(request, timeout=11)
    except urllib.error.HTTPError as e:
        response = e
    raw_body = response.read()
    elapsed = time.monotonic() - t
    result = json.loads(raw_body) if raw_body else None
    assert elapsed < (10 if path.startswith('/_test/') and path != '/_test/clock' else 5), (path, 'latency', elapsed)
    if response.status != 204:
        assert 'application/json' in response.headers.get('Content-Type', ''), (path, 'content-type')
        if not path.startswith('/_mock/'):
            assert 'charset=utf-8' in response.headers.get('Content-Type', '').lower().replace(' ', ''), (path, 'charset')
    if response.status >= 400:
        assert isinstance(result, dict) and isinstance(result.get('error'), dict), (path, response.status, result)
        assert isinstance(result['error'].get('code'), str) and isinstance(result['error'].get('message'), str), result
    assert response.status < 500, (path, response.status, result)
    return response.status, result

def status(result, want, code=None):
    safe=result
    if isinstance(result[1],dict) and 'token' in result[1]:
        safe=(result[0],{**result[1],'token':'<redacted>'})
    assert result[0] == want, (want, safe)
    if code:
        assert result[1]['error']['code'] == code, result
    return result[1]

def admin(path, body=None, at=None):
    return req('/_mock/' + path, 'POST' if body is not None else 'GET', body, auth=False, at=at or mock, extra={'X-Mock-Admin': 'reader-local-admin'})

def log():
    return status(admin('log'), 200)['calls']

def reset(at=None):
    global token
    status(req('/_test/reset', 'POST', FIXTURE, auth=False, at=at), 204)
    data = status(req('/auth/login', 'POST', {'email':'a@reader.test', 'password':'reader-pass-a'}, auth=False, at=at), 200)
    assert data['user_id'] == 'reader_a'
    token = data['token']
    if at is None:
        status(admin('reset', {'epoch':0}), 204)
    return data

def create(domain, key=None, at=None):
    return req('/dossiers', 'POST', {'domain': domain}, key or uuid.uuid4().hex, at=at)

def get(domain, at=None):
    return status(req('/dossiers/' + urllib.parse.quote(domain, safe=''), at=at), 200)

def ready(domain, at=None, seconds=12):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        d = get(domain, at)
        if d['state'] != 'building':
            return d
        time.sleep(.075)
    raise AssertionError((domain, 'build did not finish', seconds))

def known(d, f, value):
    actual = d['fields'][f]
    assert actual['value'] == value, (d['domain'], f, 'expected', value, 'actual', actual)
    candidates=actual['candidates']
    distinct={json.dumps(c['value'],ensure_ascii=False,sort_keys=True) for c in candidates}
    expected_status='unknown' if not distinct else ('known' if len(distinct)==1 else 'contested')
    assert actual['status']==expected_status,actual
    assert bool(candidates)==(value is not None),actual
    assert isinstance(actual['citations'], list)
    assert bool(actual['citations']) == (value is not None), actual
    if value is not None:
        if f in ('founded_year', 'funding_total'):
            assert type(actual['value']) is int, actual
        else:
            assert isinstance(actual['value'], str)

def safe_span(text, excerpt):
    """R1-7 edge oracle for generated one-sentence fixtures, independent of product code."""
    assert excerpt==excerpt.strip()
    text=re.sub(r'\s+',' ',text)
    excerpt=re.sub(r'\s+',' ',excerpt)
    protected=[]
    for m in re.finditer(r'[0-9]+(?:[,.][0-9]+)*',text):protected.append(m.span())
    number=r'(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?'
    amount=r'(?:US\$|USD|\$) ?'+number+r'(?:mn|bn|k|m| (?:thousand|million|billion))?|'+number+r'(?: (?:thousand|million|billion))? (?:US dollars|dollars)'
    for m in re.finditer(amount,text,re.I):protected.append(m.span())
    caps=[m for m in re.finditer(r'[^\W\d_]+',text,re.UNICODE) if len(m.group())>=2 and m.group()[0].isupper() and m.group()[1:].islower()]
    run=None
    for m in caps:
        if run and text[run[1]:m.start()] in [' ','-']:
            run=(run[0],m.end())
        else:
            if run:protected.append(run)
            run=m.span()
    if run:protected.append(run)
    start=0
    while True:
        start=text.find(excerpt,start)
        if start<0:return False
        end=start+len(excerpt)
        word_cut=(start>0 and text[start-1].isalnum() and text[start].isalnum()) or (end<len(text) and text[end-1].isalnum() and text[end].isalnum())
        if not word_cut and not any(a<start<b or a<end<b for a,b in protected):return True
        start+=1

def provenance(d, calls=None):
    served = [(c['provider'], p['url'], p['text']) for c in (calls or log()) for p in c.get('served', [])]
    assert list(d['fields']) == FIELDS + ['executives'], ('field set/order',list(d['fields']))
    assert isinstance(d['dossier_id'], str) and len(d['dossier_id']) <= 64
    assert d['domain'] == d['domain'].lower().strip()
    for f in FIELDS:
        v = d['fields'][f]
        known(d, f, v['value'])
        candidates=v['candidates']
        assert candidates==sorted(candidates,key=rank_key),('candidate rank',d['domain'],f,candidates)
        assert len({(c['url'],json.dumps(c['value'],ensure_ascii=False,sort_keys=True)) for c in candidates})==len(candidates),('duplicate page/value candidate',f,candidates)
        assert sum(c['selected'] is True for c in candidates)==bool(candidates),('selected flags',f,candidates)
        if candidates:
            assert candidates[0]['selected'] is True and v['value']==candidates[0]['value'],v
        assert v['citations']==[{k:c[k] for k in ['url','excerpt','provider']} for c in candidates if c['value']==v['value']],('selected citations',f,v)
        for c in candidates:
            assert set(c)=={'value','url','excerpt','provider','kind','published_at','retrieved_at','selected','true_from','learned_at'},c
            assert c['kind'] in ['own','filing','news','aggregator',None] and type(c['selected']) is bool,c
            assert c['retrieved_at']==d['researched_at'],c
            assert 1<=len(c['excerpt'])<=500,c
            canon=lambda x:re.sub(r'\s+',' ',x)
            pages=[prose(text) for provider,url,text in served if provider==c['provider'] and url==c['url']]
            assert any(canon(c['excerpt']) in canon(text) for text in pages),('candidate not in served prose',d['domain'],f,c)
        for citation in v['citations']:
            assert set(citation) == {'url','excerpt','provider'}, citation
            excerpt = citation['excerpt']
            assert 1 <= len(excerpt) <= 500, citation
            canon = lambda x: re.sub(r'\s+', ' ', x)
            matching = [text for provider, url, text in served if provider == citation['provider'] and url == citation['url'] and canon(excerpt) in canon(text)]
            assert matching, ('unserved citation', d['domain'], citation)
            assert not excerpt.startswith(('Facts:', 'Registrant:', 'Kind:')), citation

def prose(text):
    first=text.splitlines()[0] if text.splitlines() else ''
    if re.match(r'^[A-Z][a-z]+(?:-[A-Z][a-z]+)*:',first):
        return text.split('\n\n',1)[1] if '\n\n' in text else ''
    return text

def instant(value):
    match=re.fullmatch(r'(\d{4}-\d\d-\d\d[Tt]\d\d:\d\d:\d\d)(?:\.(\d+))?([Zz]|[+-]\d\d:\d\d)',value)
    assert match,('not RFC3339',value)
    parsed=datetime.datetime.fromisoformat(match[1]+match[3].upper().replace('Z','+00:00'))
    whole=int((parsed-datetime.datetime(1970,1,1,tzinfo=datetime.timezone.utc)).total_seconds())
    return Decimal(whole)+(Decimal('0.'+match[2]) if match[2] else Decimal(0))

def rank_key(c):
    authority={None:2,'aggregator':2,'news':1,'own':0,'filing':0}
    publication=(1,Decimal(0)) if c['published_at'] is None else (0,-instant(c['published_at']))
    value=c['value'].strip() if isinstance(c['value'],str) else c['value']
    return (authority[c['kind']],publication,c['url'],['nimble','tavily','kernel','browserbase'].index(c['provider']),value)

def case(name):
    def deco(fn):
        def run():
            t = time.monotonic()
            try:
                fn()
                results.append({'case':name, 'result':'pass', 'seconds':round(time.monotonic()-t,3)})
                print('PASS', name, flush=True)
            except Exception as e:
                results.append({'case':name,'result':'fail','seconds':round(time.monotonic()-t,3),'detail':str(e),'traceback':traceback.format_exc()})
                print('FAIL', name, str(e), flush=True)
        run.case=name
        tests.append(run)
        return run
    return deco

tests = []
corpus = []
grammar = []

def company(domain, texts, research=None):
    name = domain.split('.')[0].replace('-', ' ')
    pages = []
    for i, text in enumerate(texts):
        if isinstance(text, dict):
            page = dict(text)
            page.setdefault('text','')
        else:
            page = {'text':text}
        page.setdefault('url', f'https://{domain}/page-{i}')
        page.setdefault('kind','own')
        page.setdefault('epochs',[0,1])
        page.setdefault('title', domain + ' ' + name)
        page.setdefault('facts',{})
        page.setdefault('lineage', {'registrant':domain,'canonical':None,'first_published_by':None})
        pages.append(page)
    value = dict(domain=domain, names=[name], pages=pages, research=research or {})
    corpus.append(value)
    return value

def case_domain(i):
    return 'reader-'+''.join(chr(97+(i//(26**k))%26) for k in [2,1,0])+'.test'

def gram(label, field, template, value, **kwargs):
    domain = case_domain(len(grammar)+100)
    name = domain.split('.')[0].replace('-', ' ')
    text = template.format(name=name,domain=domain)
    if isinstance(value,str): value=value.replace('$NAME$',name).replace('$DOMAIN$',domain)
    c = company(domain,[dict(text=text,**kwargs)])
    grammar.append((label,field,domain,value,c))

gram('ceo-two-words','ceo','{name} CEO: Dana Ruiz.','Dana Ruiz')
gram('ceo-three-words','ceo','{name} chief executive officer: Dana Maria Ruiz.','Dana Maria Ruiz')
gram('ceo-four-words','ceo','{name} CEO: Dana Maria Elena Ruiz.',None)
gram('ceo-unicode','ceo','{name} chief executive: Élodie Müller.','Élodie Müller')
gram('city-unicode','hq_city','{name} is headquartered in Zürich.','Zürich')
gram('city-hyphen','hq_city','{name} has its head office in Aix-en-Provence.', 'Aix')
gram('city-multiword','hq_city','{name} is based in New York.','New York')
gram('wrong-statement','hq_city','{name} opened a sales office in Porto.',None)
gram('negation','ceo','{name} reportedly appointed CEO Dana Ruiz.',None)
gram('negative-word-boundary','ceo','{name} CEO Dana Ruiz works with Notable.', 'Dana Ruiz')
gram('year-lower','founded_year','{name} was founded in 1800.',1800)
gram('year-upper','founded_year','{name} was incorporated in 2099.',2099)
gram('year-below','founded_year','{name} was established in 1799.',None)
gram('year-above','founded_year','{name} was founded in 2100.',None)
gram('year-conflict','founded_year','{name} was founded in 2014 and established in 2015.',None)
gram('year-repeat','founded_year','{name} was founded in 2014 and incorporated in 2014.',2014)
gram('amount-is-not-year','founded_year','{name} founded a business with $2014.',None)
gram('headcount-same-range','headcount_range','{name} employs 51-200 people.','51-200')
gram('headcount-cross-range','headcount_range','{name} employs 50-51 people.',None)
gram('headcount-zero','headcount_range','{name} employs 0 people.',None)
gram('headcount-decimal','headcount_range','{name} employs 12.5 people.',None)
gram('headcount-grouping','headcount_range','{name} workforce totals 1,200 people.','1001-5000')
gram('headcount-malformed-grouping','headcount_range','{name} employs 12,34 people.',None)
gram('headcount-amount','headcount_range','{name} invested $120 in employees.',None)
gram('funding-suffix','funding_total','{name} raised 12 million dollars.',12000000)
gram('funding-prefix','funding_total','{name} raised US$12.5 million.',12500000)
gram('funding-mn','funding_total','{name} funding is USD 12mn.',12000000)
gram('funding-whole-fraction','funding_total','{name} raised $0.001k.',1)
gram('funding-sub-dollar','funding_total','{name} raised $0.0001k.',None)
gram('funding-other-currency','funding_total','{name} raised EUR 12 million.',None)
gram('funding-conflict','funding_total','{name} raised $12M and $13M.',None)
gram('funding-equivalent','funding_total','{name} raised $12M and 12 million dollars.',12000000)
gram('company-name-boundary','ceo','x{name} CEO Dana Ruiz.',None)
gram('domain-names-company','ceo','{domain} CEO: Dana Ruiz.','Dana Ruiz')
gram('no-cross-sentence','ceo','{name} has news. Its CEO is Dana Ruiz.',None)
gram('header-not-evidence','ceo','No executive is named here.',None,facts={'ceo':'Dana Ruiz'})
gram('legal-domain','legal_name','{domain} registered as {domain}, Inc.','$DOMAIN$, Inc.')
gram('legal-suffix-case','legal_name','{name} legal name is {name}, inc.',None)
gram('legal-uppercase-expansion','legal_name','{name} legal entity is {name} AI, LLC.','$NAME$ AI, LLC')
gram('phrase-whitespace','hq_city','{name} is based   in   Zürich.','Zürich')
gram('quote-sentence','ceo','{name} CEO Dana Ruiz!" More news follows.','Dana Ruiz')

for n, suffix in enumerate(['Inc.','Corp.','LLC','LLP','L.P.','Ltd','Limited','Pty Ltd','plc','PLC','GmbH','AG','KG','SE','AS','A/S','ASA','AB','Oy','Oyj','B.V.','N.V.','S.A.','S.A.S.','S.L.','S.r.l.','S.p.A.','s.r.o.','a.s.','K.K.']):
    name=case_domain(len(grammar)+100).split('.')[0].replace('-',' ')
    gram('legal-suffix-'+str(n),'legal_name','{name} registered name is {name}, '+suffix,name+', '+suffix)
for n, phrase in enumerate(['in talks to','plans to','planning to','wants to','expects to','hopes to','aims to','seeking','could','would','might','reportedly','rumoured','former','formerly','will become','not']):
    gram('negator-'+str(n),'ceo','{name} '+phrase+' appoint CEO Dana Ruiz.',None)
for n,phrase in enumerate(['headquartered in','headquarters in','head office in','based in','registered office in','registered seat in']):
    gram('headquarters-phrase-'+str(n),'hq_city','{name} '+phrase+' Lisbon.','Lisbon')
for n,phrase in enumerate(['founded','founding','established','incorporated']):
    gram('founding-phrase-'+str(n),'founded_year','{name} '+phrase+' 2014.',2014)
for n,phrase in enumerate(['employs','employees','staff','people','headcount','workforce']):
    gram('headcount-phrase-'+str(n),'headcount_range','{name} '+phrase+' 120.','51-200')
for n,phrase in enumerate(['raised','funding','invested','investment']):
    gram('funding-phrase-'+str(n),'funding_total','{name} '+phrase+' $12M.',12000000)
for n,phrase in enumerate(['legal name','registered name','registered as','registered company','legal entity','name of record']):
    name=case_domain(len(grammar)+100).split('.')[0].replace('-',' ')
    gram('legal-phrase-'+str(n),'legal_name','{name} '+phrase+' {name}, Inc.',name+', Inc.')
for count,bucket in [(1,'1-10'),(10,'1-10'),(11,'11-50'),(50,'11-50'),(51,'51-200'),(200,'51-200'),(201,'201-500'),(500,'201-500'),(501,'501-1000'),(1000,'501-1000'),(1001,'1001-5000'),(5000,'1001-5000'),(5001,'5001-10000'),(10000,'5001-10000'),(10001,'10001+')]:
    gram('headcount-boundary-'+str(count),'headcount_range','{name} employs about '+str(count)+' people.',bucket)
for n,(amount,value) in enumerate([('$12M',12000000),('$12.5 million',12500000),('US$12 million',12000000),('USD 12 million',12000000),('$12m',12000000),('$12,000,000',12000000),('12,000,000 US dollars',12000000),('$2bn',2000000000),('$2 billion',2000000000),('$2 thousand',2000),('$12.34',12.34),('$12.000',12),('USD 1,20',None),('x$12M',None),('$12Mx',None)]):
    gram('amount-form-'+str(n),'funding_total','{name} raised '+amount+'.',value if type(value) is int else None)

full = company('reader-full.test',[
    dict(text='Reader Full registered name is Reader Full, Inc.\nReader Full is headquartered in Lisbon.\nReader Full CEO: Dana Ruiz.\nReader Full was founded in 2014.\nReader Full employs 120 people.\nReader Full has raised $12M.',epochs=[0]),
    dict(text='Reader Full registered name is Reader Full, Inc.\nReader Full is headquartered in Zürich.\nReader Full CEO: Élodie Müller.\nReader Full was founded in 2014.\nReader Full employs 200 people.\nReader Full has raised $13M.',epochs=[1])])
company('reader-blank.test',['No company facts are available.'])
company('reader-research.test',[dict(text='Reader Research CEO: Dana Ruiz.',searchable=False)],
        {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://reader-research.test/page-0',excerpt='Reader Research CEO: Dana Ruiz.')]}})
company('reader-bogus.test',['Reader Bogus opened an office in Porto.'],
        {'nimble':{'0':[dict(field='hq_city',value='Porto',url='https://reader-bogus.test/page-0',excerpt='Reader Bogus opened an office in Porto.')]}})
company('reader-long.test',['Unrelated background. '*20 + 'Reader Long CEO: Dana Ruiz.'])
company('reader-hidden.test', [dict(title='Reader Hidden general company profile '*10,text='Reader Hidden company profile and other background. '*20) for _ in range(11)] +
        [dict(title='Chief executive biography',text='Reader Hidden chief executive officer: Dana Ruiz.')])
budget_terms=['general company profile','legal name registered name registered as registered company legal entity name of record','headquartered in headquarters in head office in based in registered office in registered seat in','chief executive officer chief executive CEO','founded founding established incorporated','employs employees staff people headcount workforce','raised funding invested investment']
company('reader-budget.test',[dict(title='Reader Budget '+terms,text=('Reader Budget '+terms+' information without facts. ')*20) for terms in budget_terms for _ in range(10)])
company('reader-vanish.test',[dict(text='Reader Vanish company background. '*20+'Reader Vanish CEO: Dana Ruiz.',epochs=[0])])
verbatim_domain='reader-research-verbatim.test'
verbatim_claims=[
    ('legal_name','Reader Research Verbatim, LLC','Reader Research Verbatim legal name is Reader Research Verbatim, LLC.'),
    ('hq_city','Zürich','Reader Research Verbatim is based in Zürich.'),
    ('ceo','Élodie Müller','Reader Research Verbatim CEO: Élodie Müller.'),
    ('founded_year',2014,'Reader Research Verbatim was founded in 2014.'),
    ('headcount_range','51-200','Reader Research Verbatim employs 120 people.'),
    ('funding_total',12500000,'Reader Research Verbatim has raised $12.5 million.')]
company(verbatim_domain,[dict(text='\n'.join(excerpt for field,value,excerpt in verbatim_claims),searchable=False)],
        {'nimble':{'0':[dict(field=field,value=value,url='https://'+verbatim_domain+'/page-0',excerpt=excerpt) for field,value,excerpt in verbatim_claims]}})
header_domain='reader-research-header.test'
header_text='Facts: {"ceo":"Reader Research Header CEO: Dana Ruiz."}'
company(header_domain,[dict(text='Reader Research Header shares an ordinary company overview.',searchable=False,facts={'ceo':'Reader Research Header CEO: Dana Ruiz.'})],
        {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://'+header_domain+'/page-0',excerpt=header_text)]}})
prose_domain='reader-research-prose.test'
prose_excerpt='Profile: Reader Research Prose CEO: Dana Ruiz.'
company(prose_domain,[dict(text=prose_excerpt,searchable=False)],
        {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://'+prose_domain+'/page-0',excerpt=prose_excerpt)]}})
long_domain='reader-research-long.test'
long_excerpt='Reader Research Long CEO: Dana Ruiz'+(' with published company background'*30)+'.'
company(long_domain,[dict(text=long_excerpt,searchable=False)],
        {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://'+long_domain+'/page-0',excerpt=long_excerpt)]}})
span_cases=[]
for domain,text,searchable,expected in [
    ('reader-tail-span.test','context '*150+'Reader Tail Span CEO: Dana Ruiz.',False,'Dana Ruiz'),
    ('reader-middle-span.test','context '*100+'Reader Middle Span CEO: Dana Ruiz'+(' context'*100)+'.',False,'Dana Ruiz'),
    ('reader-search-span.test','Reader Search Span offers background '+('context '*100)+'Reader Search Span CEO: Dana Ruiz'+(' context'*100)+'.',True,'Dana Ruiz'),
    ('reader-distant-span.test','Reader Distant Span '+('context '*100)+'CEO: Dana Ruiz.',False,None)]:
    company(domain,[dict(text=text,searchable=searchable)],{} if searchable else
            {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://'+domain+'/page-0',excerpt=text)]}})
    span_cases.append((domain,text,expected))

edge_cases=[]
def edge_company(domain,field,value,sentence,claim=None):
    claim=value if value is not None else (claim if claim is not None else {'ceo':'Dana Ruiz','founded_year':2014}[field])
    company(domain,[dict(text=sentence,searchable=False)],{'nimble':{'0':[dict(field=field,value=claim,url='https://'+domain+'/page-0',excerpt=sentence)]}})
    edge_cases.append((domain,field,value,sentence))
edge_company('reader-short-whole.test','ceo','Dana Ruiz','Reader Short Whole CEO: Dana Ruiz.')
edge_company('reader-short-negation.test','ceo',None,'Reader Short Negation CEO: Dana Ruiz, not Sam Ortiz.')
edge_company('reader-short-conflict.test','founded_year',None,'Reader Short Conflict was founded in 2014 and incorporated in 2015.')
edge_company('reader-amount-edge.test','funding_total',12000000,'background '*80+'Reader Amount Edge raised $12 million.')
edge_company('reader-number-edge.test','headcount_range','1001-5000','background '*80+'Reader Number Edge employs 1,200 people.')
edge_company('reader-year-amount.test','founded_year',None,'background '*80+'Reader Year Amount was founded using $2014.')
edge_company('reader-name-run.test','ceo',None,'background '*80+'Reader Name Run CEO: Dana Maria Elena Ruiz.',claim='Dana Maria Elena')
edge_company('reader-city-run.test','hq_city','San Luis Obispo','background '*80+'Reader City Run is based in San Luis Obispo.')
edge_company('reader-unicode-run.test','ceo','Élodie Maria Müller','background '*80+'Reader Unicode Run CEO: Élodie Maria Müller.')
edge_company('reader-suffix-amount.test','funding_total',12000000,'background '*80+'Reader Suffix Amount has raised 12 million dollars.')
edge_company('reader-fraction-amount.test','funding_total',12500000,'background '*80+'Reader Fraction Amount raised $12.5 million.')
year_domain='reader-year-span.test'
year_ending=' and Reader Year Span was founded in 1952 by two sisters.'
year_start='Reader Year Span provides background '
year_text=year_start+('context '*100)[:799-len(year_start)-len(year_ending)]+year_ending
assert len(year_text)==799
company(year_domain,[dict(text=year_text,searchable=True)])
performance_cases=[]
for domain,text,value in [
    ('reader-very-long.test','context '*25000+'Reader Very Long CEO: Dana Ruiz'+(' context'*25000)+'.','Dana Ruiz'),
    ('reader-dense-negative.test',('might Reader Dense Negative might CEO might Dana Ruiz might and '*100)+'background.',None)]:
    company(domain,[dict(text=text,searchable=False)],{'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://'+domain+'/page-0',excerpt=text)]}})
    performance_cases.append((domain,text,value))

# Additional Stage 2 evidence corpora; none is copied from product or peer tests.
rank_domain='amber-rank.test'
rank_pages=[
    dict(url='https://amber-rank.test/z-own',kind='own',published_at='2020-01-01T00:00:00+00:00',text='Amber Rank CEO: Ava Stone.'),
    dict(url='https://filings-source.test/amber-rank/a',kind='filing',published_at='2025-04-01T01:00:00+01:00',text='Amber Rank CEO: Sam Ortiz.'),
    dict(url='https://amber-rank.test/a-own',kind='own',published_at='2025-04-01T00:00:00+00:00',text='Amber Rank CEO: Lina Park.\nAmber Rank chief executive: Lina Park.\nAmber Rank CEO: Zara Lane.\nAmber Rank CEO: Ava Stone.'),
    dict(url='https://wire-rank.test/latest',kind='news',published_at='2090-01-01T00:00:00+00:00',text='Amber Rank CEO: Reza Noor.'),
    dict(url='https://archive-rank.test/profile',kind='aggregator',published_at='2099-01-01T00:00:00+00:00',text='Amber Rank CEO: Dana Ruiz.'),
    dict(url='https://amber-rank.test/undated',kind='own',text='Amber Rank CEO: Petra Cole.')]
company(rank_domain,rank_pages)
metadata_domain='cedar-metadata.test'
metadata_pages=[
    dict(url='https://www.cedar-metadata.test/case',kind=None,published_at='invalid',text='Cedar Metadata CEO: Dana Ruiz.'),
    dict(url='https://sub.cedar-metadata.test/profile',kind='OWN',published_at='2026-01-01T03:00:00+03:00',text='Cedar Metadata CEO: Lina Park.'),
    dict(url='https://meta-news.test/cedar',kind='filing',published_at='2010-01-01T00:00:00+00:00',text='Cedar Metadata CEO: Sam Ortiz.'),
    dict(url='https://cedar-metadata.test/future',kind='bogus',published_at='2090-01-01T00:00:00+00:00',text='Cedar Metadata CEO: Cleo Ward.')]
company(metadata_domain,metadata_pages)
money_domain='silver-value.test'
company(money_domain,[
    dict(url='https://silver-value.test/a',kind='own',published_at='2025-01-01T00:00:00+00:00',text='Silver Value has raised $9.\nSilver Value raised $10.\nSilver Value funding is $0M.'),
    dict(url='https://wire-value.test/zero',kind='news',published_at='2090-01-01T00:00:00+00:00',text='Silver Value funding is $0.')])
claim_domain='orion-claim.test'
company(claim_domain,[dict(kind='filing',published_at='2025-01-01T00:00:00+00:00',searchable=False,text='Orion Claim opened a sales office in Porto.\nOrion Claim was founded in 2014.\nOrion Claim CEO: Sam Ortiz.')],
        {'nimble':{'0':[dict(field='ceo',value='Dana Ruiz',url='https://orion-claim.test/page-0',excerpt='Orion Claim opened a sales office in Porto.')]}})
complete_domain='maple-complete.test'
company(complete_domain,[
    dict(url='https://maple-complete.test/about',kind='own',published_at='2020-01-01T00:00:00+00:00',text='Maple Complete legal name is Maple Complete, LLC.\nMaple Complete is based in Lisbon.\nMaple Complete CEO: Dana Ruiz.\nMaple Complete was founded in 2014.\nMaple Complete employs 120 people.\nMaple Complete raised $12M.'),
    dict(url='https://filing-complete.test/record',kind='filing',published_at='2027-01-01T00:00:00+00:00',text='Maple Complete CEO: Bob Stone.')])
visible_domain='visible-dossier.test'
company(visible_domain,[dict(text='Visible Dossier CEO: Dana Ruiz.\nVisible Dossier CEO: Sam Ortiz.')],
        {'nimble':{'0':[dict(field='ceo',value='Cara Jones',url='https://visible-dossier.test/page-0',excerpt='Visible Dossier CEO: Cara Jones.')]}})
legacy_domain='legacy-amber.test'
company(legacy_domain,[
    dict(url='https://legacy-amber.test/about',kind='own',published_at='2020-01-01T00:00:00+00:00',text='Legacy Amber legal name is Legacy Amber, LLC and CEO: Zara Lane.\nLegacy Amber is registered as Legacy Amber, LLC and its chief executive is Zara Lane.'),
    dict(url='https://news-legacy.test/b',kind='news',published_at='2025-01-01T00:00:00+00:00',text='Legacy Amber CEO: Ava Stone.'),
    dict(url='https://data-legacy.test/c',kind='aggregator',published_at='2026-01-01T00:00:00+00:00',text='Legacy Amber CEO: Ava Stone.'),
    dict(url='https://wire-legacy.test/d',kind='news',published_at='2024-01-01T00:00:00+00:00',text='Legacy Amber CEO: Ava Stone.')])

@case('runtime-health-and-initial-clock')
def test_runtime():
    status(req('/health',auth=False),200)
    assert not log()
    fresh=status(req('/auth/signup','POST',{'email':'initial@reader.test','password':'initial-password','display_name':'Initial'},auth=False),201)
    global_token(fresh['token'])
    status(create('reader-blank.test'),202);first=ready('reader-blank.test')
    time.sleep(.2)
    status(create('reader-full.test'),202);later=ready('reader-full.test')
    assert datetime.datetime.fromisoformat(later['researched_at'])>datetime.datetime.fromisoformat(first['researched_at'])
    delta=datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(later['researched_at'])
    assert abs(delta.total_seconds())<10
    # Before reset no provider calls are needed to test clock validation.
    past = '2000-01-01T00:00:00+00:00'
    status(req('/_test/clock','POST',{'now':past},auth=False),422,'validation_failed')
    future = '2090-01-01T00:00:00+00:00'
    status(req('/_test/clock','POST',{'now':future},auth=False),204)
    status(req('/_test/clock','POST',{'now':future},auth=False),204)
    for domain in ['reader-long.test','reader-bogus.test']:
        status(create(domain),202);d=ready(domain)
        assert datetime.datetime.fromisoformat(d['researched_at'])==datetime.datetime.fromisoformat(future)
        time.sleep(.1)

@case('authentication-and-errors')
def test_auth():
    reset()
    for path,method,body in [('/dossiers','GET',None),('/dossiers','POST',{}),('/dossiers/reader-full.test','GET',None),('/dossiers/reader-full.test/refresh','POST',None)]:
        status(req(path,method,body,auth=False),401,'unauthenticated')
        status(req(path,method,body,extra={'Authorization':'Bearer missing-token'}),401,'unauthenticated')
    data = status(req('/auth/signup','POST',{'email':'new@reader.test','password':'eight-or-more','display_name':'New','unknown':[]},auth=False),201)
    assert len(data['user_id']) <= 64 and data['display_name'] == 'New'
    for _ in range(2):
        new = status(req('/auth/login','POST',{'email':'new@reader.test','password':'eight-or-more'},auth=False),200)
        assert new['user_id'] == data['user_id']
        status(req('/dossiers',extra={'Authorization':'Bearer '+new['token']}),200)
    status(req('/dossiers',extra={'Authorization':'Bearer '+data['token']}),200)
    status(req('/auth/signup','POST',{'email':'new@reader.test','password':'eight-or-more','display_name':'New'},auth=False),409,'email_taken')
    for override in [{'password':'1234567'}, {'email':'invalid'}, {'email':'@invalid'}, {'display_name':''},{'display_name':'x'*101}]:
        body = dict(email='valid@reader.test',password='12345678',display_name='X'); body.update(override)
        status(req('/auth/signup','POST',body,auth=False),422,'validation_failed')
    for body in [{'email':'absent@reader.test','password':'reader-pass-a'},{'email':'a@reader.test','password':'x'}]:
        status(req('/auth/login','POST',body,auth=False),401,'unauthenticated')
    for body in [{'email':42,'password':'reader-pass-a'},{'email':'a@reader.test','password':None}]:
        status(req('/auth/login','POST',body,auth=False),400,'malformed_request')
    status(req('/auth/login','POST',auth=False,raw=b'{'),400,'malformed_request')
    assert not log()

@case('domain-and-input-boundaries')
def test_domains():
    reset()
    for d in ['localhost','https://valid.test','valid.test/path','a..test','-bad.test','bad-.test','a'*64+'.test','www..','valid.test..','ä.test','a_b.test']:
        status(create(d),422,'validation_failed')
        if '/' in d: continue
        result=req('/dossiers/'+urllib.parse.quote(d,safe=''))
        assert result[0]==422 and result[1]['error']['code']=='validation_failed', ('invalid path domain',d,result)
        result=req('/dossiers/'+urllib.parse.quote(d,safe='')+'/refresh','POST',key=uuid.uuid4().hex)
        assert result[0]==422 and result[1]['error']['code']=='validation_failed', ('invalid refresh path domain',d,result)
    for body in [{},{'domain':None},{'domain':1}]:
        status(req('/dossiers','POST',body,key=uuid.uuid4().hex),422 if not body else 400,'validation_failed' if not body else 'malformed_request')
    for key in [None,'']:
        status(req('/dossiers','POST',{'domain':'reader-full.test'},key=key),400,'missing_idempotency_key')
    status(create('reader-full.test','k'*256),422,'validation_failed')
    d = status(create('  WWW.READER-FULL.TEST.  ','k'*255),202)
    assert d['domain'] == 'reader-full.test'
    finished = ready('reader-full.test')
    assert get('READER-FULL.TEST.')['dossier_id'] == d['dossier_id']
    before = len(log())
    again = status(create('reader-full.test','k'),200)
    assert set(again) == {'dossier_id','domain','state'} and again['dossier_id'] == d['dossier_id']
    assert len(log()) == before
    # A normalized 253-character host with four labels is valid.
    maximum = '.'.join(['a'*63,'b'*63,'c'*63,'d'*61])
    status(create(maximum),202); ready(maximum)
    status(create(maximum+'e'),422,'validation_failed')
    provenance(finished)

@case('encoded-path-domain-validation')
def test_encoded_paths():
    reset()
    failures=[]
    for domain in ['https://valid.test','valid.test/path']:
        encoded=urllib.parse.quote(domain,safe='')
        for method,path in [('GET','/dossiers/'+encoded),('POST','/dossiers/'+encoded+'/refresh')]:
            result=req(path,method,key='encoded-path-key')
            if result[0]!=422 or result[1]['error']['code']!='validation_failed':
                failures.append((method,path,result))
    assert not failures, failures

@case('idempotency-precedence-and-replay')
def test_idempotency():
    reset()
    first = status(req('/dossiers','POST',{'domain':'reader-full.test','x':1},key='same'),202)
    status(req('/dossiers','POST',{'domain':'bad domain'},key='same'),409,'idempotency_key_reuse')
    for body in [{},{'domain':None},{'domain':42}]:
        status(req('/dossiers','POST',body,key='same'),409,'idempotency_key_reuse')
    status(req('/dossiers','POST',key='same',raw=b'{'),400,'malformed_request')
    ready('reader-full.test')
    before = len(log())
    repeated = status(req('/dossiers','POST',{'x':{'new':[1,2]},'domain':'reader-full.test'},key='same'),200)
    assert repeated == first
    assert len(log()) == before
    status(req('/dossiers','POST',{},key='failed'),422,'validation_failed')
    status(create('reader-blank.test','failed'),202); ready('reader-blank.test')
    # Same key is independent on refresh and across raw paths; all bodies ignored.
    refreshed = status(req('/dossiers/reader-full.test/refresh','POST',key='same',raw=b'{bad'),202)
    assert status(req('/dossiers/reader-full.test/refresh','POST',key='same',raw=b'null'),200) == refreshed
    ready('reader-full.test')
    status(req('/dossiers/READER-FULL.TEST/refresh','POST',key='same'),202); ready('reader-full.test')
    other = status(req('/auth/login','POST',{'email':'b@reader.test','password':'reader-pass-b'},auth=False),200)['token']
    status(req('/dossiers','POST',{'domain':'reader-blank.test'},key='same',extra={'Authorization':'Bearer '+other}),200)
    status(req('/dossiers/reader-blank.test',extra={'Authorization':'Bearer '+other}),200)

@case('concurrency-single-dossier-and-replay')
def test_concurrency():
    reset()
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':2}),204)
    with futures.ThreadPoolExecutor(max_workers=50) as pool:
        batch = list(pool.map(lambda _:create('reader-full.test','race'),range(50)))
    assert sum(s == 202 for s,b in batch) == 1, [s for s,b in batch]
    assert all(s in [200,202] and b == batch[0][1] for s,b in batch), batch
    before = log()
    with futures.ThreadPoolExecutor(max_workers=20) as pool:
        refreshes = list(pool.map(lambda i:req('/dossiers/reader-full.test/refresh','POST',key='r'+str(i)),range(20)))
    assert all(s == 202 for s,b in refreshes)
    d = ready('reader-full.test')
    exact = [c for c in log() if c['method']=='search' and c['query']=='reader-full.test' and c['status']==200]
    assert len(exact) == 1, exact
    assert len(status(req('/dossiers'),200)['dossiers']) == 1
    provenance(d)
    status(admin('reset',{'epoch':0}),204)
    reset()
    with futures.ThreadPoolExecutor(max_workers=30) as pool:
        values=list(pool.map(lambda i:create(['reader-full.test','WWW.READER-FULL.TEST.'][i%2],str(i)),range(30)))
    assert len({b['dossier_id'] for s,b in values})==1
    assert sum(s==202 for s,b in values)==1
    ready('reader-full.test')

@case('clock-and-refresh-state')
def test_clock_refresh():
    reset()
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':.6}),204)
    status(create('reader-full.test'),202)
    building = get('reader-full.test')
    assert building['state']=='building' and building['researched_at'] is None
    for field in FIELDS: known(building,field,None)
    status(req('/_test/clock','POST',{'now':LATER},auth=False),204)
    d = ready('reader-full.test')
    assert d['researched_at']==NOW
    status(req('/_test/clock','POST',{'now':'2026-03-02T09:30:00+00:00'},auth=False),204)
    status(req('/_test/clock','POST',{'now':NOW},auth=False),422,'validation_failed')
    status(req('/_test/clock','POST',{'now':'2026-03-02T10:00:00'},auth=False),422,'validation_failed')
    status(req('/_test/clock','POST',{'now':1},auth=False),400,'malformed_request')
    status(admin('epoch',{'epoch':1}),204)
    before = d['spent_units']
    status(req('/dossiers/reader-full.test/refresh','POST',key='refresh'),202)
    active = get('reader-full.test')
    assert active['state']=='building' and active['fields']==d['fields'] and active['researched_at']==NOW
    refreshed = ready('reader-full.test')
    assert refreshed['researched_at']=='2026-03-02T09:30:00+00:00'
    assert refreshed['spent_units']>before
    known(refreshed,'hq_city','Zürich'); known(refreshed,'funding_total',13000000)
    provenance(refreshed)
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'error'}),204)
    status(req('/dossiers/reader-full.test/refresh','POST',key='fail'),202)
    failed = ready('reader-full.test')
    assert failed['state']=='failed' and failed['fields']==refreshed['fields'] and failed['researched_at']==refreshed['researched_at']
    assert failed['spent_units']==refreshed['spent_units']

@case('research-completeness-and-provenance')
def test_evidence():
    reset()
    for domain,field,value in [('reader-research.test','ceo','Dana Ruiz'),('reader-bogus.test','hq_city',None),('reader-long.test','ceo','Dana Ruiz'),('reader-hidden.test','ceo','Dana Ruiz')]:
        begin=time.monotonic(); status(create(domain),202); d=ready(domain)
        assert time.monotonic()-begin<10
        known(d,field,value)
        provenance(d)
        assert d['state']=='ready'
        assert d['spent_units'] <= 80
        calls=[c for c in log() if c.get('query') and domain in c['query']]
        assert len([c for c in calls if c['method']=='search' and c['query']==domain and c['status']==200])==1
    for c in log():
        if c['method']=='research' and c['status']==200:
            assert set(c['fields'])==set(FIELDS)

@case('list-pagination-and-query-validation')
def test_list():
    reset()
    for domain in ['reader-full.test','reader-blank.test','reader-long.test']:
        status(create(domain),202); ready(domain)
    all_items=status(req('/dossiers?unknown=x'),200)
    assert [d['domain'] for d in all_items['dossiers']]==['reader-blank.test','reader-full.test','reader-long.test']
    assert all_items['has_more'] is False
    for item in all_items['dossiers']:
        d=get(item['domain'])
        assert item==dict(dossier_id=d['dossier_id'],domain=d['domain'],state=d['state'],legal_name=d['fields']['legal_name']['value'],researched_at=d['researched_at'],spent_units=d['spent_units'])
    one=status(req('/dossiers?q=FULL&limit=1&offset=0'),200)
    assert [d['domain'] for d in one['dossiers']]==['reader-full.test'] and one['has_more'] is False
    assert len(status(req('/dossiers?q=Inc.'),200)['dossiers'])==1
    assert status(req('/dossiers?q='),200)==all_items
    assert status(req('/dossiers?limit=1&offset=0'),200)['has_more'] is True
    assert status(req('/dossiers?limit=1&offset=2'),200)['has_more'] is False
    assert status(req('/dossiers?limit=1&offset=99'),200)=={'dossiers':[],'has_more':False}
    for name,values in [('limit',['','0','201','-1','1e9','4.0','+4',' 4','abc']),('offset',['','-1','1e9','4.0','+4',' 4','abc'])]:
        for value in values:
            status(req('/dossiers?'+name+'='+urllib.parse.quote(value,safe='')),422,'validation_failed')
    for query in ['limit=1','limit=200','offset=0','offset=9999999999999999999999999999']:
        status(req('/dossiers?'+query),200)
    before=len(log())
    with futures.ThreadPoolExecutor(max_workers=50) as pool:
        list(pool.map(lambda i:req('/dossiers' if i%2 else '/dossiers/reader-full.test'),range(50)))
    status(req('/health',auth=False),200)
    status(req('/_test/export',auth=False),200)
    assert len(log())==before

@case('research-citations-verbatim-prose-and-reuse')
def test_research_verbatim():
    reset()
    status(create(verbatim_domain),202)
    d=ready(verbatim_domain)
    for field,value,excerpt in verbatim_claims:
        known(d,field,value)
        assert all(c['excerpt']==excerpt and c['provider']=='nimble' for c in d['fields'][field]['citations'])
    provenance(d)
    calls=log()
    extracts=[c for c in calls if c['method']=='extract' and 'https://'+verbatim_domain+'/page-0' in c['urls']]
    assert len(extracts)==1 and extracts[0]['cost']==3
    assert d['spent_units']==sum(c['cost'] for c in calls) and d['spent_units']<=80

@case('research-header-citation-is-not-prose')
def test_research_header():
    reset()
    status(create(header_domain),202)
    d=ready(header_domain)
    known(d,'ceo',None)
    provenance(d)

@case('research-header-shaped-prose-is-evidence')
def test_research_prose():
    reset()
    status(create(prose_domain),202)
    d=ready(prose_domain)
    try:
        known(d,'ceo','Dana Ruiz')
    except AssertionError as exc:
        raise AssertionError({'domain':prose_domain,'state':d['state'],'spent_units':d['spent_units'],
                              'ceo':d['fields']['ceo'],
                              'research_served':[p for c in log() if c['method']=='research' for p in c.get('served',[])]}) from exc
    provenance(d)

@case('atomic-reset-and-invalid-reset')
def test_reset():
    reset()
    old=token
    status(create('reader-full.test','old-key'),202); d=ready('reader-full.test')
    bad=json.loads(json.dumps(FIXTURE)); bad['users'].append(dict(bad['users'][0]))
    status(req('/_test/reset','POST',bad,auth=False),422,'validation_failed')
    assert get('reader-full.test')==d
    status(req('/_test/reset','POST',{'users':[]},auth=False),422,'validation_failed')
    assert get('reader-full.test')==d
    status(req('/_test/reset','POST',{'now':NOW,'users':'bad'},auth=False),400,'malformed_request')
    reset()
    status(req('/dossiers',extra={'Authorization':'Bearer '+old}),401,'unauthenticated')
    assert status(req('/dossiers'),200)['dossiers']==[]
    status(create('reader-full.test','old-key'),202); ready('reader-full.test')
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':1}),204)
    status(req('/dossiers/reader-full.test/refresh','POST',key='old-build'),202)
    reset()
    time.sleep(2)
    assert status(req('/dossiers'),200)['dossiers']==[]

@case('research-excerpt-length-limit')
def test_research_length():
    reset()
    status(create(long_domain),202)
    d=ready(long_domain)
    known(d,'ceo','Dana Ruiz')
    for field in FIELDS:
        for citation in d['fields'][field]['citations']:
            assert 1<=len(citation['excerpt'])<=500, ('research citation length',len(citation['excerpt']),citation['url'],'field',field,'state',d['state'])
    for citation in d['fields']['ceo']['citations']:
        assert 'reader research long' in citation['excerpt'].lower() and 'ceo' in citation['excerpt'].lower() and 'Dana Ruiz' in citation['excerpt'], citation
        assert citation['excerpt'] in long_excerpt,citation
    provenance(d)

@case('fixture-id-length-boundary')
def test_fixture_ids():
    reset()
    fixture=json.loads(json.dumps(FIXTURE));fixture['users'][0]['id']='u'*64
    status(req('/_test/reset','POST',fixture,auth=False),204)
    user=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200)
    assert user['user_id']=='u'*64
    fixture['users'][0]['id']='u'*65
    response=req('/_test/reset','POST',fixture,auth=False)
    actual_length=None
    if response[0]==204:
        created=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200)
        actual_length=len(created['user_id'])
    assert response[0]==422 and response[1]['error']['code']=='validation_failed', ('overlong fixture id accepted',response,'returned user_id length',actual_length)
    user=status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False),200)
    assert user['user_id']=='u'*64

for span_domain,span_text,span_expected in span_cases:
    @case('bounded-supporting-span-'+span_domain)
    def test_span(domain=span_domain,text=span_text,expected=span_expected):
        reset()
        status(create(domain),202)
        d=ready(domain)
        try:
            known(d,'ceo',expected)
        except AssertionError as exc:
            raise AssertionError({'domain':domain,'expected_ceo':expected,'state':d['state'],'spent_units':d['spent_units'],'ceo':d['fields']['ceo']}) from exc
        name=domain.split('.')[0].replace('-',' ')
        for citation in d['fields']['ceo']['citations']:
            excerpt=citation['excerpt']
            assert 1<=len(excerpt)<=500 and excerpt in text,citation
            assert name in excerpt.lower() and 'ceo' in excerpt.lower() and 'Dana Ruiz' in excerpt,citation
            assert safe_span(text,excerpt),('unsafe citation edge',citation)
        provenance(d)

@case('late-founded-year-799-character-sentence')
def test_late_year():
    reset()
    status(create(year_domain),202)
    d=ready(year_domain)
    known(d,'founded_year',1952)
    for citation in d['fields']['founded_year']['citations']:
        assert safe_span(year_text,citation['excerpt']) and len(citation['excerpt'])<=500,citation
    provenance(d)

for edge_domain,edge_field,edge_value,edge_sentence in edge_cases:
    @case('r1-7-edge-'+edge_domain)
    def test_edge(domain=edge_domain,field=edge_field,value=edge_value,sentence=edge_sentence):
        reset()
        status(create(domain),202)
        d=ready(domain)
        known(d,field,value)
        for citation in d['fields'][field]['citations']:
            excerpt=citation['excerpt']
            assert 1<=len(excerpt)<=500 and safe_span(sentence,excerpt),('unsafe citation edge',citation)
            if len(sentence)<=500:assert excerpt==sentence,('short sentence must be cited whole',citation)
        provenance(d)

for perf_domain,perf_sentence,perf_value in performance_cases:
    @case('long-sentence-response-time-'+perf_domain)
    def test_performance(domain=perf_domain,sentence=perf_sentence,value=perf_value):
        reset()
        t=time.monotonic()
        status(create(domain),202)
        with futures.ThreadPoolExecutor(max_workers=50) as pool:
            responses=list(pool.map(lambda _:req('/health',auth=False),range(50)))
        assert all(s==200 for s,b in responses)
        d=ready(domain,seconds=max(.1,10-(time.monotonic()-t)))
        elapsed=time.monotonic()-t
        assert elapsed<10,('long sentence build time',len(sentence),elapsed)
        known(d,'ceo',value)
        for citation in d['fields']['ceo']['citations']:
            assert safe_span(sentence,citation['excerpt']) and len(citation['excerpt'])<=500,citation
        provenance(d)

@case('export-import-cross-process-and-retries')
def test_transfer():
    reset()
    original_token=token
    first=status(create('reader-full.test','persist-key'),202); source=ready('reader-full.test')
    status(req('/dossiers/reader-blank.test/refresh','POST',key='failed-key'),404,'not_found')
    exported=status(req('/_test/export',auth=False),200)
    assert exported['track']=='dossier' and exported['format_version']==1 and type(exported['format_version']) is int and isinstance(exported['state'],dict)
    reset(at=second)
    destination_token=token
    status(req('/_test/clock','POST',{'now':LATER},auth=False,at=second),204)
    before=len(log())
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    assert len(log())==before
    status(req('/dossiers',at=second,extra={'Authorization':'Bearer '+destination_token}),401,'unauthenticated')
    global_token(original_token)
    assert get('reader-full.test',second)==source
    assert status(req('/dossiers','POST',{'domain':'reader-full.test'},key='persist-key',at=second),200)==first
    status(req('/auth/login','POST',{'email':'a@reader.test','password':'reader-pass-a'},auth=False,at=second),200)
    status(req('/dossiers','POST',{'domain':'reader-blank.test'},key='failed-key',at=second),202)
    destination=ready('reader-blank.test',second)
    assert datetime.datetime.fromisoformat(destination['researched_at'])==datetime.datetime.fromisoformat(LATER)
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    status(req('/dossiers/reader-blank.test',at=second),404,'not_found')
    assert get('reader-full.test',second)==source
    for bad in [{},{'track':'wrong','format_version':1,'state':{}},{'track':'dossier','format_version':2,'state':{}},{'track':'dossier','format_version':1,'state':{}},[],None]:
        status(req('/_test/import','POST',bad,auth=False,at=second,raw=b'null' if bad is None else None),422,'validation_failed')
        assert get('reader-full.test',second)==source
    status(req('/_test/import','POST',auth=False,at=second,raw=b'{'),400,'malformed_request')
    # Import replacement while destination build runs must suppress its completion.
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':1}),204)
    status(create('reader-long.test',at=second),202)
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    time.sleep(2)
    status(req('/dossiers/reader-long.test',at=second),404,'not_found')
    # A stop/restart of the source may lose source state; the export remains portable.
    cmd('docker','stop',service_name,timeout=30)
    cmd('docker','start',service_name,timeout=30)
    wait(base)
    status(req('/_test/import','POST',exported,auth=False,at=second),204)
    assert get('reader-full.test',second)==source
    status(req('/_test/reset','POST',FIXTURE,auth=False,at=second),204)
    status(req('/dossiers',at=second,extra={'Authorization':'Bearer '+original_token}),401,'unauthenticated')

def global_token(value):
    global token
    token=value

@case('mid-build-export-snapshot')
def test_midbuild():
    reset()
    original=status(create('reader-full.test','first'),202); previous=ready('reader-full.test')
    status(admin('epoch',{'epoch':1}),204)
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'delay','seconds':1}),204)
    refresh=status(req('/dossiers/reader-full.test/refresh','POST',key='middle'),202)
    time.sleep(.15)
    export=status(req('/_test/export',auth=False),200)
    status(req('/_test/import','POST',export,auth=False,at=second),204)
    assert get('reader-full.test',second)==previous
    assert status(req('/dossiers/reader-full.test/refresh','POST',key='middle',at=second),200)==refresh
    ready('reader-full.test')
    status(create('reader-blank.test','initial-mid'),202)
    first_export=status(req('/_test/export',auth=False),200)
    status(req('/_test/import','POST',first_export,auth=False,at=second),204)
    imported=get('reader-blank.test',second)
    assert imported['state']=='failed' and imported['researched_at'] is None and imported['spent_units']==0
    for f in FIELDS: known(imported,f,None)
    ready('reader-blank.test')

@case('provider-errors-budget-and-call-accounting')
def test_cost():
    reset()
    status(admin('faults',{'provider':'nimble','methods':['search'],'mode':'throttle'}),204)
    status(create('reader-full.test'),202); d=ready('reader-full.test',seconds=15)
    calls=log()
    assert d['state']=='ready'
    assert len([c for c in calls if c['method']=='search' and c['query']=='reader-full.test' and c['status']==200])==1
    assert d['spent_units']==sum(c['cost'] for c in calls), (d['spent_units'],sum(c['cost'] for c in calls))
    assert d['spent_units']<=80
    status(admin('reset',{'epoch':0}),204)
    reset()
    status(admin('faults',{'provider':'nimble','methods':['search','extract','research'],'mode':'error'}),204)
    status(create('reader-full.test'),202); d=ready('reader-full.test')
    assert d['state']=='failed' and d['researched_at'] is None and d['spent_units']==0
    assert all(c['status']>=400 and c['cost']==0 for c in log())
    for f in FIELDS: known(d,f,None)

@case('budget-pressure-reserves-before-calls')
def test_budget():
    reset()
    status(create('reader-budget.test'),202)
    d=ready('reader-budget.test')
    calls=log()
    assert d['state']=='ready' and d['spent_units']==sum(c['cost'] for c in calls)
    assert d['spent_units']<=80
    for f in FIELDS: known(d,f,None)
    total=0
    for c in calls:
        total+=c['cost']
        assert total<=80

@case('empty-extract-and-connection-loss-accounting')
def test_transport():
    reset()
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'delay','seconds':1}),204)
    status(create('reader-vanish.test'),202)
    deadline=time.monotonic()+4
    while time.monotonic()<deadline:
        if any(c['method']=='search' and c['status']==200 for c in log()):break
        time.sleep(.01)
    status(admin('epoch',{'epoch':1}),204)
    d=ready('reader-vanish.test')
    calls=log()
    missing=[c for c in calls if c['method']=='extract' and not c['served']]
    assert missing, calls
    assert all(c['cost']==3*len(c['urls']) for c in missing)
    assert d['spent_units']==sum(c['cost'] for c in calls)
    reset()
    cmd('docker','stop',PREFIX+'-web',timeout=30)
    try:
        status(create('reader-full.test'),202)
        failed=ready('reader-full.test',seconds=15)
        assert failed['state']=='failed' and 27<=failed['spent_units']<=80, failed
    finally:
        cmd('docker','start',PREFIX+'-web',timeout=30)
        wait(mock,'/_mock/health')

for label,field,domain,value,c in grammar:
    @case('grammar-'+label)
    def test_one(field=field,domain=domain,value=value):
        reset()
        status(create(domain),202)
        d=ready(domain)
        known(d,field,value)
        provenance(d)
        calls=log()
        assert d['spent_units']==sum(x['cost'] for x in calls) and d['spent_units']<=80
        assert len([x for x in calls if x['method']=='search' and x['query']==domain and x['status']==200])==1

@case('stage2-complete-candidates-and-ranking')
def test_stage2_ranking():
    reset();status(create(rank_domain),202);d=ready(rank_domain)
    known(d,'ceo','Ava Stone');provenance(d)
    f=d['fields']['ceo']
    expected={(p['url'],value) for p,values in zip(rank_pages,[['Ava Stone'],['Sam Ortiz'],['Lina Park','Zara Lane','Ava Stone'],['Reza Noor'],['Dana Ruiz'],['Petra Cole']]) for value in values}
    assert {(c['url'],c['value']) for c in f['candidates']}==expected,f
    assert len(f['candidates'])==8 and f['status']=='contested',f
    assert [c['value'] for c in f['candidates'][:3]]==['Ava Stone','Lina Park','Zara Lane'],f
    assert all(c['kind'] is not None for c in f['candidates'])
    assert [c['url'] for c in f['citations']]==['https://amber-rank.test/a-own','https://amber-rank.test/z-own']

@case('stage2-kind-fallback-and-publication')
def test_stage2_metadata():
    reset();status(create(metadata_domain),202);d=ready(metadata_domain)
    known(d,'ceo','Cleo Ward');provenance(d)
    by_url={c['url']:c for c in d['fields']['ceo']['candidates']}
    assert set(by_url)=={p['url'] for p in metadata_pages},by_url
    for p,kind in zip(metadata_pages,['own','aggregator','filing','own']):
        assert by_url[p['url']]['kind']==kind,by_url[p['url']]
    assert by_url[metadata_pages[0]['url']]['published_at'] is None
    assert instant(by_url[metadata_pages[1]['url']]['published_at'])==instant(metadata_pages[1]['published_at'])

@case('stage2-integer-tie-and-zero-value')
def test_stage2_zero():
    reset();status(create(money_domain),202);d=ready(money_domain)
    known(d,'funding_total',0);provenance(d)
    f=d['fields']['funding_total']
    assert [c['value'] for c in f['candidates']]==[0,9,10,0],f
    assert f['status']=='contested' and len(f['citations'])==2

@case('stage2-unsupported-research-cited-page-is-evidence')
def test_stage2_claim_page():
    reset();status(create(claim_domain),202);d=ready(claim_domain)
    known(d,'ceo','Sam Ortiz');known(d,'founded_year',2014);known(d,'hq_city',None)
    provenance(d)
    assert [c['value'] for c in d['fields']['ceo']['candidates']]==['Sam Ortiz']

@case('stage2-gather-after-all-fields-have-values')
def test_stage2_gather_all():
    reset();status(create(complete_domain),202);d=ready(complete_domain)
    known(d,'ceo','Bob Stone');provenance(d)
    assert all(d['fields'][field]['value'] is not None for field in FIELDS)
    assert {c['value'] for c in d['fields']['ceo']['candidates']}=={'Bob Stone','Dana Ruiz'}

@case('stage2-loaded-no-click-text-only')
def test_stage2_visible():
    reset();status(create(visible_domain),202);d=ready(visible_domain)
    known(d,'ceo','Dana Ruiz');provenance(d)
    assert [c['value'] for c in d['fields']['ceo']['candidates']]==['Dana Ruiz','Sam Ortiz'],{'field':d['fields']['ceo'],'rendered_text':[p for c in log() if c['method']=='extract' for p in c['served']]}
    assert d['fields']['ceo']['status']=='contested'

@case('stage2-rate-limit-waits-and-accounting')
def test_stage2_rate_limits():
    reset();status(req('/__probe/reset','POST',{},auth=False,at=proxy),204)
    status(admin('faults',{'provider':'nimble','methods':['search','research','extract'],'mode':'rate_limit'}),204)
    t=time.monotonic();status(create(rank_domain),202);d=ready(rank_domain,seconds=25);elapsed=time.monotonic()-t
    known(d,'ceo','Ava Stone');provenance(d)
    trace=status(req('/__probe/log',auth=False,at=proxy),200)['calls']
    previous={};waits=[]
    for c in sorted(trace,key=lambda c:c['started']):
        signature=(c['method'],c['path'],c['arguments'])
        if signature in previous and previous[signature]['status']==429:
            gap=c['started']-previous[signature]['answered'];waits.append(gap)
            assert gap>=1.0,('early retry after 429',gap,c['path'])
        previous[signature]=c
    assert waits and elapsed>=6.0,('rate-limit wait exercise',elapsed,waits)
    calls=log();assert any(c['status']==429 for c in calls)
    assert all(c['cost']==0 for c in calls if c['status']==429)
    assert d['spent_units']==sum(c['cost'] for c in calls) and d['spent_units']<=80

@case('stage2-legacy-upgrade-cross-field-citations')
def test_stage2_upgrade():
    reset();reset(at=legacy)
    legacy_token=token
    status(admin('reset',{'epoch':0}),204)
    original=status(create(legacy_domain,'legacy-key',at=legacy),202)
    old=ready(legacy_domain,at=legacy)
    assert old['fields']['legal_name']['value']=='Legacy Amber, LLC'
    assert old['fields']['ceo']['value']=='Ava Stone',('legacy fixture did not exercise losing-value recovery',old['fields']['ceo']['value'])
    exported=status(req('/_test/export',auth=False,at=legacy),200)
    source_calls=log()
    reset();status(req('/_test/clock','POST',{'now':LATER},auth=False),204)
    before=len(log());status(req('/_test/import','POST',exported,auth=False),204)
    assert len(log())==before
    global_token(legacy_token)
    new=get(legacy_domain);provenance(new,calls=source_calls)
    assert new['dossier_id']==old['dossier_id'] and new['researched_at']==old['researched_at'] and new['spent_units']==old['spent_units']
    expected_ceo={('https://legacy-amber.test/about','Zara Lane'),('https://news-legacy.test/b','Ava Stone'),('https://data-legacy.test/c','Ava Stone'),('https://wire-legacy.test/d','Ava Stone')}
    assert {(c['url'],c['value']) for c in new['fields']['ceo']['candidates']}==expected_ceo,new['fields']['ceo']
    assert new['fields']['ceo']['status']=='contested'
    for field in FIELDS:
        for c in new['fields'][field]['candidates']:
            assert c['kind'] is None and c['published_at'] is None and c['retrieved_at']==old['researched_at'],c
    first=old['fields']['legal_name']['citations'][0]
    assert new['fields']['legal_name']['candidates'][0]['excerpt']==first['excerpt']
    assert next(c for c in new['fields']['ceo']['candidates'] if c['url']==first['url'])['excerpt']==first['excerpt']
    assert status(create(legacy_domain,'legacy-key'),200)==original
    assert len(log())==before
    stage2_export=status(req('/_test/export',auth=False),200)
    status(req('/_test/import','POST',stage2_export,auth=False,at=second),204)
    assert get(legacy_domain,at=second)==new
    status(req('/dossiers/'+legacy_domain+'/refresh','POST',key='upgrade-refresh'),202)
    refreshed=ready(legacy_domain);provenance(refreshed)
    known(refreshed,'ceo','Zara Lane')
    assert all(c['kind'] is not None and instant(c['retrieved_at'])==instant(LATER) for f in FIELDS for c in refreshed['fields'][f]['candidates'])

@case('stage2-slow-research-then-throttled-extract')
def test_stage2_late_throttle():
    reset()
    status(admin('faults',{'provider':'nimble','methods':['research'],'mode':'delay','seconds':7}),204)
    status(admin('faults',{'provider':'nimble','methods':['extract'],'mode':'throttle'}),204)
    status(create('reader-full.test'),202)
    d=ready('reader-full.test',seconds=20)
    try:known(d,'ceo','Dana Ruiz')
    except AssertionError as exc:
        raise AssertionError({'state':d['state'],'spent_units':d['spent_units'],'ceo':d['fields']['ceo'],'extract_statuses':[c['status'] for c in log() if c['method']=='extract']}) from exc
    provenance(d)
    extracts=[c for c in log() if c['method']=='extract']
    assert [c['status'] for c in extracts]==[429,200],('late throttled extract trace',[c['status'] for c in extracts])
    assert d['spent_units']==sum(c['cost'] for c in log()) and d['spent_units']<=80,('late throttled extract spending',d['spent_units'])
    forwarded=[c for c in status(req('/__probe/log',auth=False,at=proxy),200)['calls'] if c['path'].endswith('/v2/extract') and 'reader-full.test/page-0' in c['arguments']]
    forwarded=sorted(forwarded,key=lambda c:c['started'])
    assert forwarded[-1]['started']-forwarded[-2]['answered']>=1.0,('early late-extract retry',forwarded[-1]['started']-forwarded[-2]['answered'])

@case('stage2-html-shell-content-negotiation')
def test_stage2_html():
    reset()
    for path in ['/','/signup','/login','/contested','/dossiers/'+rank_domain,'/dossiers/'+rank_domain+'/evidence']:
        request=urllib.request.Request(base+path,headers={'Accept':'text/html,application/xhtml+xml'})
        with urllib.request.urlopen(request,timeout=5) as response:
            assert response.status==200 and 'text/html' in response.headers.get('Content-Type',''),path
            assert response.read().strip(),path
    status(req('/dossiers/'+rank_domain,auth=False),401,'unauthenticated')

def browser_suite():
    config=WORK/'config.json'
    config.write_text(json.dumps({'base':'http://'+PREFIX+'-service:8097','mock':'http://'+PREFIX+'-web:8080','legacy':'http://'+PREFIX+'-legacy:8097','only':os.environ.get('SECOND_READER_BROWSER_ONLY')}))
    config.chmod(0o600)
    name=PREFIX+'-browser'
    try:
        output=cmd('with-slot','docker','run','--rm','--name',name,'--network',network,'--cpus','2','--memory','3g','-v',str(ROOT)+':/probes:ro','-v',str(WORK)+':/work','df-harness-runner','python','/probes/browser.py',timeout=1100,check=False)
        print(output,flush=True)
        path=WORK/'browser-results.json'
        if path.exists():results.extend(json.loads(path.read_text())['results'])
        else:results.append({'case':'browser-infrastructure','result':'fail','detail':output[-3000:]})
    finally:
        cmd('docker','rm','-f',name,check=False)
        config.unlink(missing_ok=True)

def wait(url,path='/health'):
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        try:
            with urllib.request.urlopen(url+path,timeout=2) as r:
                if r.status==200:return
        except Exception:pass
        time.sleep(.15)
    raise RuntimeError('service did not become healthy within 60 seconds')

def run_container(name,image,network,port,env=None,volume=None,command=None):
    hostport=20040+len(containers)
    args=['docker','run','-d','--name',name,'--network',network,'--cpus','2','--memory','3g','-p',f'127.0.0.1:{hostport}:{port}']
    for k,v in (env or {}).items(): args+=['-e',k+'='+v]
    if volume: args+=['-v',volume]
    args.append(image)
    args.extend(command or [])
    cmd(*args);containers.append(name)
    for _ in range(25):
        mapped=cmd('docker','port',name,str(port)+'/tcp',check=False)
        if mapped.startswith('127.0.0.1:'):
            return 'http://127.0.0.1:'+mapped.split(':')[-1]
        state=cmd('docker','inspect','--format','{{.State.Status}}',name)
        if state=='exited':
            raise RuntimeError(name+' exited: '+cmd('docker','logs',name,check=False))
        time.sleep(.2)
    raise RuntimeError(name+' has no port mapping: '+cmd('docker','inspect','--format','{{json .NetworkSettings.Ports}}',name))

exec(compile((ROOT/'temporal.py').read_text(),str(ROOT/'temporal.py'),'exec'))

try:
    print('PROBE_WORK',WORK,flush=True)
    cmd('with-slot','docker','build','-q','-t',PREFIX+'-service',str(STAGE),timeout=1800)
    cmd('with-slot','docker','build','-q','-t',PREFIX+'-web',str(KIT/'challenges/dossier/web'),timeout=1800)
    network=PREFIX+'-net';cmd('docker','network','create',network);networks.append(network)
    # First run the required sample corpus without opening its answer key.
    sample_mock=run_container(PREFIX+'-sample-web',PREFIX+'-web',network,8080,{'MOCK_ADMIN_TOKEN':'reader-local-admin'},str(KIT/'challenges/dossier/web/corpus/sample')+':/data/corpus:ro')
    sample_base=run_container(PREFIX+'-sample-service',PREFIX+'-service',network,8097,{'PORT':'8097','NIMBLE_API_KEY':'reader-opaque-mock-key','NIMBLE_BASE_URL':'http://'+PREFIX+'-sample-web:8080/nimble'})
    wait(sample_base)
    base=sample_base;mock=sample_mock
    def sample_case():
        reset()
        files=sorted((KIT/'challenges/dossier/web/corpus/sample').glob('*.test.json'))
        for path in files:
            domain=path.name[:-5]
            status(create(domain),202); d=ready(domain)
            assert d['state']=='ready' and d['spent_units']<=80
            provenance(d)
        assert len(status(req('/dossiers'),200)['dossiers'])==len(files)
    case('sample-corpus-nimble-only')(sample_case)()
    cmd('docker','rm','-f',PREFIX+'-sample-service',PREFIX+'-sample-web')
    containers.remove(PREFIX+'-sample-service');containers.remove(PREFIX+'-sample-web')
    corpusdir=WORK/'corpus';corpusdir.mkdir()
    for c in corpus: (corpusdir/(c['domain']+'.json')).write_text(json.dumps(c))
    (corpusdir/'traits.json').write_text(json.dumps({'seed':713,'providers':{'nimble':{'noise':0,'rate_limit':0}}}))
    mock=run_container(PREFIX+'-web',PREFIX+'-web',network,8080,{'MOCK_ADMIN_TOKEN':'reader-local-admin'},str(corpusdir)+':/data/corpus:ro')
    time.sleep(.25)
    if cmd('docker','inspect','--format','{{.State.Status}}',PREFIX+'-web')=='exited':
        raise RuntimeError(cmd('docker','logs',PREFIX+'-web',check=False))
    wait(mock,'/_mock/health')
    proxy=run_container(PREFIX+'-proxy','python:3.12-slim',network,8080,{'PROBE_TARGET':'http://'+PREFIX+'-web:8080'},str(ROOT)+':/probes:ro',['python','-u','/probes/provider_proxy.py'])
    wait(proxy,'/__probe/log')
    service_name=PREFIX+'-service'
    env={'PORT':'8097','NIMBLE_API_KEY':'reader-opaque-mock-key','NIMBLE_BASE_URL':'http://'+PREFIX+'-proxy:8080/nimble'}
    base=run_container(service_name,PREFIX+'-service',network,8097,env)
    second=run_container(PREFIX+'-second',PREFIX+'-service',network,8097,env)
    legacy_folder=STAGE.parent/'stage-1'
    if not legacy_folder.is_dir():
        cmd('fclone','a8789dcd65a18ca385d968116c51d23590913c33',str(WORK/'legacy-repo'))
        legacy_folder=WORK/'legacy-repo/stage-1'
    cmd('with-slot','docker','build','-q','-t',PREFIX+'-legacy',str(legacy_folder),timeout=1800)
    legacy=run_container(PREFIX+'-legacy',PREFIX+'-legacy',network,8097,env)
    legacy2_folder=STAGE.parent/'stage-2'
    if not legacy2_folder.is_dir():
        cmd('fclone','bc19abf8cbde23c3a2fa50f23baa55dbfe48d731',str(WORK/'legacy2-repo'))
        legacy2_folder=WORK/'legacy2-repo/stage-2'
    cmd('with-slot','docker','build','-q','-t',PREFIX+'-legacy2',str(legacy2_folder),timeout=1800)
    legacy2=run_container(PREFIX+'-legacy2',PREFIX+'-legacy2',network,8097,env)
    wait(base);wait(second);wait(legacy);wait(legacy2)
    # sample wrapper is added last; its one execution already occurred.
    selected=tests[:-1]
    only=os.environ.get('SECOND_READER_ONLY')
    if only: selected=[test for test in selected if test.case in only.split(',')]
    first=os.environ.get('SECOND_READER_FIRST','').split(',')
    selected=sorted(selected,key=lambda test:-1 if test.case=='runtime-health-and-initial-clock' else (0 if test.case in first else 1))
    for test in selected: test()
    if not os.environ.get('SECOND_READER_NO_BROWSER'):
        browser_suite()
except Exception as e:
    results.append({'case':'infrastructure','result':'fail','detail':str(e),'traceback':traceback.format_exc()})
    print('FAIL infrastructure',e,flush=True)
finally:
    for name in reversed(containers):
        (WORK/(name+'.log')).write_text(cmd('docker','logs',name,check=False))
        cmd('docker','rm','-f',name,check=False)
    for network in reversed(networks):cmd('docker','network','rm',network,check=False)
    out={'stage_folder':str(STAGE),'results':results,'passed':sum(x['result']=='pass' for x in results),'failed':sum(x['result']=='fail' for x in results)}
    (ROOT/'last-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print('COUNTS',out['passed'],'passed',out['failed'],'failed',flush=True)
sys.exit(bool(out['failed']))
