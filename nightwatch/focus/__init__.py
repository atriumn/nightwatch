"""Focus areas for audits."""

from nightwatch.focus.base import BaseFocus
from nightwatch.focus.security import SecurityFocus
from nightwatch.focus.docs import DocsFocus

FOCUS_AREAS: dict[str, type[BaseFocus]] = {
    "security": SecurityFocus,
    "docs": DocsFocus,
}

__all__ = ["FOCUS_AREAS", "BaseFocus", "SecurityFocus", "DocsFocus"]
