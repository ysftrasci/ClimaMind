"""Matplotlib weekly temperature chart embedded in Tkinter."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import matplotlib.pyplot as plt
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from climamind.domain.models.weather import DailyForecast


def render_weekly_chart(
    parent: tk.Misc,
    forecast: Sequence[DailyForecast | Mapping[str, Any]],
    city: str,
) -> FigureCanvasTkAgg | None:
    """
    Draw a 5-day temperature line chart (mirrors ``display_weekly_graph``).

    Returns the FigureCanvasTkAgg wrapper so the view can retain a reference.
    """
    if not forecast:
        return None

    dates: list[str] = []
    temps: list[float] = []
    for day in forecast:
        if isinstance(day, DailyForecast):
            dates.append(day.date)
            temps.append(day.temp)
        else:
            dates.append(str(day["date"]))
            temps.append(float(day["temp"]))

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.plot(dates, temps, marker="o", color="blue")
    ax.set_title(f"5-Day Temperature in {city}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Temperature (°C)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)
    return canvas
