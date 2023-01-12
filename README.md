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

While depending on the type of data, figures are created from Pandas DataFrames of different
structure and with different parameters, all plot classes follow the same protocol.

The plot is instantiated with the required and optional parameters and the resulting
object assigned to a variable. For example:

```Python
plot = Radar(df)
```

It can then be shown in a notbeook with:
```Python
plot.show()
```

and saved to a file with:
```Python
plot.save("myplot.png")
```

Showing and saving the plot can also be achieved as a one-liner without assigning the
plot to a variable like so:
```Python
Radar(df).show().save("myplot.png")
```

Make sure to check the docstring of a plot to find out what kind of data it expects
and how it can be modified.

### Theming

ACNE VIZ comes with two color schemes. Light mode and dark mode on white and black
background, respectively. Light mode is default; to activate dark mode do:
```Python
Radar(df, darkmode=True)
```

### Advanced

Since ACNE VIZ is a thin wrapper around Plotly, the underlying `plotly.graph_object.Figure`
can be accessed with:
```Python
plot._figure
```
That way we can do more advanced modifications by dropping down to the Plotly API.
For example, we could use modify the layout with:
```Python
plot._figure.update_layout()
```

To see which settings are availble, check out
[https://plotly.com/python/reference/layout/](https://plotly.com/python/reference/layout/).
