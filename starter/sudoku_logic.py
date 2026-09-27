import copy
import random

SIZE = 9
EMPTY = 0
BOX_SIZE = 3
VALUES = set(range(1, SIZE + 1))
DIFFICULTY_CONFIG = {
    "easy": 40,
    "medium": 35,
    "hard": 26,
}

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def _unit_is_valid(values):
    filled_values = [value for value in values if value != EMPTY]
    return all(value in VALUES for value in filled_values) and len(filled_values) == len(set(filled_values))

def is_valid_board(board):
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False
    if any(value != EMPTY and value not in VALUES for row in board for value in row):
        return False

    if any(not _unit_is_valid(row) for row in board):
        return False
    if any(not _unit_is_valid([board[row][col] for row in range(SIZE)]) for col in range(SIZE)):
        return False

    for box_row in range(0, SIZE, BOX_SIZE):
        for box_col in range(0, SIZE, BOX_SIZE):
            box = [
                board[row][col]
                for row in range(box_row, box_row + BOX_SIZE)
                for col in range(box_col, box_col + BOX_SIZE)
            ]
            if not _unit_is_valid(box):
                return False
    return True

def evaluate_board(board, puzzle, solution):
    incorrect = []
    incomplete_cells = []
    solved = True

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                incomplete_cells.append([row, col])
                solved = False
            elif value != solution[row][col]:
                solved = False
                if puzzle[row][col] == EMPTY:
                    incorrect.append([row, col])

    return {
        "incorrect": incorrect,
        "incomplete_cells": incomplete_cells,
        "incomplete": bool(incomplete_cells),
        "solved": solved,
    }

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for box_row in range(start_row, start_row + BOX_SIZE):
        for box_col in range(start_col, start_col + BOX_SIZE):
            if board[box_row][box_col] == num:
                return False
    return True

def _find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None

def solve(board):
    if not is_valid_board(board):
        return None
    solution = deep_copy(board)

    def backtrack():
        cell = _find_empty_cell(solution)
        if cell is None:
            return True
        row, col = cell
        for candidate in range(1, SIZE + 1):
            if is_safe(solution, row, col, candidate):
                solution[row][col] = candidate
                if backtrack():
                    return True
                solution[row][col] = EMPTY
        return False

    return solution if backtrack() else None

def count_solutions(board):
    if not is_valid_board(board):
        return 0
    working_board = deep_copy(board)
    solution_count = 0

    def backtrack():
        nonlocal solution_count
        if solution_count > 1:
            return
        cell = _find_empty_cell(working_board)
        if cell is None:
            solution_count += 1
            return
        row, col = cell
        for candidate in range(1, SIZE + 1):
            if is_safe(working_board, row, col, candidate):
                working_board[row][col] = candidate
                backtrack()
                working_board[row][col] = EMPTY
                if solution_count > 1:
                    return

    backtrack()
    return solution_count

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

def remove_cells(board, clues):
    target_clues = max(0, min(SIZE * SIZE, clues))
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    for row, col in cells:
        clue_count = sum(value != EMPTY for line in board for value in line)
        if clue_count <= target_clues:
            break
        value = board[row][col]
        if value == EMPTY:
            continue
        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = value

def generate_puzzle(clues=None, difficulty="medium"):
    if difficulty not in DIFFICULTY_CONFIG:
        raise ValueError(f"Unknown difficulty: {difficulty}")
    if clues is None:
        clues = DIFFICULTY_CONFIG[difficulty]

    board = create_empty_board()
    if not fill_board(board):
        raise RuntimeError('Could not generate a complete Sudoku board')
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
