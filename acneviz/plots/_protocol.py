from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable

from pandas import DataFrame
from plotly.graph_objects import Figure

from acneviz.utils import validate_png


@runtime_checkable
class Plot(Protocol):
    _data: DataFrame
    _figure: Figure
    _background_color: str

    def __init__(self, data: DataFrame, dark_mode: bool) -> None:
        ...

    def show(self) -> Plot:
        self._figure.show()
        return self

    def save(
        self,
        path: Path | str,
        *,
        transparent_background: bool = False,
        scale: int | float = 2,
    ) -> None:
        """Save the plot to a file. Accepts only .png as file extension."""
        if transparent_background:
            self._figure.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            self._figure.update_layout(plot_bgcolor="rgba(0,0,0,0)")

        self._figure.write_image(validate_png(path), scale=scale)

        if transparent_background:
            self._figure.update_layout(paper_bgcolor=self._background_color)
            self._figure.update_layout(plot_bgcolor=self._background_color)

    def _plot(self) -> Figure:
        ...
