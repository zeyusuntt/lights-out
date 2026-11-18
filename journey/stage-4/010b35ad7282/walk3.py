import time
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:21001"
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_context(viewport={"width":375,"height":812}).new_page()
    pg.goto(B+"/login"); pg.fill('[data-testid=login-email]',"ada@example.com"); pg.fill('[data-testid=login-password]',"correct horse"); pg.click('[data-testid=login-submit]'); pg.wait_for_timeout(800)
    # out-of-order: first GET after click reload delayed 3s with stale body
    pg.goto(B+"/dossiers/brightwater-labs.test"); pg.wait_for_selector('[data-testid=dossier-state]')
    st={"n":0}
    def h(route):
        if route.request.method!="GET" or "text/html" in route.request.headers.get("accept",""): return route.continue_()
        st["n"]+=1
        if st["n"]==1:
            r=route.fetch(); time.sleep(3.5); route.fulfill(response=r)  # delayed old read
        else: route.continue_()
    pg.route("**/dossiers/brightwater-labs.test",h)
    pg.click('[data-testid=dossier-refresh]'); pg.wait_for_timeout(500)
    pg.wait_for_selector('[data-testid=dossier-state]:text-is("ready")',timeout=30000); pg.wait_for_timeout(5000)
    print("final state after delayed read:",pg.inner_text('[data-testid=dossier-state]'), "spent",pg.get_attribute('[data-testid=dossier-spent]','data-units'),"gets",st["n"])
    pg.unroute("**/dossiers/brightwater-labs.test")
    # hang refresh
    pg.route("**/dossiers/brightwater-labs.test/refresh",lambda r:None)
    pg.click('[data-testid=dossier-refresh]'); 
    for s in (3,8,15):
        pg.wait_for_timeout(s*1000 if s==3 else 5000); print("t+",s,"uncertain",pg.locator('[data-testid=refresh-uncertain]').count(),"err",pg.locator('[data-testid=refresh-error]').count(),"btn disabled",pg.is_disabled('[data-testid=dossier-refresh]'))
    pg.screenshot(path="/Users/sunzeyu/dev/band-factory/work/result/journey/stage-4/010b35ad7282/m-23-refresh-hang.png")
    br.close()
