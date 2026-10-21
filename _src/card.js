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

  // Full-screen QR for scanning across a table: name above, close hint below, screen kept awake.
  const qr = document.querySelector(".share-qr");
  const openZoom = async () => {
    if (document.querySelector(".zoom")) return;
    const zoom = document.createElement("div");
    zoom.className = "zoom";
    zoom.innerHTML =
      `<div class="zoom-name">${document.querySelector(".pass-name").innerHTML}</div>${qr.innerHTML}` +
      '<div class="zoom-hint"><span data-l="uk">Торкніться, щоб закрити</span><span data-l="en">Tap to close</span></div>';
    let lock = null;
    const close = () => {
      zoom.remove();
      document.removeEventListener("keydown", onKey);
      lock?.release().catch(() => {});
    };
    const onKey = (e) => { if (e.key === "Escape") close(); };
    zoom.addEventListener("click", close);
    document.addEventListener("keydown", onKey);
    document.body.append(zoom);
    try { lock = await navigator.wakeLock?.request("screen"); } catch {}
    if (!zoom.isConnected) lock?.release().catch(() => {});
  };
  qr?.addEventListener("click", openZoom);
  // ?qr=1 opens the big code at once: add the card to the home screen from that link for a one-tap QR.
  if (qr && new URLSearchParams(location.search).has("qr")) openZoom();

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
