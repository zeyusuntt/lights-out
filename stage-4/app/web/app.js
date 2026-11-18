"use strict";

const FIELDS = [
  ["legal_name", "Legal name"],
  ["hq_city", "Headquarters"],
  ["ceo", "Chief executive"],
  ["founded_year", "Founded"],
  ["headcount_range", "Employees"],
  ["funding_total", "Total funding"],
];
const TITLE_LABEL = { cfo: "Chief financial officer", coo: "Chief operating officer", cto: "Chief technology officer" };
const KIND_LABEL = { own: "Company site", filing: "Filing registry", news: "News report", aggregator: "Data aggregator" };
const PROVIDER_LABEL = { nimble: "Nimble", tavily: "Tavily", kernel: "Kernel", browserbase: "Browserbase" };
const STATE_LABEL = { building: "Researching", ready: "Ready", failed: "Research failed" };
const POLL_MS = 1000;
const REQUEST_TIMEOUT_MS = 10000;

/* ---------- session: the bearer token and the name to show ---------- */

const session = {
  read() {
    try { return JSON.parse(localStorage.getItem("dossier.session")) || null; } catch { return null; }
  },
  save(token, name) { localStorage.setItem("dossier.session", JSON.stringify({ token, name })); },
  clear() { localStorage.removeItem("dossier.session"); },
};

/* ---------- DOM helper ---------- */

function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "on") for (const [ev, fn] of Object.entries(v)) el.addEventListener(ev, fn);
    else if (k === "testid") el.setAttribute("data-testid", v);
    else el.setAttribute(k, v === true ? "" : String(v));
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

/* ---------- API ---------- */

class Unreachable extends Error {}

async function api(method, path, { body, key } = {}) {
  const headers = { Accept: "application/json" };
  const current = session.read();
  if (current) headers.Authorization = `Bearer ${current.token}`;
  if (key) headers["Idempotency-Key"] = key;
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response;
  try {
    response = await fetch(path, { method, headers, body: body === undefined ? undefined : JSON.stringify(body), signal: controller.signal });
  } catch {
    throw new Unreachable();
  } finally {
    clearTimeout(timer);
  }
  if (response.status >= 500) throw new Unreachable();
  let data = null;
  try { data = response.status === 204 ? null : await response.json(); } catch { throw new Unreachable(); }
  if (response.status === 401 && current && path !== "/auth/login") {
    session.clear();
    goLogin();
  }
  return { status: response.status, data };
}

function errorText(result, fallback) {
  return (result.data && result.data.error && result.data.error.message) || fallback;
}

function newKey() {
  return (crypto.randomUUID && crypto.randomUUID()) || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function listAll(q) {
  const items = [];
  for (let offset = 0; ; offset += 200) {
    const params = new URLSearchParams({ limit: "200", offset: String(offset) });
    if (q) params.set("q", q);
    const result = await api("GET", `/dossiers?${params}`);
    if (result.status !== 200) return null;
    items.push(...result.data.dossiers);
    if (!result.data.has_more) return items;
  }
}

/* ---------- formatting, people first ---------- */

function normaliseDomain(raw) {
  let d = String(raw).trim().toLowerCase();
  if (d.endsWith(".")) d = d.slice(0, -1);
  if (d.startsWith("www.")) d = d.slice(4);
  return d;
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function formatTime(rfc3339) {
  const m = /^(\d{4})-(\d{2})-(\d{2})[Tt ](\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?([Zz]|[+-]\d{2}:\d{2})$/.exec(rfc3339 || "");
  if (!m) return rfc3339 || "";
  const offset = m[6].toUpperCase() === "Z" ? "+00:00" : m[6];
  return `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${m[1]}, ${m[4]}:${m[5]} (UTC${offset})`;
}

function formatDate(day) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(day || "");
  return m ? `${Number(m[3])} ${MONTHS[Number(m[2]) - 1]} ${m[1]}` : day || "";
}

function dateElement(day) {
  return h("time", { datetime: day, "data-value": day }, formatDate(day));
}

function timeElement(rfc3339) {
  return h("span", {},
    h("time", { datetime: rfc3339, "data-value": rfc3339 }, formatTime(rfc3339)),
    h("span", { class: "exact" }, rfc3339));
}

function formatMoney(n) {
  const scaled = (value, word) => `$${Number(value.toFixed(2)).toLocaleString("en-US")} ${word}`;
  if (n >= 1e9) return scaled(n / 1e9, "billion");
  if (n >= 1e6) return scaled(n / 1e6, "million");
  return `$${n.toLocaleString("en-US")}`;
}

function formatValue(field, value) {
  if (value === null || value === undefined) return "";
  if (field === "funding_total") return formatMoney(value);
  if (field === "headcount_range") {
    const [low, high] = String(value).replace("+", "").split("-").map(Number);
    return high ? `${low}-${high} employees` : `${low}+ employees`;
  }
  return String(value);
}

function dataValue(value) {
  return value === null || value === undefined ? null : String(value);
}

function formatUnits(n) {
  return `${n.toLocaleString("en-US")} ${n === 1 ? "unit" : "units"}`;
}

/* ---------- routing ---------- */

let view = 0;
const pending = { research: null, refresh: {} };

function navigate(path, { replace = false } = {}) {
  if (replace) history.replaceState(null, "", path); else history.pushState(null, "", path);
  render();
}

function goLogin() {
  const here = location.pathname + location.search;
  if (location.pathname === "/login" || location.pathname === "/signup") return;
  navigate(`/login?next=${encodeURIComponent(here)}`, { replace: true });
}

function route(pathname) {
  if (pathname === "/") return { screen: listScreen, nav: "list", protect: true };
  if (pathname === "/login") return { screen: loginScreen };
  if (pathname === "/signup") return { screen: signupScreen };
  if (pathname === "/contested") return { screen: contestedScreen, nav: "contested", protect: true };
  const m = /^\/dossiers\/([^/]+)(\/evidence)?\/?$/.exec(pathname);
  if (m) {
    const raw = decodeURIComponent(m[1]);
    return { screen: m[2] ? evidenceScreen : dossierScreen, arg: raw, protect: true, nav: "list" };
  }
  return { screen: missingScreen };
}

function render() {
  view += 1;
  const r = route(location.pathname);
  renderSession();
  for (const a of document.querySelectorAll("[data-nav]")) {
    if (a.dataset.nav === r.nav) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  }
  if (r.protect && !session.read()) { goLogin(); return; }
  const main = document.getElementById("main");
  main.replaceChildren(h("p", { class: "placeholder" }, "Loading…"));
  r.screen(main, r.arg, view);
}

function isCurrent(token) { return token === view; }

function renderSession() {
  const box = document.getElementById("session");
  const current = session.read();
  document.querySelector(".nav").hidden = !current;
  if (!current) {
    box.replaceChildren(h("a", { href: "/login" }, "Sign in"), h("a", { href: "/signup", class: "button secondary" }, "Create account"));
    return;
  }
  box.replaceChildren(
    h("span", { class: "who", testid: "current-user", title: current.name }, "Signed in as ", h("strong", {}, current.name)),
    h("button", { type: "button", class: "button quiet", testid: "logout-button", on: { click: () => { session.clear(); navigate("/login"); } } }, "Sign out"));
}

document.addEventListener("click", (event) => {
  const link = event.target.closest("a[href]");
  if (!link || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || link.target) return;
  const url = new URL(link.href, location.href);
  if (url.origin !== location.origin) return;
  event.preventDefault();
  navigate(url.pathname + url.search);
});
window.addEventListener("popstate", render);

/* ---------- small pieces ---------- */

function notice(kind, testid, text) {
  return h("div", { class: `notice ${kind}`, testid, role: kind === "refused" ? "alert" : "status" }, text);
}

function field(id, labelText, input, hint) {
  return h("div", {}, h("label", { for: id }, labelText), input, hint ? h("p", { class: "hint" }, hint) : null);
}

function statePill(state) {
  return h("span", { class: `pill ${state}` }, STATE_LABEL[state] || state);
}

function sourceMeta(url, provider, extra) {
  return h("div", { class: "source-meta" }, extra, h("a", { href: url, target: "_blank", rel: "noopener" }, url),
    ` — served by ${PROVIDER_LABEL[provider] || provider}`);
}

/* ---------- auth screens ---------- */

function authScreen(main, kind) {
  const isSignup = kind === "signup";
  const p = isSignup ? "signup" : "login";
  const email = h("input", { id: `${p}-email`, type: "email", autocomplete: "email", required: true, testid: `${p}-email` });
  const password = h("input", { id: `${p}-password`, type: "password", autocomplete: isSignup ? "new-password" : "current-password", required: true, testid: `${p}-password` });
  const name = isSignup ? h("input", { id: "signup-display-name", type: "text", autocomplete: "name", required: true, testid: "signup-display-name" }) : null;
  const submit = h("button", { type: "submit", class: "button", testid: `${p}-submit` }, isSignup ? "Create account" : "Sign in");
  const feedback = h("div", { "aria-live": "polite" });
  const next = new URLSearchParams(location.search).get("next") || "/";
  const form = h("form", { novalidate: true, on: { submit: async (event) => {
    event.preventDefault();
    submit.disabled = true;
    const body = { email: email.value, password: password.value };
    if (isSignup) body.display_name = name.value;
    try {
      const result = await api("POST", isSignup ? "/auth/signup" : "/auth/login", { body });
      if (result.status === 200 || result.status === 201) {
        session.save(result.data.token, result.data.display_name);
        navigate(next.startsWith("/") ? next : "/");
        return;
      }
      feedback.replaceChildren(notice("refused", "auth-error", authMessage(isSignup, result)));
    } catch {
      feedback.replaceChildren(notice("refused", "auth-error", "The service could not be reached. Try again."));
    } finally {
      submit.disabled = false;
    }
  } } },
    field(`${p}-email`, "Email", email),
    field(`${p}-password`, "Password", password, isSignup ? "At least 8 characters." : null),
    isSignup ? field("signup-display-name", "Display name", name, "Shown to you while you are signed in.") : null,
    feedback, submit);
  main.replaceChildren(h("section", { class: "auth sheet stack" },
    h("div", {}, h("h1", { class: "page-title" }, isSignup ? "Create your account" : "Sign in"),
      h("p", { class: "lede" }, "Company profiles with every value tied to its source.")),
    form,
    h("p", { class: "switch" }, isSignup ? "Already have an account? " : "New here? ",
      h("a", { href: (isSignup ? "/login" : "/signup") + location.search }, isSignup ? "Sign in" : "Create an account"))));
}

function authMessage(isSignup, result) {
  if (!isSignup) return result.status === 401 ? "Email or password is incorrect." : "Enter your email and password.";
  if (result.status === 409) return "An account with this email already exists. Sign in instead.";
  if (result.status === 422) return "Check the form: a valid email, a password of at least 8 characters, and a display name of 1 to 100 characters.";
  return "We could not create that account. Check the form and try again.";
}

function loginScreen(main) { authScreen(main, "login"); }
function signupScreen(main) { authScreen(main, "signup"); }

function missingScreen(main) {
  main.replaceChildren(h("section", { class: "sheet" }, h("h1", { class: "page-title" }, "Page not found"),
    h("p", { class: "lede" }, "There is nothing at this address. ", h("a", { href: "/" }, "Go to your dossiers"), ".")));
}

/* ---------- dossier list ---------- */

function listScreen(main, _arg, token) {
  const domain = h("input", { id: "research-domain", type: "text", inputmode: "url", autocomplete: "off", spellcheck: "false", placeholder: "acme-robotics.com", testid: "research-domain" });
  const submit = h("button", { type: "submit", class: "button", testid: "research-submit" }, "Research");
  const feedback = h("div", { "aria-live": "polite" });
  const search = h("input", { id: "dossier-search", type: "search", autocomplete: "off", placeholder: "Domain or legal name", testid: "dossier-search" });
  const results = h("div", {}, h("p", { class: "placeholder" }, "Loading dossiers…"));
  let reads = 0;
  let shown = 0;

  async function load() {
    const seq = ++reads;
    let items;
    try { items = await listAll(search.value); } catch { items = null; }
    if (!isCurrent(token) || seq < shown) return;
    shown = seq;
    if (items === null) {
      results.replaceChildren(notice("failed", null, "The list could not be loaded. Check your connection and search again."));
      return;
    }
    if (!items.length) {
      results.replaceChildren(h("div", { class: "empty", testid: "empty-dossiers" },
        search.value ? `No dossier matches “${search.value}”.` : "No dossiers yet. Research a domain above to start one."));
      return;
    }
    results.replaceChildren(h("ul", { class: "list", testid: "dossier-list" }, items.map((d) =>
      h("li", { class: "list-item", testid: `dossier-item-${d.domain}`, "data-state": d.state },
        h("a", { href: `/dossiers/${d.domain}` },
          h("span", {}, h("span", { class: "domain" }, d.domain), d.legal_name ? h("span", { class: "name" }, ` — ${d.legal_name}`) : null),
          statePill(d.state),
          h("span", { class: "meta" }, d.researched_at ? `Researched ${formatTime(d.researched_at)}` : "Not researched yet", `, ${formatUnits(d.spent_units)} spent`))))));
  }

  const form = h("form", { class: "research-form", novalidate: true, on: { submit: async (event) => {
    event.preventDefault();
    const body = { domain: domain.value };
    const bodyText = JSON.stringify(body);
    if (!pending.research || pending.research.body !== bodyText) pending.research = { body: bodyText, key: newKey() };
    const { key } = pending.research;
    submit.disabled = true;
    try {
      const result = await api("POST", "/dossiers", { body, key });
      if (result.status === 200 || result.status === 202) {
        pending.research = null;
        feedback.replaceChildren();
        navigate(`/dossiers/${result.data.domain}`);
        return;
      }
      pending.research = null;
      if (result.status !== 401) feedback.replaceChildren(notice("refused", "research-error", result.status === 422 ? "That is not a domain we can research. Enter a host name such as example.com, without https:// or a path." : errorText(result, "The research request was refused.")));
    } catch {
      if (isCurrent(token)) feedback.replaceChildren(notice("uncertain", "research-uncertain", "We could not confirm whether this research request went through. Press Research again to retry it safely; it will not start a second build."));
    } finally {
      submit.disabled = false;
    }
  } } }, field("research-domain", "Company domain", domain), submit);

  let debounce = null;
  search.addEventListener("input", () => { clearTimeout(debounce); debounce = setTimeout(load, 200); });

  main.replaceChildren(h("div", { class: "stack" },
    h("section", { class: "sheet" }, h("h1", { class: "page-title" }, "Research a company"), h("div", { class: "stack" }, form),
      h("p", { class: "hint" }, "We search the web for this company and cite every value we find."), feedback),
    h("section", { class: "sheet" },
      h("div", { class: "toolbar" }, h("h2", {}, "Dossiers"), h("div", { class: "search" }, field("dossier-search", "Search", search))),
      results)));
  load();
}

/* ---------- one dossier ---------- */

function citationList(fieldName, citations) {
  return h("ol", { class: "sources", testid: `field-citations-${fieldName}` }, citations.map((c, i) =>
    h("li", { testid: `citation-${fieldName}-${i + 1}`, "data-provider": c.provider },
      h("blockquote", { class: "quote" }, c.excerpt),
      sourceMeta(c.url, c.provider))));
}

function timesLine(f) {
  if (f.value === null || f.value === undefined) return null;
  return h("p", { class: "times" },
    f.true_from ? ["Holds from ", dateElement(f.true_from)] : "Start date not stated",
    f.learned_at ? [". Learned ", h("time", { datetime: f.learned_at }, formatTime(f.learned_at))] : null);
}

function statusLine(domain, anchor, f, distinct, pendingFirst, testid) {
  if (f.status === "contested") {
    return h("div", { class: "status contested", testid }, `Contested — ${distinct}`, h("a", { href: `/dossiers/${domain}/evidence#evidence-${anchor}` }, "Compare sources"));
  }
  const sources = `${f.citations.length} ${f.citations.length === 1 ? "source" : "sources"}`;
  return h("div", { class: `status ${f.status}` }, f.status === "known" ? `Known — ${sources}` : pendingFirst ? "Not researched yet" : "Unknown");
}

function fieldRow(domain, [name, label], f, pendingFirst) {
  const distinct = new Set(f.candidates.map((c) => JSON.stringify(typeof c.value === "string" ? c.value.trim() : c.value))).size;
  const known = f.value !== null && f.value !== undefined;
  return h("div", { class: "row", testid: `field-${name}`, "data-status": f.status },
    h("div", { class: "label" }, label),
    h("div", {},
      known ? h("div", { class: "value", testid: `field-value-${name}`, "data-value": dataValue(f.value) }, formatValue(name, f.value))
        : h("div", { class: "value none" }, pendingFirst ? "Research in progress" : "Not found in sources"),
      statusLine(domain, name, f, `${distinct} values`, pendingFirst, `field-contested-${name}`),
      timesLine(f)),
    citationList(name, f.citations));
}

function executivesRow(domain, f, pendingFirst) {
  const members = f.value || [];
  const contestedTitles = Object.keys(TITLE_LABEL).filter((t) => new Set(f.candidates.filter((c) => c.title === t).map((c) => c.value)).size > 1);
  return h("div", { class: "row", id: "executives", "data-field": "executives", "data-status": f.status },
    h("div", { class: "label" }, "Executives"),
    h("div", {},
      members.length
        ? h("ul", { class: "members" }, members.map((m) => h("li", { "data-title": m.title, "data-value": m.name },
          h("span", { class: "member-title" }, TITLE_LABEL[m.title]), h("span", { class: "value" }, m.name))))
        : h("div", { class: "value none" }, pendingFirst ? "Research in progress" : "No chief financial, operating or technology officer found in sources"),
      statusLine(domain, "executives", f, `sources disagree on ${contestedTitles.map((t) => t.toUpperCase()).join(", ")}`, pendingFirst, null),
      timesLine(f)),
    h("ol", { class: "sources" }, f.citations.map((c) => h("li", { "data-provider": c.provider },
      h("blockquote", { class: "quote" }, c.excerpt), sourceMeta(c.url, c.provider)))));
}

function dossierScreen(main, raw, token) {
  const domain = normaliseDomain(raw);
  let reads = 0;
  let shown = 0;
  let timer = null;
  let data = null;
  let feedback = null;
  const pollAgain = () => { clearTimeout(timer); timer = setTimeout(load, POLL_MS); };

  async function load() {
    const seq = ++reads;
    let result;
    try { result = await api("GET", `/dossiers/${encodeURIComponent(raw)}`); } catch { result = null; }
    if (!isCurrent(token) || seq < shown) return;
    shown = seq;
    if (result === null) {
      if (!data) main.replaceChildren(h("section", { class: "sheet" }, notice("failed", null, "The dossier could not be loaded. Check your connection."), h("button", { type: "button", class: "button secondary", testid: "dossier-reload", on: { click: load } }, "Try again")));
      if (data && data.state === "building") pollAgain();
      return;
    }
    if (result.status === 404 || result.status === 422) { showMissing(); return; }
    if (result.status !== 200) return;
    data = result.data;
    show();
    if (data.state === "building") pollAgain(); else clearTimeout(timer);
  }

  function showMissing() {
    main.replaceChildren(h("section", { class: "sheet stack" },
      h("h1", { class: "page-title", testid: "dossier-domain" }, domain),
      h("div", { testid: "dossier-not-found" }, h("p", {}, "There is no dossier for this domain yet."),
        h("a", { href: "/", class: "button" }, "Research it from your dossiers"))));
  }

  async function refresh(button) {
    if (!pending.refresh[domain]) pending.refresh[domain] = newKey();
    button.disabled = true;
    try {
      const result = await api("POST", `/dossiers/${domain}/refresh`, { key: pending.refresh[domain] });
      if (!isCurrent(token)) return;
      if (result.status === 200 || result.status === 202) {
        delete pending.refresh[domain];
        feedback = null;
        await load();
        return;
      }
      delete pending.refresh[domain];
      feedback = result.status === 401 ? null : notice("refused", "refresh-error", errorText(result, "The refresh was refused."));
      show();
    } catch {
      if (!isCurrent(token)) return;
      feedback = notice("uncertain", "refresh-uncertain", "We could not confirm whether the refresh went through. Press Refresh again to retry it safely; it will not start a second build.");
      show();
    } finally {
      button.disabled = false;
    }
  }

  function show() {
    const d = data;
    const refreshButton = h("button", { type: "button", class: "button", testid: "dossier-refresh" }, "Refresh research");
    refreshButton.addEventListener("click", () => refresh(refreshButton));
    const facts = h("dl", { class: "facts" },
      h("div", {}, h("dt", {}, "Research spend"), h("dd", { testid: "dossier-spent", "data-units": d.spent_units }, formatUnits(d.spent_units))),
      d.researched_at ? h("div", {}, h("dt", {}, "Researched"), h("dd", { testid: "dossier-researched-at" }, timeElement(d.researched_at))) : h("div", {}, h("dt", {}, "Researched"), h("dd", {}, "not yet")));
    const status = d.state === "building"
      ? h("div", {}, h("div", { class: "progress", role: "progressbar", "aria-label": "Research in progress" }), notice("building", null, d.researched_at ? "Researching again. The fields below are from the last completed research." : "Researching the web for this company. Fields appear when research completes."))
      : d.state === "failed"
        ? notice("failed", null, d.researched_at ? "The latest research failed. The fields below are from the last research that completed." : "Research failed before any field could be found. Try refreshing.")
        : null;
    main.replaceChildren(h("article", { class: "sheet" },
      h("div", { class: "dossier-head" },
        h("div", {},
          h("div", { class: "title" }, h("h1", { class: "page-title", testid: "dossier-domain" }, d.domain),
            h("span", { class: `pill ${d.state}` }, h("span", { testid: "dossier-state" }, d.state))),
          facts),
        h("div", { class: "actions" }, refreshButton,
          h("button", { type: "button", class: "button secondary", testid: "dossier-reload", on: { click: load } }, "Reload"),
          h("a", { href: `/dossiers/${d.domain}/evidence`, class: "button secondary", testid: "dossier-evidence-link" }, "All evidence"))),
      h("div", { "aria-live": "polite" }, feedback),
      status,
      h("div", { class: "register" }, FIELDS.map((f) => fieldRow(d.domain, f, d.fields[f[0]], d.state === "building" && !d.researched_at)),
        d.fields.executives ? executivesRow(d.domain, d.fields.executives, d.state === "building" && !d.researched_at) : null)));
  }

  load();
}

/* ---------- evidence ---------- */

function evidenceScreen(main, raw, token) {
  const domain = normaliseDomain(raw);
  (async () => {
    let result;
    try { result = await api("GET", `/dossiers/${encodeURIComponent(raw)}`); } catch { result = null; }
    if (!isCurrent(token)) return;
    if (result === null) { main.replaceChildren(h("section", { class: "sheet" }, notice("failed", null, "The evidence could not be loaded. Check your connection and reload the page."))); return; }
    if (result.status !== 200) {
      main.replaceChildren(h("section", { class: "sheet stack" }, h("h1", { class: "page-title" }, domain),
        h("div", { testid: "dossier-not-found" }, h("p", {}, "There is no dossier for this domain yet."), h("a", { href: "/", class: "button" }, "Go to your dossiers"))));
      return;
    }
    const d = result.data;
    main.replaceChildren(h("article", { class: "sheet" },
      h("p", {}, h("a", { href: `/dossiers/${d.domain}` }, `Back to ${d.domain}`)),
      h("h1", { class: "page-title" }, `Evidence for ${d.domain}`),
      h("p", { class: "lede" }, "Every value the sources support, ranked: company sites and filings first, then news, then data aggregators; newer before older. The selected value is marked."),
      FIELDS.map(([name, label]) => {
        const f = d.fields[name];
        return h("section", { class: "evidence-field", id: `evidence-${name}` },
          h("h2", {}, label, h("span", { class: `status ${f.status}` }, f.status === "contested" ? "Contested" : f.status === "known" ? "Known" : "Unknown")),
          f.candidates.length
            ? h("ol", { class: "candidates", testid: `evidence-${name}` }, f.candidates.map((c, i) =>
              h("li", { class: "candidate", testid: `candidate-${name}-${i + 1}`, "data-value": dataValue(c.value), "data-provider": c.provider,
                "data-kind": c.kind === null ? "" : c.kind, "data-url": c.url, "data-published-at": c.published_at || "", "data-selected": c.selected ? "true" : "false" },
                candidateBody(name, c))))
            : h("ol", { class: "candidates", testid: `evidence-${name}` }, h("li", { class: "empty", testid: `evidence-empty-${name}` }, "No source supports a value for this field.")));
      }),
      d.fields.executives ? executivesEvidence(d.fields.executives) : null));
  })();
}

function candidateBody(name, c) {
  return [
    h("div", { class: "cvalue" }, c.selected ? h("span", { class: "tag selected" }, "Selected") : null, formatValue(name, c.value)),
    h("blockquote", { class: "quote" }, c.excerpt),
    h("dl", { class: "facts" },
      h("div", {}, h("dt", {}, "Source"), h("dd", {}, c.kind ? KIND_LABEL[c.kind] : "Imported, kind not recorded")),
      h("div", {}, h("dt", {}, "Published"), h("dd", {}, c.published_at ? timeElement(c.published_at) : "date not stated")),
      h("div", {}, h("dt", {}, "Holds from"), h("dd", {}, c.true_from ? dateElement(c.true_from) : "not stated")),
      h("div", {}, h("dt", {}, "First learned"), h("dd", {}, c.learned_at ? timeElement(c.learned_at) : "not recorded")),
      h("div", {}, h("dt", {}, "Retrieved"), h("dd", {}, timeElement(c.retrieved_at)))),
    sourceMeta(c.url, c.provider),
  ];
}

function executivesEvidence(f) {
  return h("section", { class: "evidence-field", id: "evidence-executives", "data-field": "executives" },
    h("h2", {}, "Executives", h("span", { class: `status ${f.status}` }, f.status === "contested" ? "Contested" : f.status === "known" ? "Known" : "Unknown")),
    f.candidates.length
      ? Object.keys(TITLE_LABEL).map((title) => {
        const mine = f.candidates.filter((c) => c.title === title);
        return mine.length ? h("div", { class: "title-group", "data-title": title },
          h("h3", {}, TITLE_LABEL[title]),
          h("ol", { class: "candidates" }, mine.map((c) => h("li", { class: "candidate", "data-title": title, "data-value": c.value, "data-selected": c.selected ? "true" : "false" }, candidateBody("ceo", c))))) : null;
      })
      : h("p", { class: "empty" }, "No source names a chief financial, operating or technology officer."));
}

/* ---------- contested ---------- */

function contestedScreen(main, _arg, token) {
  (async () => {
    let items;
    try {
      const listed = await listAll("");
      items = listed === null ? null : [];
      for (let i = 0; listed && i < listed.length; i += 6) {
        const batch = await Promise.all(listed.slice(i, i + 6).map((d) => api("GET", `/dossiers/${d.domain}`)));
        for (const r of batch) {
          if (r.status !== 200) continue;
          for (const [name, label] of FIELDS) {
            const f = r.data.fields[name];
            if (f.status === "contested") items.push({ domain: r.data.domain, name, label, f });
          }
        }
      }
    } catch { items = null; }
    if (!isCurrent(token)) return;
    const intro = [h("h1", { class: "page-title" }, "Contested fields"), h("p", { class: "lede" }, "Fields where sources disagree, across every dossier. The selected value comes first.")];
    if (items === null) { main.replaceChildren(h("section", { class: "sheet" }, intro, notice("failed", null, "The contested fields could not be loaded. Reload the page to try again."))); return; }
    items.sort((a, b) => (a.domain < b.domain ? -1 : a.domain > b.domain ? 1 : FIELDS.findIndex((f) => f[0] === a.name) - FIELDS.findIndex((f) => f[0] === b.name)));
    main.replaceChildren(h("section", { class: "sheet" }, intro,
      items.length
        ? h("ul", { class: "list", testid: "contested-list" }, items.map(({ domain, name, label, f }) => {
          const values = [];
          for (const c of f.candidates) if (!values.some((v) => JSON.stringify(v) === JSON.stringify(c.value))) values.push(c.value);
          return h("li", { class: "list-item contested-item", testid: `contested-item-${domain}-${name}`, "data-value": dataValue(f.value) },
            h("a", { href: `/dossiers/${domain}/evidence` },
              h("div", { class: "head" }, h("strong", {}, domain), h("span", { class: "status contested" }, label), h("span", { class: "exact" }, `field ${name}`)),
              h("div", { class: "values" }, values.map((v, i) => h("span", { class: i === 0 ? "chip selected" : "chip" },
                formatValue(name, v), name === "funding_total" ? h("span", { class: "exact" }, ` (${v} USD)`) : null, i === 0 ? " (selected)" : "")))));
        }))
        : h("div", { class: "empty", testid: "empty-contested" }, "No field is contested. Every researched field has sources that agree.")));
  })();
}

render();
