from pathlib import Path
from typing import Iterable, cast
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pl_colors
from statistics import mean

import numpy as np
from ast import literal_eval

from acneviz.colors import AcneColors


class CorrelationNetworkGraph:
    def __init__(
        self,
        correlation_matrix: pd.DataFrame,
        *,
        color: str = AcneColors.dark_sea_green,
        background_color: str = "white",
        label_color: str = "black",
        label_size: int = 20,
    ) -> None:
        self.color = color
        self.background_color = background_color
        self.label_color = label_color
        self.label_size = label_size

        self._graph = _build_graph_from_correlation_matrix(correlation_matrix)
        self._figure = self._plot()

    def show(self) -> None:
        self._figure.show()

    def save(self, path: Path | str) -> None:
        pass

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
            width=800,
            height=800,
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
                line_width=abs(correlation) * 100,
                line_color=self.color,
                opacity=abs(correlation),
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
                    size=avg_correlation * 500,
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

    if not np.allclose(np.abs(correlation_matrix.values), correlation_matrix.values):
        raise ValueError("Correlation matrix must be absolute")


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


# def get_color_for_val(val, vmin, vmax, pl_colors):

#     if pl_colors[0][:3] != "rgb":
#         raise ValueError("This function works only with Plotly rgb-colorscales")
#     if vmin >= vmax:
#         raise ValueError("vmin should be < vmax")

#     scale = [k / (len(pl_colors) - 1) for k in range(len(pl_colors))]

#     colors_01 = (
#         np.array([literal_eval(color[3:]) for color in pl_colors]) / 255.0
#     )  # color codes in [0,1]

#     v = (val - vmin) / (vmax - vmin)  # val is mapped to v in [0,1]
#     # find two consecutive values in plotly_scale such that   v is in  the corresponding interval
#     idx = 1

#     while v > scale[idx]:
#         idx += 1
#     vv = (v - scale[idx - 1]) / (scale[idx] - scale[idx - 1])

#     # get   [0,1]-valued color code representing the rgb color corresponding to val
#     val_color01 = colors_01[idx - 1] + vv * (colors_01[idx] - colors_01[idx - 1])
#     val_color_0255 = (255 * val_color01 + 0.5).astype(int)
#     return f"rgb{str(tuple(val_color_0255))}"
