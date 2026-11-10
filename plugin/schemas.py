"""Model-facing structural schema; exact UTF-8/evidence gates live in core."""

_ID = {"type": "string", "maxLength": 64,
       "pattern": "^[A-Za-z][A-Za-z0-9_-]{0,63}$"}
_TEXT = {"type": "string", "maxLength": 1024,
         "description": "At most 1024 UTF-8 bytes; no NUL or invalid Unicode."}
_LIST = {"type": "array", "maxItems": 16, "items": _TEXT}

INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["requested_route", "facts", "assumptions", "constraints", "unknowns"],
    "properties": {
        "language": {"type": "string", "enum": ["en", "zh-CN"], "default": "en",
                     "description": "Generated labels and route guidance only; original text and quotes stay unchanged. Defaults to English. Validation errors remain English."},
        "goal": _TEXT,
        "requested_route": {
            "type": "string", "maxLength": 64,
            "description": "Use compare or extract_actions. Other routes return unsupported.",
        },
        "sources": {
            "type": "array", "maxItems": 8,
            "description": "Unique IDs; text total <=32768 UTF-8 bytes. Compare needs exactly two nonblank sources; extract_actions needs 1..8. Missing material returns needs_input.",
            "items": {"type": "object", "additionalProperties": False,
                      "required": ["source_id", "text"],
                      "properties": {"source_id": _ID, "text": {
                          "type": "string", "maxLength": 8192,
                          "description": "Original text, <=8192 UTF-8 bytes; no NUL or invalid Unicode."}}},
        },
        "facts": {
            "type": "array", "maxItems": 32,
            "description": "Caller-provided claims, NOT verified semantics. Quotes must exactly occur in their referenced sources. May be empty.",
            "items": {"type": "object", "additionalProperties": False,
                      "required": ["text", "source_id", "quote"],
                      "properties": {"text": _TEXT, "source_id": _ID,
                                     "quote": {**_TEXT, "minLength": 1}}},
        },
        "assumptions": _LIST, "constraints": _LIST, "unknowns": _LIST,
    },
}

TOOL_SCHEMA = {
    "name": "navigator_prepare",
    "description": "Validate bounded supplied text and prepare a data-only handoff. Does not compare, extract, invoke tools, verify semantic claims, authorize execution, or complete downstream work. Host must independently check session capability and approval after data_ready.",
    "parameters": INPUT_SCHEMA,
}
