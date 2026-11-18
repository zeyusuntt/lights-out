from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_context(viewport={"width":375,"height":812}).new_page()
    pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
    pg.goto(B+"/dossiers/mosaic-freight.test/evidence"); pg.wait_for_timeout(800)
    print(pg.evaluate("""()=>[...document.querySelectorAll('a,button')].map(e=>[e.tagName,(e.innerText||'').slice(0,50),Math.round(e.getBoundingClientRect().height)]).filter(x=>x[2]<40)"""))
