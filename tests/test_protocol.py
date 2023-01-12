from acneviz import CorrelationNetworkGraph, Radar
from acneviz.plots._protocol import Plot


def test_correlation_network_graph():
    assert isinstance(CorrelationNetworkGraph, Plot)


def test_radar():
    assert isinstance(Radar, Plot)
