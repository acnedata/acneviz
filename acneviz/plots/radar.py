from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from acneviz.colors import AcneColors, DarkMode, LightMode
from acneviz.utils import validate_png


class Radar:
    """Creates a radar plot from a dataframe in long format.

    Accepted color values are any valid CSS color formated as a string, e.g. "red", "#ff0000",
    "rgb(255, 0, 0)", "rgb(1, 0, 0)", "rgba(1, 0, 0, 0.5).

    Require Parameters
    ------------------
    data : pd.DataFrame
        A dataframe in long format with a column corresponding to the variables and a
        column corresponding to the aggregated values. Optionally, a column corresponding
        to the id of each observation can be provided, e.g. the cluster id)

    Optional Keyword Parameters
    ---------------------------
    id_column : str | None
        The name of the column corresponding to the id of each observation, by default None
    variable_column : str
        The name of the column corresponding to the variables, by default "variable"
    value_column : str
        The name of the column corresponding to the aggregated values, by default "value"
    min_value : int | float
        The minimum value of the radar plot, by default 0
    max_value : int | float | None
        The maximum value of the radar plot, defaults to the maximum value in the data
    grid_interval : int | float
        The interval between the grid lines, by default 1
    color_palette : list[str] | None
        The color palette to use, defaults to AcneColors.discrete_palette
    label_size : int
        The size of the labels, by default 30
    tick_size : int
        The size of the tick labels, by default 24
    height : int
        The height of the plot in pixels, by default 1080
    width : int | None
        The width of the plot in pixels. If 'None', defaults to width of a 4:3 aspect ratio in
        respect to the height
    legend_title : str | None
        The title of the legend. If "None", the id column name is used
    darkmode : bool
        Whether to use dark mode, by default False
    """

    def __init__(
        self,
        data: pd.DataFrame,
        *,
        id_column: str | None = None,
        variable_column: str,
        value_column: str,
        min_value: int | float = 0,
        max_value: int | float | None = None,
        grid_interval: int | float = 1,
        color_palette: list[str] = AcneColors.discrete_palette,
        label_size: int = 30,
        tick_size: int = 24,
        height: int = 1080,
        width: int | None = None,
        legend_title: str | None = None,
        darkmode: bool = False,
    ) -> None:
        self._data = data.copy()
        self._variable_column = variable_column
        self._value_column = value_column
        self._id_column = id_column

        self.min_value = min_value

        if max_value:
            self.max_value = max_value
        else:
            self.max_value = int(data[value_column].max())

        self.grid_interval = grid_interval

        if width:
            self.width = width
        else:
            self.width = height / 3 * 4

        if darkmode:
            mode = DarkMode
        else:
            mode = LightMode

        self.background_color = mode.background_color
        self.grid_color = mode.grid_color
        self.label_color = mode.text_color
        self.tick_color = mode.annotation_color

        self.color_palette = color_palette
        self.label_size = label_size
        self.tick_size = tick_size
        self.height = height
        self.legend_title = legend_title
        self.gridwith = 2
        self.griddash = "dot"

        self._figure = self._plot()

    def show(self) -> Radar:
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
            self._figure.update_layout(paper_bgcolor=self.background_color)
            self._figure.update_layout(plot_bgcolor=self.background_color)

    def _plot(self) -> go.Figure:
        figure = px.line_polar(
            self._data,
            r=self._value_column,
            theta=self._variable_column,
            color=self._id_column,
            line_close=True,
            width=self.width,
            height=self.height,
            range_r=[self.min_value, self.max_value * 1.01],
            color_discrete_sequence=self.color_palette,
        )

        if self.legend_title:
            figure.update_layout(legend_title_text=self.legend_title)

        figure.update_layout(
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            legend_font_size=self.label_size * 0.9,
            legend_font_color=self.label_color,
        )
        figure.update_polars(
            angularaxis_griddash=self.griddash,
            angularaxis_gridwidth=self.gridwith,
            angularaxis_gridcolor=self.grid_color,
            angularaxis_tickfont_color=self.label_color,
            angularaxis_tickfont_size=self.label_size,
            angularaxis_showline=False,
            radialaxis_griddash=self.griddash,
            radialaxis_gridwidth=self.gridwith,
            radialaxis_gridcolor=self.grid_color,
            radialaxis_tickfont_color=self.tick_color,
            radialaxis_tickfont_size=self.tick_size,
            radialaxis_tick0=self.min_value,
            radialaxis_dtick=self.grid_interval,
            radialaxis_ticklabelstep=self.max_value,
            radialaxis_showline=False,
            bgcolor=self.background_color,
        )

        figure.update_traces(line_width=4)

        return figure


def radar_chart(data: pd.DataFrame, palette: list[str], color: str) -> go.Figure:
    fig = px.line_polar(
        data,
        r="value",
        theta="variable",
        color=color,
        line_close=True,
        width=640,
        height=448,
        template="plotly_white",
        range_r=[1, 7],
        color_discrete_sequence=palette,
    )

    fig.update_polars(
        angularaxis_tickfont_family="Helvetica Neue",
        radialaxis_tickfont_family="Helvetica Neue",
        angularaxis_tickfont_size=16,
        radialaxis_tickfont_size=14,
        radialaxis_tickfont_color="#aaa",
        radialaxis_tickmode="array",
        radialaxis_tickvals=[1, 2, 3, 4, 5, 6, 7],
        radialaxis_ticktext=["1"] + [""] * 5 + ["7"],
        bgcolor="rgba(0,0,0,0)",
    )

    # change line width
    fig.update_traces(line_width=4)

    # remmove legend
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig
