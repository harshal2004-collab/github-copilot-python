const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const test = require('node:test');

const source = fs.readFileSync(require.resolve('../static/leaderboard.js'), 'utf8');

function createStorage(initialValue = null) {
  const values = new Map();
  if (initialValue !== null) values.set('sudokuLeaderboard', initialValue);
  return {
    values,
    localStorage: {
      getItem: (key) => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, value)
    }
  };
}

function loadModule(context) {
  vm.runInNewContext(source, context);
  return context.Leaderboard;
}

function score(overrides = {}) {
  return {
    gameId: `game-${Math.random()}`,
    playerName: 'Ada',
    timeSeconds: 42,
    formattedTime: '00:42',
    difficulty: 'hard',
    hintsUsed: 2,
    ...overrides
  };
}

test('saves completed score details and reloads them from storage', () => {
  const context = createStorage();
  const leaderboard = loadModule(context);
  leaderboard.addScore(score());

  const reloaded = loadModule(context);
  const [saved] = reloaded.loadScores();
  assert.equal(saved.playerName, 'Ada');
  assert.equal(saved.difficulty, 'hard');
  assert.equal(saved.hintsUsed, 2);
  assert.equal(saved.formattedTime, '00:42');
});

test('sorts scores fastest first and keeps only ten', () => {
  const context = createStorage();
  const leaderboard = loadModule(context);
  for (let seconds = 12; seconds >= 1; seconds--) {
    leaderboard.addScore(score({gameId: `game-${seconds}`, timeSeconds: seconds}));
  }

  const scores = leaderboard.loadScores();
  assert.equal(scores.length, 10);
  assert.deepEqual(Array.from(scores, (entry) => entry.timeSeconds), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
});

test('returns an empty leaderboard for malformed or invalid stored data', () => {
  assert.deepEqual(Array.from(loadModule(createStorage('{broken')).loadScores()), []);
  assert.deepEqual(Array.from(loadModule(createStorage('{"not":"scores"}')).loadScores()), []);
});

test('ignores duplicate submissions for the same game', () => {
  const leaderboard = loadModule(createStorage());
  const completedGame = score({gameId: 'one-game'});
  leaderboard.addScore(completedGame);
  leaderboard.addScore(completedGame);

  assert.equal(leaderboard.loadScores().length, 1);
});

test('rejects incomplete or invalid score records', () => {
  const leaderboard = loadModule(createStorage());
  leaderboard.addScore({playerName: 'Ada', timeSeconds: 20});
  leaderboard.addScore(score({timeSeconds: -1}));

  assert.deepEqual(Array.from(leaderboard.loadScores()), []);
});