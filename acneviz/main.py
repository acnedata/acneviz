from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol, Union

import matplotlib.pyplot as plt
from numpy.typing import ArrayLike
from typing_extensions import Self


class Kind(Enum):
    BAR = auto()
    BOX = auto()


class Orientation(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


@dataclass
class Plot:
    x: ArrayLike
    y: ArrayLike

    def bar(self) -> Self:
        self.kind = Kind.BAR
        return self

    def vertical(self) -> Self:
        self.orientation = Orientation.VERTICAL
        return self

    def compile(self):
        ...

    def plot(self):
        ...

    def save(self):
        ...


@dataclass
class BarPlot:
    x: ArrayLike
    y: ArrayLike

    def plot(self):
        plt.bar(self.x, self.y)
