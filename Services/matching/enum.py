# Services/matching/enum.py
# Single source of truth for all enum columns in the matching module.
# DB stores the integer; Python converts on read/write.

# Match Status: 1=matched, 2=shortlisted, 3=contacted, 4=accepted, 5=rejected
MATCH_STATUS = {
    1: "matched",
    2: "shortlisted",
    3: "contacted",
    4: "accepted",
    5: "rejected",
}

MATCH_STATUS_ID = {v: k for k, v in MATCH_STATUS.items()}
