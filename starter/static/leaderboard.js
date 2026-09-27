(function (root) {
  const STORAGE_KEY = 'sudokuLeaderboard';
  const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);

  function getStorage() {
    try {
      return root.localStorage || null;
    } catch (_error) {
      return null;
    }
  }

  function isValidScore(score) {
    return score !== null &&
      typeof score === 'object' &&
      typeof score.playerName === 'string' &&
      score.playerName.trim().length > 0 &&
      Number.isInteger(score.timeSeconds) &&
      score.timeSeconds >= 0 &&
      typeof score.formattedTime === 'string' &&
      DIFFICULTIES.has(score.difficulty) &&
      Number.isInteger(score.hintsUsed) &&
      score.hintsUsed >= 0 &&
      (score.gameId === undefined || typeof score.gameId === 'string');
  }

  function sortAndLimit(scores) {
    return scores.sort((left, right) => left.timeSeconds - right.timeSeconds).slice(0, 10);
  }

  function loadScores() {
    const storage = getStorage();
    if (!storage) return [];

    try {
      const stored = storage.getItem(STORAGE_KEY);
      if (stored === null) return [];
      const scores = JSON.parse(stored);
      if (!Array.isArray(scores) || !scores.every(isValidScore)) return [];
      const topScores = sortAndLimit(scores);
      if (scores.length > topScores.length) {
        storage.setItem(STORAGE_KEY, JSON.stringify(topScores));
      }
      return topScores;
    } catch (_error) {
      return [];
    }
  }

  function addScore(score) {
    const scores = loadScores();
    if (!isValidScore(score)) return scores;
    if (score.gameId && scores.some((entry) => entry.gameId === score.gameId)) return scores;

    const updatedScores = sortAndLimit([...scores, score]);
    const storage = getStorage();
    if (storage) {
      try {
        storage.setItem(STORAGE_KEY, JSON.stringify(updatedScores));
      } catch (_error) {
        return updatedScores;
      }
    }
    return updatedScores;
  }

  function render() {
    const scores = loadScores();
    const body = root.document.getElementById('leaderboard-scores');
    const emptyMessage = root.document.getElementById('leaderboard-empty');
    body.replaceChildren();
    emptyMessage.hidden = scores.length > 0;

    scores.forEach((score, index) => {
      const row = root.document.createElement('tr');
      [index + 1, score.playerName, score.formattedTime, score.difficulty, score.hintsUsed].forEach((value) => {
        const cell = root.document.createElement('td');
        cell.textContent = value;
        row.appendChild(cell);
      });
      body.appendChild(row);
    });
  }

  root.Leaderboard = {addScore, loadScores, render};
})(typeof globalThis === 'undefined' ? this : globalThis);