from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"; O="/Users/[REDACTED]/dev/band-factory/work/result/journey/stage-3/cd24f51fb21b/"
with sync_playwright() as p:
    br=p.chromium.launch()
    for w,h,t in [(375,812,"m"),(1440,900,"d")]:
        pg=br.new_context(viewport={"width":w,"height":h}).new_page()
        pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
        pg.goto(B+"/"); pg.fill('[data-testid=research-domain]',["mosaic-freight.test","ashgrove-solar.test"][t=="d"])
        pg.click('[data-testid=research-submit]'); pg.wait_for_selector('[data-testid=dossier-state]')
        pg.screenshot(path=f"{O}{t}-24-first-build.png",full_page=True)
        print(t,pg.inner_text('[data-testid=dossier-state]'),pg.inner_text('[data-testid=field-ceo]').replace("\n"," | "))
        pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000)
        print(t,"tap<44:",pg.evaluate("""()=>[...document.querySelectorAll('a,button')].map(e=>{const r=e.getBoundingClientRect();return [(e.innerText||'').slice(0,20),Math.round(r.height)]}).filter(x=>x[1]<44)"""))
        pg.goto(B+"/contested"); pg.screenshot(path=f"{O}{t}-25-contested.png"); 
        pg.goto(B+"/dossiers/mosaic-freight.test/evidence"); print(t,"evid tap<44",pg.evaluate("""()=>[...document.querySelectorAll('a,button')].map(e=>Math.round(e.getBoundingClientRect().height)).filter(x=>x<44)"""))
    br.close()
