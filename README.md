# ACNE VIZ

ACNE VIZ is a plotting library thinly wrapping around Plotly. It's goal is not to be a general
purpose plotting library, but to provide a easy access to pre-defined, good looking graphs for client
presentations following a consistent visual identity.

## Installation

Since this is a private repo, so long as the GitHub credentials are set up properly,
we can simply install the package with Poetry.

```Bash
poetry add acneviz --git https://github.com/acnedata/acneviz
```

## Usage

While depending on the type of data, figures are created from DataFrames of different
structure and with different parameters, all plot classes follow the same protocol.

The plot is instantiated with the required and optional parameters and the resulting
object assigned to a variable.

```Python
plot = Plot(df)
```

It can then be shown in a notbeook with
```Python
plot.show()
```

and saved to a file with
```Python
plot.save("./figures/myplot.png")
```