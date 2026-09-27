import pytest

import sudoku_logic


KNOWN_PUZZLE = (
    "530070000",
    "600195000",
    "098000060",
    "800060003",
    "400803001",
    "700020006",
    "060000280",
    "000419005",
    "000080079",
)

KNOWN_SOLUTION = (
    "534678912",
    "672195348",
    "198342567",
    "859761423",
    "426853791",
    "713924856",
    "961537284",
    "287419635",
    "345286179",
)


def _parse_board(rows):
    return [[int(value) for value in row] for row in rows]


@pytest.fixture(scope="module")
def generated_puzzle():
    return sudoku_logic.generate_puzzle(clues=35)


def test_create_empty_board_has_nine_rows_of_nine_empty_cells():
    board = sudoku_logic.create_empty_board()

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(value == sudoku_logic.EMPTY for row in board for value in row)


def test_is_safe_accepts_candidate_without_conflicts():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5)


@pytest.mark.parametrize(
    ("occupied_row", "occupied_col"),
    [(0, 1), (1, 0), (1, 1)],
    ids=["row", "column", "box"],
)
def test_is_safe_rejects_row_column_and_box_conflicts(occupied_row, occupied_col):
    board = sudoku_logic.create_empty_board()
    board[occupied_row][occupied_col] = 5

    assert not sudoku_logic.is_safe(board, 0, 0, 5)


def test_is_valid_board_accepts_completed_board(solved_board):
    assert sudoku_logic.is_valid_board(solved_board)


def test_is_valid_board_rejects_duplicate_in_row():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 5

    assert not sudoku_logic.is_valid_board(board)


def test_is_valid_board_rejects_duplicate_in_column():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[1][0] = 5

    assert not sudoku_logic.is_valid_board(board)


def test_is_valid_board_rejects_duplicate_in_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[1][1] = 5

    assert not sudoku_logic.is_valid_board(board)


def test_evaluate_board_accepts_correct_entry_on_incomplete_board(solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = sudoku_logic.EMPTY
    board = [row.copy() for row in puzzle]
    board[0][0] = solved_board[0][0]
    board[0][1] = sudoku_logic.EMPTY

    result = sudoku_logic.evaluate_board(board, puzzle, solved_board)

    assert result == {
        "incorrect": [],
        "incomplete_cells": [[0, 1]],
        "incomplete": True,
        "solved": False,
    }


def test_evaluate_board_reports_incorrect_nonempty_entry(solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = sudoku_logic.EMPTY
    board = [row.copy() for row in puzzle]
    board[0][0] = solved_board[0][0] % sudoku_logic.SIZE + 1

    result = sudoku_logic.evaluate_board(board, puzzle, solved_board)

    assert result["incorrect"] == [[0, 0]]
    assert result["incomplete_cells"] == []
    assert result["incomplete"] is False
    assert result["solved"] is False


def test_evaluate_board_reports_empty_cells_as_incomplete(solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = sudoku_logic.EMPTY
    board = [row.copy() for row in solved_board]
    board[0][0] = sudoku_logic.EMPTY

    result = sudoku_logic.evaluate_board(board, puzzle, solved_board)

    assert result["incorrect"] == []
    assert result["incomplete_cells"] == [[0, 0]]
    assert result["incomplete"] is True
    assert result["solved"] is False


def test_evaluate_board_detects_completely_solved_board(solved_board):
    result = sudoku_logic.evaluate_board(solved_board, solved_board, solved_board)

    assert result == {
        "incorrect": [],
        "incomplete_cells": [],
        "incomplete": False,
        "solved": True,
    }


def test_evaluate_board_preserves_prefilled_values(solved_board):
    puzzle = [row.copy() for row in solved_board]
    board = [row.copy() for row in solved_board]
    board[0][0] = board[0][0] % sudoku_logic.SIZE + 1
    original_puzzle = [row.copy() for row in puzzle]

    result = sudoku_logic.evaluate_board(board, puzzle, solved_board)

    assert result["incorrect"] == []
    assert result["solved"] is False
    assert puzzle == original_puzzle
    assert board[0][0] != puzzle[0][0]


def test_solve_returns_expected_solution_for_valid_puzzle():
    puzzle = _parse_board(KNOWN_PUZZLE)
    expected_solution = _parse_board(KNOWN_SOLUTION)

    assert sudoku_logic.solve(puzzle) == expected_solution


def test_solve_returns_none_for_unsolvable_puzzle():
    puzzle = _parse_board(KNOWN_PUZZLE)
    puzzle[0][2] = 1

    assert sudoku_logic.is_valid_board(puzzle)
    assert sudoku_logic.solve(puzzle) is None


def test_count_solutions_returns_one_for_unique_puzzle():
    puzzle = _parse_board(KNOWN_PUZZLE)

    assert sudoku_logic.count_solutions(puzzle) == 1


def test_count_solutions_returns_two_for_multiple_solution_puzzle():
    puzzle = sudoku_logic.create_empty_board()
    puzzle[0][0] = 1

    assert sudoku_logic.count_solutions(puzzle) == 2


def test_generate_puzzle_returns_valid_solution_and_matching_clues(generated_puzzle):
    puzzle, solution = generated_puzzle
    expected_values = set(range(1, sudoku_logic.SIZE + 1))

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in solution)
    assert sudoku_logic.is_valid_board(puzzle)
    assert sudoku_logic.is_valid_board(solution)
    assert all(set(row) == expected_values for row in solution)
    assert all(
        {solution[row_index][col_index] for row_index in range(sudoku_logic.SIZE)}
        == expected_values
        for col_index in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            solution[row_index][col_index]
            for row_index in range(box_row, box_row + 3)
            for col_index in range(box_col, box_col + 3)
        }
        == expected_values
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )
    assert any(value == sudoku_logic.EMPTY for row in puzzle for value in row)
    assert all(
        value == sudoku_logic.EMPTY or value == solution[row_index][col_index]
        for row_index, row in enumerate(puzzle)
        for col_index, value in enumerate(row)
    )


def test_generated_puzzle_has_exactly_one_solution(generated_puzzle):
    puzzle, _ = generated_puzzle

    assert sudoku_logic.count_solutions(puzzle) == 1


def test_difficulty_configuration_is_valid_and_ordered():
    assert set(sudoku_logic.DIFFICULTY_CONFIG) == {"easy", "medium", "hard"}
    assert all(
        isinstance(clues, int) and 1 <= clues <= sudoku_logic.SIZE * sudoku_logic.SIZE
        for clues in sudoku_logic.DIFFICULTY_CONFIG.values()
    )
    assert (
        sudoku_logic.DIFFICULTY_CONFIG["easy"]
        >= sudoku_logic.DIFFICULTY_CONFIG["medium"]
        >= sudoku_logic.DIFFICULTY_CONFIG["hard"]
    )


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_each_difficulty_generates_a_valid_unique_puzzle(difficulty):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    prefilled_count = sum(value != sudoku_logic.EMPTY for row in puzzle for value in row)

    assert sudoku_logic.is_valid_board(puzzle)
    assert sudoku_logic.is_valid_board(solution)
    assert prefilled_count >= sudoku_logic.DIFFICULTY_CONFIG[difficulty]
    assert all(
        value == sudoku_logic.EMPTY or value == solution[row_index][col_index]
        for row_index, row in enumerate(puzzle)
        for col_index, value in enumerate(row)
    )
    assert sudoku_logic.count_solutions(puzzle) == 1


def test_difficulties_generate_ordered_prefilled_counts(monkeypatch):
    monkeypatch.setattr(sudoku_logic.random, "shuffle", lambda values: None)
    prefilled_counts = {}

    for difficulty in ("easy", "medium", "hard"):
        puzzle, _ = sudoku_logic.generate_puzzle(difficulty=difficulty)
        prefilled_counts[difficulty] = sum(
            value != sudoku_logic.EMPTY for row in puzzle for value in row
        )

    assert prefilled_counts["easy"] >= prefilled_counts["medium"]
    assert prefilled_counts["medium"] >= prefilled_counts["hard"]


def test_generate_puzzle_rejects_unknown_difficulty():
    with pytest.raises(ValueError, match="Unknown difficulty"):
        sudoku_logic.generate_puzzle(difficulty="expert")