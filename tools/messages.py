from typing import Any, Dict, List


def normalize_message_content(content: Any) -> str:
    if isinstance(content, list):
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        return "".join(text_parts)

    if content is None:
        return ""

    return str(content)


def extract_last_user_message(messages: List[Dict[str, Any]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return normalize_message_content(message.get("content", ""))
    return ""
