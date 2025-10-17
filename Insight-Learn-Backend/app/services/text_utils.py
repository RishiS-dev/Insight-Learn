import re

def _strip_control_chars(s: str) -> str:
    if s is None:
        return ""
    # Remove NULs explicitly
    s = s.replace("\x00", "")
    # Remove other control chars except tab/newline/CR
    s = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    # Collapse repeated spaces/tabs
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def clean_text(s: str) -> str:
    """
    Sanitize text for DB and downstream processing:
    - Attempt to fix UTF-16-like interleaved NUL patterns.
    - Remove any remaining NULs/control chars.
    - Collapse whitespace.
    """
    if not s:
        return ""
    txt = s

    # Heuristic: if many NULs present, try decoding as UTF-16
    if "\x00" in txt and txt.count("\x00") > (len(txt) // 4):
        try:
            decoded = txt.encode("latin1", errors="ignore").decode("utf-16", errors="ignore")
            if decoded:
                txt = decoded
        except Exception:
            pass

    # Final cleanup
    txt = _strip_control_chars(txt)
    # Remove replacement char if present
    txt = txt.replace("\uFFFD", "")
    return txt