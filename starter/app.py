from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0
}

def _is_valid_board(board):
    return (
        isinstance(board, list)
        and len(board) == sudoku_logic.SIZE
        and all(
            isinstance(row, list)
            and len(row) == sudoku_logic.SIZE
            and all(type(value) is int and 0 <= value <= sudoku_logic.SIZE for value in row)
            for row in board
        )
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty', 'medium').lower()
    if difficulty not in sudoku_logic.DIFFICULTY_CONFIG:
        return jsonify({'error': 'Invalid difficulty'}), 400
    legacy_clues = request.args.get('clues')
    if legacy_clues is not None and 'difficulty' not in request.args:
        try:
            puzzle, solution = sudoku_logic.generate_puzzle(clues=int(legacy_clues))
        except ValueError:
            return jsonify({'error': 'Invalid clue count'}), 400
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if not _is_valid_board(board):
        return jsonify({'error': 'Invalid board'}), 400

    return jsonify(sudoku_logic.evaluate_board(board, puzzle, solution))

@app.route('/hint', methods=['POST'])
def give_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    if not _is_valid_board(board):
        return jsonify({'error': 'Invalid board'}), 400

    empty_cell = next(
        (
            (row, col)
            for row in range(sudoku_logic.SIZE)
            for col in range(sudoku_logic.SIZE)
            if puzzle[row][col] == sudoku_logic.EMPTY and board[row][col] == sudoku_logic.EMPTY
        ),
        None,
    )
    if empty_cell is None:
        return jsonify({
            'error': 'No empty cells available for a hint',
            'hints_used': CURRENT['hints_used'],
        }), 409

    row, col = empty_cell
    value = solution[row][col]
    CURRENT['hints_used'] += 1
    hinted_board = [line.copy() for line in board]
    hinted_board[row][col] = value
    solved = sudoku_logic.evaluate_board(hinted_board, puzzle, solution)['solved']
    return jsonify({
        'row': row,
        'col': col,
        'value': value,
        'locked': True,
        'hints_used': CURRENT['hints_used'],
        'solved': solved,
    })

if __name__ == '__main__':
    app.run(debug=True)