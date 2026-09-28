(() => {
  let lang = new URLSearchParams(location.search).get("lang");
  if (lang !== "uk" && lang !== "en") {
    try { lang = localStorage.getItem("card-lang"); } catch {}
  }
  if (lang !== "uk" && lang !== "en") {
    const prefs = navigator.languages || [navigator.language || ""];
    lang = prefs.some((l) => /^(uk|ru)\b/i.test(l)) ? "uk" : "en";
  }
  document.documentElement.dataset.lang = lang;
  document.documentElement.lang = lang;
})();
