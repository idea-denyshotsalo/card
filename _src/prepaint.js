(() => {
  const root = document.documentElement;
  const params = new URLSearchParams(location.search);
  let lang = params.get("lang");
  if (lang !== "uk" && lang !== "en") {
    try { lang = localStorage.getItem("card-lang"); } catch {}
  }
  if (lang !== "uk" && lang !== "en") {
    const prefs = navigator.languages || [navigator.language || ""];
    lang = prefs.some((l) => /^(uk|ru)\b/i.test(l)) ? "uk" : "en";
  }
  root.dataset.lang = lang;
  root.lang = lang;
  // ?theme= previews another colour; the card's own colour comes from people.json.
  const theme = params.get("theme");
  if (theme && (root.dataset.themes || "").split(" ").includes(theme)) root.dataset.theme = theme;
})();
