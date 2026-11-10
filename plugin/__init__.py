"""Native, data-only Hermes adapter. No runtime permissions are inferred."""
import json
import re
from pathlib import Path


def _available():
    # Preparation is standard-library-only; this is not a downstream permission.
    return True


def _handle(args, **kwargs):
    # Host dispatch metadata is deliberately not input to the pure core.
    return json.dumps(prepare(args), ensure_ascii=True)


def _housekeeper_handle(args, **kwargs):
    # housekeeper.prepare already returns its complete immutable JSON wire result.
    return housekeeper_prepare_core(args)


_REMINDER = (
    "Default-first workflow: call `housekeeper_prepare` for every substantive user request "
    "before answering or using other tools. If it is not listed, discover it once with "
    "`tool_search`. Treat the card and route suggestions as advisory; independently check "
    "actual tool availability and user/policy permission. This reminder does not enforce "
    "tool use, block action, or grant authority."
)
_MAX_HOOK_CLASSIFICATION_CHARS = 512

_NO_PREPARATION_MESSAGES = {
    "hi", "hello", "hey", "thanks", "thank you", "ok", "okay",
    "hello there", "how are you", "how are you doing",
    "good morning", "good afternoon", "good evening", "good night",
    "早安", "午安", "晚安", "嗨", "你好", "謝謝", "好的",
    "stop", "cancel", "never mind", "nevermind", "forget it",
    "停止", "取消", "先不用", "算了",
}
_CLEAR_CANCELLATION = re.compile(
    r"^(?:please\s+)?(?:"
    r"stop(?:\s+(?:now|here|working|the task|this task|the current task|the previous task))?|"
    r"cancel\s+(?:it|that|this|the task|the previous task|the current task|"
    r"this request|that request|the request|the previous request|the current request)|"
    r"abort(?:\s+(?:it|that|this|the task))?|"
    r"never\s+mind(?:[,;:]?\s*(?:do not|don't)\s+(?:continue|proceed))?|"
    r"forget\s+it|(?:do not|don't)\s+(?:continue|proceed)|"
    r"(?:請)?(?:停止|取消|中止)(?:(?:(?:目前|現在|這個|這項|上一個|前一個)(?:的)?|剛才的?)?"
    r"(?:任務|請求|操作|動作))?(?:[，,；;、 ]*(?:不要|別)(?:再)?(?:繼續|執行|進行))?|"
    r"算了[，,；;、 ]*(?:不要|別)(?:再)?(?:繼續|執行|進行)"
    r")(?:[.!? ]*)$",
    flags=re.IGNORECASE,
)


def _pre_llm_reminder(user_message=None, **kwargs):
    """Return one fixed discoverability reminder for substantial textual requests.

    The installed native hook API supplies ``user_message`` (not TurnContext's
    ``original_user_message``). Never inspect history, multimodal payloads, or other
    hook metadata; this callback is advisory and the host remains fail-open.
    """
    if type(user_message) is not str:
        return None
    # Bound all inspection/copying, even when a caller supplies a very large
    # message. Large inputs get the fixed reminder without normalization.
    sample = user_message[:_MAX_HOOK_CLASSIFICATION_CHARS + 1]
    text = sample.strip()
    if not text:
        return None if len(user_message) <= _MAX_HOOK_CLASSIFICATION_CHARS else _REMINDER
    if text.startswith("/"):
        return None
    if len(user_message) > _MAX_HOOK_CLASSIFICATION_CHARS:
        return _REMINDER
    # Only inspect the message for a small set of pure-social/explicit-cancel
    # forms. All other non-empty text gets the same fixed reminder; user text is
    # never reflected in the hook result.
    normalized = text.casefold().strip(" .!?！？，,。\t\n")
    if normalized in _NO_PREPARATION_MESSAGES or _CLEAR_CANCELLATION.fullmatch(normalized):
        return None
    return _REMINDER


def register(ctx):
    # Defer package imports until the host invokes the registration entrypoint.
    global prepare, housekeeper_prepare_core
    from .navigator import prepare
    from .housekeeper import prepare as housekeeper_prepare_core
    from .schemas import TOOL_SCHEMA
    from .housekeeper_schema import TOOL_SCHEMA as HOUSEKEEPER_TOOL_SCHEMA

    ctx.register_tool(
        name="navigator_prepare", toolset="task_navigator",
        schema=TOOL_SCHEMA, handler=_handle, check_fn=_available,
        requires_env=[], description="Prepare bounded supplied-text task data only.",
    )
    ctx.register_tool(
        name="housekeeper_prepare", toolset="task_navigator",
        schema=HOUSEKEEPER_TOOL_SCHEMA, handler=_housekeeper_handle, check_fn=_available,
        requires_env=[], description=HOUSEKEEPER_TOOL_SCHEMA["description"],
    )
    ctx.register_skill(
        "workflow", Path(__file__).parent / "skills/workflow/SKILL.md",
        description="Use token家政婦 before substantive answers; keep social/control exceptions minimal.",
    )
    ctx.register_hook("pre_llm_call", _pre_llm_reminder)
