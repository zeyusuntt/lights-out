from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"
with sync_playwright() as p:
    br=p.chromium.launch()
    for w in (375,1440):
        pg=br.new_context(viewport={"width":w,"height":900}).new_page()
        for u in ["/login","/signup"]:
            pg.goto(B+u); print(w,u,pg.evaluate("()=>[...document.querySelectorAll('input,button,a')].map(e=>[e.tagName,Math.round(e.getBoundingClientRect().height)]).filter(x=>x[1]<44)"))
        pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
        pg.goto(B+"/"); print(w,"home",pg.evaluate("()=>[...document.querySelectorAll('input,button,a')].map(e=>[e.tagName,(e.innerText||e.placeholder||'').slice(0,20),Math.round(e.getBoundingClientRect().height)]).filter(x=>x[2]<44)"))
