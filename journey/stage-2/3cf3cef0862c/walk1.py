import json, httpx, sys
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"; O="/Users/[REDACTED]/dev/band-factory/work/result/journey/stage-2/3cf3cef0862c/"
httpx.post(B+"/_test/reset",json={"now":"2026-03-01T09:00:00+00:00","users":[{"id":"u_ada","email":"ada@example.com","password":"correct horse","display_name":"Ada"}]})
def probe(p,name,pg):
    m=pg.evaluate("()=>({sw:document.documentElement.scrollWidth,iw:innerWidth})")
    print(name,m, "OVERFLOW" if m['sw']>m['iw'] else "")
with sync_playwright() as p:
    br=p.chromium.launch()
    for w,h,tag in [(1440,900,"d"),(375,812,"m")]:
        ctx=br.new_context(viewport={"width":w,"height":h}); pg=ctx.new_page()
        pg.on("console",lambda m: print("console",m.type,m.text) if m.type in("error","warning") else None)
        def shot(n,full=True): pg.screenshot(path=f"{O}{tag}-{n}.png",full_page=full); probe(p,f"{tag}-{n}",pg)
        pg.goto(B+"/"); shot("01-home-anon")
        pg.goto(B+"/login"); shot("02-login")
        pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(500); shot("03-login-empty-err")
        pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"wrongwrong"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(700); shot("04-login-wrong")
        pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(1000); shot("05-after-login"); print(pg.url)
        pg.goto(B+"/"); shot("06-home-empty")
        pg.fill('[data-testid=research-domain]',"http://x.test/a"); pg.click('[data-testid=research-submit]'); pg.wait_for_timeout(700); shot("07-research-invalid")
        pg.fill('[data-testid=research-domain]',"Halvorsen-Robotics.TEST."); pg.click('[data-testid=research-submit]')
        pg.wait_for_timeout(300); shot("08-building"); print(pg.url)
        pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000); shot("09-ready")
        print(pg.inner_text('[data-testid=dossier-spent]'), pg.inner_text('[data-testid=dossier-researched-at]'))
        pg.goto(B+"/dossiers/halvorsen-robotics.test/evidence"); shot("10-evidence")
        pg.goto(B+"/contested"); shot("11-contested")
        pg.goto(B+"/"); shot("12-home-list")
        pg.goto(B+"/dossiers/nope.test"); shot("13-notfound")
        pg.goto(B+"/signup"); shot("14-signup")
        ctx.close()
    br.close()
