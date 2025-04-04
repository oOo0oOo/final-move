# STEP 4: Process all the data and save to file

from collections import Counter, defaultdict
import json
import os
from pprint import pprint


from config import (
    BASE_URL,
    CHECKED_PATH,
    FINAL_PATH,
    LOCATIONS_PATH,
    CANDIDATES_PATH,
    OMEGA_PATH,
    PROJECT_PATH,
    TACTICS,
    TIERS,
)

# Load all checked
if os.path.exists(CHECKED_PATH):
    with open(CHECKED_PATH, "r") as f:
        checked = json.load(f)

num = sum([len(v) for v in checked.values()])

# Collect all tactics that solve a goal
solved = defaultdict(list)

num_total = 0
for file, locs in checked.items():
    for loc in locs:

        # Something went wrong when testing this single location
        # .lake/packages/mathlib/Mathlib/Combinatorics/SetFamily/KruskalKatona.lean:281:50
        if (
            loc[0]
            == ".lake/packages/mathlib/Mathlib/Combinatorics/SetFamily/KruskalKatona.lean"
            and loc[1] == 280
            and loc[2] == 49
        ):
            continue

        # Check all tactics
        start = {"line": loc[1], "character": loc[2]}
        valid_tactic = [loc[-1][0]]
        for tactic, diagnostics, goal in loc[-1][1:]:
            num_total += 1

            if goal is None:
                continue

            if goal.get("goals", 1) != []:
                continue

            msgs = [
                d["message"] for d in diagnostics if d["fullRange"]["start"] == start
            ]

            if any([msg.startswith("(deterministic) timeout") for msg in msgs]):
                continue

            if tactic == "omega":
                if any(
                    [msg.startswith("omega could not prove the goal") for msg in msgs]
                ):
                    continue

                if any([msg.startswith("unknown free variable") for msg in msgs]):
                    continue

            if tactic == "infer_instance":
                if any(
                    [msg.startswith("type class instance expected") for msg in msgs]
                ):
                    continue

                if any([msg.startswith("failed to synthesize") for msg in msgs]):
                    continue

            if tactic == "assumption":
                if any([msg.startswith("tactic 'assumption' failed") for msg in msgs]):
                    continue

            if tactic == "tauto":
                if any(
                    [msg.startswith("tauto failed to solve some goals") for msg in msgs]
                ):
                    continue

            if tactic == "decide":
                if any([msg.startswith("tactic 'decide' failed") for msg in msgs]):
                    continue

            if tactic == "aesop":
                if any([msg.startswith("tactic 'aesop' failed") for msg in msgs]):
                    continue

            # OK messages
            if tactic == "abel":
                if any([msg.startswith("Try this: abel_nf") for msg in msgs]):
                    valid_tactic.append("abel")
                    continue

            if tactic == "ring":
                if any([msg.startswith("Try this: ring_nf") for msg in msgs]):
                    valid_tactic.append("ring")
                    continue

            if msgs:
                print(f"{PROJECT_PATH + loc[0]}:{loc[1] + 1}:{loc[2] + 1}")
                print(tactic)
                print(msgs)

            valid_tactic.append(tactic)

        solved[(file, loc[1], loc[2])] = valid_tactic


print(
    f"Checked {num} goals in {len(checked)} files with {len(TACTICS)} tactics: {num_total} checks"
)

num = sum([len(v) for v in solved.values()])

# Do some stats
flatten = [tactic for v in solved.values() for tactic in v]
count = Counter(flatten)
sorted_by_count = sorted(count.items(), key=lambda x: x[1], reverse=True)

# Find locations that are only solved by one tactic
only_one = {k: v for k, v in solved.items() if len(v) == 1}
num_unique = sum([len(v) for v in only_one.values()])

count_only_one = Counter([v[0] for v in only_one.values()])

# Layout counters in a table
print("Tactic           | Solved | Uniquely solved by this tactic")
for t, cnt in sorted_by_count:
    space = " " * (16 - len(t))
    print(f"{t}{space} | {cnt}\t  | {count_only_one[t]}")

print("TOTAL            |", num, " |", num_unique)

# # Find tactics that are often valid together
# valid_together = defaultdict(int)
# for v in solved.values():
#     for i in range(len(v)):
#         for j in range(i + 1, len(v)):
#             valid_together[tuple(sorted([v[i], v[j]]))] += 1
# sort = sorted(valid_together.items(), key=lambda x: x[1], reverse=True)
# pprint(sort)


# Load candidates
with open(CANDIDATES_PATH, "r") as f:
    candidates = json.load(f)

MAX_GOAL_LEN = 2000


def tactics_to_int(tactics):
    ints = [TACTICS.index(t) for t in tactics]
    # Encode as 16 bit int
    return sum([2**i for i in ints])


# Combine goal from candidates with valid tactics
final = []
for cand in candidates:
    for file, line, char, name, before, after in cand:
        key = (file, line, char)
        if key in solved:
            if before is not None:
                goal = before["rendered"][8:-4]
                if len(goal) > MAX_GOAL_LEN:
                    continue
                final.append((file[31:], line, goal, tuple(solved[key])))

print(f"Found {len(final)} valid tactics for {len(candidates)} candidates")

# Split into tiers
data = []

accumulated_tactics = set()
prev_goals = set()
for i, (tactics, cost) in enumerate(TIERS):
    tier = {"tactics": tactics, "cost": cost, "goals": []}
    accumulated_tactics.update(tactics)

    for goal in final:
        if goal in prev_goals:
            continue

        if set(goal[3]) & accumulated_tactics:
            tier["goals"].append(goal)
            prev_goals.add(goal)

    print(f"Tier {i}: {len(tier['goals'])} goals")
    data.append(tier)

# Save to file

d = {"tiers": data, "mathlib_url": BASE_URL}

with open(FINAL_PATH, "w") as f:
    json.dump(d, f, separators=(",", ":"))
