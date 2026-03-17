from typing import Any, List, Optional, Set


def safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def extract_pic_ids(payload: Any) -> List[int]:
    pic_ids: Set[int] = set()

    def walk(node: Any):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"pic_id", "pic_id_list"}:
                    if isinstance(value, list):
                        for item in value:
                            parsed = safe_int(item)
                            if parsed is not None:
                                pic_ids.add(parsed)
                    else:
                        parsed = safe_int(value)
                        if parsed is not None:
                            pic_ids.add(parsed)
                else:
                    walk(value)
            return

        if isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return sorted(pic_ids)
