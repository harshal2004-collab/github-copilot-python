# Sudoku Flask Project - Copilot Instructions

## Project Goal

Build and refactor the legacy Flask Sudoku application into a maintainable, responsive, accessible, and feature-rich Sudoku game.

The application must remain a Python Flask application and should use modular, readable code.

## Technology Requirements

* Python 3
* Flask
* HTML5
* CSS3
* JavaScript
* Browser localStorage for persistent leaderboard data
* Existing project dependencies should be reused where practical

## Code Quality

* Prefer clear, readable, maintainable code.
* Use small functions with a single responsibility.
* Avoid unnecessary duplication.
* Use descriptive variable and function names.
* Add comments only when they clarify non-obvious logic.
* Handle errors gracefully.
* Preserve existing functionality when refactoring.
* Do not introduce unnecessary dependencies.
* Do not make large unrelated changes.
* Prefer simple solutions over unnecessarily complex abstractions.

## Sudoku Logic

The application must:

* Generate valid 9x9 Sudoku puzzles.
* Ensure every generated puzzle has exactly one solution.
* Support Easy, Medium, and Hard difficulty levels.
* Adjust the number of prefilled cells according to difficulty.
* Keep original/prefilled cells locked.
* Validate user entries against the solution.
* Detect invalid moves.
* Detect when the puzzle has been completely and correctly solved.

Sudoku rules must be enforced for:

* Rows
* Columns
* 3x3 boxes

## Game Features

Implement:

* Difficulty selector
* Timer
* Check button
* Hint button
* Completion message
* Top 10 leaderboard
* Player name
* Completion time
* Difficulty
* Number of hints used
* Persistent leaderboard using localStorage
* Dark mode toggle

The Hint button must:

* Fill one correct empty cell.
* Lock the inserted value.
* Increase the hint counter.

The Check button must:

* Identify incorrect user-entered cells.
* Provide immediate visual feedback.
* Not incorrectly mark valid entries.

## UI Requirements

The interface should:

* Work on desktop and mobile.
* Support light and dark modes.
* Use readable typography.
* Maintain clear contrast.
* Keep controls easy to understand.
* Use alternating visual styling for the 3x3 Sudoku boxes.
* Avoid layout shifts when cells are highlighted.
* Keep locked, user-entered, incorrect, and hinted cells visually distinguishable.

## Accessibility

Prefer accessible HTML and UI practices:

* Use semantic HTML.
* Use labels for form controls.
* Ensure keyboard usability.
* Maintain sufficient color contrast.
* Do not rely only on color to communicate important information.
* Use appropriate ARIA attributes when necessary.

## Testing

Before making major changes:

1. Establish a working test framework.
2. Run the baseline tests.
3. Confirm all baseline tests pass.
4. Run tests after every significant feature or refactor.

When fixing a failing test, identify the underlying cause rather than simply weakening or removing the test.

## Copilot Behavior

When suggesting code:

* Explain important architectural decisions when appropriate.
* Do not blindly modify unrelated files.
* Clearly identify assumptions.
* Prefer incremental changes.
* Preserve working functionality.
* If an existing implementation conflicts with these requirements, explain the issue before making a large change.

## Responsible AI Use

Copilot suggestions must be reviewed before accepting them.

If a suggestion appears unnecessary, incorrect, overly complicated, or inconsistent with the project requirements, reject or modify it rather than accepting it blindly.

## Project Structure

Prefer logical separation between:

* Flask/application logic
* Sudoku generation and validation
* Game state
* Routes/API behavior
* Templates
* JavaScript interactions
* CSS styling
* Tests

Do not introduce unnecessary architectural complexity.

## Important Constraint

Do not replace the entire application with an unrelated implementation.

Build on and refactor the existing legacy Sudoku project while preserving its core purpose.
