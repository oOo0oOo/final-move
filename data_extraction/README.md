# Final Tactic Extraction from Mathlib

These Python scripts find candidates for final tactics, check if they solve the goal and check all other tactics.

## Usage

1. `extract.py`: Find candidate locations for final tactics, and check if they solve the goal. 20 minutes and lots of RAM.
2. `find_locations.py`: Filter out valid tactics and reduce the number of files. Instant.
3. `check_tactics.py`: For each location, try all other tactics in the game: Get goal and diagnostics. 10h and lots of RAM.
4. `final_data.py`: Evaluate diagnostics and compile final data. Instant.
