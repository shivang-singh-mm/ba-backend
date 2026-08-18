# Services/campaigns/enum.py
# Single source of truth for all enum columns in the campaigns module.
# DB stores the integer; Python converts on read/write.

# Status: 1=draft, 2=pending, 3=active, 4=completed, 5=deleted
STATUS = {
    1: "draft",
    2: "pending",
    3: "active",
    4: "completed",
    5: "deleted",
}

STATUS_ID = {v: k for k, v in STATUS.items()}
