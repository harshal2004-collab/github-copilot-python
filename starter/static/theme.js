(() => {
  const storageKey = 'sudokuTheme';
  const root = document.documentElement;
  const savedTheme = window.localStorage.getItem(storageKey);
  root.dataset.theme = savedTheme === 'dark' ? 'dark' : 'light';

  document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('theme-toggle');
    if (!toggle) return;

    const updateToggle = () => {
      const darkMode = root.dataset.theme === 'dark';
      toggle.setAttribute('aria-pressed', String(darkMode));
      toggle.textContent = darkMode ? 'Light mode' : 'Dark mode';
    };

    updateToggle();
    toggle.addEventListener('click', () => {
      root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
      window.localStorage.setItem(storageKey, root.dataset.theme);
      updateToggle();
    });
  });
})();