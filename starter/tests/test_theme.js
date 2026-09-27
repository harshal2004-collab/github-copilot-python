const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync(require.resolve('../static/theme.js'), 'utf8');

function loadTheme(initialTheme = null) {
  const values = new Map();
  if (initialTheme !== null) values.set('sudokuTheme', initialTheme);
  const documentListeners = {};
  const buttonListeners = {};
  const button = {
    attributes: {},
    addEventListener: (type, listener) => { buttonListeners[type] = listener; },
    setAttribute: (name, value) => { button.attributes[name] = value; },
    textContent: ''
  };
  const context = {
    document: {
      documentElement: {dataset: {}},
      addEventListener: (type, listener) => { documentListeners[type] = listener; },
      getElementById: () => button
    },
    window: {
      localStorage: {
        getItem: (key) => values.get(key) ?? null,
        setItem: (key, value) => values.set(key, value)
      }
    }
  };

  vm.runInNewContext(source, context);
  documentListeners.DOMContentLoaded();
  return {button, buttonListeners, context, values};
}

test('restores the saved theme and persists subsequent toggles', () => {
  const {button, buttonListeners, context, values} = loadTheme('dark');

  assert.equal(context.document.documentElement.dataset.theme, 'dark');
  assert.equal(button.textContent, 'Light mode');
  assert.equal(button.attributes['aria-pressed'], 'true');

  buttonListeners.click();
  assert.equal(context.document.documentElement.dataset.theme, 'light');
  assert.equal(values.get('sudokuTheme'), 'light');
  assert.equal(button.textContent, 'Dark mode');
  assert.equal(button.attributes['aria-pressed'], 'false');
});

test('defaults to light mode and persists enabling dark mode', () => {
  const {button, buttonListeners, context, values} = loadTheme();

  assert.equal(context.document.documentElement.dataset.theme, 'light');
  assert.equal(button.textContent, 'Dark mode');

  buttonListeners.click();
  assert.equal(context.document.documentElement.dataset.theme, 'dark');
  assert.equal(values.get('sudokuTheme'), 'dark');
});