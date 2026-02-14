"""Focus areas for audits."""

from nightwatch.focus.base import BaseFocus
from nightwatch.focus.dependencies import DependenciesFocus
from nightwatch.focus.docs import DocsFocus
from nightwatch.focus.hygiene import HygieneFocus
from nightwatch.focus.patterns import PatternsFocus
from nightwatch.focus.performance import PerformanceFocus
from nightwatch.focus.security import SecurityFocus
from nightwatch.focus.testing import TestingFocus

FOCUS_AREAS: dict[str, type[BaseFocus]] = {
    "security": SecurityFocus,
    "docs": DocsFocus,
    "patterns": PatternsFocus,
    "testing": TestingFocus,
    "hygiene": HygieneFocus,
    "dependencies": DependenciesFocus,
    "performance": PerformanceFocus,
}

__all__ = [
    "FOCUS_AREAS",
    "BaseFocus",
    "SecurityFocus",
    "DocsFocus",
    "PatternsFocus",
    "TestingFocus",
    "HygieneFocus",
    "DependenciesFocus",
    "PerformanceFocus",
]
