(() => {
  const data = JSON.parse(document.getElementById("guide-data").textContent);
  const root = document.documentElement;
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => [...document.querySelectorAll(sel)];
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch {} },
  };

  const qrSvg = (q) =>
    `<svg viewBox="0 0 ${q.n} ${q.n}" shape-rendering="crispEdges" aria-hidden="true"><rect width="${q.n}" height="${q.n}" fill="#fff"/><path class="qr-d" d="${q.d}"/></svg>`;

  // ── Device ─────────────────────────────────────────────────────
  const ua = navigator.userAgent;
  const isIOS = /iPhone|iPad|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
  const isAndroid = /Android/.test(ua);
  const setOS = (os) => {
    root.dataset.os = os;
    $$(".g-os [data-os]").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.os === os)));
    if (os === "android") renderPreview();
  };
  $$(".g-os [data-os]").forEach((b) => b.addEventListener("click", () => setOS(b.dataset.os)));
  $(".g-handoff").hidden = isIOS || isAndroid;

  // ── Person + state ─────────────────────────────────────────────
  const select = $("#person");
  const byId = Object.fromEntries(data.people.map((p) => [p.id, p]));
  let person = byId[new URLSearchParams(location.search).get("p")] || byId[store.get("guide-person")] || data.people[0];
  let cardLang = "uk";
  let cardTheme = person.theme;
  let done = new Set();

  const fullName = (p, lang) => `${p.first[lang]} ${p.last[lang]}`;
  const values = () => ({
    name: fullName(person, "uk"),
    title: person.title.uk,
    url: person.url,
    urlEn: `${person.url}?lang=en`,
    cardName: fullName(person, cardLang),
    cardTitle: person.title[cardLang],
    company: data.company,
    cardColor: data.themes[cardTheme].dark.toUpperCase(),
    color: data.themes[cardTheme].dark.toUpperCase(),
    done: String(done.size),
  });

  const bind = () => {
    const v = values();
    $$("[data-bind]").forEach((el) => { el.textContent = v[el.dataset.bind]; });
    $$("[data-href]").forEach((el) => { el.href = v[el.dataset.href]; });
    $$("[data-qr]").forEach((el) => { el.innerHTML = qrSvg(person[el.dataset.qr]); });
    $$("[data-card-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.cardLang === cardLang)));
    $$("[data-card-theme]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.cardTheme === cardTheme)));
    $$("[data-theme-link]").forEach((a) => {
      a.href = `${person.url}?theme=${a.dataset.themeLink}`;
      a.setAttribute("aria-current", String(a.dataset.themeLink === person.theme));
    });
    $$(".swatch").forEach((s) => { s.style.background = data.themes[cardTheme].dark; });
    $(".g-bar i").style.width = `${(done.size / steps.length) * 100}%`;
    $(".g-finish").hidden = done.size < steps.length;
    if (root.dataset.os === "android") renderPreview();
  };

  const choose = (p) => {
    person = p;
    cardTheme = p.theme;
    root.dataset.theme = p.theme;
    select.value = p.id;
    store.set("guide-person", p.id);
    history.replaceState(null, "", `?p=${encodeURIComponent(p.id)}`);
    try { done = new Set(JSON.parse(store.get(`guide-done:${p.id}`) || "[]")); } catch { done = new Set(); }
    steps.forEach((s) => s.classList.toggle("done", done.has(s.dataset.step)));
    open(steps.find((s) => !done.has(s.dataset.step)));
    bind();
  };
  select.addEventListener("change", () => choose(byId[select.value]));

  // ── Steps accordion ────────────────────────────────────────────
  const steps = $$(".step");
  const open = (step) => steps.forEach((s) => {
    const on = s === step;
    s.classList.toggle("open", on);
    s.querySelector(".step-h").setAttribute("aria-expanded", String(on));
  });
  steps.forEach((s) => {
    s.querySelector(".step-h").addEventListener("click", () => open(s.classList.contains("open") ? null : s));
    s.querySelector(".step-done").addEventListener("click", () => {
      done.add(s.dataset.step);
      s.classList.add("done");
      store.set(`guide-done:${person.id}`, JSON.stringify([...done]));
      const next = steps.find((x) => !done.has(x.dataset.step));
      open(next);
      bind();
      (next || $(".g-finish")).scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  $$("[data-card-lang]").forEach((b) => b.addEventListener("click", () => { cardLang = b.dataset.cardLang; bind(); }));
  $$("[data-card-theme]").forEach((b) => b.addEventListener("click", () => { cardTheme = b.dataset.cardTheme; bind(); }));

  // ── Copy ───────────────────────────────────────────────────────
  const copyText = async (text) => {
    try { await navigator.clipboard.writeText(text); return true; } catch {}
    const ta = Object.assign(document.createElement("textarea"), { value: text, readOnly: true });
    ta.style.cssText = "position:fixed;opacity:0";
    document.body.append(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand("copy"); } catch {}
    ta.remove();
    return ok;
  };
  $$("[data-copy]").forEach((b) => b.addEventListener("click", async () => {
    if (!(await copyText(values()[b.dataset.copy]))) return;
    const label = b.querySelector("span");
    b.classList.add("ok");
    label.textContent = "Скопійовано";
    setTimeout(() => { b.classList.remove("ok"); label.textContent = "Копіювати"; }, 1600);
  }));

  // ── Canvas: wallet card + logo ────────────────────────────────
  const drawMark = (g, d, x, y, h, color) => {
    g.save();
    g.translate(x, y);
    g.scale(h / 1080, h / 1080);
    g.fillStyle = color;
    g.fill(new Path2D(d));
    g.restore();
  };
  const fit = (g, text, weight, size, min, maxW) => {
    for (; size > min; size -= 2) {
      g.font = `${weight} ${size}px Inter, system-ui, sans-serif`;
      if (g.measureText(text).width <= maxW) break;
    }
    return size;
  };

  const walletCanvas = async () => {
    await Promise.all(["700 96px Inter", "500 40px Inter", "600 26px Inter"].map((f) => document.fonts.load(f)));
    const W = 1080, H = 1350, pad = 84;
    const c = Object.assign(document.createElement("canvas"), { width: W, height: H });
    const g = c.getContext("2d");
    const theme = data.themes[cardTheme];
    g.fillStyle = theme.dark;
    g.fillRect(0, 0, W, H);
    drawMark(g, data.brand.sign, W * 0.3, -H * 0.06, H * 1.12, theme.mark);
    drawMark(g, data.brand.logo, pad, pad, 54, "#ffffff");

    const tag = cardLang === "en" ? "BUSINESS CARD" : "ВІЗИТКА";
    g.font = "600 26px Inter, system-ui, sans-serif";
    if ("letterSpacing" in g) g.letterSpacing = "4px";
    g.fillStyle = "rgba(237,233,228,.76)";
    g.textAlign = "right";
    g.fillText(tag, W - pad, pad + 38);
    const tagW = g.measureText(tag).width;
    if ("letterSpacing" in g) g.letterSpacing = "0px";
    const t = Math.tan((11 * Math.PI) / 180), bx = W - pad - tagW - 62, by = pad + 17;
    g.save();
    g.transform(1, 0, -t, 1, t * (by + 11), 0);
    g.fillStyle = "#eb3c28";
    g.fillRect(bx, by, 40, 22);
    g.restore();

    g.textAlign = "left";
    g.fillStyle = "#ffffff";
    const first = person.first[cardLang], last = person.last[cardLang];
    const size = Math.min(fit(g, first, 700, 100, 56, W - 2 * pad), fit(g, last, 700, 100, 56, W - 2 * pad));
    g.font = `700 ${size}px Inter, system-ui, sans-serif`;
    g.fillText(first, pad, 300);
    g.fillText(last, pad, 300 + size * 0.98);
    g.fillStyle = "rgba(237,233,228,.8)";
    fit(g, person.title[cardLang], 500, 40, 26, W - 2 * pad);
    g.fillText(person.title[cardLang], pad, 300 + size * 0.98 + 70);

    const q = person.qr, box = 660, bx0 = (W - box) / 2, by0 = 560;
    g.fillStyle = "#ffffff";
    g.beginPath();
    g.roundRect(bx0, by0, box, box, 36);
    g.fill();
    const m = Math.floor((box - 40) / q.n), qx = Math.round(bx0 + (box - m * q.n) / 2), qy = Math.round(by0 + (box - m * q.n) / 2);
    g.save();
    g.translate(qx, qy);
    g.scale(m, m);
    g.fillStyle = theme.dark;
    g.fill(new Path2D(q.d));
    g.restore();

    g.fillStyle = "rgba(237,233,228,.85)";
    g.textAlign = "center";
    fit(g, person.url.replace(/^https:\/\//, "").replace(/\/$/, ""), 500, 32, 22, W - 2 * pad);
    g.fillText(person.url.replace(/^https:\/\//, "").replace(/\/$/, ""), W / 2, by0 + box + 72);
    return c;
  };

  const logoCanvas = () => {
    const c = Object.assign(document.createElement("canvas"), { width: 600, height: 157 });
    drawMark(c.getContext("2d"), data.brand.logo, 0, 0, 157, "#ffffff");
    return c;
  };

  let previewToken = 0;
  const renderPreview = async () => {
    const token = ++previewToken;
    const c = await walletCanvas();
    if (token === previewToken) $("[data-wallet-preview]").src = c.toDataURL("image/png");
  };

  const save = (canvas, name) => canvas.toBlob((blob) => {
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: name });
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  }, "image/png");

  $$("[data-download]").forEach((b) => b.addEventListener("click", async () => {
    if (b.dataset.download === "logo") save(logoCanvas(), "idea-logo.png");
    else save(await walletCanvas(), `vizytka-idea-${person.id}.png`);
  }));

  setOS(isAndroid ? "android" : "ios");
  choose(person);
})();
