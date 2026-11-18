import json, httpx
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"; O="/Users/sunzeyu/dev/band-factory/work/result/journey/stage-4/b928822534e8/"
F=["legal_name","hq_city","ceo","founded_year","headcount_range","funding_total"]
with sync_playwright() as p:
    br=p.chromium.launch()
    for w,h,tag in [(1440,900,"d"),(375,812,"m")]:
        ctx=br.new_context(viewport={"width":w,"height":h}); pg=ctx.new_page()
        pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
        pg.goto(B+"/dossiers/halvorsen-robotics.test"); pg.wait_for_selector('[data-testid=dossier-state]')
        print(tag,"testids missing:",[t for t in ["dossier-domain","dossier-state","dossier-spent","dossier-researched-at","dossier-evidence-link","dossier-refresh","dossier-reload","current-user","logout-button"]+[f"field-{f}" for f in F]+[f"field-value-{f}" for f in F]+[f"field-citations-{f}" for f in F]+["field-contested-hq_city","citation-legal_name-2"] if pg.locator(f'[data-testid={t}]').count()==0])
        print(pg.get_attribute('[data-testid=dossier-spent]','data-units'),pg.get_attribute('[data-testid=field-value-funding_total]','data-value'),pg.get_attribute('[data-testid=field-hq_city]','data-status'))
        # tap targets & small text
        small=pg.evaluate("""()=>[...document.querySelectorAll('a,button,input')].map(e=>{const r=e.getBoundingClientRect();return [e.tagName,(e.innerText||e.id||'').slice(0,25),Math.round(r.width),Math.round(r.height)]}).filter(x=>x[3]<32&&x[3]>0)""")
        print(tag,"small controls:",small[:12])
        fs=pg.evaluate("()=>Math.min(...[...document.querySelectorAll('body *')].filter(e=>e.childNodes.length&&[...e.childNodes].some(n=>n.nodeType==3&&n.textContent.trim())).map(e=>parseFloat(getComputedStyle(e).fontSize)))"); print(tag,"min font",fs)
        # focus
        pg.keyboard.press("Tab"); pg.keyboard.press("Tab"); pg.screenshot(path=f"{O}{tag}-15-focus.png")
        # refresh
        pg.click('[data-testid=dossier-refresh]'); pg.wait_for_timeout(250); pg.screenshot(path=f"{O}{tag}-16-refresh-building.png")
        pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000); print(tag,"spent after refresh",pg.get_attribute('[data-testid=dossier-spent]','data-units'))
        # uncertain: abort refresh response
        pg.route("**/dossiers/halvorsen-robotics.test/refresh",lambda r:r.abort()); pg.click('[data-testid=dossier-refresh]'); pg.wait_for_timeout(800)
        print(tag,"uncertain:",pg.locator('[data-testid=refresh-uncertain]').count(),"err:",pg.locator('[data-testid=refresh-error]').count()); pg.screenshot(path=f"{O}{tag}-17-refresh-uncertain.png")
        pg.unroute("**/dossiers/halvorsen-robotics.test/refresh")
        pg.click('[data-testid=dossier-refresh]'); pg.wait_for_timeout(1500)
        print(tag,"after retry uncertain:",pg.locator('[data-testid=refresh-uncertain]').count(),pg.locator('[data-testid=refresh-error]').count())
        pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000)
        # research uncertain
        pg.goto(B+"/"); pg.route("**/dossiers",lambda r:r.abort() if r.request.method=="POST" else r.continue_())
        pg.fill('[data-testid=research-domain]',"brightwater-labs.test"); pg.click('[data-testid=research-submit]'); pg.wait_for_timeout(800)
        print(tag,"research uncertain",pg.locator('[data-testid=research-uncertain]').count(),pg.locator('[data-testid=research-error]').count()); pg.screenshot(path=f"{O}{tag}-18-research-uncertain.png")
        pg.unroute("**/dossiers"); pg.click('[data-testid=research-submit]'); pg.wait_for_timeout(1500); print(tag,pg.url,pg.locator('[data-testid=research-uncertain]').count())
        pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000); pg.screenshot(path=f"{O}{tag}-19-second-ready.png",full_page=True)
        pg.goto(B+"/"); pg.fill('[data-testid=dossier-search]',"zzzz"); pg.wait_for_timeout(700); print(tag,"empty",pg.locator('[data-testid=empty-dossiers]').count()); pg.screenshot(path=f"{O}{tag}-20-search-empty.png")
        pg.fill('[data-testid=dossier-search]',"bright"); pg.wait_for_timeout(700); print(tag,"items",pg.locator('[data-testid^=dossier-item-]').count())
        pg.click('[data-testid=logout-button]'); pg.wait_for_timeout(600); print(tag,"after logout",pg.url,pg.locator('[data-testid=current-user]').count()); pg.screenshot(path=f"{O}{tag}-21-logged-out.png")
        pg.goto(B+"/dossiers/brightwater-labs.test"); pg.wait_for_timeout(800); print(tag,"anon dossier",pg.url); pg.screenshot(path=f"{O}{tag}-22-anon-dossier.png")
        ctx.close()
    br.close()
