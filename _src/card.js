(() => {
  const root = document.documentElement;
  const langButtons = document.querySelectorAll("[data-set-lang]");
  const setLang = (lang) => {
    root.dataset.lang = lang;
    root.lang = lang;
    document.title = root.dataset[lang === "en" ? "titleEn" : "titleUk"];
    langButtons.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.setLang === lang)));
  };
  langButtons.forEach((b) => b.addEventListener("click", () => {
    setLang(b.dataset.setLang);
    try { localStorage.setItem("card-lang", b.dataset.setLang); } catch {}
  }));
  setLang(root.dataset.lang);

  const qr = document.querySelector(".share-qr");
  qr?.addEventListener("click", () => {
    const zoom = document.createElement("div");
    zoom.className = "zoom";
    zoom.innerHTML = qr.innerHTML;
    const close = () => { zoom.remove(); document.removeEventListener("keydown", onKey); };
    const onKey = (e) => { if (e.key === "Escape") close(); };
    zoom.addEventListener("click", close);
    document.addEventListener("keydown", onKey);
    document.body.append(zoom);
  });

  const share = document.querySelector(".share-btn");
  share?.addEventListener("click", async () => {
    const url = document.querySelector('link[rel="canonical"]').href;
    if (navigator.share) {
      try { await navigator.share({ title: document.title, url }); } catch {}
      return;
    }
    const label = share.querySelector(`[data-l="${root.dataset.lang}"]`);
    try {
      await navigator.clipboard.writeText(url);
      const prev = label.textContent;
      label.textContent = label.dataset.done;
      setTimeout(() => { label.textContent = prev; }, 2000);
    } catch {
      window.prompt("", url);
    }
  });
})();
