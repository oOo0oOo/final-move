# STEP 2: Find and filter finishing locations

from collections import Counter, defaultdict
import json
import os
from pprint import pprint
import random

from config import (
    MATHLIB_PATH,
    PROJECT_PATH,
    TACTICS_BLACKLIST,
    CANDIDATES_PATH,
    LOCATIONS_PATH,
    LIMIT_TACTICS_MAX,
    LIMIT_TACTICS_MIN,
)

random.seed(42)

# Load all candidates
with open(CANDIDATES_PATH, "r") as f:
    all_candidates = json.load(f)

num = sum([len(v) for v in all_candidates])
print(f"Found {num} candidates")

candidates = []
for f_candidates in all_candidates:
    for candidate in f_candidates:
        if candidate[3] in TACTICS_BLACKLIST:
            continue
        after = candidate[-1]
        if after is None:
            continue
        if after["goals"] == []:
            candidates.append(candidate)

print(f"Found {len(candidates)} candidates")

tactic_names = [candidate[3] for candidate in candidates]
counter = Counter(tactic_names)
print(f"Found {len(counter)} tactics")

# Filter out tactics with less than LIMIT_TACTICS occurrences
too_few = [tactic for tactic, count in counter.items() if count < LIMIT_TACTICS_MIN]
print(f"Filtering out {len(too_few)} tactics: {too_few}")
candidates = [candidate for candidate in candidates if candidate[3] not in too_few]

locations = defaultdict(list)
for candidate in candidates:
    file = candidate[0]
    line = candidate[1]
    char = candidate[2]
    tactic = candidate[3]
    locations[file].append((line, char, tactic))

unique_tactics = set([t[3] for t in candidates])
print(
    f"Found {len(locations)} files, {len(candidates)} candidates, and {len(unique_tactics)} tactics"
)

# Reduce the number of files/tactics
# Remove files repeatedly, heuristic: Remove files which only contain tactics, of which there are too many.

iteration = 0
while True:
    iteration += 1
    counter = Counter([t for locs in locations.values() for _, _, t in locs])
    too_many = [
        tactic for tactic, count in counter.items() if count > LIMIT_TACTICS_MAX
    ]

    # Find files where every tactic is in the too_many list.
    filtered_files = [
        file
        for file, locs in locations.items()
        if locs and all([tactic in too_many for _, _, tactic in locs])
    ]

    if not filtered_files:
        print(f"No files to filter on iteration {iteration}. Stopping iteration.")
        break

    if len(filtered_files) > 10:
        filtered_files = random.sample(filtered_files, 10)

    locations = {
        file: locs for file, locs in locations.items() if file not in filtered_files
    }

# file_sizes = {file: os.path.getsize(PROJECT_PATH + file) for file in locations.keys()}
# while True:
#     counter = Counter([t for locs in locations.values() for _, _, t in locs])
#     too_many = [
#         tactic for tactic, count in counter.items() if count > LIMIT_TACTICS_MAX
#     ]
#     if not too_many:
#         print("No tactics with too many occurrences. Stopping iteration.")
#         break
#     # Sort files by filesize
#     sorted_files = sorted(
#         locations.items(), key=lambda x: file_sizes[x[0]], reverse=True
#     )
#     # Remove in longest file
#     for file, locs in sorted_files:
#         for too in too_many:
#             locations[file] = [loc for loc in locs if loc[2] != too]
#             if all([loc[2] != too for loc in locations[file]]):
#                 break

unique_tactics = set([t for locs in locations.values() for _, _, t in locs])
num_locations = sum([len(locs) for locs in locations.values()])
print(
    f"Found {len(unique_tactics)} tactics, {len(locations)} files, and {num_locations} locations"
)

counter = Counter([t for locs in locations.values() for _, _, t in locs])
print("Tactics with counts:")
print(counter.most_common(20))

with open(LOCATIONS_PATH, "w") as f:
    data = {"tactics": list(unique_tactics), "locations": locations}
    json.dump(data, f)
print("Saved locations to disk: ", LOCATIONS_PATH)
