from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from acneviz.colors import AcneColors, DarkMode, LightMode
from acneviz.plots._protocol import Plot


class Radar(Plot):
    """Creates a radar plot from a dataframe in long format.

    Accepted color values are any valid CSS color formated as a string, e.g. "red", "#ff0000",
    "rgb(255, 0, 0)", "rgb(1, 0, 0)", "rgba(1, 0, 0, 0.5).

    Required Parameters
    ------------------
    data : pd.DataFrame
        A dataframe in long format with a column corresponding to the variables and a
        column corresponding to the aggregated values. Optionally, a column corresponding
        to the id of each observation can be provided, e.g. the cluster id)

    Optional Keyword Parameters
    ---------
    darkmode : bool
        Whether to use dark mode, by default False
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
        The title of the legend. If "None", the id column name is used by default

    Methods
    -------
    show()
        Displays the plot in a Jupyter notebook
    save(path: str, scale: int | float)
        Saves the plot as a png file
    """

    def __init__(
        self,
        data: pd.DataFrame,
        *,
        darkmode: bool = False,
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
    ) -> None:
        self.color_palette = color_palette
        self.label_size = label_size
        self.tick_size = tick_size
        self.height = height
        self.legend_title = legend_title

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

        mode = DarkMode if darkmode else LightMode

        self._background_color = mode.background_color
        self._grid_color = mode.grid_color
        self._label_color = mode.text_color
        self._tick_color = mode.annotation_color

        self.gridwith = 2
        self.griddash = "dot"

        self._data = data.copy()
        self._variable_column = variable_column
        self._value_column = value_column
        self._id_column = id_column
        self._figure = self._plot()

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
            plot_bgcolor=self._background_color,
            paper_bgcolor=self._background_color,
            legend_font_size=self.label_size * 0.9,
            legend_font_color=self._label_color,
        )
        figure.update_polars(
            angularaxis_griddash=self.griddash,
            angularaxis_gridwidth=self.gridwith,
            angularaxis_gridcolor=self._grid_color,
            angularaxis_tickfont_color=self._label_color,
            angularaxis_tickfont_size=self.label_size,
            angularaxis_showline=False,
            radialaxis_griddash=self.griddash,
            radialaxis_gridwidth=self.gridwith,
            radialaxis_gridcolor=self._grid_color,
            radialaxis_tickfont_color=self._tick_color,
            radialaxis_tickfont_size=self.tick_size,
            radialaxis_tick0=self.min_value,
            radialaxis_dtick=self.grid_interval,
            radialaxis_ticklabelstep=self.max_value,
            radialaxis_showline=False,
            bgcolor="rgba(0,0,0,0)",
        )

        figure.update_traces(line_width=4)

        return figure
