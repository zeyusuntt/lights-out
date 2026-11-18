import httpx,time
B="http://127.0.0.1:21001"
t=httpx.post(B+"/auth/login",json={"email":"ada@example.com","password":"correct horse"}).json()["token"]; H={"Authorization":"Bearer "+t}
doms=["ashgrove-solar.test","corvid-security.test","ferncliff-foods.test","larkspur-health.test","mosaic-freight.test","ostrava-mobility.test","pemberton-analytics.test","tidemark-energy.test","windrush-bakery.test","brightwater-labs.test"]
for d in doms:
    httpx.post(B+"/dossiers",headers={**H,"Idempotency-Key":"k"+d},json={"domain":d})
time.sleep(25)
for d in doms:
    r=httpx.get(B+"/dossiers/"+d,headers=H).json(); e=r["fields"]["executives"]
    print(d,r["state"],r["spent_units"],e["status"],e["value"],[ (k,f["status"]) for k,f in r["fields"].items() if f["status"]=="contested"])
