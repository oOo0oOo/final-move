# STEP 4: Process all the data and save to file

from collections import Counter, defaultdict
import json
import os
from pprint import pprint


from config import (
    CHECKED_PATH,
    FINAL_PATH,
    LOCATIONS_PATH,
    CANDIDATES_PATH,
    OMEGA_PATH,
    PROJECT_PATH,
    TACTICS,
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
print(f"Found {num} valid tactics overall")

# Do some stats
flatten = [tactic for v in solved.values() for tactic in v]
count = Counter(flatten)
pprint(count)

# Find locations that are only solved by one tactic
only_one = {k: v for k, v in solved.items() if len(v) == 1}
num = sum([len(v) for v in only_one.values()])
print(f"Found {num} locations that are only solved by one tactic")

count_only_one = Counter([v[0] for v in only_one.values()])
pprint(count_only_one)

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
                final.append((file[31:], line, goal, solved[key]))

print(f"Found {len(final)} valid tactics for {len(candidates)} candidates")

# Save to file
with open(FINAL_PATH, "w") as f:
    json.dump(final, f, separators=(",", ":"))
