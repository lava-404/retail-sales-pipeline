"""Defence in depth: even predefined SQL is checked before it is sent to BigQuery.
If you later add LLM-generated SQL, it MUST pass through this guard too.
"""
import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|merge|drop|alter|create|truncate|grant|revoke|call|execute|export|load)\b",
    re.IGNORECASE,
)
TABLE_REF = re.compile(r"(?:from|join)\s+`([^`]+)`", re.IGNORECASE)


def is_safe_select(sql: str, allowed_dataset: str) -> tuple[bool, str]:
    """Allow a single SELECT/WITH statement that reads only from the marts dataset."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        return False, "multiple statements are not allowed"
    if not re.match(r"^(select|with)\b", stripped, re.IGNORECASE):
        return False, "only SELECT queries are allowed"
    if FORBIDDEN.search(stripped):
        return False, "query contains a forbidden keyword"
    if "--" in stripped or "/*" in stripped:
        return False, "comments are not allowed"
    refs = TABLE_REF.findall(stripped)
    if not refs:
        return False, "no table reference found"
    for ref in refs:
        if f".{allowed_dataset}." not in f".{ref}.":
            return False, f"table {ref} is outside the allowed dataset"
    return True, "ok"
