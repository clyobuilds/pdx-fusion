/* PDX Fusion: repeating events are always shown. Gancio remembers an old 'hide repeating events'
   choice in a cookie; clear it once (and reload) so nobody is stuck with it. */
if (document.cookie.indexOf('showRecurrent=') !== -1) {
  document.cookie = 'showRecurrent=; Max-Age=0; path=/';
  location.reload();
}

/* Follow the device's light/dark setting (dark when unknown).
   Gancio remembers the theme in the 'theme' cookie and draws the page with it on the server, so the cookie is
   kept equal to the device setting: no flash on later visits. If the visitor picks light/dark with the sun/moon
   button, that choice wins ('pdxAutoTheme' no longer matches the cookie) and is kept. */
(function () {
  function getCookie(name) {
    var m = document.cookie.match('(?:^|; )' + name + '=([^;]*)');
    return m ? decodeURIComponent(m[1]) : null;
  }
  function setCookie(name, value) {
    document.cookie = name + '=' + value + '; path=/; max-age=31536000; SameSite=Lax';
  }
  function sync(live) {
    var device = window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    var chosen = getCookie('theme');
    var auto = getCookie('pdxAutoTheme');
    var followsDevice = chosen === null || chosen === auto;
    if (!followsDevice) return;               // the visitor chose a theme: keep it
    setCookie('pdxAutoTheme', device);
    setCookie('theme', device);
    var shown = document.querySelector('.v-application.v-theme--dark') ? 'dark' : 'light';
    var reloaded = false;
    try { reloaded = sessionStorage.getItem('pdxThemeReload') === device; } catch (e) {}
    if (shown !== device && !reloaded) {
      try { sessionStorage.setItem('pdxThemeReload', device); } catch (e) {}
      location.reload();
    }
  }
  sync(false);
  try {
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function () {
      try { sessionStorage.removeItem('pdxThemeReload'); } catch (e) {}
      sync(true);
    });
  } catch (e) {}
})();
