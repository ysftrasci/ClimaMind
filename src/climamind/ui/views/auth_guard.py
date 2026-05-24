"""Shared login checks for protected screens."""

from __future__ import annotations

from collections.abc import Callable
from tkinter import messagebox

from climamind.context import AppContext


def require_email(ctx: AppContext, on_denied: Callable[[], None]) -> str | None:
    """Return the logged-in email or run *on_denied* after showing an error."""
    email = ctx.session_manager.email
    if not email:
        messagebox.showerror("Error", "You must be logged in to access this feature.")
        on_denied()
        return None
    return email
