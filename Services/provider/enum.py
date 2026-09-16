# Services/provider/enum.py

PROVIDER_TYPE = {
    1: "individual",
    2: "agency",
    3: "freelancer",
}
PROVIDER_TYPE_ID = {v: k for k, v in PROVIDER_TYPE.items()}

PROFICIENCY = {
    1: "basic",
    2: "conversational",
    3: "fluent",
    4: "native",
}
PROFICIENCY_ID = {v: k for k, v in PROFICIENCY.items()}

DOCUMENT_TYPE = {
    1: "id_proof",
    2: "certification",
    3: "portfolio",
    4: "other",
}
DOCUMENT_TYPE_ID = {v: k for k, v in DOCUMENT_TYPE.items()}
