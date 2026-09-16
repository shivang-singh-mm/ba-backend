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

# Language Proficiency: 1=basic, 2=conversational, 3=fluent, 4=native
PROFICIENCY = {
    1: "basic",
    2: "conversational",
    3: "fluent",
    4: "native",
}

PROFICIENCY_ID = {v: k for k, v in PROFICIENCY.items()}

# Matching Rule: 1=hard, 2=soft, 3=ignore
MATCHING_RULE = {
    1: "hard",
    2: "soft",
    3: "ignore",
}

MATCHING_RULE_ID = {v: k for k, v in MATCHING_RULE.items()}

