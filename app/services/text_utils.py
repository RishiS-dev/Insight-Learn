import re

def _strip_control_chars(s: str) -> str:
    if s is None:
        return ""
    # Remove NULs explicitly
    s = s.replace("\x00", "")
    # Remove other non-printable control chars except tab/newline/CR
    s = re.sub(r"[\x01-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    # Collapse runs of spaces/tabs
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def clean_text(s: str) -> str:
    """
    Sanitize text for DB and downstream processing:
    - Attempt to fix UTF-16-like interleaved NUL patterns.
    - Remove any remaining NULs/control chars.
    """
    if not s:
        return ""
    txt = s

    # Heuristic: if a large fraction are NULs, try decoding as UTF-16
    if "\x00" in txt and txt.count("\x00") > (len(txt) // 4):
        try:
            # Encode to bytes (latin1 keeps code points <= 255) then decode as UTF-16
            decoded = txt.encode("latin1", errors="ignore").decode("utf-16", errors="ignore")
            if decoded:
                txt = decoded
        except Exception:
            # Fall back to plain removal below
            pass

    # Final cleanup
    txt = _strip_control_chars(txt)
    # Optional: remove U+FFFD replacement chars if any
    txt = txt.replace("\uFFFD", "")
    return txt