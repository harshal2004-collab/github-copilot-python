import app as flask_app
import pytest
import sudoku_logic


def test_home_page_renders(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sudoku Game" in response.data
    assert b'aria-label="Elapsed time" aria-live="off">00:00</time>' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'/static/theme.js' in response.data


def test_new_game_returns_puzzle_and_stores_solution(client):
    response = client.get("/new")

    assert response.status_code == 200
    data = response.get_json()
    puzzle = data["puzzle"]
    solution = flask_app.CURRENT["solution"]

    assert data["difficulty"] == "medium"
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert len(solution) == 9
    assert all(len(row) == 9 for row in solution)
    assert all(
        value == 0 or value == solution[row_index][col_index]
        for row_index, row in enumerate(puzzle)
        for col_index, value in enumerate(row)
    )
    assert flask_app.CURRENT["puzzle"] == puzzle


def test_new_game_uses_requested_difficulty(client):
    response = client.get("/new?difficulty=hard")

    assert response.status_code == 200
    assert response.get_json()["difficulty"] == "hard"
    assert flask_app.CURRENT["puzzle"] == response.get_json()["puzzle"]
    assert flask_app.CURRENT["hints_used"] == 0


def test_new_game_rejects_unknown_difficulty(client):
    response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid difficulty"}


def test_new_game_preserves_legacy_clues_parameter(client):
    response = client.get("/new?clues=35")

    assert response.status_code == 200
    assert response.get_json()["difficulty"] == "medium"
    assert flask_app.CURRENT["puzzle"] == response.get_json()["puzzle"]


def test_check_solution_requires_game_in_progress(client):
    response = client.post("/check", json={"board": []})

    assert response.status_code == 400
    assert response.get_json() == {"error": "No game in progress"}


def test_check_solution_accepts_correct_board(client, solved_board):
    flask_app.CURRENT["solution"] = solved_board
    flask_app.CURRENT["puzzle"] = [row.copy() for row in solved_board]

    response = client.post("/check", json={"board": solved_board})

    assert response.status_code == 200
    assert response.get_json() == {
        "incorrect": [],
        "incomplete_cells": [],
        "incomplete": False,
        "solved": True,
    }


def test_check_solution_reports_incorrect_cells(client, solved_board):
    flask_app.CURRENT["solution"] = solved_board
    flask_app.CURRENT["puzzle"] = [row.copy() for row in solved_board]
    flask_app.CURRENT["puzzle"][0][0] = 0
    board = [row.copy() for row in solved_board]
    board[0][0] = board[0][0] % 9 + 1

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {
        "incorrect": [[0, 0]],
        "incomplete_cells": [],
        "incomplete": False,
        "solved": False,
    }


def test_check_solution_reports_empty_cells_without_marking_them_incorrect(client, solved_board):
    flask_app.CURRENT["solution"] = solved_board
    flask_app.CURRENT["puzzle"] = [row.copy() for row in solved_board]
    flask_app.CURRENT["puzzle"][0][0] = 0
    board = [row.copy() for row in solved_board]
    board[0][0] = 0

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json() == {
        "incorrect": [],
        "incomplete_cells": [[0, 0]],
        "incomplete": True,
        "solved": False,
    }


def test_check_solution_does_not_change_prefilled_cells_or_expose_solution(client, solved_board):
    flask_app.CURRENT["solution"] = solved_board
    flask_app.CURRENT["puzzle"] = [row.copy() for row in solved_board]
    original_puzzle = [row.copy() for row in flask_app.CURRENT["puzzle"]]
    board = [row.copy() for row in solved_board]
    board[0][0] = board[0][0] % 9 + 1

    response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    assert response.get_json()["solved"] is False
    assert response.get_json()["incorrect"] == []
    assert "solution" not in response.get_json()
    assert flask_app.CURRENT["puzzle"] == original_puzzle


def test_check_solution_rejects_malformed_board(client):
    flask_app.CURRENT["puzzle"] = [[0] * 9 for _ in range(9)]
    flask_app.CURRENT["solution"] = [[1] * 9 for _ in range(9)]

    response = client.post("/check", json={"board": []})

    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid board"}


def _set_game(puzzle, solution):
    flask_app.CURRENT.update(
        puzzle=[row.copy() for row in puzzle],
        solution=[row.copy() for row in solution],
        hints_used=0,
    )


def test_hint_fills_one_empty_cell_correctly_and_locks_it(client, solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = 0
    puzzle[0][1] = 0
    _set_game(puzzle, solved_board)
    board = [row.copy() for row in puzzle]
    board[0][1] = solved_board[0][1]
    original_board = [row.copy() for row in board]

    response = client.post("/hint", json={"board": board})
    data = response.get_json()

    assert response.status_code == 200
    assert (data["row"], data["col"]) == (0, 0)
    assert data["value"] == solved_board[0][0]
    assert data["locked"] is True
    assert data["hints_used"] == 1
    assert "solution" not in data
    assert board == original_board
    assert flask_app.CURRENT["puzzle"] == puzzle
    assert flask_app.CURRENT["hints_used"] == 1


def test_hint_preserves_prefilled_cells_and_player_entries(client, solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = 0
    puzzle[0][1] = 0
    _set_game(puzzle, solved_board)
    board = [row.copy() for row in puzzle]
    board[0][1] = solved_board[0][1]
    prefilled_values = [row.copy() for row in board]

    response = client.post("/hint", json={"board": board})
    data = response.get_json()

    assert data["row"] == 0 and data["col"] == 0
    assert board[0][1] == prefilled_values[0][1]
    assert all(
        board[row][col] == value
        for row in range(9)
        for col, value in enumerate(prefilled_values[row])
        if (row, col) != (0, 0)
    )


def test_hint_skips_existing_and_previously_hinted_entries(client, solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[0][0] = 0
    puzzle[0][1] = 0
    puzzle[1][0] = 0
    _set_game(puzzle, solved_board)
    board = [row.copy() for row in puzzle]

    first_hint = client.post("/hint", json={"board": board}).get_json()
    board[first_hint["row"]][first_hint["col"]] = first_hint["value"]
    board[0][1] = solved_board[0][1]
    second_response = client.post("/hint", json={"board": board})
    second_hint = second_response.get_json()

    assert (first_hint["row"], first_hint["col"]) == (0, 0)
    assert (second_hint["row"], second_hint["col"]) == (1, 0)
    assert second_hint["hints_used"] == 2


def test_hint_returns_message_when_no_empty_cells_remain(client, solved_board):
    _set_game(solved_board, solved_board)

    response = client.post("/hint", json={"board": solved_board})

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "No empty cells available for a hint",
        "hints_used": 0,
    }
    assert flask_app.CURRENT["hints_used"] == 0


def test_last_hint_can_complete_puzzle_and_check_reports_solved(client, solved_board):
    puzzle = [row.copy() for row in solved_board]
    puzzle[8][8] = 0
    _set_game(puzzle, solved_board)
    board = [row.copy() for row in puzzle]

    hint_response = client.post("/hint", json={"board": board})
    data = hint_response.get_json()
    board[data["row"]][data["col"]] = data["value"]
    check_response = client.post("/check", json={"board": board})

    assert hint_response.status_code == 200
    assert data["solved"] is True
    assert check_response.get_json()["solved"] is True


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_hint_works_for_each_difficulty(client, difficulty):
    new_game_response = client.get(f"/new?difficulty={difficulty}")
    puzzle = new_game_response.get_json()["puzzle"]
    solution = flask_app.CURRENT["solution"]

    response = client.post("/hint", json={"board": puzzle})
    data = response.get_json()

    assert response.status_code == 200
    assert puzzle[data["row"]][data["col"]] == 0
    assert data["value"] == solution[data["row"]][data["col"]]