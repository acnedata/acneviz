from __future__ import annotations
import math
import io

from pathlib import Path
from joblib import Parallel, delayed

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from tqdm import tqdm
from PIL import Image
from acneviz.colors import DarkMode, LightMode, AcneColors
from acneviz.plots._protocol import Plot


AXIS_EXPANSION_FACTOR = 0.2


class Embedding3D(Plot):
    def __init__(
        self,
        data: pd.DataFrame,
        x_column: str,
        y_column: str,
        z_column: str,
        id_column: str | None = None,
        size_column: str | None = None,
        label_size: int = 30,
        color_palette: list[str] = AcneColors.discrete_palette,
        dark_mode: bool = False,
        legend_title: str | None = None,
    ) -> None:
        self._data = data
        self._x = x_column
        self._y = y_column
        self._z = z_column
        self._id = id_column
        self._size = size_column
        self._label_size = label_size
        self._color_palette = color_palette
        self._legend_title = legend_title

        self._grid_width = 3

        mode = DarkMode if dark_mode else LightMode
        self._background_color = mode.background_color
        self._grid_color = mode.grid_color
        self._label_color = mode.text_color

        self._figure = self._plot()

    def overlay(self, other: Embedding3D) -> Embedding3D:
        """Overlay another Embedding3D plot on top of this one."""
        self._figure.add_trace(other._figure.data)
        return self

    def save_gif(
        self, path: Path | str, fps: int = 30, speed: float = 30, scale: int | None = 2
    ) -> None:
        """
        Creates and saves a GIF of a 3D plot, rotating around the Z-axis.
        'speed' is in deg/s
        """

        fig = self._figure
        x_eye, y_eye, z_eye = (1.2, 1.2, 0.5)
        step = math.radians(speed / fps)
        fig.update_layout(scene_camera_eye=dict(x=x_eye, y=y_eye, z=z_eye))

        frames = []
        for t in np.arange(0, math.radians(360), step):
            xe, ye, ze = _rotate_around_z(x_eye, y_eye, z_eye, -t)
            frames.append(dict(x=xe, y=ye, z=ze))

        gif_frames: list[Image.Image] = list(
            Parallel(n_jobs=-1)(
                delayed(_render_frame)(fig, frame, scale) for frame in tqdm(frames)
            )  # type: ignore
        )

        gif_frames[0].save(
            path,
            save_all=True,
            append_images=gif_frames[1:],
            optimize=False,
            duration=int(round(1000 / fps, 0)),
            loop=0,
            interlace=False,
        )

    def _plot(self) -> go.Figure:
        if self._id:
            figure = px.scatter_3d(
                self._data,
                x=self._x,
                y=self._y,
                z=self._z,
                color=self._id,
                color_discrete_sequence=self._color_palette,
                width=1600,
                height=1200,
            )
        elif self._size:
            figure = px.scatter_3d(
                self._data,
                x=self._x,
                y=self._y,
                z=self._z,
                size=self._size,
                color_discrete_sequence=self._color_palette,
                width=1600,
                height=1200,
            )
        elif self._id and self._size:
            figure = px.scatter_3d(
                self._data,
                x=self._x,
                y=self._y,
                z=self._z,
                color=self._id,
                size=self._size,
                color_discrete_sequence=self._color_palette,
                width=1600,
                height=1200,
            )
        else:
            figure = px.scatter_3d(
                self._data,
                x=self._x,
                y=self._y,
                z=self._z,
                color=self._id,
                color_discrete_sequence=self._color_palette,
                width=1600,
                height=1200,
            )

        x_min, x_max = self._data[self._x].min(), self._data[self._x].max()
        y_min, y_max = self._data[self._y].min(), self._data[self._y].max()
        z_min, z_max = self._data[self._z].min(), self._data[self._z].max()

        x_range = (
            x_min - (x_max - x_min) * AXIS_EXPANSION_FACTOR,
            x_max + (x_max - x_min) * AXIS_EXPANSION_FACTOR,
        )
        y_range = (
            y_min - (y_max - y_min) * AXIS_EXPANSION_FACTOR,
            y_max + (y_max - y_min) * AXIS_EXPANSION_FACTOR,
        )
        z_range = (
            z_min - (z_max - z_min) * AXIS_EXPANSION_FACTOR,
            z_max + (z_max - z_min) * AXIS_EXPANSION_FACTOR,
        )

        figure.update_layout(
            plot_bgcolor=self._background_color,
            paper_bgcolor=self._background_color,
            scene=dict(
                xaxis=dict(
                    showticklabels=False,
                    title="",
                    visible=True,
                    range=x_range,
                    showbackground=False,
                    gridcolor=self._grid_color,
                    gridwidth=self._grid_width,
                    showline=False,
                    zeroline=False,
                ),
                yaxis=dict(
                    showticklabels=False,
                    title="",
                    visible=True,
                    range=y_range,
                    showbackground=False,
                    gridcolor=self._grid_color,
                    gridwidth=self._grid_width,
                    showline=False,
                    zeroline=False,
                ),
                zaxis=dict(
                    showticklabels=False,
                    title="",
                    range=z_range,
                    showbackground=False,
                    gridcolor=self._grid_color,
                    gridwidth=self._grid_width,
                    showline=False,
                    zeroline=False,
                ),
            ),
            legend_font_size=self._label_size * 0.9,
            legend_font_color=self._label_color,
        )

        if self._legend_title:
            figure.update_layout(legend_title_text=self._legend_title)

        return figure


def _rotate_around_z(x, y, z, theta):
    """Rotates a 3D vector around it's Z-axis. 'theta' is in radians."""
    w = x + 1j * y
    return (np.real(np.exp(1j * theta) * w), np.imag(np.exp(1j * theta) * w), z)


def _render_frame(fig: go.Figure, frame: dict[str, float], scale: int) -> Image.Image:
    fig.update_layout(scene_camera_eye=frame)
    return Image.open(io.BytesIO(fig.to_image(format="png", scale=scale))).copy()
