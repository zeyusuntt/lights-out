from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"; O="/Users/[REDACTED]/dev/band-factory/work/result/journey/stage-3/cd24f51fb21b/"
with sync_playwright() as p:
    br=p.chromium.launch()
    for w,h,t in [(375,812,"m"),(1440,900,"d")]:
        pg=br.new_context(viewport={"width":w,"height":h}).new_page()
        pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
        for n,u in [("30-tidemark","/dossiers/tidemark-energy.test"),("31-tidemark-evidence","/dossiers/tidemark-energy.test/evidence"),("32-contested-all","/contested"),("33-home-many","/"),("34-ferncliff","/dossiers/ferncliff-foods.test")]:
            pg.goto(B+u); pg.wait_for_timeout(900); pg.screenshot(path=f"{O}{t}-{n}.png",full_page=True)
            print(t,n,pg.evaluate("()=>[document.documentElement.scrollWidth,innerWidth]"))
    br.close()
