from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Sequence,
)
from typing import (
    Any,
    Literal,
    NamedTuple,
    overload,
)

from matplotlib.axes import Axes
from matplotlib.colors import Colormap
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from pandas import Series
from pandas.core.frame import DataFrame
from scipy.stats.kde import gaussian_kde
from typing_extensions import TypeAlias

from pandas._typing import (
    ArrayLike,
    HashableT,
    HashableT1,
    HashableT2,
    HashableT3,
    npt,
)

class _BoxPlotT(NamedTuple):
    ax: Axes
    lines: dict[str, list[Line2D]]

_SingleColor: TypeAlias = (
    str | list[float] | tuple[float, float, float] | tuple[float, float, float, float]
)
_PlotAccessorColor: TypeAlias = str | list[_SingleColor] | dict[HashableT, _SingleColor]

@overload
def boxplot(
    data: DataFrame,
    column: Hashable | list[HashableT1] | None = ...,
    by: Hashable | list[HashableT2] | None = ...,
    ax: Axes | None = ...,
    fontsize: float | str | None = ...,
    rot: float = ...,
    grid: bool = ...,
    figsize: tuple[float, float] | None = ...,
    layout: tuple[int, int] | None = ...,
    return_type: Literal["axes"] | None = ...,
    **kwargs,
) -> Axes:
    """
Make a box plot from DataFrame columns.

Make a box-and-whisker plot from DataFrame columns, optionally grouped
by some other columns. A box plot is a method for graphically depicting
groups of numerical data through their quartiles.
The box extends from the Q1 to Q3 quartile values of the data,
with a line at the median (Q2). The whiskers extend from the edges
of box to show the range of the data. By default, they extend no more than
`1.5 * IQR (IQR = Q3 - Q1)` from the edges of the box, ending at the farthest
data point within that interval. Outliers are plotted as separate dots.

For further details see
Wikipedia's entry for `boxplot <https://en.wikipedia.org/wiki/Box_plot>`_.

Parameters
----------
data : DataFrame
    The data to visualize.
column : str or list of str, optional
    Column name or list of names, or vector.
    Can be any valid input to :meth:`pandas.DataFrame.groupby`.
by : str or array-like, optional
    Column in the DataFrame to :meth:`pandas.DataFrame.groupby`.
    One box-plot will be done per value of columns in `by`.
ax : object of class matplotlib.axes.Axes, optional
    The matplotlib axes to be used by boxplot.
fontsize : float or str
    Tick label font size in points or as a string (e.g., `large`).
rot : float, default 0
    The rotation angle of labels (in degrees)
    with respect to the screen coordinate system.
grid : bool, default True
    Setting this to True will show the grid.
figsize : A tuple (width, height) in inches
    The size of the figure to create in matplotlib.
layout : tuple (rows, columns), optional
    For example, (3, 5) will display the subplots
    using 3 rows and 5 columns, starting from the top-left.
return_type : {'axes', 'dict', 'both'} or None, default 'axes'
    The kind of object to return. The default is ``axes``.

    * 'axes' returns the matplotlib axes the boxplot is drawn on.
    * 'dict' returns a dictionary whose values are the matplotlib
      Lines of the boxplot.
    * 'both' returns a namedtuple with the axes and dict.
    * when grouping with ``by``, a Series mapping columns to
      ``return_type`` is returned.

      If ``return_type`` is `None`, a NumPy array
      of axes with the same shape as ``layout`` is returned.

**kwargs
    All other plotting keyword arguments to be passed to
    :func:`matplotlib.pyplot.boxplot`.

Returns
-------
result
    See Notes.

See Also
--------
pandas.Series.plot.hist: Make a histogram.
matplotlib.pyplot.boxplot : Matplotlib equivalent plot.

Notes
-----
The return type depends on the `return_type` parameter:

* 'axes' : object of class matplotlib.axes.Axes
* 'dict' : dict of matplotlib.lines.Line2D objects
* 'both' : a namedtuple with structure (ax, lines)

For data grouped with ``by``, return a Series of the above or a numpy
array:

* :class:`~pandas.Series`
* :class:`~numpy.array` (for ``return_type = None``)

Use ``return_type='dict'`` when you want to tweak the appearance
of the lines after plotting. In this case a dict containing the Lines
making up the boxes, caps, fliers, medians, and whiskers is returned.

Examples
--------

Boxplots can be created for every column in the dataframe
by ``df.boxplot()`` or indicating the columns to be used:

.. plot::
    :context: close-figs

    >>> np.random.seed(1234)
    >>> df = pd.DataFrame(np.random.randn(10, 4),
    ...                   columns=['Col1', 'Col2', 'Col3', 'Col4'])
    >>> boxplot = df.boxplot(column=['Col1', 'Col2', 'Col3'])  # doctest: +SKIP

Boxplots of variables distributions grouped by the values of a third
variable can be created using the option ``by``. For instance:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame(np.random.randn(10, 2),
    ...                   columns=['Col1', 'Col2'])
    >>> df['X'] = pd.Series(['A', 'A', 'A', 'A', 'A',
    ...                      'B', 'B', 'B', 'B', 'B'])
    >>> boxplot = df.boxplot(by='X')

A list of strings (i.e. ``['X', 'Y']``) can be passed to boxplot
in order to group the data by combination of the variables in the x-axis:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame(np.random.randn(10, 3),
    ...                   columns=['Col1', 'Col2', 'Col3'])
    >>> df['X'] = pd.Series(['A', 'A', 'A', 'A', 'A',
    ...                      'B', 'B', 'B', 'B', 'B'])
    >>> df['Y'] = pd.Series(['A', 'B', 'A', 'B', 'A',
    ...                      'B', 'A', 'B', 'A', 'B'])
    >>> boxplot = df.boxplot(column=['Col1', 'Col2'], by=['X', 'Y'])

The layout of boxplot can be adjusted giving a tuple to ``layout``:

.. plot::
    :context: close-figs

    >>> boxplot = df.boxplot(column=['Col1', 'Col2'], by='X',
    ...                      layout=(2, 1))

Additional formatting can be done to the boxplot, like suppressing the grid
(``grid=False``), rotating the labels in the x-axis (i.e. ``rot=45``)
or changing the fontsize (i.e. ``fontsize=15``):

.. plot::
    :context: close-figs

    >>> boxplot = df.boxplot(grid=False, rot=45, fontsize=15)  # doctest: +SKIP

The parameter ``return_type`` can be used to select the type of element
returned by `boxplot`.  When ``return_type='axes'`` is selected,
the matplotlib axes on which the boxplot is drawn are returned:

    >>> boxplot = df.boxplot(column=['Col1', 'Col2'], return_type='axes')
    >>> type(boxplot)
    <class 'matplotlib.axes._axes.Axes'>

When grouping with ``by``, a Series mapping columns to ``return_type``
is returned:

    >>> boxplot = df.boxplot(column=['Col1', 'Col2'], by='X',
    ...                      return_type='axes')
    >>> type(boxplot)
    <class 'pandas.core.series.Series'>

If ``return_type`` is `None`, a NumPy array of axes with the same shape
as ``layout`` is returned:

    >>> boxplot = df.boxplot(column=['Col1', 'Col2'], by='X',
    ...                      return_type=None)
    >>> type(boxplot)
    <class 'numpy.ndarray'>
    """
    pass
@overload
def boxplot(
    data: DataFrame,
    column: Hashable | list[HashableT1] | None = ...,
    by: Hashable | list[HashableT2] | None = ...,
    ax: Axes | None = ...,
    fontsize: float | str | None = ...,
    rot: float = ...,
    grid: bool = ...,
    figsize: tuple[float, float] | None = ...,
    layout: tuple[int, int] | None = ...,
    *,
    return_type: Literal["dict"],
    **kwargs,
) -> dict[str, list[Line2D]]: ...
@overload
def boxplot(
    data: DataFrame,
    column: Hashable | list[HashableT1] | None = ...,
    by: Hashable | list[HashableT2] | None = ...,
    ax: Axes | None = ...,
    fontsize: float | str | None = ...,
    rot: float = ...,
    grid: bool = ...,
    figsize: tuple[float, float] | None = ...,
    layout: tuple[int, int] | None = ...,
    *,
    return_type: Literal["both"],
    **kwargs,
) -> _BoxPlotT: ...

class PlotAccessor:
    def __init__(self, data) -> None: ...
    @overload
    def __call__(
        self,
        *,
        data: Series | DataFrame | None = ...,
        x: Hashable = ...,
        y: Hashable | Sequence[Hashable] = ...,
        kind: Literal[
            "line",
            "bar",
            "barh",
            "hist",
            "box",
            "kde",
            "density",
            "area",
            "pie",
            "scatter",
            "hexbin",
        ] = ...,
        ax: Axes | None = ...,
        subplots: Literal[False] | None = ...,
        sharex: bool = ...,
        sharey: bool = ...,
        layout: tuple[int, int] = ...,
        figsize: tuple[float, float] = ...,
        use_index: bool = ...,
        title: Sequence[str] | None = ...,
        grid: bool | None = ...,
        legend: bool | Literal["reverse"] = ...,
        style: str | list[str] | dict[HashableT1, str] = ...,
        logx: bool | Literal["sym"] = ...,
        logy: bool | Literal["sym"] = ...,
        loglog: bool | Literal["sym"] = ...,
        xticks: Sequence[float] = ...,
        yticks: Sequence[float] = ...,
        xlim: tuple[float, float] | list[float] = ...,
        ylim: tuple[float, float] | list[float] = ...,
        xlabel: str = ...,
        ylabel: str = ...,
        rot: float = ...,
        fontsize: float = ...,
        colormap: str | Colormap | None = ...,
        colorbar: bool = ...,
        position: float = ...,
        table: bool | Series | DataFrame = ...,
        yerr: DataFrame | Series | ArrayLike | dict | str = ...,
        xerr: DataFrame | Series | ArrayLike | dict | str = ...,
        stacked: bool = ...,
        secondary_y: bool | list[HashableT2] | tuple[HashableT2, ...] = ...,
        mark_right: bool = ...,
        include_bool: bool = ...,
        backend: str = ...,
        **kwargs: Any,
    ) -> Axes: ...
    @overload
    def __call__(
        self,
        *,
        data: Series | DataFrame | None = ...,
        x: Hashable = ...,
        y: Hashable | Sequence[Hashable] = ...,
        kind: Literal[
            "line",
            "bar",
            "barh",
            "hist",
            "kde",
            "density",
            "area",
            "pie",
            "scatter",
            "hexbin",
        ] = ...,
        ax: Axes | None = ...,
        subplots: Literal[True] | Sequence[Iterable[HashableT1]],
        sharex: bool = ...,
        sharey: bool = ...,
        layout: tuple[int, int] = ...,
        figsize: tuple[float, float] = ...,
        use_index: bool = ...,
        title: Sequence[str] | None = ...,
        grid: bool | None = ...,
        legend: bool | Literal["reverse"] = ...,
        style: str | list[str] | dict[HashableT2, str] = ...,
        logx: bool | Literal["sym"] = ...,
        logy: bool | Literal["sym"] = ...,
        loglog: bool | Literal["sym"] = ...,
        xticks: Sequence[float] = ...,
        yticks: Sequence[float] = ...,
        xlim: tuple[float, float] | list[float] = ...,
        ylim: tuple[float, float] | list[float] = ...,
        xlabel: str = ...,
        ylabel: str = ...,
        rot: float = ...,
        fontsize: float = ...,
        colormap: str | Colormap | None = ...,
        colorbar: bool = ...,
        position: float = ...,
        table: bool | Series | DataFrame = ...,
        yerr: DataFrame | Series | ArrayLike | dict | str = ...,
        xerr: DataFrame | Series | ArrayLike | dict | str = ...,
        stacked: bool = ...,
        secondary_y: bool | list[HashableT3] | tuple[HashableT3, ...] = ...,
        mark_right: bool = ...,
        include_bool: bool = ...,
        backend: str = ...,
        **kwargs: Any,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def __call__(
        self,
        *,
        data: Series | DataFrame | None = ...,
        x: Hashable = ...,
        y: Hashable | Sequence[Hashable] = ...,
        kind: Literal["box"],
        ax: Axes | None = ...,
        subplots: Literal[True] | Sequence[Iterable[HashableT1]],
        sharex: bool = ...,
        sharey: bool = ...,
        layout: tuple[int, int] = ...,
        figsize: tuple[float, float] = ...,
        use_index: bool = ...,
        title: Sequence[str] | None = ...,
        grid: bool | None = ...,
        legend: bool | Literal["reverse"] = ...,
        style: str | list[str] | dict[HashableT2, str] = ...,
        logx: bool | Literal["sym"] = ...,
        logy: bool | Literal["sym"] = ...,
        loglog: bool | Literal["sym"] = ...,
        xticks: Sequence[float] = ...,
        yticks: Sequence[float] = ...,
        xlim: tuple[float, float] | list[float] = ...,
        ylim: tuple[float, float] | list[float] = ...,
        xlabel: str = ...,
        ylabel: str = ...,
        rot: float = ...,
        fontsize: float = ...,
        colormap: str | Colormap | None = ...,
        colorbar: bool = ...,
        position: float = ...,
        table: bool | Series | DataFrame = ...,
        yerr: DataFrame | Series | ArrayLike | dict | str = ...,
        xerr: DataFrame | Series | ArrayLike | dict | str = ...,
        stacked: bool = ...,
        secondary_y: bool | list[HashableT3] | tuple[HashableT3, ...] = ...,
        mark_right: bool = ...,
        include_bool: bool = ...,
        backend: str = ...,
        **kwargs: Any,
    ) -> pd.Series: ...
    @overload
    def line(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes:
        """
Plot Series or DataFrame as lines.

This function is useful to plot lines using DataFrame's values
as coordinates.

Parameters
----------
x : label or position, optional
    Allows plotting of one column versus another. If not specified,
    the index of the DataFrame is used.
y : label or position, optional
    Allows plotting of one column versus another. If not specified,
    all numerical columns are used.
color : str, array-like, or dict, optional
    The color for each of the DataFrame's columns. Possible values are:

    - A single color string referred to by name, RGB or RGBA code,
        for instance 'red' or '#a98d19'.

    - A sequence of color strings referred to by name, RGB or RGBA
        code, which will be used for each column recursively. For
        instance ['green','yellow'] each column's line will be filled in
        green or yellow, alternatively. If there is only a single column to
        be plotted, then only the first color from the color list will be
        used.

    - A dict of the form {column name : color}, so that each column will be
        colored accordingly. For example, if your columns are called `a` and
        `b`, then passing {'a': 'green', 'b': 'red'} will color lines for
        column `a` in green and lines for column `b` in red.

**kwargs
    Additional keyword arguments are documented in
    :meth:`DataFrame.plot`.

Returns
-------
matplotlib.axes.Axes or np.ndarray of them
    An ndarray is returned with one :class:`matplotlib.axes.Axes`
    per column when ``subplots=True``.

        See Also
        --------
        matplotlib.pyplot.plot : Plot y versus x as lines and/or markers.

        Examples
        --------

        .. plot::
            :context: close-figs

            >>> s = pd.Series([1, 3, 2])
            >>> s.plot.line()  # doctest: +SKIP

        .. plot::
            :context: close-figs

            The following example shows the populations for some animals
            over the years.

            >>> df = pd.DataFrame({
            ...    'pig': [20, 18, 489, 675, 1776],
            ...    'horse': [4, 25, 281, 600, 1900]
            ...    }, index=[1990, 1997, 2003, 2009, 2014])
            >>> lines = df.plot.line()

        .. plot::
           :context: close-figs

           An example with subplots, so an array of axes is returned.

           >>> axes = df.plot.line(subplots=True)
           >>> type(axes)
           <class 'numpy.ndarray'>

        .. plot::
           :context: close-figs

           Let's repeat the same example, but specifying colors for
           each column (in this case, for each animal).

           >>> axes = df.plot.line(
           ...     subplots=True, color={"pig": "pink", "horse": "#742802"}
           ... )

        .. plot::
            :context: close-figs

            The following example shows the relationship between both
            populations.

            >>> lines = df.plot.line(x='pig', y='horse')
        """
        pass
    @overload
    def line(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def bar(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes:
        """
Vertical bar plot.

A bar plot is a plot that presents categorical data with
rectangular bars with lengths proportional to the values that they
represent. A bar plot shows comparisons among discrete categories. One
axis of the plot shows the specific categories being compared, and the
other axis represents a measured value.

Parameters
----------
x : label or position, optional
    Allows plotting of one column versus another. If not specified,
    the index of the DataFrame is used.
y : label or position, optional
    Allows plotting of one column versus another. If not specified,
    all numerical columns are used.
color : str, array-like, or dict, optional
    The color for each of the DataFrame's columns. Possible values are:

    - A single color string referred to by name, RGB or RGBA code,
        for instance 'red' or '#a98d19'.

    - A sequence of color strings referred to by name, RGB or RGBA
        code, which will be used for each column recursively. For
        instance ['green','yellow'] each column's bar will be filled in
        green or yellow, alternatively. If there is only a single column to
        be plotted, then only the first color from the color list will be
        used.

    - A dict of the form {column name : color}, so that each column will be
        colored accordingly. For example, if your columns are called `a` and
        `b`, then passing {'a': 'green', 'b': 'red'} will color bars for
        column `a` in green and bars for column `b` in red.

**kwargs
    Additional keyword arguments are documented in
    :meth:`DataFrame.plot`.

Returns
-------
matplotlib.axes.Axes or np.ndarray of them
    An ndarray is returned with one :class:`matplotlib.axes.Axes`
    per column when ``subplots=True``.

        See Also
        --------
        DataFrame.plot.barh : Horizontal bar plot.
        DataFrame.plot : Make plots of a DataFrame.
        matplotlib.pyplot.bar : Make a bar plot with matplotlib.

        Examples
        --------
        Basic plot.

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame({'lab':['A', 'B', 'C'], 'val':[10, 30, 20]})
            >>> ax = df.plot.bar(x='lab', y='val', rot=0)

        Plot a whole dataframe to a bar plot. Each column is assigned a
        distinct color, and each row is nested in a group along the
        horizontal axis.

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot.bar(rot=0)

        Plot stacked bar charts for the DataFrame

        .. plot::
            :context: close-figs

            >>> ax = df.plot.bar(stacked=True)

        Instead of nesting, the figure can be split by column with
        ``subplots=True``. In this case, a :class:`numpy.ndarray` of
        :class:`matplotlib.axes.Axes` are returned.

        .. plot::
            :context: close-figs

            >>> axes = df.plot.bar(rot=0, subplots=True)
            >>> axes[1].legend(loc=2)  # doctest: +SKIP

        If you don't like the default colours, you can specify how you'd
        like each column to be colored.

        .. plot::
            :context: close-figs

            >>> axes = df.plot.bar(
            ...     rot=0, subplots=True, color={"speed": "red", "lifespan": "green"}
            ... )
            >>> axes[1].legend(loc=2)  # doctest: +SKIP

        Plot a single column.

        .. plot::
            :context: close-figs

            >>> ax = df.plot.bar(y='speed', rot=0)

        Plot only selected categories for the DataFrame.

        .. plot::
            :context: close-figs

            >>> ax = df.plot.bar(x='lifespan', rot=0)
        """
        pass
    @overload
    def bar(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def barh(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes:
        """
Make a horizontal bar plot.

A horizontal bar plot is a plot that presents quantitative data with
rectangular bars with lengths proportional to the values that they
represent. A bar plot shows comparisons among discrete categories. One
axis of the plot shows the specific categories being compared, and the
other axis represents a measured value.

Parameters
----------
x : label or position, optional
    Allows plotting of one column versus another. If not specified,
    the index of the DataFrame is used.
y : label or position, optional
    Allows plotting of one column versus another. If not specified,
    all numerical columns are used.
color : str, array-like, or dict, optional
    The color for each of the DataFrame's columns. Possible values are:

    - A single color string referred to by name, RGB or RGBA code,
        for instance 'red' or '#a98d19'.

    - A sequence of color strings referred to by name, RGB or RGBA
        code, which will be used for each column recursively. For
        instance ['green','yellow'] each column's bar will be filled in
        green or yellow, alternatively. If there is only a single column to
        be plotted, then only the first color from the color list will be
        used.

    - A dict of the form {column name : color}, so that each column will be
        colored accordingly. For example, if your columns are called `a` and
        `b`, then passing {'a': 'green', 'b': 'red'} will color bars for
        column `a` in green and bars for column `b` in red.

**kwargs
    Additional keyword arguments are documented in
    :meth:`DataFrame.plot`.

Returns
-------
matplotlib.axes.Axes or np.ndarray of them
    An ndarray is returned with one :class:`matplotlib.axes.Axes`
    per column when ``subplots=True``.

        See Also
        --------
        DataFrame.plot.bar: Vertical bar plot.
        DataFrame.plot : Make plots of DataFrame using matplotlib.
        matplotlib.axes.Axes.bar : Plot a vertical bar plot using matplotlib.

        Examples
        --------
        Basic example

        .. plot::
            :context: close-figs

            >>> df = pd.DataFrame({'lab': ['A', 'B', 'C'], 'val': [10, 30, 20]})
            >>> ax = df.plot.barh(x='lab', y='val')

        Plot a whole DataFrame to a horizontal bar plot

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot.barh()

        Plot stacked barh charts for the DataFrame

        .. plot::
            :context: close-figs

            >>> ax = df.plot.barh(stacked=True)

        We can specify colors for each column

        .. plot::
            :context: close-figs

            >>> ax = df.plot.barh(color={"speed": "red", "lifespan": "green"})

        Plot a column of the DataFrame to a horizontal bar plot

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot.barh(y='speed')

        Plot DataFrame versus the desired column

        .. plot::
            :context: close-figs

            >>> speed = [0.1, 17.5, 40, 48, 52, 69, 88]
            >>> lifespan = [2, 8, 70, 1.5, 25, 12, 28]
            >>> index = ['snail', 'pig', 'elephant',
            ...          'rabbit', 'giraffe', 'coyote', 'horse']
            >>> df = pd.DataFrame({'speed': speed,
            ...                    'lifespan': lifespan}, index=index)
            >>> ax = df.plot.barh(x='lifespan')
        """
        pass
    @overload
    def barh(
        self,
        x: Hashable = ...,
        y: Hashable = ...,
        color: _PlotAccessorColor = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def box(
        self,
        by: Hashable | list[HashableT] = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def box(
        self,
        by: Hashable | list[HashableT] = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> Series: ...
    @overload
    def hist(
        self,
        by: Hashable | list[HashableT] | None = ...,
        bins: int = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def hist(
        self,
        by: Hashable | list[HashableT] | None = ...,
        bins: int = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def kde(
        self,
        bw_method: (
            Literal["scott", "silverman"]
            | float
            | Callable[[gaussian_kde], float]
            | None
        ) = ...,
        ind: npt.NDArray[np.double] | int | None = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def kde(
        self,
        bw_method: (
            Literal["scott", "silverman"]
            | float
            | Callable[[gaussian_kde], float]
            | None
        ) = ...,
        ind: npt.NDArray[np.double] | int | None = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def area(
        self,
        x: Hashable | None = ...,
        y: Hashable | None = ...,
        stacked: bool = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def area(
        self,
        x: Hashable | None = ...,
        y: Hashable | None = ...,
        stacked: bool = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def pie(
        self, y: Hashable, *, subplots: Literal[False] | None = ..., **kwargs
    ) -> Axes: ...
    @overload
    def pie(
        self, y: Hashable, *, subplots: Literal[True], **kwargs
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def scatter(
        self,
        x: Hashable,
        y: Hashable,
        s: Hashable | Sequence[float] | None = ...,
        c: Hashable | list[str] = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def scatter(
        self,
        x: Hashable,
        y: Hashable,
        s: Hashable | Sequence[float] | None = ...,
        c: Hashable | list[str] = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...
    @overload
    def hexbin(
        self,
        x: Hashable,
        y: Hashable,
        C: Hashable | None = ...,
        reduce_C_function: Callable[[list], float] | None = ...,
        gridsize: int | tuple[int, int] | None = ...,
        *,
        subplots: Literal[False] | None = ...,
        **kwargs,
    ) -> Axes: ...
    @overload
    def hexbin(
        self,
        x: Hashable,
        y: Hashable,
        C: Hashable | None = ...,
        reduce_C_function: Callable[[list], float] | None = ...,
        gridsize: int | tuple[int, int] | None = ...,
        *,
        subplots: Literal[True],
        **kwargs,
    ) -> npt.NDArray[np.object_]: ...

    density = kde
