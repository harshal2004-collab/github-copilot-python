// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let latestValidation = 0;
let hintCount = 0;
let elapsedSeconds = 0;
let timerInterval = null;
let scoreSubmitted = false;
let activeGameId = '';
let activeDifficulty = 'medium';

function createGameId() {
  return typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function formatElapsedTime(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = seconds % 60;
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function submitCompletedScore() {
  if (scoreSubmitted) return;
  scoreSubmitted = true;
  const playerName = document.getElementById('player-name').value.trim() || 'Player';
  window.Leaderboard.addScore({
    gameId: activeGameId,
    playerName,
    timeSeconds: elapsedSeconds,
    formattedTime: formatElapsedTime(elapsedSeconds),
    difficulty: activeDifficulty,
    hintsUsed: hintCount
  });
  window.Leaderboard.render();
}

function renderTimer() {
  const minutes = Math.floor(elapsedSeconds / 60).toString().padStart(2, '0');
  const seconds = (elapsedSeconds % 60).toString().padStart(2, '0');
  document.getElementById('timer').innerText = `${minutes}:${seconds}`;
}

function stopTimer() {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  renderTimer();
  timerInterval = setInterval(() => {
    elapsedSeconds++;
    renderTimer();
  }, 1000);
}

function getCurrentBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let row = 0; row < SIZE; row++) {
    board[row] = [];
    for (let col = 0; col < SIZE; col++) {
      const value = inputs[row * SIZE + col].value;
      board[row][col] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

async function validateBoard() {
  const validationId = ++latestValidation;
  const response = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: getCurrentBoard()})
  });
  const data = await response.json();
  if (validationId !== latestValidation) return;

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const incorrect = new Set((data.incorrect || []).map(([row, col]) => row * SIZE + col));
  const message = document.getElementById('message');
  message.classList.toggle('success', Boolean(data.solved));
  for (let index = 0; index < inputs.length; index++) {
    const input = inputs[index];
    if (input.disabled) continue;
    input.classList.toggle('incorrect', incorrect.has(index));
    input.setAttribute('aria-invalid', incorrect.has(index) ? 'true' : 'false');
  }

  if (data.error) {
    message.innerText = data.error;
  } else if (data.solved) {
    stopTimer();
    submitCompletedScore();
    message.innerText = 'Congratulations! You solved it!';
  } else if (data.incorrect.length && data.incomplete) {
    message.innerText = 'Some entries are incorrect, and the puzzle is incomplete.';
  } else if (data.incorrect.length) {
    message.innerText = 'Some entries are incorrect.';
  } else if (data.incomplete) {
    message.innerText = 'The puzzle is incomplete.';
  } else {
    message.innerText = '';
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.dataset.location = `Row ${i + 1}, column ${j + 1}`;
      input.setAttribute('aria-label', `${input.dataset.location}, editable cell`);
      if ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 1) {
        input.classList.add('box-shade');
      }
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        e.target.classList.remove('incorrect');
        e.target.setAttribute('aria-invalid', 'false');
        document.getElementById('message').innerText = '';
        document.getElementById('message').classList.remove('success');
        validateBoard();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
        inp.setAttribute('aria-label', `${inp.dataset.location}, prefilled and locked`);
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.setAttribute('aria-label', `${inp.dataset.location}, editable cell`);
      }
    }
  }
}

async function newGame() {
  latestValidation++;
  document.getElementById('hint').disabled = true;
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok || !data.puzzle) {
    const message = document.getElementById('message');
    message.classList.remove('success');
    message.innerText = data.error || 'Unable to start a new game.';
    document.getElementById('hint').disabled = false;
    return;
  }
  renderPuzzle(data.puzzle);
  startTimer();
  activeGameId = createGameId();
  activeDifficulty = data.difficulty;
  scoreSubmitted = false;
  hintCount = 0;
  document.getElementById('hint-count').innerText = `Hints used: ${hintCount}`;
  const message = document.getElementById('message');
  message.innerText = '';
  message.classList.remove('success');
  document.getElementById('hint').disabled = false;
}

async function requestHint() {
  const hintButton = document.getElementById('hint');
  const message = document.getElementById('message');
  hintButton.disabled = true;
  try {
    const response = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: getCurrentBoard()})
    });
    const data = await response.json();
    if (!response.ok) {
      message.classList.remove('success');
      message.innerText = data.error || 'Unable to get a hint.';
      return;
    }

    const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
    const input = inputs[data.row * SIZE + data.col];
    input.value = data.value;
    input.disabled = data.locked;
    input.classList.remove('incorrect');
    input.classList.add('hinted');
    input.setAttribute('aria-invalid', 'false');
    input.setAttribute('aria-label', `${input.dataset.location}, hinted value ${data.value}${data.locked ? ', locked' : ''}`);
    hintCount = data.hints_used;
    document.getElementById('hint-count').innerText = `Hints used: ${hintCount}`;
    await validateBoard();
  } finally {
    hintButton.disabled = false;
  }
}

// Wire buttons
window.addEventListener('load', () => {
  window.Leaderboard.render();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', validateBoard);
  document.getElementById('hint').addEventListener('click', requestHint);
  // initialize
  newGame();
});