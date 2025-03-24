# STEP 1: Check promising locations, whether they have no goals after applying the tactic
# 40+ minutes and 60GB of RAM! (reduce workers if needed)

import os
import json
import random
import re
import json
from collections import Counter, defaultdict
import time

import leanclient as lc

from config import (
    CANDIDATES_PATH,
    MATHLIB_PATH,
    PROJECT_PATH,
    BATCH_SIZE,
    TACTICS_BLACKLIST,
    TACTICS,
    MINIMUM_OCCURRENCES,
    MAXIMUM_OCCURRENCES,
)

random.seed(42)

# Regex to capture finishing tactics
patterns = [
    # re.compile(r"(?:^|;|\sby)\s*(\w+)\s*(?:$|--)")
    re.compile(r";\s*(\w+)\s*(?:$|\)\s*$|\}\s*$|--)"),
    re.compile(r"by\s+(\w+)\s*(?:$|\)\s*$|\}\s*$|--)"),
    re.compile(r"^\s+(\w+)\s*(?:$|--)"),
]


# Find all files recursively in a directory
def scan_directory(path: str) -> list[str]:
    files = []
    for file in os.listdir(path):
        full_path = os.path.join(path, file)
        if os.path.isdir(full_path):
            files.extend(scan_directory(full_path))
        else:
            files.append(full_path)
    return files


# Find all files recursively in the mathlib directory
files = scan_directory(MATHLIB_PATH)
l = len(PROJECT_PATH)
files = [f[l:] for f in files]
# random.shuffle(files)
print(f"Found {len(files)} files in mathlib")

# Extract all tactics from the files
locations_per_file = defaultdict(list)
for file in files:
    with open(PROJECT_PATH + file, "r") as f:
        lines = f.readlines()

    for il, line in enumerate(lines):
        for pattern in patterns:
            match = pattern.search(line)
            if match:
                key = match.group(1)
                if key not in TACTICS:
                    continue
                char = match.start(1)
                locations_per_file[file].append((key, il, char))

num = sum([len(v) for v in locations_per_file.values()])
print(f"Found {num} tactics in {len(locations_per_file)} files")

names = []
for locs in locations_per_file.values():
    names.extend([name for name, _, _ in locs])

counter = Counter(names)

# Keep only tactics that appear at least MINIMUM_OCCURRENCES times
names = [name for name, count in counter.items() if count >= MINIMUM_OCCURRENCES]
for file, locs in locations_per_file.items():
    locations_per_file[file] = [
        (name, line, char) for name, line, char in locs if name in names
    ]

num = sum([len(v) for v in locations_per_file.values()])
print(f"Found {num} tactics in mathlib that appear at least 50 times")


# Reduce the number of files
# Remove files repeatedly, heuristic: Remove files which only contain tactics, of which there are too many.
while True:
    counter = Counter([t for locs in locations_per_file.values() for t, _, _ in locs])
    too_many = [
        tactic for tactic, count in counter.items() if count > MAXIMUM_OCCURRENCES
    ]

    if not too_many:
        break

    filtered_files = [
        file
        for file, locs in locations_per_file.items()
        if all(tactic in too_many for tactic, _, _ in locs)
    ]

    if not filtered_files:
        break

    if len(filtered_files) > 5:
        filtered_files = random.sample(filtered_files, 5)

    locations_per_file = {
        file: locs
        for file, locs in locations_per_file.items()
        if file not in filtered_files
    }

# Per tactic
per_tactic = defaultdict(list)
for file, locs in locations_per_file.items():
    for name, line, char in locs:
        per_tactic[name].append((file, line, char))

# Remove tactics with too few OCCURRENCES
for tactic, locs in per_tactic.items():
    if len(locs) < MINIMUM_OCCURRENCES:
        del per_tactic[tactic]

# Limit (random sample) tactics with too many OCCURRENCES
for tactic, locs in per_tactic.items():
    if len(locs) > MAXIMUM_OCCURRENCES:
        per_tactic[tactic] = random.sample(locs, MAXIMUM_OCCURRENCES)

# Reconstruct locations_per_file
locations_per_file = defaultdict(list)
for name, locs in per_tactic.items():
    for file, line, char in locs:
        locations_per_file[file].append((name, line, char))

num = sum([len(v) for v in locations_per_file.values()])
print(f"Found {num} tactics in {len(locations_per_file)} files")


# Use leanclient to extract the goal before and after the tactic
def extract_goals(client: lc.SingleFileClient):
    file_path = client.file_path
    locs = locations_per_file.get(file_path, [])
    states = []
    client.open_file()
    for name, line, char in locs:
        before = client.get_goal(line, char)
        after = client.get_goal(line, char + len(name))
        states.append((file_path, line, char, name, before, after))
    print("Processed", file_path)
    return states


# Only run files, which are in locations_per_file
files = list(locations_per_file.keys())
print(f"Processing {len(files)} files")

all_states = []
t0 = time.time()
total = len(files)
num_processed = 0
# Process files in batches
for i in range(0, len(files), BATCH_SIZE):
    batch_files = files[i : i + BATCH_SIZE]

    # Sort by file size
    batch_files = sorted(
        batch_files, key=lambda x: os.path.getsize(PROJECT_PATH + x), reverse=True
    )

    print(f"Processing batch {i//BATCH_SIZE + 1}: {len(batch_files)} files")
    with lc.LeanClientPool(PROJECT_PATH, num_workers=16) as pool:
        batch_states = pool.map(extract_goals, batch_files)

    num = sum([len(v) for v in batch_states])
    if num == 0:
        continue

    all_states += batch_states
    with open(CANDIDATES_PATH, "w") as f:
        json.dump(all_states, f)

    num_processed += len(batch_files)
    duration = time.time() - t0
    estimate = duration / num_processed * (total - num_processed)
    print(
        f"Processed {num_processed}/{total} files in {duration / 60:.2f} minutes, ETA: {estimate / 60:.2f} minutes"
    )

print(f"Finished in {(time.time() - t0) / 60:.2f} minutes")
