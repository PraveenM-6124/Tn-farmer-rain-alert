/**
 * Tamil Nadu Farmer Rain Alert - Client-side Theme and Language Handler
 * Zero-dependency vanilla JS for fast execution on low-end Android / 3G connections.
 */

(function () {
  'use strict';

  var THEME_KEY = 'tn_farmer_theme';
  var LANG_KEY = 'tn_farmer_lang';

  // 1. Theme Management (☀️ / 🌙)
  function getPreferredTheme() {
    var storedTheme = localStorage.getItem(THEME_KEY);
    if (storedTheme === 'dark' || storedTheme === 'light') {
      return storedTheme;
    }
    // Respect system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    // Also save in cookie for SSR hydration
    document.cookie = THEME_KEY + '=' + theme + ';path=/;max-age=31536000;SameSite=Lax';
    
    // Update theme toggle button icon/text if present
    var themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      if (theme === 'dark') {
        themeBtn.setAttribute('aria-label', 'Switch to light mode');
        themeBtn.innerHTML = '<span>☀️</span> <span class="d-none d-sm-inline">Light</span>';
      } else {
        themeBtn.setAttribute('aria-label', 'Switch to dark mode');
        themeBtn.innerHTML = '<span>🌙</span> <span class="d-none d-sm-inline">Dark</span>';
      }
    }
  }

  function toggleTheme() {
    var currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    var newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    localStorage.setItem(THEME_KEY, newTheme);
    applyTheme(newTheme);
  }

  // 2. Language Selection Handler
  function selectLanguage(lang) {
    if (lang !== 'ta' && lang !== 'en') {
      lang = 'ta';
    }
    localStorage.setItem(LANG_KEY, lang);
    document.cookie = LANG_KEY + '=' + lang + ';path=/;max-age=31536000;SameSite=Lax';

    // Navigate to homepage or current page with updated lang
    window.location.href = '/?lang=' + encodeURIComponent(lang);
  }

  // Initialize on script execution
  var initialTheme = getPreferredTheme();
  applyTheme(initialTheme);

  // Bind events once DOM is loaded
  document.addEventListener('DOMContentLoaded', function () {
    var themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) {
      themeBtn.addEventListener('click', toggleTheme);
      // Re-run applyTheme to ensure correct icon text
      applyTheme(getPreferredTheme());
    }

    // Listen to system theme changes if user hasn't explicitly set one
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!localStorage.getItem(THEME_KEY)) {
          applyTheme(e.matches ? 'dark' : 'light');
        }
      });
    }
  });

  // Expose global methods
  window.TNFarmer = {
    selectLanguage: selectLanguage,
    toggleTheme: toggleTheme,
    applyTheme: applyTheme
  };
})();
