PROJECT_PATH = "lake_env/MathlibProject/"
MATHLIB_PATH = "lake_env/MathlibProject/.lake/packages/mathlib/Mathlib/"

CANDIDATES_PATH = "data/candidates.json"
LOCATIONS_PATH = "data/locations.json"
CHECKED_PATH = "data/checked.json"
OMEGA_PATH = "data/omega.json"
FINAL_PATH = "../final-move/static/data.json"

BATCH_SIZE = 2000

MAXIMUM_OCCURRENCES = 1000
MINIMUM_OCCURRENCES = 10  # Not very important, keep low, we work with a whitelist...

LIMIT_TACTICS_MAX = 500
LIMIT_TACTICS_MIN = 100

BLACKLIST_MATHLIB_FOLDERS = ["Tactic", "Util", "Testing", "Lean"]

# leanprover/lean4:v4.18.0-rc1
BASE_URL = "https://github.com/leanprover-community/mathlib4/tree/6cecf71a82a22ea7c01598800e12f3e8eb66894b/Mathlib/"

TACTICS = [
    "decide",
    "assumption",
    "tauto",
    "congr",
    "simp",
    "abel",
    "norm_num",
    "linarith",
    "infer_instance",
    "aesop",
    "gcongr",
    "omega",
    "positivity",
    "fun_prop",
    "contradiction",
    "ring",
    # "rfl",
    # "contradiction",
    # "assumption",
    # "trivial",
    # "constructor",
    # "simp",
    # "simpa",
    # "dsimp",
    # "simp_all",
    # "tauto",
    # "ring",
    # "linarith",
    # "norm_num",
    # "nlinarith",
    # "group",
    # "aesop",
    # "abel",
    # "exfalso",
    # "omega",
    # "dsimp",
    # "ring1",
    # "norm_cast",
    # "simpa",
    # "ring_nf",
    # "simp_all",
    # "aesop_cat",
]


TACTICS_BLACKLIST = [
    "section",
    "end",
    "rfl",
    "constructor",
    "ext",
    "calc",
    "classical",
    "else",
    "exact",
    "noncomputable",
    "try",
    "return",
    "where",
    "refine",
    # These are removed, simply to reduce the number of tactics
    "norm_cast",
    "ring1",
    "ring_nf",
    "simp_all",
    "simpa",
    "aesop_cat",
]


BLACKLISTED_FILES = ["LocallyInjective.lean"]

TIERS = [
    [["simp", "assumption", "contradiction", "tauto", "decide", "congr"], 10],
    [["norm_num", "ring", "abel"], 15],
    [["linarith", "positivity", "omega"], 20],
    [["infer_instance", "fun_prop", "gcongr"], 25],
    [["aesop"], 30],
]
