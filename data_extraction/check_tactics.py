# STEP 3: Check all tactics at all locations, collect diagnostics and goals

from collections import Counter, defaultdict
import json
import os
import time

import leanclient as lc

from config import BLACKLISTED_FILES, LOCATIONS_PATH, CHECKED_PATH, PROJECT_PATH

# Load locations and previous results
with open(LOCATIONS_PATH, "r") as f:
    location_data = json.load(f)

all_tactics = location_data["tactics"]
locations = location_data["locations"]

if os.path.exists(CHECKED_PATH):
    with open(CHECKED_PATH, "r") as f:
        checked = json.load(f)
else:
    checked = {}


def check_tactic(client: lc.SingleFileClient):
    file = client.file_path
    if file in checked:
        return checked[file]
    client.open_file(timeout=0.01)

    print(f"Checking {file} with {len(locations[file])} locations")

    location_results = []
    for line, char, tactic in locations[file]:
        current_len = len(tactic)
        solves = [tactic]
        # Try replacing with every other tactic
        for new_tactic in (t for t in all_tactics if t != tactic):
            change = lc.DocumentContentChange(
                text=new_tactic,
                start=[line, char],
                end=[line, char + current_len],
            )
            diag = client.update_file([change], timeout=40)
            current_len = len(new_tactic)
            goal = client.get_goal(line, char + current_len)
            solves.append((new_tactic, diag, goal))
        location_results.append((file, line, char, solves))
    print(f"Checked {file}")
    return location_results


# Get these imports in?
# -- import Mathlib.Tactic.Basic
# -- import Mathlib.Tactic.FunProp
# -- import Mathlib.Tactic.Abel
# -- import Mathlib.Tactic.Linarith
# -- import Mathlib.Tactic.NormNum
# -- import Mathlib.Tactic.Positivity
# -- import Mathlib.Tactic.Tauto
# -- import Mathlib.Tactic.Ring


# def check_tactic(client: lc.SingleFileClient):

#     print(PROJECT_PATH + client.file_path)
#     file = client.file_path
#     if file in checked:
#         return checked[file]
#     client.open_file(timeout=2)

#     # Add import tactics if not already present
#     content = client.get_file_content()

#     locs = locations[file]
#     results = {}
#     for i, tactic in enumerate(all_tactics):
#         # Change all locations in the file to this tactic
#         changes = []
#         for line, char, current_tactic in locs:
#             if i == 0:
#                 end = len(current_tactic)
#             else:
#                 end = len_last_tactic
#             changes.append(
#                 lc.DocumentContentChange(
#                     text=tactic,
#                     start=[line, char],
#                     end=[line, char + end],
#                 )
#             )

#         len_last_tactic = len(tactic)
#         diagnostics = client.update_file(changes, timeout=60)
#         goals = [
#             (line, char, client.get_goal(line, char + len_last_tactic))
#             for line, char, _ in locs
#         ]
#         results[tactic] = {"diagnostics": diagnostics, "goals": goals}

#         print(f"Checked {file} with {tactic}")
#         content = client.get_file_content()
#         print(content)
#         print([d["message"] for d in diagnostics])

#     print(f"Checked {file}")
#     return results


BATCH_SIZE_CHECK = 200

start_time = time.time()
files = list(locations.keys())
files = [f for f in files if not any([b in f for b in BLACKLISTED_FILES])]

# Sort files by file size
# files = sorted(files, key=lambda x: os.path.getsize(PROJECT_PATH + x), reverse=True)

total_files = len(files)
processed_files = 0

for i in range(0, total_files, BATCH_SIZE_CHECK):
    batch_files = files[i : i + BATCH_SIZE_CHECK]

    # Sort by number of locations
    # batch_files = sorted(batch_files, key=lambda x: len(locations[x]), reverse=True)
    batch_files = sorted(
        batch_files, key=lambda x: os.path.getsize(PROJECT_PATH + x), reverse=True
    )

    print(f"Processing batch {i // BATCH_SIZE_CHECK + 1}: {len(batch_files)} files")

    with lc.LeanClientPool(PROJECT_PATH, num_workers=18) as pool:
        batch_states = pool.map(check_tactic, batch_files)

    for file, state in zip(batch_files, batch_states):
        if state is not None:
            checked[file] = state

    # Write interim results
    with open(CHECKED_PATH, "w") as f:
        json.dump(checked, f)

    processed_files += len(batch_files)
    elapsed = time.time() - start_time
    print(f"Processed {processed_files}/{total_files} files in {elapsed:.2f} seconds")


print(f"Finished in {(time.time() - start_time) / 60:.1f} minutes")
