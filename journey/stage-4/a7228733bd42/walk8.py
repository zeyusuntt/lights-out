import httpx,json
B="http://127.0.0.1:21001"
t=httpx.post(B+"/auth/login",json={"email":"ada@example.com","password":"correct horse"}).json()["token"]; H={"Authorization":"Bearer "+t}
for d in ["tidemark-energy.test","halvorsen-robotics.test","ferncliff-foods.test"]:
    r=httpx.get(B+"/dossiers/"+d,headers=H).json()
    for k in ("investors","legal_name","ceo"):
        f=r["fields"][k]; print(d,k,f["status"],json.dumps(f["value"]),f.get("origins"),f.get("corroborated"),f.get("corroborated_since"))
