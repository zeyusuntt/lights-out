- `test_a_runtime.py::test_reset_missing_required[currency]` — **PRODUCT_DEFECT** — Reset without currency returns 204 and silently chooses EUR. Stage 1 §4: “The service has **one currency**, declared in the fixture.” Required-field failures are 422 (§5). R01.
- `test_b_auth.py::test_signup_missing[display_name]` — **AMBIGUOUS** — Signup without display_name returns 201 with “nu”. The §6 signup body shows {email,password,display_name}, suggesting a required input; §5 assigns 422 only when “A required field or query parameter is missing”. The text never explicitly identifies display_name as required or specifies omission behavior. Reading the example as a mandatory schema supports the test; reading it as an example permitting a generated display name supports the service.
- `test_b_auth.py::test_signup_wrong_type[None-display_name]` — **PRODUCT_DEFECT** — Signup with display_name:null returns 201 and substitutes “nu”. The §6 string field and §5 “a field of the wrong JSON type” require 400 malformed_request. R03.
- `test_c_payments.py::test_balance_cap_payment` — **PRODUCT_DEFECT** — Paying 101 into a wallet at 2^53−100 returns 201, debits 101 but credits only 100, losing one unit. §4: “Monetary arithmetic must preserve exact minor-unit values without rounding error.” The mathematical credit also exceeds the balance limit. R04.
- `test_c_payments.py::test_balance_cap_request_pay` — **PRODUCT_DEFECT** — Paying a request for 101 into 2^53−100 likewise succeeds and loses one unit, violating the same §4 exact-arithmetic and balance-range sentence. R05.
- `test_g_idempotency.py::test_pay_no_body` — **AMBIGUOUS** — A zero-byte body returns 400; {} succeeds. §8 says “The body carries visibility only, optional, default public”, which can suggest omission is valid, but §5 assigns 400 to an “Unparseable body” and §7 defines equality “after parsing”. No supplied text equates absent bytes with {}.
- `test_h_settlements.py::test_batch_shape[body13]` — **AMBIGUOUS** — transfers:[{from_handle:1,to_handle:"bob",amount:1}] returns 400. §11 says “malformed batch shape is 422 validation_failed”; §5 says “a field of the wrong JSON type” is 400. Whether an inner handle type is batch shape or a field error is not defined.
- `test_h_settlements.py::test_balance_cap_settlement` — **PRODUCT_DEFECT** — A settlement credit of 101 into 2^53−100 commits and loses one unit. §4 requires exact arithmetic and “no operation produces a balance outside ±2⁵³”. R06.
- `test_i_export_import.py::test_import_corrupt_each_part` — **TEST_BUG** — The first failure is state.schema replaced with an object being accepted (204); seq and counter replacements also succeed. §10 calls state “an implementation-defined JSON object” and its format “opaque to the caller”. An arbitrary changed metadata value is not necessarily an invalid state; blanket rejection of every top-level substitution is unsupported.
- `test_k_rulings_ledger.py::test_import_non_object[[1]]` — **AMBIGUOUS** — Importing parsed JSON [1] returns 400. §10 says “missing fields ... give 422 validation_failed”, supporting the test, but also “Invalid JSON follows §5”, whose wrong-type rule supports rejecting an array where an object is expected with 400. Non-object import precedence is not explicit.
- `test_k_rulings_ledger.py::test_reset_users_wrong_type` — **PRODUCT_DEFECT** — Reset with users:"x" returns 422 instead of 400. §5 reserves 400 for “a field of the wrong JSON type”; reset has no users-type exception. R07.
- `test_k_rulings_ledger.py::test_pay_precedence` — **AMBIGUOUS** — A nonpayer submitting visibility:"bad" gets 422. §8 says “The caller is not the request’s payer | 403 forbidden”; §5 says “any visibility other than public or private” is 422. Neither orders these two checks for an unused key; the test adds that precedence.
- `test_m_authorizations.py::test_capture_zero_length_body` — **AMBIGUOUS** — A zero-byte capture returns 400, while {} takes the remaining amount. Stage 2 says “amount is optional and defaults to the authorisation’s remaining amount”; stage 1 §5 assigns 400 to an “Unparseable body”. The text does not say that an absent document parses as {}.
- `test_m_authorizations.py::test_capture_errors` — **PRODUCT_DEFECT** — For an open hold of 500, amount:1000000001 returns validation_failed instead of capture_exceeds_authorization. Stage 2 explicitly assigns that specific code to “amount above the authorisation’s uncaptured remainder”; §5 says “unless an endpoint specifies a different error” and “Endpoint-specific field rules take precedence”. R08.
- `test_m_authorizations.py::test_capture_over_range` — **PRODUCT_DEFECT** — Capturing 5 into a wallet already at 2^53 returns 201 and a balance of 9007199254740996. §4: “no operation produces a balance outside ±2⁵³”; this also rounds the mathematical balance. R09.
- `test_m_authorizations.py::test_capture_seeded_closed[expired]` — **PRODUCT_DEFECT** — This test seeds status:expired with a future expires_at (the helper default is +3 hours). Capture returns authorization_expired, although only the non-open predicate applies: stage 2 specifies “The authorisation is not open | 409 authorization_not_open”, and the expiry-specific predicate is “expires_at is at or before now”. R11.
- `test_n_hold_concurrency.py::test_import_corrupt_integers_with_holds[1000000000000000000000000000000]` — **PRODUCT_DEFECT** — An exported state with ttl changed to 10^30 imports with 204; a subsequent valid authorization returns 500. §5: “Requests must not produce 5xx responses, including under concurrent load.” Rejecting the import or refusing creation would avoid the defect. R10.
- `test_r_ui_competing.py::test_hung_response_becomes_uncertain` — **TEST_BUG** — The test holds a committed response unresolved and demands uncertainty within 9.5 seconds. Stage 2 requires uncertainty when a response “is lost” but specifies no browser timeout or 8/9.5-second deadline; the service request itself already finished. DOM execution confirms the pending state, but a chosen finite browser deadline is an added assertion.
- `test_s_ui_holds_quality.py::test_labels_app[/-ids0]` — **TEST_BUG** — The failed amount input has a visible “Amount” label next to its wrapper. The helper accepts only input.labels/aria-labelledby; its for attribute points to the wrapper. Stage 2 says “Inputs need visible labels”, without requiring those particular programmatic associations. The test rejects an actually present visible label.
- `test_s_ui_holds_quality.py::test_labels_authorize` — **TEST_BUG** — The authorize amount input likewise has visible “Amount” text, but its label points to the wrapper. The assertion adds programmatic association to stage 2’s “Inputs need visible labels”. Served DOM confirms the label exists.
- `test_s_ui_holds_quality.py::test_labels_capture` — **PRODUCT_DEFECT** — The incoming capture amount has only aria-label="Amount to collect"; no visible amount label is rendered. Stage 2: “Inputs need visible labels”. This differs from the visible Amount labels in the two preceding cases. R16.
- `test_s_ui_holds_quality.py::test_contrast[wallet-available]` — **TEST_BUG** — The contrast helper ignores background-image and measures the pale text against a white ancestor. The wallet actually has a dark green gradient: #f4fbf8 against its endpoints is approximately 7.51:1 and 9.68:1, not the helper’s 1.05:1 against white. The test’s background calculation is wrong.
- `test_t_rulings_stage2.py::test_huge_ttl_refused_at_create_not_at_reset[1000000000000]` — **PRODUCT_DEFECT** — Reset rejects the positive integer TTL 10^12 with 422. Stage 2: “If supplied, it must be a positive integer number of seconds.” No TTL maximum is stated. The first failure is at reset, independently of the separate representability issue at creation. R12.
- `test_t_rulings_stage2.py::test_seeded_history_defaults[captured-2000]` — **TEST_BUG** — The fixture supplies captured status but no capture amount or payment history. The text permits seeded closed records and says they “need not reconstruct a prior lifecycle” (stage 3); it never defines the claimed captured_amount=amount default. Returning 0 does not contradict a specified default.
- `test_t_rulings_stage2.py::test_capture_order[expired-7200-authorization_not_open-False]` — **PRODUCT_DEFECT** — Here “7200” is positive: the seeded expired record’s deadline is still two hours ahead. Returning authorization_expired contradicts the stage-2 capture table’s deadline predicate; the non-open record must give authorization_not_open. R11 reproduces the same case with a +3-hour deadline.
- `test_t_rulings_stage2.py::test_state_outranks_amount[captured--7200-authorization_not_open-body0]` — **AMBIGUOUS** — For a captured record and amount:0, the service returns 422. Stage 2 specifies both “The authorisation is not open | 409 authorization_not_open” and “amount below 1, or not an integer | 422 validation_failed”. No amount-versus-state ordering is stated for an unused key.
- `test_t_rulings_stage2.py::test_capture_over_range_keeps_key_free` — **PRODUCT_DEFECT** — The over-limit capture succeeds and claims the key, instead of leaving the hold open and the key reusable. The first failure is the same §4 range violation as R09; R09b also shows the erroneous 200 replay after recipient capacity is freed.
- `test_v_postseal_stage2.py::test_retry_not_blocked_by_hung_read` — **TEST_BUG** — This test also depends on pay-uncertain appearing within 9.5 seconds while both the committed response and later reads are held. Stage 2 gives no such browser deadline. The read-blocked retry assertion is never reached in this failure; it cannot establish a read/retry coupling defect.
- `test_v_postseal_stage2.py::test_ttl_raw_numbers[1e30-code2]` — **PRODUCT_DEFECT** — Reset rejects raw JSON authorization_ttl_seconds:1e30 with 422. It is an exact positive integer numeric value; stage 2 requires a “positive integer number of seconds” and states no maximum. R13.
- `test_x_corrections.py::test_known_at_future_equals_now` — **TEST_BUG** — It compares whole statements for different windows after removing only snapshot and known_at. One request uses default to=now; the other explicitly supplies a future to. The service returns their different to metadata while entries and balances agree. Stage 3 says “to ... defaults ... to now”; whole-response equality is unsupported.
- `test_x_corrections.py::test_correction_over_range` — **PRODUCT_DEFECT** — Correcting an original 50 to 500 credits the receiver above 2^53 and returns 201. §4’s “no operation produces a balance outside ±2⁵³” still applies to corrections. R14.
- `test_z_history_upgrade.py::test_upgrade_from_stage2` — **TEST_BUG** — The assertions at part.created_at−1µs and part.created_at assume the preceding 300 hold has a strictly earlier creation instant and the following capture has a later instant. No stage requires distinct timestamps for adjacent calls. Tied events must be combined at their shared instant; the hard-coded 500/900 expectations need verified distinct times. Same-version import control passed; the actual earlier-stage export was not supplied.
- `test_z_history_upgrade.py::test_round_trip_keeps_history` — **TEST_BUG** — The first and second statements are fresh reads with different default to=now values; only snapshot is removed before equality. The entries, balances and revision history match in the round-trip experiment. Stage 3 freezes default to only for paging the same snapshot, not for later fresh statements.
- `test_z_history_upgrade.py::test_upgrade_stage2_closed_holds` — **TEST_BUG** — The test assumes the stage-2 void time was not exported and demands no historical 60-unit voided hold. §10 makes state implementation-defined; an earlier service may retain that event. A round-trip preserving real events returns 73 (=13+60) at the voided hold’s creation, exactly the reported failure shape and consistent with stage 3’s “A hold starts at authorization creation”.
- `test_za_rulings_stage3.py::test_order_linked_before_validation` — **AMBIGUOUS** — An invalid correction to a settlement member returns validation_failed. Stage 3 says “Single-payment corrections reject settlement members with 422 linked_payment_immutable”, and also “Invalid input is 422 validation_failed”. Neither clause orders linkage against malformed correction fields for an unused key.
- `test_za_rulings_stage3.py::test_raw_plus_refused[/me?as_of=]` — **TEST_BUG** — The service accepts a raw + as a literal RFC 3339 offset and echoes it; %2B also works. The specification requires an “RFC 3339 instant with an offset”, but never mandates application/x-www-form-urlencoded query decoding or raw-plus rejection. This test assumes a decoder convention rather than an instant-validation rule.
- `test_za_rulings_stage3.py::test_seeded_hold_future_created_at[open]` — **TEST_BUG** — Only seeded payment created_at is explicitly forbidden in the future. For holds, stage 3 says “Seeded open holds are assumed created at reset unless created_at is supplied”; it states no corresponding future-created_at prohibition. The asserted 422 for this hold is unsupported.
- `test_ze_stage4_upgrade.py::test_upgrade_from_stage3` — **TEST_BUG** — The test requires a fresh revision-history record to equal a saved stage-3 correction response exactly, rejecting a legal added correction_batch_id:null; the text only requires batch revisions to expose the field and original idempotent replays to remain identical. It also requires refund_of to be absent in the earlier service, though stage 3 never forbids that extra field. Those schema-absence assertions are unsupported. Genuine old-image replay is unavailable; an actual change to frozen snapshot entries would separately violate stage 4’s “saved statements must remain available in their original form”, but has not been established here.
- `test_zf_rulings_stage4.py::test_refund_order[0]` — **AMBIGUOUS** — A refund of a refund with amount:0 returns validation_failed. Stage 4 says “Refunds of refunds give 422 invalid_refund_target” and “Invalid amount is 422 validation_failed”. Neither orders those simultaneous failures; the test imports an extra precedence ruling.
- `test_zf_rulings_stage4.py::test_item_inner_order` — **AMBIGUOUS** — An item naming p_nope with amount:-1 returns 422. Stage 4 says “Unknown payment is 404” and “Every item has the ordinary correction fields and validation” (stage 3: “Invalid input is 422 validation_failed”). “Item errors in input order” orders items, not the errors within one item.
- `test_zf_rulings_stage4.py::test_batch_auth_order` — **AMBIGUOUS** — The failing call is a nonoperator posting syntactically invalid JSON "{" with a key; it gets 400. Stage 4 requires “the same 401/403 rules as settlements”, supporting 403, while §5 assigns 400 to an “Unparseable body”. No authentication-versus-JSON-parsing precedence is specified.
- `test_zf_rulings_stage4.py::test_batch_credit_cap` — **PRODUCT_DEFECT** — A batch changes the original 50 to 101 when the receiver started at 2^53−100. It returns 201, rounds the credit and loses one unit. §4 exact arithmetic and the balance cap apply to all operations. R15.
- `test_zf_rulings_stage4.py::test_correction_batch_id_placement` — **TEST_BUG** — The test immediately rejects correction_batch_id:null on a single correction. Stage 4 requires batch revisions to expose correction_batch_id, but nowhere requires nonbatch revisions to omit it rather than return null, or prohibits additional response fields. The asserted field-absence contract is not in spec/.
- `test_zg_postseal_stage4.py::test_members_differ_below_a_microsecond` — **PRODUCT_DEFECT** — Settlement members corrected at .0000001 and .0000002 are accepted together. Stage 4: “Members of one settlement must have identical effective instants ... else 422 validation_failed.” These valid RFC 3339 instants differ by 100 ns. R17.
- `test_zg_postseal_stage4.py::test_as_of_below_a_microsecond` — **PRODUCT_DEFECT** — A revision effective at .0000002 already affects as_of=.0000001. Stage 3 requires the balance “before every payment after it” and applies revisions by effective time. R18.
- `test_zg_postseal_stage4.py::test_window_below_a_microsecond` — **PRODUCT_DEFECT** — A revision at .0000002 is missing from a statement ending at .0000003. Stage 3 requires the “half-open window [from, to)”. The 100 ns gap is positive. R19.
- `test_zg_postseal_stage4.py::test_snapshot_keeps_finer_window` — **PRODUCT_DEFECT** — The test fails before export: the first statement ending at .0000003 wrongly has zero entries for a revision at .0000002. This is the same half-open-window violation, not evidence of an additional import/snapshot corruption. R20 reproduces the initial read and its unchanged but incorrect saved page.
- `test_zh_oracle.py::test_model_agrees[0]` — **PRODUCT_DEFECT** — Seed 0 fails on statement ordering, not on the model’s overdraft policy: an effective time .00000010 is placed before an exact whole-second time. Stage 3: “Statement ordering is now by selected effective_at, then payment id.” R21 reduces that failure to two payments.

Totals (failed test instances, not distinct underlying defects):

- PRODUCT_DEFECT: **22**
- TEST_BUG: **15**
- AMBIGUOUS: **11**
- Total: **48**

**Reproductions and evidence**

All product reproductions below were run against `http://127.0.0.1:23150` on 2026-11-07. They use only HTTP, public browser assets and dummy fixtures; no service source was inspected. Each case resets the service. Generated tokens, IDs and timestamps will vary. “Expected” means the specification outcome; “Observed” is what the experiment actually returned. The two current-service URLs used for same-version import controls intentionally pointed at this one instance; those controls are not presented as genuine earlier-version migrations. Earlier-stage services/exports were not provided.

The API reproductions use Python’s standard library. Save this shared setup as `repro.py`, then append any individual case below and run `python3 repro.py`. The setup includes the complete reset fixture, authentication, request serialization and response handling.

```python
import json, urllib.request, urllib.error, urllib.parse, datetime, copy, sys, time

BASE='http://127.0.0.1:23150'

MISSING=object()

def call(method,path,body=MISSING,token=None,key=None,raw=None):
    headers={'Accept':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    if key: headers['Idempotency-Key']=key
    data=raw
    if body is not MISSING: data=json.dumps(body).encode()
    if data is not None: headers['Content-Type']='application/json; charset=utf-8'
    req=urllib.request.Request(BASE+path,data=data,headers=headers,method=method)
    try: r=urllib.request.urlopen(req,timeout=10)
    except urllib.error.HTTPError as e: r=e
    data=r.read()
    return r.status,json.loads(data) if data else None

def fx(bal=None):
    bal=bal or {'ada':10000,'bob':2500,'cy':0,'op':0}
    return {'currency':'EUR','minor_units':2,'users':[{'id':'u_'+n,'email':n+'@example.com','password':'correct horse','display_name':n.capitalize(),'handle':n,'balance':v} for n,v in bal.items()], 'payments':[], 'requests':[], 'settlement_operator_ids':['u_op'] if 'op' in bal else []}

def reset(f=None):
    status,_=call('POST','/_test/reset',f or fx()); assert status==204
    return {u['handle']:call('POST','/auth/login',{'email':u['email'],'password':u['password']})[1]['token'] for u in (f or fx())['users']}

def write(path,body,tok,key='k'): return call('POST',path,body,tok,key)

def pay(t,amount=500): return write('/payments',{'to_handle':'bob','amount':amount},t['ada'])[1]

def hold(t,amount=5): return write('/authorizations',{'to_handle':'bob','amount':amount},t['ada'])[1]['authorization_id']

def balances(t): return {n:call('GET','/me',token=v)[1]['balance'] for n,v in t.items()}

def correction(p,amount=500,eff=None): return {'expected_revision':1,'amount':amount,'effective_at':eff or p['created_at'],'reason':'r'}

def out(name,*values): print(name,json.dumps(values,ensure_ascii=False))

T0='2026-03-01T12:00:00.0000001+00:00'

T1='2026-03-01T12:00:00.0000002+00:00'

T2='2026-03-01T12:00:00.0000003+00:00'

def precision_setup():
 t=reset();p=pay(t);r=write('/payments/'+p['payment_id']+'/corrections',correction(p,500,T1),t['ada']);assert r[0]==201;return t,p
```

**R01 — Missing fixture currency**

Specification: Stage 1 §4: “The service has **one currency**, declared in the fixture.” Stage 1 §5: “A required field or query parameter is missing” → 422 validation_failed.

Expected: 422 validation_failed without replacing state.

Observed: 204; the newly installed default-currency fixture is usable (login 200).

```python
def currency():
 t=reset(); f=fx();del f['currency'];out('R01',call('POST','/_test/reset',f),call('POST','/auth/login',{'email':'ada@example.com','password':'correct horse'})[0])

currency()
```

**R03 — Null signup display_name**

Specification: Stage 1 §6 specifies display_name as a string in both request and response. §5: “Unparseable body, or a field of the wrong JSON type” → 400 malformed_request.

Expected: 400 malformed_request.

Observed: 201 with display_name:"nu"; null is silently treated as omission.

```python
def signup_null():
 reset();out('R03',call('POST','/auth/signup',{'email':'nu@example.com','password':'correct horse','display_name':None}))

signup_null()
```

**R04 — Direct payment at the balance limit**

Specification: Stage 1 §4: “amount is at most 1000000000 on any single request, and no operation produces a balance outside ±2⁵³. Monetary arithmetic must preserve exact minor-unit values without rounding error.” §1: “The sum of wallet balances always equals the total seeded by the last POST /_test/reset.”

Expected: 422 validation_failed, no transfer: 2^53−100+101 is 2^53+1.

Observed: 201; ada=899, bob=9007199254740992. Seeded total=9007199254741892, observed sum=9007199254741891: one unit disappeared.

```python
def cap_pay():
 t=reset(fx({'ada':1000,'bob':2**53-100}));out('R04',write('/payments',{'to_handle':'bob','amount':101},t['ada']),balances(t))

cap_pay()
```

**R05 — Paying a request at the balance limit**

Specification: The same stage-1 §4 arithmetic/range sentences and §1 conservation rule apply to request payments.

Expected: 422 validation_failed, request remains pending and balances unchanged.

Observed: 201; ada=899, bob=9007199254740992. The request is paid and one seeded unit disappears.

```python
def cap_request():
 t=reset(fx({'ada':1000,'bob':2**53-100}));q=write('/requests',{'payer_handle':'ada','amount':101},t['bob'])[1];out('R05',write('/requests/'+q['request_id']+'/pay',{},t['ada']),balances(t))

cap_request()
```

**R06 — Settlement at the balance limit**

Specification: Stage 1 §4: “no operation produces a balance outside ±2⁵³. Monetary arithmetic must preserve exact minor-unit values without rounding error.”

Expected: 422 validation_failed with no settlement committed.

Observed: 201; ada=899, bob=9007199254740992, op=0, one unit below the exact seeded total.

```python
def cap_settlement():
 t=reset(fx({'ada':1000,'bob':2**53-100,'op':0}));out('R06',write('/settlements',{'transfers':[{'from_handle':'ada','to_handle':'bob','amount':101}]},t['op']),balances(t))

cap_settlement()
```

**R07 — Wrong JSON type in reset users**

Specification: Stage 1 §5: “Reserve 400 malformed_request for a body that does not parse or a field of the wrong type.” The fixture defines users as an array; reset provides no overriding users-type error.

Expected: 400 malformed_request.

Observed: 422 validation_failed, message:"invalid fixture: users must be an array".

```python
def users_type():
 reset();f=fx();f['users']='x';out('R07',call('POST','/_test/reset',f))

users_type()
```

**R08 — Specific capture error overridden by generic amount validation**

Specification: Stage 2 capture table: “amount above the authorisation’s uncaptured remainder” → 422 capture_exceeds_authorization. Stage 1 §5: “A field of the correct JSON type with an invalid format or out-of-range value gives 422 validation_failed, unless an endpoint specifies a different error.” Also: “Endpoint-specific field rules take precedence”.

Expected: 422 capture_exceeds_authorization, just as amount:501 does for this 500-unit hold.

Observed: 422 validation_failed for 1000000001; the endpoint-specific error is lost when the amount also crosses the generic maximum.

```python
def capture_amount():
 t=reset();aid=hold(t,500);out('R08',write('/authorizations/'+aid+'/capture',{'amount':1000000001},t['bob']))

capture_amount()
```

**R09 — Capture exceeds the wallet range (two failed tests)**

Specification: Stage 1 §4: “no operation produces a balance outside ±2⁵³.” Stage 2 carries the earlier requirements forward; captures transfer the reserved money.

Expected: 422 validation_failed; authorization remains open and the key remains reusable.

Observed: 201; ada=95, bob=9007199254740996 (>2^53), cy=0. The receiver was credited 4 instead of 5. R09b below verifies the explicit-amount/key variant.

```python
def cap_capture():
 t=reset(fx({'ada':100,'bob':2**53,'cy':0}));aid=hold(t);out('R09',write('/authorizations/'+aid+'/capture',{},t['bob']),balances(t))

cap_capture()
```

**R09b — Explicit amount and key reuse**, also actually run with the shared setup:

```python
t = reset(fx({"ada": 100, "bob": 2**53, "cy": 0}))
aid = hold(t)
path = "/authorizations/" + aid + "/capture"
print(write(path, {"amount": 5}, t["bob"], "capkey"))
print(call("GET", "/authorizations", token=t["ada"]))
print(write("/payments", {"to_handle": "cy", "amount": 5}, t["bob"], "drain"))
print(write(path, {"amount": 5}, t["bob"], "capkey"))
```

Observed statuses: **201, 200, 201, 200**. The hold is already captured with remaining_amount=0 after the first call. Expected: first capture 422 with an open hold; after freeing recipient capacity, capture with that key should be a first success (201). The first range violation already suffices to classify the failed test.

**R10 — Accepted import causes a later valid request to return 500**

Specification: Stage 1 §5: “Requests must not produce 5xx responses, including under concurrent load.” §10 permits rejecting an invalid state with 422.

Expected: Either reject this import with 422, or handle authorization creation without 5xx.

Observed: Import 204, then POST /authorizations → 500 internal_error. The sole changed export value is state.ttl=10^30; no sweep or complicated hold history is necessary.

```python
def imported_ttl():
 t=reset();d=call('GET','/_test/export')[1];d['state']['ttl']=10**30;out('R10',call('POST','/_test/import',d),write('/authorizations',{'to_handle':'bob','amount':1},t['ada']))

imported_ttl()
```

**R11 — Seeded closed authorization with a future deadline (two failed tests)**

Specification: Stage 2: “Seeded status is open, captured, voided or expired. Only open holds anything.” Capture table: “The authorisation is not open” → 409 authorization_not_open; “expires_at is at or before now” → 409 authorization_expired.

Expected: 409 authorization_not_open: the record is explicitly closed, and its deadline is still in the future.

Observed: 409 authorization_expired. Both failed cases use a future deadline (+3 hours in test_capture_seeded_closed, +2 hours in test_capture_order). This run uses +3 hours, well beyond the fixture’s required one-hour distance.

```python
def expired_future():
 f=fx();f['authorizations']=[{'id':'a_1','from_user_id':'u_ada','to_user_id':'u_bob','amount':2000,'status':'expired','note':'deposit','visibility':'public','expires_at':(datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=3)).isoformat()}];t=reset(f);out('R11',f['authorizations'][0],write('/authorizations/a_1/capture',{},t['bob']))

expired_future()
```

**R12 — Positive 10^12-second TTL refused at reset**

Specification: Stage 2 Model: “authorization_ttl_seconds applies to every authorisation created through the API. It defaults to 600 when omitted. If supplied, it must be a positive integer number of seconds.” No maximum is specified.

Expected: Reset 204 for this positive integer. This repro makes no claim about which creation-time error should handle an unrepresentable future timestamp.

Observed: Reset 422 validation_failed, message:"invalid fixture: authorization_ttl_seconds must be a positive integer", although it is positive and integral.

```python
def ttl12():
 reset();f=fx();f['authorization_ttl_seconds']=10**12;out('R12',call('POST','/_test/reset',f))

ttl12()
```

**R13 — Integral scientific-notation TTL refused at reset**

Specification: Stage 2 requires a “positive integer number of seconds” without a maximum. Stage 1 §4 explains integral numeric values using “JSON 1000, 1000.0 and 1e3”. Here 1e30 is exactly an integer, not a fractional value or a string.

Expected: Reset 204; later inability to represent expires_at does not make the supplied reset value fractional or nonpositive.

Observed: Reset 422 validation_failed with the same positive-integer message.

```python
def ttl30():
 reset();f=fx();raw=json.dumps(f)[:-1]+',"authorization_ttl_seconds":1e30}';out('R13',call('POST','/_test/reset',raw=raw.encode()))

ttl30()
```

**R14 — Single correction exceeds the balance range**

Specification: Stage 1 §4: “no operation produces a balance outside ±2⁵³.” Stage 3: “The difference from the previous amount moves between the same two wallets in the same atomic step.”

Expected: 422 validation_failed; previous 50-unit payment and balances retained.

Observed: 201 revision 2 for amount 500; ada=500, bob=9007199254741392, which exceeds 2^53 by 400.

```python
def cap_correction():
 t=reset(fx({'ada':1000,'bob':2**53-100}));p=pay(t,50);out('R14',write('/payments/'+p['payment_id']+'/corrections',correction(p),t['ada']),balances(t))

cap_correction()
```

**R15 — Batch correction exceeds the balance range**

Specification: Stage 4: “All requirements from stages 1–3 continue to apply.” Stage 1 §4 requires both the ±2^53 balance range and exact arithmetic.

Expected: 422 validation_failed; the original amount 50 remains.

Observed: 201; correcting the total payment amount to 101 gives ada=899, bob=9007199254740992, op=0, losing one unit. The test correctly treats amount as the replacement total, not an additional debit.

```python
def cap_batch():
 t=reset(fx({'ada':1000,'bob':2**53-100,'op':0}));p=pay(t,50);out('R15',write('/correction-batches',{'corrections':[dict(correction(p,101),payment_id=p['payment_id'])]},t['op']),balances(t))

cap_batch()
```

**R17 — Different submicrosecond settlement instants accepted**

Specification: Stage 4: “Members of one settlement must have identical effective instants (offset spellings may differ), else 422 validation_failed.”

Expected: 422 validation_failed: .0000001 and .0000002 are distinct instants, not alternate offset spellings of one instant.

Observed: 201 correction batch, with the two different effective_at strings echoed on the member revisions.

```python
def member_instants():
 t=reset();s=write('/settlements',{'transfers':[{'from_handle':'ada','to_handle':'cy','amount':40},{'from_handle':'bob','to_handle':'cy','amount':50}]},t['op'])[1];items=[dict(correction(p,0,eff),payment_id=p['payment_id']) for p,eff in zip(s['payments'],[T0,T1])];out('R17',write('/correction-batches',{'corrections':items},t['op']))

member_instants()
```

**R18 — Inclusive historical balance collapses distinct instants**

Specification: Stage 3: balance is “before every payment after it”; “Then apply selected revisions according to their effective times. as_of retains its inclusive meaning”.

Expected: balance=10000 at .0000001, since the selected 500-unit revision is effective at the later .0000002.

Observed: 200 with balance=total=available=9500, held=0, while echoing as_of=.0000001.

```python
def asof():
 t,p=precision_setup();out('R18',call('GET','/me?'+urllib.parse.urlencode({'as_of':T0}),token=t['ada']))

asof()
```

**R19 — Statement drops a payment inside its half-open window**

Specification: Stage 3: “Returns the payments the caller sent or received in the half-open window [from, to)”.

Expected: One entry for the 500-unit revision at .0000002 when to=.0000003; closing_balance=9500.

Observed: 200 with entries:[], opening_balance=closing_balance=10000.

```python
def window():
 t,p=precision_setup();s=call('GET','/statement?'+urllib.parse.urlencode({'to':T2}),token=t['ada']);out('R19',s)

window()
```

**R20 — Snapshot precision test fails on its initial window read**

Specification: The same stage-3 “half-open window [from, to)” sentence applies before any snapshot export/import.

Expected: Initial statement contains one entry; saved pages retain it.

Observed: Initial statement has entries:[], closing_balance=10000. Export/import returns 204 and the token still pages that same incorrect empty result. This repro does not attribute a separate defect to import.

```python
def snapshot():
 t,p=precision_setup();s=call('GET','/statement?'+urllib.parse.urlencode({'to':T2}),token=t['ada']);d=call('GET','/_test/export')[1];i=call('POST','/_test/import',d);page=call('GET','/statement?'+urllib.parse.urlencode({'snapshot':s[1]['snapshot']}),token=t['ada']);out('R20',s,i,page)

snapshot()
```

**R21 — Minimal reduction of oracle seed 0: statement order**

Specification: Stage 3: “Statement ordering is now by selected effective_at, then payment id.”

Expected: The second-created payment (effective at the whole second) precedes the first-created payment (effective 100 ns later), regardless of their IDs.

Observed: The service returns p_1 at .0000001 before p_2 at the whole second. In the original seed-0 rerun the analogous mismatch was p_3 at .00000010 before p_5 at the whole second; this failure precedes any disputed overdraft-model interpretation.

```python
def ordering():
 t=reset();p=pay(t);q=write('/payments',{'to_handle':'bob','amount':20},t['ada'],'other')[1]
 for x,eff in [(p,T0),(q,'2026-03-01T12:00:00+00:00')]:
  r=write('/payments/'+x['payment_id']+'/corrections',correction(x,x['amount'],eff),t['ada']);assert r[0]==201
 s=call('GET','/statement',token=t['ada'])[1];out('R21',{'created_first':p['payment_id'],'created_second':q['payment_id'],'entries':[{'payment_id':e['payment']['payment_id'],'effective_at':e['effective_at']} for e in s['entries']]})

ordering()
```

**R16 — Capture amount has no visible label**

Specification, stage 2 Product and visual direction: “Inputs need visible labels”.

This experiment fetches and executes the public UI served by the target, lets it load the authorization through the actual API, and inspects its generated DOM. Chromium itself could not launch under the host sandbox (MachPortRendezvous permission failure), so this is a DOM-runtime reproduction, not a claimed rendered-browser pass. The relevant DOM has no amount-label text at all; the only label in its action group is for the separate keep-open checkbox. CSS supplies no generated amount label. `aria-label` provides an accessible name but is not visible text.

Run the following saved as `capture-label.cjs` in a directory with `jsdom` installed (`npm install jsdom`, then `node capture-label.cjs`):

```javascript
const {JSDOM}=require('jsdom');
const base='http://127.0.0.1:23150';
async function post(path,body,token,key){
 const r=await fetch(base+path,{method:'POST',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...(key?{'Idempotency-Key':key}:{})},body:JSON.stringify(body)});
 if(r.status===204)return; return r.json();
}
(async()=>{
 await post('/_test/reset',{currency:'EUR',minor_units:2,users:['ada','bob'].map(n=>({id:'u_'+n,email:n+'@example.com',password:'correct horse',display_name:n,handle:n,balance:1000})),payments:[],requests:[]});
 const login=async n=>(await post('/auth/login',{email:n+'@example.com',password:'correct horse'})).token;
 const a=await post('/authorizations',{to_handle:'bob',amount:100},await login('ada'),'hold');
 const token=await login('bob');
 const html=await (await fetch(base+'/authorizations',{headers:{Accept:'text/html'}})).text();
 const d=new JSDOM(html,{url:base+'/authorizations',runScripts:'dangerously',resources:'usable',beforeParse(w){
  w.localStorage.setItem('pocketful.token',token);w.CSS={escape:x=>x};w.scrollTo=()=>{};
  w.fetch=(path,opts)=>fetch(new URL(path,base),opts);
 }});
 for(let n=0;n<100;n++){
  const e=d.window.document.querySelector(`[data-testid="authorization-capture-amount-${a.authorization_id}"]`);
  if(e){console.log(e.outerHTML);console.log('Associated labels:',e.labels.length);console.log(e.closest('.item-actions').outerHTML);d.window.close();return;}
  await new Promise(r=>setTimeout(r,20));
 }
 throw Error('capture input did not load');
})();
```

Observed input:

```html
<input type="text" inputmode="decimal" autocomplete="off" data-testid="authorization-capture-amount-a_1" placeholder="0.00" aria-label="Amount to collect">
```

Observed surrounding action group, excluding only generated attributes unrelated to the issue:

```html
<div class="item-actions">
  <div style="width:150px"><div class="money-input">
    <input data-testid="authorization-capture-amount-a_1" aria-label="Amount to collect">
    <span class="cur" aria-hidden="true">EUR</span>
  </div></div>
  <button data-testid="authorization-capture-a_1">Collect</button>
  <label for="keep-a_1"><input type="checkbox" id="keep-a_1">Keep the rest on hold</label>
</div>
```

Expected: a visible label describing the capture amount. Observed: only an invisible aria-label for that amount.
