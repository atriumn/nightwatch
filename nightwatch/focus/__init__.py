"""Focus areas for audits."""

from nightwatch.focus.base import BaseFocus
from nightwatch.focus.docs import DocsFocus
from nightwatch.focus.patterns import PatternsFocus
from nightwatch.focus.security import SecurityFocus

FOCUS_AREAS: dict[str, type[BaseFocus]] = {
    "security": SecurityFocus,
    "docs": DocsFocus,
    "patterns": PatternsFocus,
}

__all__ = ["FOCUS_AREAS", "BaseFocus", "SecurityFocus", "DocsFocus", "PatternsFocus"]
