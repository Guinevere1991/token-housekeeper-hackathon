"""Model-facing shape for host-drafted 5W1H cards; core enforces exact bounds."""

_ID = {"type": "string", "maxLength": 64,
       "pattern": "^[A-Za-z][A-Za-z0-9_-]{0,63}$"}
_TEXT = {"type": "string", "maxLength": 1024,
         "description": "At most 1024 UTF-8 bytes; no NUL or invalid Unicode."}
_CLAIM = {
    "type": "object", "additionalProperties": False,
    "required": ["text", "source_id", "quote"],
    "properties": {"text": _TEXT, "source_id": _ID,
                   "quote": {**_TEXT, "minLength": 1}},
}

_FIELDS = ("who", "what", "when", "where", "why", "how")
_KINDS = ["question", "search", "compare", "summarize", "extract_actions",
          "plan", "draft", "execute", "unclear"]

INPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["language", "message_kind", "sources", "dimensions", "tasks",
                 "constraints", "questions"],
    "properties": {
        "response_mode": {"type": "string", "enum": ["full", "compact"],
                          "description": "Optional; default full includes Markdown. Prefer compact for machine consumption: identical card and safety fields, without duplicate Markdown."},
        "language": {"type": "string", "enum": ["zh-TW", "en"]},
        "message_kind": {"type": "string", "enum": [
            "request", "question", "smalltalk", "cancellation", "confirmation", "unclear"]},
        "sources": {
            "type": "array", "minItems": 1, "maxItems": 8,
            "description": "Preserve the complete original user prompt and any supplied sources verbatim. Each source <=8192 UTF-8 bytes; aggregate <=32768.",
            "items": {"type": "object", "additionalProperties": False,
                      "required": ["source_id", "text"],
                      "properties": {"source_id": _ID,
                                     "text": {"type": "string", "maxLength": 8192}}},
        },
        "dimensions": {
            "type": "object", "additionalProperties": False,
            "required": list(_FIELDS),
            "properties": {
                field: {
                    "type": "object", "additionalProperties": False,
                    "required": ["status", "items"],
                    "properties": {
                        "status": {"type": "string", "enum": [
                            "explicit", "not_provided", "not_applicable", "ambiguous"]},
                        "items": {"type": "array", "maxItems": 8, "items": _CLAIM},
                    },
                } for field in _FIELDS
            },
        },
        "tasks": {
            "type": "array", "maxItems": 8,
            "items": {"type": "object", "additionalProperties": False,
                      "required": ["id", "kind", "intent", "depends_on", "questions"],
                      "properties": {
                          "id": _ID,
                          "kind": {"type": "string", "enum": _KINDS},
                          "intent": _CLAIM,
                          "depends_on": {"type": "array", "maxItems": 7, "items": _ID},
                          "questions": {"type": "array", "maxItems": 16, "items": _TEXT},
                      }},
        },
        "constraints": {"type": "array", "maxItems": 16, "items": _CLAIM},
        "questions": {"type": "array", "maxItems": 16, "items": _TEXT},
    },
}

TOOL_SCHEMA = {
    "name": "housekeeper_prepare",
    "description": "token家政婦: validate a host-drafted, source-grounded 5W1H task card and derive advisory capability suggestions. The host/model supplies semantic interpretation; this tool validates bounded structure and citations only. Suggestions do not prove actual tool availability or grant permission; the host must independently check tools and user/policy authorization. No action is executed.",
    "parameters": INPUT_SCHEMA,
}
