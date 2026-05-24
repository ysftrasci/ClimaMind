"""Screen navigation and root window lifecycle."""

from __future__ import annotations

from collections.abc import Callable

import tkinter as tk

from climamind.ui.theme import UiTheme

ViewBuilder = Callable[[], None]
CleanupCallback = Callable[[], None]


class NavigationController:
    """
    Manages clearing the root window and switching between views.

    Mirrors ``clear_window`` and view transitions from maincode.py.
    Each navigation can register an *on_leave* hook to stop animations or audio.
    """

    def __init__(
        self,
        root: tk.Tk,
        theme: UiTheme | None = None,
        default_bg: str | None = None,
    ) -> None:
        self.root = root
        self.theme = theme or UiTheme()
        self._default_bg = default_bg or self.theme.default_window_bg
        self._current_cleanup: CleanupCallback | None = None
        self._current_view_name: str | None = None

    @property
    def current_view(self) -> str | None:
        return self._current_view_name

    def clear(self, bg_color: str | None = None) -> None:
        """Remove all widgets from the root (``clear_window`` behavior)."""
        self._run_cleanup()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg=bg_color or self._default_bg)

    def navigate(
        self,
        builder: ViewBuilder,
        *,
        view_name: str | None = None,
        bg_color: str | None = None,
        on_leave: CleanupCallback | None = None,
    ) -> None:
        """
        Replace the current screen with a new one.

        Args:
            builder: Callable that constructs widgets on ``self.root``.
            view_name: Optional label for debugging or future history stack.
            bg_color: Root background for the new screen.
            on_leave: Called before the next ``navigate`` or ``clear`` (stop timers, etc.).
        """
        self.clear(bg_color)
        self._current_cleanup = on_leave
        self._current_view_name = view_name
        builder()

    def set_cleanup(self, on_leave: CleanupCallback | None) -> None:
        """Register or replace the cleanup callback for the active view."""
        self._current_cleanup = on_leave

    def _run_cleanup(self) -> None:
        if self._current_cleanup is not None:
            try:
                self._current_cleanup()
            except Exception as exc:
                print(f"⚠️ View cleanup error: {exc}")
        self._current_cleanup = None
        self._current_view_name = None
