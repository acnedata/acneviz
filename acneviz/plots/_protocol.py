from __future__ import annotations

from typing import Protocol, runtime_checkable

from pandas import DataFrame
from plotly.graph_objects import Figure


@runtime_checkable
class Plot(Protocol):
    def __init__(self, data: DataFrame, *, dark_mode: bool) -> None:
        ...

    def show(self) -> Plot:
        ...

    def save(self, path: str, transparent_background: bool, scale: int | float) -> None:
        ...

    def _plot(self) -> Figure:
        ...
