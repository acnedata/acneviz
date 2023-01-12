from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from statistics import mean
from typing import cast

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from acneviz.colors import AcneColors
from acneviz.utils import clamp, validate_png

MAX_NODE_SIZE = 500
MAX_EDGE_WIDTH = 100


class CorrelationNetworkGraph:
    """Creater a network graph plot from a correlation matric.

    Accepted color values are any valid CSS color formated as a string, e.g. "red", "#ff0000",
    "rgb(255, 0, 0)", "rgb(1, 0, 0)", "rgba(1, 0, 0, 0.5).

    Require Parameters
    ------------------
    correlation_matrix : pd.DataFrame
        A correlation matrix with the same index and columns.

    Optional Keyword Parameters
    ---------------------------
    size : int
        The size of the plot in pixels, by default 1080
    color : str
        The color of the edges, by default AcneColors.dark_sea_green
    background_color : str
        The background color of the plot, by default "white"
    label_color : str
        The color of the node labels, by default "black"
    label_size : int
        The size of the node labels, by default 20
    node_size_factor : int | float
        The factor to scale the node size by, by default 1.0
    edge_width_factor : int | float
        The factor to scale the edge width by, by default 1.0
    opacity_factor : int | float
        The factor to scale the edge opacity by, by default 1.0

    Methods
    -------
    show()
        Show the plot, for use in a Jupyter notebook.
    save(path: Path | str)
        Save the plot to a file.
    """

    def __init__(
        self,
        correlation_matrix: pd.DataFrame,
        *,
        size: int = 1080,
        color: str = AcneColors.dark_sea_green,
        background_color: str = "white",
        label_color: str = "black",
        label_size: int = 20,
        node_size_factor: int | float = 1.0,
        edge_width_factor: int | float = 1.0,
        opacity_factor: int | float = 1.0,
    ) -> None:
        self.size = size
        self.color = color
        self.background_color = background_color
        self.label_color = label_color
        self.label_size = label_size
        self.node_size_factor = node_size_factor
        self.edge_width_factor = edge_width_factor
        self.opacity_factor = opacity_factor

        self._graph = _build_graph_from_correlation_matrix(correlation_matrix)
        self._figure = self._plot()

    def show(self) -> CorrelationNetworkGraph:
        self._figure.show()
        return self

    def save(self, path: Path | str, *, trasparent_background: bool = False) -> None:
        """Save the plot to a file. Accepts only .png as file extension."""
        if trasparent_background:
            self._figure.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
            )

        self._figure.write_image(validate_png(path), scale=2)

        if trasparent_background:
            self._figure.update_layout(
                plot_bgcolor=self.background_color, paper_bgcolor=self.background_color
            )

    def _plot(self) -> go.Figure:
        # Get node x,y positions
        self._node_positions = nx.circular_layout(self._graph)

        edge_traces = self._edge_traces()
        node_traces = self._node_traces()

        layout = go.Layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )

        plot = go.Figure(data=list(edge_traces) + list(node_traces), layout=layout)
        plot.update_layout(
            width=self.size,
            height=self.size,
            template="plotly_white",
            plot_bgcolor=self.background_color,
            paper_bgcolor=self.background_color,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        return plot

    def _edge_traces(self) -> Iterable[go.Scatter]:
        """Create a line trace for each edge in the graph"""
        for node_0, node_1, data in self._graph.edges(data=True):  # type: ignore
            x0, y0 = self._node_positions[node_0]
            x1, y1 = self._node_positions[node_1]

            correlation = data["weight"]  # type: ignore

            yield go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line_width=abs(correlation) * MAX_EDGE_WIDTH * self.edge_width_factor,
                line_color=self.color,
                opacity=clamp(abs(correlation) * self.opacity_factor, 0, 1),
            )

    def _node_traces(self) -> Iterable[go.Scatter]:
        """Create a point trace for each node in the graph"""

        for node in self._graph.nodes():
            node_x, node_y = self._node_positions[node]

            avg_correlation = _avg_edge_weight_of_node(self._graph, cast(str, node))

            yield go.Scatter(
                x=[node_x],
                y=[node_y],
                mode="markers+text",
                marker=dict(
                    size=avg_correlation * MAX_NODE_SIZE * self.node_size_factor,
                    opacity=1,
                    line_width=5,
                    color=self.background_color,
                    line_color=self.color,
                ),
                text=node,
                textfont=dict(size=self.label_size, color=self.label_color),
                textposition="middle center",
            )


def _validate_correlation_matrix(correlation_matrix: pd.DataFrame) -> None:
    """Check that the correlation matrix is valid"""
    if not isinstance(correlation_matrix, pd.DataFrame):
        raise TypeError("Correlation matrix must be a pandas DataFrame")

    if not correlation_matrix.index.equals(correlation_matrix.columns):
        raise ValueError("Correlation matrix must be square")

    if not np.allclose(correlation_matrix.values, correlation_matrix.values.T):
        raise ValueError("Correlation matrix must be symmetric")

    if not np.allclose(correlation_matrix.values.diagonal(), 1):
        raise ValueError("Correlation matrix must have 1 on the diagonal")

    if not correlation_matrix.index.equals(correlation_matrix.columns):
        raise ValueError("Correlation matrix must have same index and columns")


def _build_graph_from_correlation_matrix(correlation_matrix: pd.DataFrame) -> nx.Graph:
    """Create a graph from the correlation matrix keeping order of nodes"""
    _validate_correlation_matrix(correlation_matrix)
    edges = nx.from_pandas_adjacency(correlation_matrix).edges(data=True)
    graph = nx.Graph()
    graph.add_edges_from(edges)
    graph.add_nodes_from(correlation_matrix.columns)
    graph.remove_edges_from(nx.selfloop_edges(graph))
    _remove_edges_wo_weight(graph)

    return graph


def _remove_edges_wo_weight(graph: nx.Graph):
    """
    Remove edges with missing values inplace.
    """
    graph.remove_edges_from(
        [
            (node1, node2)
            for node1, node2, edge_data in graph.edges(data=True)  # type: ignore
            if pd.isna(edge_data["weight"])  # type: ignore
        ]
    )


def _avg_edge_weight_of_node(graph: nx.Graph, node: str) -> float:
    """Calculate the average edge weight of the given node"""
    return mean(
        abs(edge_data["weight"])  # type: ignore
        for _, _, edge_data in graph.edges(node, data=True)  # type: ignore
    )
