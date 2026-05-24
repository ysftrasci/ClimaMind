"""Central registry for navigating between views."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

from climamind.context import AppContext

ViewHandler = Callable[[], None]


class ViewRouter:
    """Maps view names to show handlers; unknown routes show a placeholder dialog."""

    _PLACEHOLDER_LABELS: dict[str, str] = {}

    def __init__(self, ctx: AppContext) -> None:
        self._ctx = ctx
        self._routes: dict[str, ViewHandler] = {}

    def register(self, name: str, handler: ViewHandler) -> None:
        self._routes[name] = handler

    def go(self, name: str) -> None:
        handler = self._routes.get(name)
        if handler is not None:
            handler()
            return
        label = self._PLACEHOLDER_LABELS.get(name, name.replace("_", " ").title())
        messagebox.showinfo(
            "Clima Mind",
            f"The '{label}' screen is not available yet.\n"
            "It will be added in the next development step (7B).",
        )
