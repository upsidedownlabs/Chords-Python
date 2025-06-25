from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Sequence,
)
from typing import (
    Any,
    Generic,
    Literal,
    NamedTuple,
    final,
    overload,
)

from matplotlib.axes import Axes as PlotAxes
import numpy as np
from pandas.core.frame import DataFrame
from pandas.core.groupby.groupby import (
    GroupBy,
    GroupByPlot,
)
from pandas.core.series import Series
from typing_extensions import (
    Self,
    TypeAlias,
)

from pandas._libs.lib import NoDefault
from pandas._typing import (
    S1,
    AggFuncTypeBase,
    AggFuncTypeFrame,
    ArrayLike,
    Axis,
    ByT,
    CorrelationMethod,
    Dtype,
    IndexLabel,
    Level,
    ListLike,
    Scalar,
    TakeIndexer,
    WindowingEngine,
    WindowingEngineKwargs,
)

AggScalar: TypeAlias = str | Callable[..., Any]

class NamedAgg(NamedTuple):
    column: str
    aggfunc: AggScalar

class SeriesGroupBy(GroupBy[Series[S1]], Generic[S1, ByT]):
    @overload
    def aggregate(
        self,
        func: list[AggFuncTypeBase],
        *args,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
        **kwargs,
    ) -> DataFrame:
        """
Aggregate using one or more operations over the specified axis.

Parameters
----------
func : function, str, list, dict or None
    Function to use for aggregating the data. If a function, must either
    work when passed a Series or when passed to Series.apply.

    Accepted combinations are:

    - function
    - string function name
    - list of functions and/or function names, e.g. ``[np.sum, 'mean']``
    - None, in which case ``**kwargs`` are used with Named Aggregation. Here the
      output has one column for each element in ``**kwargs``. The name of the
      column is keyword, whereas the value determines the aggregation used to compute
      the values in the column.

      Can also accept a Numba JIT function with
      ``engine='numba'`` specified. Only passing a single function is supported
      with this engine.

      If the ``'numba'`` engine is chosen, the function must be
      a user defined function with ``values`` and ``index`` as the
      first and second arguments respectively in the function signature.
      Each group's index will be passed to the user defined function
      and optionally available for use.

    .. deprecated:: 2.1.0

        Passing a dictionary is deprecated and will raise in a future version
        of pandas. Pass a list of aggregations instead.
*args
    Positional arguments to pass to func.
engine : str, default None
    * ``'cython'`` : Runs the function through C-extensions from cython.
    * ``'numba'`` : Runs the function through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or globally setting ``compute.use_numba``

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}`` and will be
      applied to the function

**kwargs
    * If ``func`` is None, ``**kwargs`` are used to define the output names and
      aggregations via Named Aggregation. See ``func`` entry.
    * Otherwise, keyword arguments to be passed into func.

Returns
-------
Series

See Also
--------
Series.groupby.apply : Apply function func group-wise
    and combine the results together.
Series.groupby.transform : Transforms the Series on each group
    based on the given function.
Series.aggregate : Aggregate using one or more
    operations over the specified axis.

Notes
-----
When using ``engine='numba'``, there will be no "fall back" behavior internally.
The group data and group index will be passed as numpy arrays to the JITed
user defined function, and no alternative execution attempts will be tried.

Functions that mutate the passed object can produce unexpected
behavior or errors and are not supported. See :ref:`gotchas.udf-mutation`
for more details.

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the passed ``func``,
    see the examples below.

Examples
--------
>>> s = pd.Series([1, 2, 3, 4])

>>> s
0    1
1    2
2    3
3    4
dtype: int64

>>> s.groupby([1, 1, 2, 2]).min()
1    1
2    3
dtype: int64

>>> s.groupby([1, 1, 2, 2]).agg('min')
1    1
2    3
dtype: int64

>>> s.groupby([1, 1, 2, 2]).agg(['min', 'max'])
   min  max
1    1    2
2    3    4

The output column names can be controlled by passing
the desired column names and aggregations as keyword arguments.

>>> s.groupby([1, 1, 2, 2]).agg(
...     minimum='min',
...     maximum='max',
... )
   minimum  maximum
1        1        2
2        3        4

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the aggregating function.

>>> s.groupby([1, 1, 2, 2]).agg(lambda x: x.astype(float).min())
1    1.0
2    3.0
dtype: float64
        """
        pass
    @overload
    def aggregate(
        self,
        func: AggFuncTypeBase | None = ...,
        *args,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
        **kwargs,
    ) -> Series: ...
    agg = aggregate
    def transform(
        self,
        func: Callable | str,
        *args,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
        **kwargs,
    ) -> Series:
        """
Call function producing a same-indexed Series on each group.

Returns a Series having the same indexes as the original object
filled with the transformed values.

Parameters
----------
f : function, str
    Function to apply to each group. See the Notes section below for requirements.

    Accepted inputs are:

    - String
    - Python function
    - Numba JIT function with ``engine='numba'`` specified.

    Only passing a single function is supported with this engine.
    If the ``'numba'`` engine is chosen, the function must be
    a user defined function with ``values`` and ``index`` as the
    first and second arguments respectively in the function signature.
    Each group's index will be passed to the user defined function
    and optionally available for use.

    If a string is chosen, then it needs to be the name
    of the groupby method you want to use.
*args
    Positional arguments to pass to func.
engine : str, default None
    * ``'cython'`` : Runs the function through C-extensions from cython.
    * ``'numba'`` : Runs the function through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or the global setting ``compute.use_numba``

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}`` and will be
      applied to the function

**kwargs
    Keyword arguments to be passed into func.

Returns
-------
Series

See Also
--------
Series.groupby.apply : Apply function ``func`` group-wise and combine
    the results together.
Series.groupby.aggregate : Aggregate using one or more
    operations over the specified axis.
Series.transform : Call ``func`` on self producing a Series with the
    same axis shape as self.

Notes
-----
Each group is endowed the attribute 'name' in case you need to know
which group you are working on.

The current implementation imposes three requirements on f:

* f must return a value that either has the same shape as the input
  subframe or can be broadcast to the shape of the input subframe.
  For example, if `f` returns a scalar it will be broadcast to have the
  same shape as the input subframe.
* if this is a DataFrame, f must support application column-by-column
  in the subframe. If f also supports application to the entire subframe,
  then a fast path is used starting from the second chunk.
* f must not mutate groups. Mutation is not supported and may
  produce unexpected results. See :ref:`gotchas.udf-mutation` for more details.

When using ``engine='numba'``, there will be no "fall back" behavior internally.
The group data and group index will be passed as numpy arrays to the JITed
user defined function, and no alternative execution attempts will be tried.

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the passed ``func``,
    see the examples below.

.. versionchanged:: 2.0.0

    When using ``.transform`` on a grouped DataFrame and the transformation function
    returns a DataFrame, pandas now aligns the result's index
    with the input's index. You can call ``.to_numpy()`` on the
    result of the transformation function to avoid alignment.

Examples
--------

>>> ser = pd.Series([390.0, 350.0, 30.0, 20.0],
...                 index=["Falcon", "Falcon", "Parrot", "Parrot"],
...                 name="Max Speed")
>>> grouped = ser.groupby([1, 1, 2, 2])
>>> grouped.transform(lambda x: (x - x.mean()) / x.std())
    Falcon    0.707107
    Falcon   -0.707107
    Parrot    0.707107
    Parrot   -0.707107
    Name: Max Speed, dtype: float64

Broadcast result of the transformation

>>> grouped.transform(lambda x: x.max() - x.min())
Falcon    40.0
Falcon    40.0
Parrot    10.0
Parrot    10.0
Name: Max Speed, dtype: float64

>>> grouped.transform("mean")
Falcon    370.0
Falcon    370.0
Parrot     25.0
Parrot     25.0
Name: Max Speed, dtype: float64

.. versionchanged:: 1.3.0

The resulting dtype will reflect the return value of the passed ``func``,
for example:

>>> grouped.transform(lambda x: x.astype(int).max())
Falcon    390
Falcon    390
Parrot     30
Parrot     30
Name: Max Speed, dtype: int64
        """
        pass
    def filter(
        self, func: Callable | str, dropna: bool = ..., *args, **kwargs
    ) -> Series: ...
    def nunique(self, dropna: bool = ...) -> Series[int]: ...
    # describe delegates to super() method but here it has keyword-only parameters
    def describe(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        *,
        percentiles: Iterable[float] | None = ...,
        include: Literal["all"] | list[Dtype] | None = ...,
        exclude: list[Dtype] | None = ...,
    ) -> DataFrame:
        """
Generate descriptive statistics.

Descriptive statistics include those that summarize the central
tendency, dispersion and shape of a
dataset's distribution, excluding ``NaN`` values.

Analyzes both numeric and object series, as well
as ``DataFrame`` column sets of mixed data types. The output
will vary depending on what is provided. Refer to the notes
below for more detail.

Parameters
----------
percentiles : list-like of numbers, optional
    The percentiles to include in the output. All should
    fall between 0 and 1. The default is
    ``[.25, .5, .75]``, which returns the 25th, 50th, and
    75th percentiles.
include : 'all', list-like of dtypes or None (default), optional
    A white list of data types to include in the result. Ignored
    for ``Series``. Here are the options:

    - 'all' : All columns of the input will be included in the output.
    - A list-like of dtypes : Limits the results to the
      provided data types.
      To limit the result to numeric types submit
      ``numpy.number``. To limit it instead to object columns submit
      the ``numpy.object`` data type. Strings
      can also be used in the style of
      ``select_dtypes`` (e.g. ``df.describe(include=['O'])``). To
      select pandas categorical columns, use ``'category'``
    - None (default) : The result will include all numeric columns.
exclude : list-like of dtypes or None (default), optional,
    A black list of data types to omit from the result. Ignored
    for ``Series``. Here are the options:

    - A list-like of dtypes : Excludes the provided data types
      from the result. To exclude numeric types submit
      ``numpy.number``. To exclude object columns submit the data
      type ``numpy.object``. Strings can also be used in the style of
      ``select_dtypes`` (e.g. ``df.describe(exclude=['O'])``). To
      exclude pandas categorical columns, use ``'category'``
    - None (default) : The result will exclude nothing.

Returns
-------
Series or DataFrame
    Summary statistics of the Series or Dataframe provided.

See Also
--------
DataFrame.count: Count number of non-NA/null observations.
DataFrame.max: Maximum of the values in the object.
DataFrame.min: Minimum of the values in the object.
DataFrame.mean: Mean of the values.
DataFrame.std: Standard deviation of the observations.
DataFrame.select_dtypes: Subset of a DataFrame including/excluding
    columns based on their dtype.

Notes
-----
For numeric data, the result's index will include ``count``,
``mean``, ``std``, ``min``, ``max`` as well as lower, ``50`` and
upper percentiles. By default the lower percentile is ``25`` and the
upper percentile is ``75``. The ``50`` percentile is the
same as the median.

For object data (e.g. strings or timestamps), the result's index
will include ``count``, ``unique``, ``top``, and ``freq``. The ``top``
is the most common value. The ``freq`` is the most common value's
frequency. Timestamps also include the ``first`` and ``last`` items.

If multiple object values have the highest count, then the
``count`` and ``top`` results will be arbitrarily chosen from
among those with the highest count.

For mixed data types provided via a ``DataFrame``, the default is to
return only an analysis of numeric columns. If the dataframe consists
only of object and categorical data without any numeric columns, the
default is to return an analysis of both the object and categorical
columns. If ``include='all'`` is provided as an option, the result
will include a union of attributes of each type.

The `include` and `exclude` parameters can be used to limit
which columns in a ``DataFrame`` are analyzed for the output.
The parameters are ignored when analyzing a ``Series``.

Examples
--------
Describing a numeric ``Series``.

>>> s = pd.Series([1, 2, 3])
>>> s.describe()
count    3.0
mean     2.0
std      1.0
min      1.0
25%      1.5
50%      2.0
75%      2.5
max      3.0
dtype: float64

Describing a categorical ``Series``.

>>> s = pd.Series(['a', 'a', 'b', 'c'])
>>> s.describe()
count     4
unique    3
top       a
freq      2
dtype: object

Describing a timestamp ``Series``.

>>> s = pd.Series([
...     np.datetime64("2000-01-01"),
...     np.datetime64("2010-01-01"),
...     np.datetime64("2010-01-01")
... ])
>>> s.describe()
count                      3
mean     2006-09-01 08:00:00
min      2000-01-01 00:00:00
25%      2004-12-31 12:00:00
50%      2010-01-01 00:00:00
75%      2010-01-01 00:00:00
max      2010-01-01 00:00:00
dtype: object

Describing a ``DataFrame``. By default only numeric fields
are returned.

>>> df = pd.DataFrame({'categorical': pd.Categorical(['d', 'e', 'f']),
...                    'numeric': [1, 2, 3],
...                    'object': ['a', 'b', 'c']
...                    })
>>> df.describe()
       numeric
count      3.0
mean       2.0
std        1.0
min        1.0
25%        1.5
50%        2.0
75%        2.5
max        3.0

Describing all columns of a ``DataFrame`` regardless of data type.

>>> df.describe(include='all')  # doctest: +SKIP
       categorical  numeric object
count            3      3.0      3
unique           3      NaN      3
top              f      NaN      a
freq             1      NaN      1
mean           NaN      2.0    NaN
std            NaN      1.0    NaN
min            NaN      1.0    NaN
25%            NaN      1.5    NaN
50%            NaN      2.0    NaN
75%            NaN      2.5    NaN
max            NaN      3.0    NaN

Describing a column from a ``DataFrame`` by accessing it as
an attribute.

>>> df.numeric.describe()
count    3.0
mean     2.0
std      1.0
min      1.0
25%      1.5
50%      2.0
75%      2.5
max      3.0
Name: numeric, dtype: float64

Including only numeric columns in a ``DataFrame`` description.

>>> df.describe(include=[np.number])
       numeric
count      3.0
mean       2.0
std        1.0
min        1.0
25%        1.5
50%        2.0
75%        2.5
max        3.0

Including only string columns in a ``DataFrame`` description.

>>> df.describe(include=[object])  # doctest: +SKIP
       object
count       3
unique      3
top         a
freq        1

Including only categorical columns from a ``DataFrame`` description.

>>> df.describe(include=['category'])
       categorical
count            3
unique           3
top              d
freq             1

Excluding numeric columns from a ``DataFrame`` description.

>>> df.describe(exclude=[np.number])  # doctest: +SKIP
       categorical object
count            3      3
unique           3      3
top              f      a
freq             1      1

Excluding object columns from a ``DataFrame`` description.

>>> df.describe(exclude=[object])  # doctest: +SKIP
       categorical  numeric
count            3      3.0
unique           3      NaN
top              f      NaN
freq             1      NaN
mean           NaN      2.0
std            NaN      1.0
min            NaN      1.0
25%            NaN      1.5
50%            NaN      2.0
75%            NaN      2.5
max            NaN      3.0
        """
        pass
    @overload
    def value_counts(
        self,
        normalize: Literal[False] = ...,
        sort: bool = ...,
        ascending: bool = ...,
        bins=...,
        dropna: bool = ...,
    ) -> Series[int]: ...
    @overload
    def value_counts(
        self,
        normalize: Literal[True],
        sort: bool = ...,
        ascending: bool = ...,
        bins=...,
        dropna: bool = ...,
    ) -> Series[float]: ...
    def fillna(
        self,
        value: (
            Scalar | ArrayLike | Series | DataFrame | Mapping[Hashable, Scalar] | None
        ) = ...,
        method: Literal["bfill", "ffill"] | None = ...,
        axis: Axis | None | NoDefault = ...,
        inplace: bool = ...,
        limit: int | None = ...,
        downcast: dict | None | NoDefault = ...,
    ) -> Series[S1] | None: ...
    def take(
        self,
        indices: TakeIndexer,
        axis: Axis | NoDefault = ...,
        **kwargs,
    ) -> Series[S1]: ...
    def skew(
        self,
        axis: Axis | NoDefault = ...,
        skipna: bool = ...,
        numeric_only: bool = ...,
        **kwargs,
    ) -> Series: ...
    @property
    def plot(self) -> GroupByPlot[Self]:
        """
Make plots of Series or DataFrame.

Uses the backend specified by the
option ``plotting.backend``. By default, matplotlib is used.

Parameters
----------
data : Series or DataFrame
    The object for which the method is called.
x : label or position, default None
    Only used if data is a DataFrame.
y : label, position or list of label, positions, default None
    Allows plotting of one column versus another. Only used if data is a
    DataFrame.
kind : str
    The kind of plot to produce:

    - 'line' : line plot (default)
    - 'bar' : vertical bar plot
    - 'barh' : horizontal bar plot
    - 'hist' : histogram
    - 'box' : boxplot
    - 'kde' : Kernel Density Estimation plot
    - 'density' : same as 'kde'
    - 'area' : area plot
    - 'pie' : pie plot
    - 'scatter' : scatter plot (DataFrame only)
    - 'hexbin' : hexbin plot (DataFrame only)
ax : matplotlib axes object, default None
    An axes of the current figure.
subplots : bool or sequence of iterables, default False
    Whether to group columns into subplots:

    - ``False`` : No subplots will be used
    - ``True`` : Make separate subplots for each column.
    - sequence of iterables of column labels: Create a subplot for each
      group of columns. For example `[('a', 'c'), ('b', 'd')]` will
      create 2 subplots: one with columns 'a' and 'c', and one
      with columns 'b' and 'd'. Remaining columns that aren't specified
      will be plotted in additional subplots (one per column).

      .. versionadded:: 1.5.0

sharex : bool, default True if ax is None else False
    In case ``subplots=True``, share x axis and set some x axis labels
    to invisible; defaults to True if ax is None otherwise False if
    an ax is passed in; Be aware, that passing in both an ax and
    ``sharex=True`` will alter all x axis labels for all axis in a figure.
sharey : bool, default False
    In case ``subplots=True``, share y axis and set some y axis labels to invisible.
layout : tuple, optional
    (rows, columns) for the layout of subplots.
figsize : a tuple (width, height) in inches
    Size of a figure object.
use_index : bool, default True
    Use index as ticks for x axis.
title : str or list
    Title to use for the plot. If a string is passed, print the string
    at the top of the figure. If a list is passed and `subplots` is
    True, print each item in the list above the corresponding subplot.
grid : bool, default None (matlab style default)
    Axis grid lines.
legend : bool or {'reverse'}
    Place legend on axis subplots.
style : list or dict
    The matplotlib line style per column.
logx : bool or 'sym', default False
    Use log scaling or symlog scaling on x axis.

logy : bool or 'sym' default False
    Use log scaling or symlog scaling on y axis.

loglog : bool or 'sym', default False
    Use log scaling or symlog scaling on both x and y axes.

xticks : sequence
    Values to use for the xticks.
yticks : sequence
    Values to use for the yticks.
xlim : 2-tuple/list
    Set the x limits of the current axes.
ylim : 2-tuple/list
    Set the y limits of the current axes.
xlabel : label, optional
    Name to use for the xlabel on x-axis. Default uses index name as xlabel, or the
    x-column name for planar plots.

    .. versionchanged:: 2.0.0

        Now applicable to histograms.

ylabel : label, optional
    Name to use for the ylabel on y-axis. Default will show no ylabel, or the
    y-column name for planar plots.

    .. versionchanged:: 2.0.0

        Now applicable to histograms.

rot : float, default None
    Rotation for ticks (xticks for vertical, yticks for horizontal
    plots).
fontsize : float, default None
    Font size for xticks and yticks.
colormap : str or matplotlib colormap object, default None
    Colormap to select colors from. If string, load colormap with that
    name from matplotlib.
colorbar : bool, optional
    If True, plot colorbar (only relevant for 'scatter' and 'hexbin'
    plots).
position : float
    Specify relative alignments for bar plot layout.
    From 0 (left/bottom-end) to 1 (right/top-end). Default is 0.5
    (center).
table : bool, Series or DataFrame, default False
    If True, draw a table using the data in the DataFrame and the data
    will be transposed to meet matplotlib's default layout.
    If a Series or DataFrame is passed, use passed data to draw a
    table.
yerr : DataFrame, Series, array-like, dict and str
    See :ref:`Plotting with Error Bars <visualization.errorbars>` for
    detail.
xerr : DataFrame, Series, array-like, dict and str
    Equivalent to yerr.
stacked : bool, default False in line and bar plots, and True in area plot
    If True, create stacked plot.
secondary_y : bool or sequence, default False
    Whether to plot on the secondary y-axis if a list/tuple, which
    columns to plot on secondary y-axis.
mark_right : bool, default True
    When using a secondary_y axis, automatically mark the column
    labels with "(right)" in the legend.
include_bool : bool, default is False
    If True, boolean values can be plotted.
backend : str, default None
    Backend to use instead of the backend specified in the option
    ``plotting.backend``. For instance, 'matplotlib'. Alternatively, to
    specify the ``plotting.backend`` for the whole session, set
    ``pd.options.plotting.backend``.
**kwargs
    Options to pass to matplotlib plotting method.

Returns
-------
:class:`matplotlib.axes.Axes` or numpy.ndarray of them
    If the backend is not the default matplotlib one, the return value
    will be the object returned by the backend.

Notes
-----
- See matplotlib documentation online for more on this subject
- If `kind` = 'bar' or 'barh', you can specify relative alignments
  for bar plot layout by `position` keyword.
  From 0 (left/bottom-end) to 1 (right/top-end). Default is 0.5
  (center)

Examples
--------
For Series:

.. plot::
    :context: close-figs

    >>> ser = pd.Series([1, 2, 3, 3])
    >>> plot = ser.plot(kind='hist', title="My plot")

For DataFrame:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame({'length': [1.5, 0.5, 1.2, 0.9, 3],
    ...                   'width': [0.7, 0.2, 0.15, 0.2, 1.1]},
    ...                   index=['pig', 'rabbit', 'duck', 'chicken', 'horse'])
    >>> plot = df.plot(title="DataFrame Plot")

For SeriesGroupBy:

.. plot::
    :context: close-figs

    >>> lst = [-1, -2, -3, 1, 2, 3]
    >>> ser = pd.Series([1, 2, 2, 4, 6, 6], index=lst)
    >>> plot = ser.groupby(lambda x: x > 0).plot(title="SeriesGroupBy Plot")

For DataFrameGroupBy:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame({"col1" : [1, 2, 3, 4],
    ...                   "col2" : ["A", "B", "A", "B"]})
    >>> plot = df.groupby("col2").plot(kind="bar", title="DataFrameGroupBy Plot")
        """
        pass
    def nlargest(
        self, n: int = ..., keep: Literal["first", "last", "all"] = ...
    ) -> Series[S1]:
        """
Return the largest `n` elements.

Parameters
----------
n : int, default 5
    Return this many descending sorted values.
keep : {'first', 'last', 'all'}, default 'first'
    When there are duplicate values that cannot all fit in a
    Series of `n` elements:

    - ``first`` : return the first `n` occurrences in order
      of appearance.
    - ``last`` : return the last `n` occurrences in reverse
      order of appearance.
    - ``all`` : keep all occurrences. This can result in a Series of
      size larger than `n`.

Returns
-------
Series
    The `n` largest values in the Series, sorted in decreasing order.

See Also
--------
Series.nsmallest: Get the `n` smallest elements.
Series.sort_values: Sort Series by values.
Series.head: Return the first `n` rows.

Notes
-----
Faster than ``.sort_values(ascending=False).head(n)`` for small `n`
relative to the size of the ``Series`` object.

Examples
--------
>>> countries_population = {"Italy": 59000000, "France": 65000000,
...                         "Malta": 434000, "Maldives": 434000,
...                         "Brunei": 434000, "Iceland": 337000,
...                         "Nauru": 11300, "Tuvalu": 11300,
...                         "Anguilla": 11300, "Montserrat": 5200}
>>> s = pd.Series(countries_population)
>>> s
Italy       59000000
France      65000000
Malta         434000
Maldives      434000
Brunei        434000
Iceland       337000
Nauru          11300
Tuvalu         11300
Anguilla       11300
Montserrat      5200
dtype: int64

The `n` largest elements where ``n=5`` by default.

>>> s.nlargest()
France      65000000
Italy       59000000
Malta         434000
Maldives      434000
Brunei        434000
dtype: int64

The `n` largest elements where ``n=3``. Default `keep` value is 'first'
so Malta will be kept.

>>> s.nlargest(3)
France    65000000
Italy     59000000
Malta       434000
dtype: int64

The `n` largest elements where ``n=3`` and keeping the last duplicates.
Brunei will be kept since it is the last with value 434000 based on
the index order.

>>> s.nlargest(3, keep='last')
France      65000000
Italy       59000000
Brunei        434000
dtype: int64

The `n` largest elements where ``n=3`` with all duplicates kept. Note
that the returned Series has five elements due to the three duplicates.

>>> s.nlargest(3, keep='all')
France      65000000
Italy       59000000
Malta         434000
Maldives      434000
Brunei        434000
dtype: int64
        """
        pass
    def nsmallest(
        self, n: int = ..., keep: Literal["first", "last", "all"] = ...
    ) -> Series[S1]:
        """
Return the smallest `n` elements.

Parameters
----------
n : int, default 5
    Return this many ascending sorted values.
keep : {'first', 'last', 'all'}, default 'first'
    When there are duplicate values that cannot all fit in a
    Series of `n` elements:

    - ``first`` : return the first `n` occurrences in order
      of appearance.
    - ``last`` : return the last `n` occurrences in reverse
      order of appearance.
    - ``all`` : keep all occurrences. This can result in a Series of
      size larger than `n`.

Returns
-------
Series
    The `n` smallest values in the Series, sorted in increasing order.

See Also
--------
Series.nlargest: Get the `n` largest elements.
Series.sort_values: Sort Series by values.
Series.head: Return the first `n` rows.

Notes
-----
Faster than ``.sort_values().head(n)`` for small `n` relative to
the size of the ``Series`` object.

Examples
--------
>>> countries_population = {"Italy": 59000000, "France": 65000000,
...                         "Brunei": 434000, "Malta": 434000,
...                         "Maldives": 434000, "Iceland": 337000,
...                         "Nauru": 11300, "Tuvalu": 11300,
...                         "Anguilla": 11300, "Montserrat": 5200}
>>> s = pd.Series(countries_population)
>>> s
Italy       59000000
France      65000000
Brunei        434000
Malta         434000
Maldives      434000
Iceland       337000
Nauru          11300
Tuvalu         11300
Anguilla       11300
Montserrat      5200
dtype: int64

The `n` smallest elements where ``n=5`` by default.

>>> s.nsmallest()
Montserrat    5200
Nauru        11300
Tuvalu       11300
Anguilla     11300
Iceland     337000
dtype: int64

The `n` smallest elements where ``n=3``. Default `keep` value is
'first' so Nauru and Tuvalu will be kept.

>>> s.nsmallest(3)
Montserrat   5200
Nauru       11300
Tuvalu      11300
dtype: int64

The `n` smallest elements where ``n=3`` and keeping the last
duplicates. Anguilla and Tuvalu will be kept since they are the last
with value 11300 based on the index order.

>>> s.nsmallest(3, keep='last')
Montserrat   5200
Anguilla    11300
Tuvalu      11300
dtype: int64

The `n` smallest elements where ``n=3`` with all duplicates kept. Note
that the returned Series has four elements due to the three duplicates.

>>> s.nsmallest(3, keep='all')
Montserrat   5200
Nauru       11300
Tuvalu      11300
Anguilla    11300
dtype: int64
        """
        pass
    def idxmin(self, axis: Axis | NoDefault = ..., skipna: bool = ...) -> Series:
        """
Return the row label of the minimum value.

If multiple values equal the minimum, the first row label with that
value is returned.

Parameters
----------
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.
skipna : bool, default True
    Exclude NA/null values. If the entire Series is NA, the result
    will be NA.
*args, **kwargs
    Additional arguments and keywords have no effect but might be
    accepted for compatibility with NumPy.

Returns
-------
Index
    Label of the minimum value.

Raises
------
ValueError
    If the Series is empty.

See Also
--------
numpy.argmin : Return indices of the minimum values
    along the given axis.
DataFrame.idxmin : Return index of first occurrence of minimum
    over requested axis.
Series.idxmax : Return index *label* of the first occurrence
    of maximum of values.

Notes
-----
This method is the Series version of ``ndarray.argmin``. This method
returns the label of the minimum, while ``ndarray.argmin`` returns
the position. To get the position, use ``series.values.argmin()``.

Examples
--------
>>> s = pd.Series(data=[1, None, 4, 1],
...               index=['A', 'B', 'C', 'D'])
>>> s
A    1.0
B    NaN
C    4.0
D    1.0
dtype: float64

>>> s.idxmin()
'A'

If `skipna` is False and there is an NA value in the data,
the function returns ``nan``.

>>> s.idxmin(skipna=False)
nan
        """
        pass
    def idxmax(self, axis: Axis | NoDefault = ..., skipna: bool = ...) -> Series:
        """
Return the row label of the maximum value.

If multiple values equal the maximum, the first row label with that
value is returned.

Parameters
----------
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.
skipna : bool, default True
    Exclude NA/null values. If the entire Series is NA, the result
    will be NA.
*args, **kwargs
    Additional arguments and keywords have no effect but might be
    accepted for compatibility with NumPy.

Returns
-------
Index
    Label of the maximum value.

Raises
------
ValueError
    If the Series is empty.

See Also
--------
numpy.argmax : Return indices of the maximum values
    along the given axis.
DataFrame.idxmax : Return index of first occurrence of maximum
    over requested axis.
Series.idxmin : Return index *label* of the first occurrence
    of minimum of values.

Notes
-----
This method is the Series version of ``ndarray.argmax``. This method
returns the label of the maximum, while ``ndarray.argmax`` returns
the position. To get the position, use ``series.values.argmax()``.

Examples
--------
>>> s = pd.Series(data=[1, None, 4, 3, 4],
...               index=['A', 'B', 'C', 'D', 'E'])
>>> s
A    1.0
B    NaN
C    4.0
D    3.0
E    4.0
dtype: float64

>>> s.idxmax()
'C'

If `skipna` is False and there is an NA value in the data,
the function returns ``nan``.

>>> s.idxmax(skipna=False)
nan
        """
        pass
    def corr(
        self,
        other: Series,
        method: CorrelationMethod = ...,
        min_periods: int | None = ...,
    ) -> Series:
        """
Compute correlation with `other` Series, excluding missing values.

The two `Series` objects are not required to be the same length and will be
aligned internally before the correlation function is applied.

Parameters
----------
other : Series
    Series with which to compute the correlation.
method : {'pearson', 'kendall', 'spearman'} or callable
    Method used to compute correlation:

    - pearson : Standard correlation coefficient
    - kendall : Kendall Tau correlation coefficient
    - spearman : Spearman rank correlation
    - callable: Callable with input two 1d ndarrays and returning a float.

    .. warning::
        Note that the returned matrix from corr will have 1 along the
        diagonals and will be symmetric regardless of the callable's
        behavior.
min_periods : int, optional
    Minimum number of observations needed to have a valid result.

Returns
-------
float
    Correlation with other.

See Also
--------
DataFrame.corr : Compute pairwise correlation between columns.
DataFrame.corrwith : Compute pairwise correlation with another
    DataFrame or Series.

Notes
-----
Pearson, Kendall and Spearman correlation are currently computed using pairwise complete observations.

* `Pearson correlation coefficient <https://en.wikipedia.org/wiki/Pearson_correlation_coefficient>`_
* `Kendall rank correlation coefficient <https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient>`_
* `Spearman's rank correlation coefficient <https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient>`_

Automatic data alignment: as with all pandas operations, automatic data alignment is performed for this method.
``corr()`` automatically considers values with matching indices.

Examples
--------
>>> def histogram_intersection(a, b):
...     v = np.minimum(a, b).sum().round(decimals=1)
...     return v
>>> s1 = pd.Series([.2, .0, .6, .2])
>>> s2 = pd.Series([.3, .6, .0, .1])
>>> s1.corr(s2, method=histogram_intersection)
0.3

Pandas auto-aligns the values with matching indices

>>> s1 = pd.Series([1, 2, 3], index=[0, 1, 2])
>>> s2 = pd.Series([1, 2, 3], index=[2, 1, 0])
>>> s1.corr(s2)
-1.0
        """
        pass
    def cov(
        self, other: Series, min_periods: int | None = ..., ddof: int | None = ...
    ) -> Series:
        """
Compute covariance with Series, excluding missing values.

The two `Series` objects are not required to be the same length and
will be aligned internally before the covariance is calculated.

Parameters
----------
other : Series
    Series with which to compute the covariance.
min_periods : int, optional
    Minimum number of observations needed to have a valid result.
ddof : int, default 1
    Delta degrees of freedom.  The divisor used in calculations
    is ``N - ddof``, where ``N`` represents the number of elements.

Returns
-------
float
    Covariance between Series and other normalized by N-1
    (unbiased estimator).

See Also
--------
DataFrame.cov : Compute pairwise covariance of columns.

Examples
--------
>>> s1 = pd.Series([0.90010907, 0.13484424, 0.62036035])
>>> s2 = pd.Series([0.12528585, 0.26962463, 0.51111198])
>>> s1.cov(s2)
-0.01685762652715874
        """
        pass
    @property
    def is_monotonic_increasing(self) -> Series[bool]: ...
    @property
    def is_monotonic_decreasing(self) -> Series[bool]: ...
    def hist(
        self,
        by: IndexLabel | None = ...,
        ax: PlotAxes | None = ...,
        grid: bool = ...,
        xlabelsize: float | str | None = ...,
        xrot: float | None = ...,
        ylabelsize: float | str | None = ...,
        yrot: float | None = ...,
        figsize: tuple[float, float] | None = ...,
        bins: int | Sequence[int] = ...,
        backend: str | None = ...,
        legend: bool = ...,
        **kwargs,
    ) -> Series: ...  # Series[Axes] but this is not allowed
    @property
    def dtype(self) -> Series:
        """
Return the dtype object of the underlying data.

Examples
--------
>>> s = pd.Series([1, 2, 3])
>>> s.dtype
dtype('int64')
        """
        pass
    def unique(self) -> Series:
        """
Draw histogram of the input series using matplotlib.

Parameters
----------
by : object, optional
    If passed, then used to form histograms for separate groups.
ax : matplotlib axis object
    If not passed, uses gca().
grid : bool, default True
    Whether to show axis grid lines.
xlabelsize : int, default None
    If specified changes the x-axis label size.
xrot : float, default None
    Rotation of x axis labels.
ylabelsize : int, default None
    If specified changes the y-axis label size.
yrot : float, default None
    Rotation of y axis labels.
figsize : tuple, default None
    Figure size in inches by default.
bins : int or sequence, default 10
    Number of histogram bins to be used. If an integer is given, bins + 1
    bin edges are calculated and returned. If bins is a sequence, gives
    bin edges, including left edge of first bin and right edge of last
    bin. In this case, bins is returned unmodified.
backend : str, default None
    Backend to use instead of the backend specified in the option
    ``plotting.backend``. For instance, 'matplotlib'. Alternatively, to
    specify the ``plotting.backend`` for the whole session, set
    ``pd.options.plotting.backend``.
legend : bool, default False
    Whether to show the legend.

**kwargs
    To be passed to the actual plotting function.

Returns
-------
matplotlib.AxesSubplot
    A histogram plot.

See Also
--------
matplotlib.axes.Axes.hist : Plot a histogram using matplotlib.

Examples
--------
For Series:

.. plot::
    :context: close-figs

    >>> lst = ['a', 'a', 'a', 'b', 'b', 'b']
    >>> ser = pd.Series([1, 2, 2, 4, 6, 6], index=lst)
    >>> hist = ser.hist()

For Groupby:

.. plot::
    :context: close-figs

    >>> lst = ['a', 'a', 'a', 'b', 'b', 'b']
    >>> ser = pd.Series([1, 2, 2, 4, 6, 6], index=lst)
    >>> hist = ser.groupby(level=0).hist()
        """
        pass
    # Overrides that provide more precise return types over the GroupBy class
    @final  # type: ignore[misc]
    def __iter__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> Iterator[tuple[ByT, Series[S1]]]: ...

class DataFrameGroupBy(GroupBy[DataFrame], Generic[ByT]):
    # error: Overload 3 for "apply" will never be used because its parameters overlap overload 1
    @overload  # type: ignore[override]
    def apply(  # type: ignore[overload-overlap]
        self,
        func: Callable[[DataFrame], Scalar | list | dict],
        *args,
        **kwargs,
    ) -> Series: ...
    @overload
    def apply(
        self,
        func: Callable[[DataFrame], Series | DataFrame],
        *args,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def apply(  # pyright: ignore[reportOverlappingOverload]
        self,
        func: Callable[[Iterable], float],
        *args,
        **kwargs,
    ) -> DataFrame: ...
    # error: overload 1 overlaps overload 2 because of different return types
    @overload
    def aggregate(self, func: Literal["size"]) -> Series: ...  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
    @overload
    def aggregate(
        self,
        func: AggFuncTypeFrame | None = ...,
        *args,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
        **kwargs,
    ) -> DataFrame:
        """
Aggregate using one or more operations over the specified axis.

Parameters
----------
func : function, str, list, dict or None
    Function to use for aggregating the data. If a function, must either
    work when passed a DataFrame or when passed to DataFrame.apply.

    Accepted combinations are:

    - function
    - string function name
    - list of functions and/or function names, e.g. ``[np.sum, 'mean']``
    - dict of axis labels -> functions, function names or list of such.
    - None, in which case ``**kwargs`` are used with Named Aggregation. Here the
      output has one column for each element in ``**kwargs``. The name of the
      column is keyword, whereas the value determines the aggregation used to compute
      the values in the column.

      Can also accept a Numba JIT function with
      ``engine='numba'`` specified. Only passing a single function is supported
      with this engine.

      If the ``'numba'`` engine is chosen, the function must be
      a user defined function with ``values`` and ``index`` as the
      first and second arguments respectively in the function signature.
      Each group's index will be passed to the user defined function
      and optionally available for use.

*args
    Positional arguments to pass to func.
engine : str, default None
    * ``'cython'`` : Runs the function through C-extensions from cython.
    * ``'numba'`` : Runs the function through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or globally setting ``compute.use_numba``

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}`` and will be
      applied to the function

**kwargs
    * If ``func`` is None, ``**kwargs`` are used to define the output names and
      aggregations via Named Aggregation. See ``func`` entry.
    * Otherwise, keyword arguments to be passed into func.

Returns
-------
DataFrame

See Also
--------
DataFrame.groupby.apply : Apply function func group-wise
    and combine the results together.
DataFrame.groupby.transform : Transforms the Series on each group
    based on the given function.
DataFrame.aggregate : Aggregate using one or more
    operations over the specified axis.

Notes
-----
When using ``engine='numba'``, there will be no "fall back" behavior internally.
The group data and group index will be passed as numpy arrays to the JITed
user defined function, and no alternative execution attempts will be tried.

Functions that mutate the passed object can produce unexpected
behavior or errors and are not supported. See :ref:`gotchas.udf-mutation`
for more details.

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the passed ``func``,
    see the examples below.

Examples
--------
>>> data = {"A": [1, 1, 2, 2],
...         "B": [1, 2, 3, 4],
...         "C": [0.362838, 0.227877, 1.267767, -0.562860]}
>>> df = pd.DataFrame(data)
>>> df
   A  B         C
0  1  1  0.362838
1  1  2  0.227877
2  2  3  1.267767
3  2  4 -0.562860

The aggregation is for each column.

>>> df.groupby('A').agg('min')
   B         C
A
1  1  0.227877
2  3 -0.562860

Multiple aggregations

>>> df.groupby('A').agg(['min', 'max'])
    B             C
  min max       min       max
A
1   1   2  0.227877  0.362838
2   3   4 -0.562860  1.267767

Select a column for aggregation

>>> df.groupby('A').B.agg(['min', 'max'])
   min  max
A
1    1    2
2    3    4

User-defined function for aggregation

>>> df.groupby('A').agg(lambda x: sum(x) + 2)
    B          C
A
1       5       2.590715
2       9       2.704907

Different aggregations per column

>>> df.groupby('A').agg({'B': ['min', 'max'], 'C': 'sum'})
    B             C
  min max       sum
A
1   1   2  0.590715
2   3   4  0.704907

To control the output names with different aggregations per column,
pandas supports "named aggregation"

>>> df.groupby("A").agg(
...     b_min=pd.NamedAgg(column="B", aggfunc="min"),
...     c_sum=pd.NamedAgg(column="C", aggfunc="sum")
... )
   b_min     c_sum
A
1      1  0.590715
2      3  0.704907

- The keywords are the *output* column names
- The values are tuples whose first element is the column to select
  and the second element is the aggregation to apply to that column.
  Pandas provides the ``pandas.NamedAgg`` namedtuple with the fields
  ``['column', 'aggfunc']`` to make it clearer what the arguments are.
  As usual, the aggregation can be a callable or a string alias.

See :ref:`groupby.aggregate.named` for more.

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the aggregating function.

>>> df.groupby("A")[["B"]].agg(lambda x: x.astype(float).min())
      B
A
1   1.0
2   3.0
        """
        pass
    agg = aggregate
    def transform(
        self,
        func: Callable | str,
        *args,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
        **kwargs,
    ) -> DataFrame:
        """
Call function producing a same-indexed DataFrame on each group.

Returns a DataFrame having the same indexes as the original object
filled with the transformed values.

Parameters
----------
f : function, str
    Function to apply to each group. See the Notes section below for requirements.

    Accepted inputs are:

    - String
    - Python function
    - Numba JIT function with ``engine='numba'`` specified.

    Only passing a single function is supported with this engine.
    If the ``'numba'`` engine is chosen, the function must be
    a user defined function with ``values`` and ``index`` as the
    first and second arguments respectively in the function signature.
    Each group's index will be passed to the user defined function
    and optionally available for use.

    If a string is chosen, then it needs to be the name
    of the groupby method you want to use.
*args
    Positional arguments to pass to func.
engine : str, default None
    * ``'cython'`` : Runs the function through C-extensions from cython.
    * ``'numba'`` : Runs the function through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or the global setting ``compute.use_numba``

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}`` and will be
      applied to the function

**kwargs
    Keyword arguments to be passed into func.

Returns
-------
DataFrame

See Also
--------
DataFrame.groupby.apply : Apply function ``func`` group-wise and combine
    the results together.
DataFrame.groupby.aggregate : Aggregate using one or more
    operations over the specified axis.
DataFrame.transform : Call ``func`` on self producing a DataFrame with the
    same axis shape as self.

Notes
-----
Each group is endowed the attribute 'name' in case you need to know
which group you are working on.

The current implementation imposes three requirements on f:

* f must return a value that either has the same shape as the input
  subframe or can be broadcast to the shape of the input subframe.
  For example, if `f` returns a scalar it will be broadcast to have the
  same shape as the input subframe.
* if this is a DataFrame, f must support application column-by-column
  in the subframe. If f also supports application to the entire subframe,
  then a fast path is used starting from the second chunk.
* f must not mutate groups. Mutation is not supported and may
  produce unexpected results. See :ref:`gotchas.udf-mutation` for more details.

When using ``engine='numba'``, there will be no "fall back" behavior internally.
The group data and group index will be passed as numpy arrays to the JITed
user defined function, and no alternative execution attempts will be tried.

.. versionchanged:: 1.3.0

    The resulting dtype will reflect the return value of the passed ``func``,
    see the examples below.

.. versionchanged:: 2.0.0

    When using ``.transform`` on a grouped DataFrame and the transformation function
    returns a DataFrame, pandas now aligns the result's index
    with the input's index. You can call ``.to_numpy()`` on the
    result of the transformation function to avoid alignment.

Examples
--------

>>> df = pd.DataFrame({'A' : ['foo', 'bar', 'foo', 'bar',
...                           'foo', 'bar'],
...                    'B' : ['one', 'one', 'two', 'three',
...                           'two', 'two'],
...                    'C' : [1, 5, 5, 2, 5, 5],
...                    'D' : [2.0, 5., 8., 1., 2., 9.]})
>>> grouped = df.groupby('A')[['C', 'D']]
>>> grouped.transform(lambda x: (x - x.mean()) / x.std())
        C         D
0 -1.154701 -0.577350
1  0.577350  0.000000
2  0.577350  1.154701
3 -1.154701 -1.000000
4  0.577350 -0.577350
5  0.577350  1.000000

Broadcast result of the transformation

>>> grouped.transform(lambda x: x.max() - x.min())
    C    D
0  4.0  6.0
1  3.0  8.0
2  4.0  6.0
3  3.0  8.0
4  4.0  6.0
5  3.0  8.0

>>> grouped.transform("mean")
    C    D
0  3.666667  4.0
1  4.000000  5.0
2  3.666667  4.0
3  4.000000  5.0
4  3.666667  4.0
5  4.000000  5.0

.. versionchanged:: 1.3.0

The resulting dtype will reflect the return value of the passed ``func``,
for example:

>>> grouped.transform(lambda x: x.astype(int).max())
C  D
0  5  8
1  5  9
2  5  8
3  5  9
4  5  8
5  5  9
        """
        pass
    def filter(
        self, func: Callable, dropna: bool = ..., *args, **kwargs
    ) -> DataFrame: ...
    @overload
    def __getitem__(  # type: ignore[overload-overlap]
        self, key: Scalar | Hashable | tuple[Hashable, ...]
    ) -> SeriesGroupBy[Any, ByT]: ...
    @overload
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, key: Iterable[Hashable] | slice
    ) -> DataFrameGroupBy[ByT]: ...
    def nunique(self, dropna: bool = ...) -> DataFrame: ...
    def idxmax(
        self,
        axis: Axis | None | NoDefault = ...,
        skipna: bool = ...,
        numeric_only: bool = ...,
    ) -> DataFrame: ...
    def idxmin(
        self,
        axis: Axis | None | NoDefault = ...,
        skipna: bool = ...,
        numeric_only: bool = ...,
    ) -> DataFrame: ...
    @overload
    def boxplot(
        self,
        subplots: Literal[True] = ...,
        column: IndexLabel | None = ...,
        fontsize: float | str | None = ...,
        rot: float = ...,
        grid: bool = ...,
        ax: PlotAxes | None = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        sharex: bool = ...,
        sharey: bool = ...,
        backend: str | None = ...,
        **kwargs,
    ) -> Series: ...  # Series[PlotAxes] but this is not allowed
    @overload
    def boxplot(
        self,
        subplots: Literal[False],
        column: IndexLabel | None = ...,
        fontsize: float | str | None = ...,
        rot: float = ...,
        grid: bool = ...,
        ax: PlotAxes | None = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        sharex: bool = ...,
        sharey: bool = ...,
        backend: str | None = ...,
        **kwargs,
    ) -> PlotAxes: ...
    @overload
    def boxplot(
        self,
        subplots: bool,
        column: IndexLabel | None = ...,
        fontsize: float | str | None = ...,
        rot: float = ...,
        grid: bool = ...,
        ax: PlotAxes | None = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        sharex: bool = ...,
        sharey: bool = ...,
        backend: str | None = ...,
        **kwargs,
    ) -> PlotAxes | Series: ...  # Series[PlotAxes]
    @overload
    def value_counts(
        self,
        subset: ListLike | None = ...,
        normalize: Literal[False] = ...,
        sort: bool = ...,
        ascending: bool = ...,
        dropna: bool = ...,
    ) -> Series[int]: ...
    @overload
    def value_counts(
        self,
        subset: ListLike | None,
        normalize: Literal[True],
        sort: bool = ...,
        ascending: bool = ...,
        dropna: bool = ...,
    ) -> Series[float]: ...
    def take(
        self, indices: TakeIndexer, axis: Axis | None | NoDefault = ..., **kwargs
    ) -> DataFrame: ...
    @overload
    def skew(  # type: ignore[overload-overlap]
        self,
        axis: Axis | None | NoDefault = ...,
        skipna: bool = ...,
        numeric_only: bool = ...,
        *,
        level: Level,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def skew(
        self,
        axis: Axis | None | NoDefault = ...,
        skipna: bool = ...,
        numeric_only: bool = ...,
        *,
        level: None = ...,
        **kwargs,
    ) -> Series: ...
    @property
    def plot(self) -> GroupByPlot[Self]:
        """
Make plots of Series or DataFrame.

Uses the backend specified by the
option ``plotting.backend``. By default, matplotlib is used.

Parameters
----------
data : Series or DataFrame
    The object for which the method is called.
x : label or position, default None
    Only used if data is a DataFrame.
y : label, position or list of label, positions, default None
    Allows plotting of one column versus another. Only used if data is a
    DataFrame.
kind : str
    The kind of plot to produce:

    - 'line' : line plot (default)
    - 'bar' : vertical bar plot
    - 'barh' : horizontal bar plot
    - 'hist' : histogram
    - 'box' : boxplot
    - 'kde' : Kernel Density Estimation plot
    - 'density' : same as 'kde'
    - 'area' : area plot
    - 'pie' : pie plot
    - 'scatter' : scatter plot (DataFrame only)
    - 'hexbin' : hexbin plot (DataFrame only)
ax : matplotlib axes object, default None
    An axes of the current figure.
subplots : bool or sequence of iterables, default False
    Whether to group columns into subplots:

    - ``False`` : No subplots will be used
    - ``True`` : Make separate subplots for each column.
    - sequence of iterables of column labels: Create a subplot for each
      group of columns. For example `[('a', 'c'), ('b', 'd')]` will
      create 2 subplots: one with columns 'a' and 'c', and one
      with columns 'b' and 'd'. Remaining columns that aren't specified
      will be plotted in additional subplots (one per column).

      .. versionadded:: 1.5.0

sharex : bool, default True if ax is None else False
    In case ``subplots=True``, share x axis and set some x axis labels
    to invisible; defaults to True if ax is None otherwise False if
    an ax is passed in; Be aware, that passing in both an ax and
    ``sharex=True`` will alter all x axis labels for all axis in a figure.
sharey : bool, default False
    In case ``subplots=True``, share y axis and set some y axis labels to invisible.
layout : tuple, optional
    (rows, columns) for the layout of subplots.
figsize : a tuple (width, height) in inches
    Size of a figure object.
use_index : bool, default True
    Use index as ticks for x axis.
title : str or list
    Title to use for the plot. If a string is passed, print the string
    at the top of the figure. If a list is passed and `subplots` is
    True, print each item in the list above the corresponding subplot.
grid : bool, default None (matlab style default)
    Axis grid lines.
legend : bool or {'reverse'}
    Place legend on axis subplots.
style : list or dict
    The matplotlib line style per column.
logx : bool or 'sym', default False
    Use log scaling or symlog scaling on x axis.

logy : bool or 'sym' default False
    Use log scaling or symlog scaling on y axis.

loglog : bool or 'sym', default False
    Use log scaling or symlog scaling on both x and y axes.

xticks : sequence
    Values to use for the xticks.
yticks : sequence
    Values to use for the yticks.
xlim : 2-tuple/list
    Set the x limits of the current axes.
ylim : 2-tuple/list
    Set the y limits of the current axes.
xlabel : label, optional
    Name to use for the xlabel on x-axis. Default uses index name as xlabel, or the
    x-column name for planar plots.

    .. versionchanged:: 2.0.0

        Now applicable to histograms.

ylabel : label, optional
    Name to use for the ylabel on y-axis. Default will show no ylabel, or the
    y-column name for planar plots.

    .. versionchanged:: 2.0.0

        Now applicable to histograms.

rot : float, default None
    Rotation for ticks (xticks for vertical, yticks for horizontal
    plots).
fontsize : float, default None
    Font size for xticks and yticks.
colormap : str or matplotlib colormap object, default None
    Colormap to select colors from. If string, load colormap with that
    name from matplotlib.
colorbar : bool, optional
    If True, plot colorbar (only relevant for 'scatter' and 'hexbin'
    plots).
position : float
    Specify relative alignments for bar plot layout.
    From 0 (left/bottom-end) to 1 (right/top-end). Default is 0.5
    (center).
table : bool, Series or DataFrame, default False
    If True, draw a table using the data in the DataFrame and the data
    will be transposed to meet matplotlib's default layout.
    If a Series or DataFrame is passed, use passed data to draw a
    table.
yerr : DataFrame, Series, array-like, dict and str
    See :ref:`Plotting with Error Bars <visualization.errorbars>` for
    detail.
xerr : DataFrame, Series, array-like, dict and str
    Equivalent to yerr.
stacked : bool, default False in line and bar plots, and True in area plot
    If True, create stacked plot.
secondary_y : bool or sequence, default False
    Whether to plot on the secondary y-axis if a list/tuple, which
    columns to plot on secondary y-axis.
mark_right : bool, default True
    When using a secondary_y axis, automatically mark the column
    labels with "(right)" in the legend.
include_bool : bool, default is False
    If True, boolean values can be plotted.
backend : str, default None
    Backend to use instead of the backend specified in the option
    ``plotting.backend``. For instance, 'matplotlib'. Alternatively, to
    specify the ``plotting.backend`` for the whole session, set
    ``pd.options.plotting.backend``.
**kwargs
    Options to pass to matplotlib plotting method.

Returns
-------
:class:`matplotlib.axes.Axes` or numpy.ndarray of them
    If the backend is not the default matplotlib one, the return value
    will be the object returned by the backend.

Notes
-----
- See matplotlib documentation online for more on this subject
- If `kind` = 'bar' or 'barh', you can specify relative alignments
  for bar plot layout by `position` keyword.
  From 0 (left/bottom-end) to 1 (right/top-end). Default is 0.5
  (center)

Examples
--------
For Series:

.. plot::
    :context: close-figs

    >>> ser = pd.Series([1, 2, 3, 3])
    >>> plot = ser.plot(kind='hist', title="My plot")

For DataFrame:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame({'length': [1.5, 0.5, 1.2, 0.9, 3],
    ...                   'width': [0.7, 0.2, 0.15, 0.2, 1.1]},
    ...                   index=['pig', 'rabbit', 'duck', 'chicken', 'horse'])
    >>> plot = df.plot(title="DataFrame Plot")

For SeriesGroupBy:

.. plot::
    :context: close-figs

    >>> lst = [-1, -2, -3, 1, 2, 3]
    >>> ser = pd.Series([1, 2, 2, 4, 6, 6], index=lst)
    >>> plot = ser.groupby(lambda x: x > 0).plot(title="SeriesGroupBy Plot")

For DataFrameGroupBy:

.. plot::
    :context: close-figs

    >>> df = pd.DataFrame({"col1" : [1, 2, 3, 4],
    ...                   "col2" : ["A", "B", "A", "B"]})
    >>> plot = df.groupby("col2").plot(kind="bar", title="DataFrameGroupBy Plot")
        """
        pass
    def corr(
        self,
        method: str | Callable[[np.ndarray, np.ndarray], float] = ...,
        min_periods: int = ...,
        numeric_only: bool = ...,
    ) -> DataFrame:
        """
Compute pairwise correlation of columns, excluding NA/null values.

Parameters
----------
method : {'pearson', 'kendall', 'spearman'} or callable
    Method of correlation:

    * pearson : standard correlation coefficient
    * kendall : Kendall Tau correlation coefficient
    * spearman : Spearman rank correlation
    * callable: callable with input two 1d ndarrays
        and returning a float. Note that the returned matrix from corr
        will have 1 along the diagonals and will be symmetric
        regardless of the callable's behavior.
min_periods : int, optional
    Minimum number of observations required per pair of columns
    to have a valid result. Currently only available for Pearson
    and Spearman correlation.
numeric_only : bool, default False
    Include only `float`, `int` or `boolean` data.

    .. versionadded:: 1.5.0

    .. versionchanged:: 2.0.0
        The default value of ``numeric_only`` is now ``False``.

Returns
-------
DataFrame
    Correlation matrix.

See Also
--------
DataFrame.corrwith : Compute pairwise correlation with another
    DataFrame or Series.
Series.corr : Compute the correlation between two Series.

Notes
-----
Pearson, Kendall and Spearman correlation are currently computed using pairwise complete observations.

* `Pearson correlation coefficient <https://en.wikipedia.org/wiki/Pearson_correlation_coefficient>`_
* `Kendall rank correlation coefficient <https://en.wikipedia.org/wiki/Kendall_rank_correlation_coefficient>`_
* `Spearman's rank correlation coefficient <https://en.wikipedia.org/wiki/Spearman%27s_rank_correlation_coefficient>`_

Examples
--------
>>> def histogram_intersection(a, b):
...     v = np.minimum(a, b).sum().round(decimals=1)
...     return v
>>> df = pd.DataFrame([(.2, .3), (.0, .6), (.6, .0), (.2, .1)],
...                   columns=['dogs', 'cats'])
>>> df.corr(method=histogram_intersection)
      dogs  cats
dogs   1.0   0.3
cats   0.3   1.0

>>> df = pd.DataFrame([(1, 1), (2, np.nan), (np.nan, 3), (4, 4)],
...                   columns=['dogs', 'cats'])
>>> df.corr(min_periods=3)
      dogs  cats
dogs   1.0   NaN
cats   NaN   1.0
        """
        pass
    def cov(
        self,
        min_periods: int | None = ...,
        ddof: int | None = ...,
        numeric_only: bool = ...,
    ) -> DataFrame:
        """
Compute pairwise covariance of columns, excluding NA/null values.

Compute the pairwise covariance among the series of a DataFrame.
The returned data frame is the `covariance matrix
<https://en.wikipedia.org/wiki/Covariance_matrix>`__ of the columns
of the DataFrame.

Both NA and null values are automatically excluded from the
calculation. (See the note below about bias from missing values.)
A threshold can be set for the minimum number of
observations for each value created. Comparisons with observations
below this threshold will be returned as ``NaN``.

This method is generally used for the analysis of time series data to
understand the relationship between different measures
across time.

Parameters
----------
min_periods : int, optional
    Minimum number of observations required per pair of columns
    to have a valid result.

ddof : int, default 1
    Delta degrees of freedom.  The divisor used in calculations
    is ``N - ddof``, where ``N`` represents the number of elements.
    This argument is applicable only when no ``nan`` is in the dataframe.

numeric_only : bool, default False
    Include only `float`, `int` or `boolean` data.

    .. versionadded:: 1.5.0

    .. versionchanged:: 2.0.0
        The default value of ``numeric_only`` is now ``False``.

Returns
-------
DataFrame
    The covariance matrix of the series of the DataFrame.

See Also
--------
Series.cov : Compute covariance with another Series.
core.window.ewm.ExponentialMovingWindow.cov : Exponential weighted sample
    covariance.
core.window.expanding.Expanding.cov : Expanding sample covariance.
core.window.rolling.Rolling.cov : Rolling sample covariance.

Notes
-----
Returns the covariance matrix of the DataFrame's time series.
The covariance is normalized by N-ddof.

For DataFrames that have Series that are missing data (assuming that
data is `missing at random
<https://en.wikipedia.org/wiki/Missing_data#Missing_at_random>`__)
the returned covariance matrix will be an unbiased estimate
of the variance and covariance between the member Series.

However, for many applications this estimate may not be acceptable
because the estimate covariance matrix is not guaranteed to be positive
semi-definite. This could lead to estimate correlations having
absolute values which are greater than one, and/or a non-invertible
covariance matrix. See `Estimation of covariance matrices
<https://en.wikipedia.org/w/index.php?title=Estimation_of_covariance_
matrices>`__ for more details.

Examples
--------
>>> df = pd.DataFrame([(1, 2), (0, 3), (2, 0), (1, 1)],
...                   columns=['dogs', 'cats'])
>>> df.cov()
          dogs      cats
dogs  0.666667 -1.000000
cats -1.000000  1.666667

>>> np.random.seed(42)
>>> df = pd.DataFrame(np.random.randn(1000, 5),
...                   columns=['a', 'b', 'c', 'd', 'e'])
>>> df.cov()
          a         b         c         d         e
a  0.998438 -0.020161  0.059277 -0.008943  0.014144
b -0.020161  1.059352 -0.008543 -0.024738  0.009826
c  0.059277 -0.008543  1.010670 -0.001486 -0.000271
d -0.008943 -0.024738 -0.001486  0.921297 -0.013692
e  0.014144  0.009826 -0.000271 -0.013692  0.977795

**Minimum number of periods**

This method also supports an optional ``min_periods`` keyword
that specifies the required minimum number of non-NA observations for
each column pair in order to have a valid result:

>>> np.random.seed(42)
>>> df = pd.DataFrame(np.random.randn(20, 3),
...                   columns=['a', 'b', 'c'])
>>> df.loc[df.index[:5], 'a'] = np.nan
>>> df.loc[df.index[5:10], 'b'] = np.nan
>>> df.cov(min_periods=12)
          a         b         c
a  0.316741       NaN -0.150812
b       NaN  1.248003  0.191417
c -0.150812  0.191417  0.895202
        """
        pass
    def hist(
        self,
        column: IndexLabel | None = ...,
        by: IndexLabel | None = ...,
        grid: bool = ...,
        xlabelsize: float | str | None = ...,
        xrot: float | None = ...,
        ylabelsize: float | str | None = ...,
        yrot: float | None = ...,
        ax: PlotAxes | None = ...,
        sharex: bool = ...,
        sharey: bool = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        bins: int | Sequence[int] = ...,
        backend: str | None = ...,
        legend: bool = ...,
        **kwargs,
    ) -> Series: ...  # Series[Axes] but this is not allowed
    @property
    def dtypes(self) -> Series:
        """
Return the dtypes in the DataFrame.

This returns a Series with the data type of each column.
The result's index is the original DataFrame's columns. Columns
with mixed types are stored with the ``object`` dtype. See
:ref:`the User Guide <basics.dtypes>` for more.

Returns
-------
pandas.Series
    The data type of each column.

Examples
--------
>>> df = pd.DataFrame({'float': [1.0],
...                    'int': [1],
...                    'datetime': [pd.Timestamp('20180310')],
...                    'string': ['foo']})
>>> df.dtypes
float              float64
int                  int64
datetime    datetime64[ns]
string              object
dtype: object
        """
        pass
    def corrwith(
        self,
        other: DataFrame | Series,
        axis: Axis | NoDefault = ...,
        drop: bool = ...,
        method: CorrelationMethod = ...,
        numeric_only: bool = ...,
    ) -> DataFrame:
        """
Compute pairwise correlation.

Pairwise correlation is computed between rows or columns of
DataFrame with rows or columns of Series or DataFrame. DataFrames
are first aligned along both axes before computing the
correlations.

Parameters
----------
other : DataFrame, Series
    Object with which to compute correlations.
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to use. 0 or 'index' to compute row-wise, 1 or 'columns' for
    column-wise.
drop : bool, default False
    Drop missing indices from result.
method : {'pearson', 'kendall', 'spearman'} or callable
    Method of correlation:

    * pearson : standard correlation coefficient
    * kendall : Kendall Tau correlation coefficient
    * spearman : Spearman rank correlation
    * callable: callable with input two 1d ndarrays
        and returning a float.

numeric_only : bool, default False
    Include only `float`, `int` or `boolean` data.

    .. versionadded:: 1.5.0

    .. versionchanged:: 2.0.0
        The default value of ``numeric_only`` is now ``False``.

Returns
-------
Series
    Pairwise correlations.

See Also
--------
DataFrame.corr : Compute pairwise correlation of columns.

Examples
--------
>>> index = ["a", "b", "c", "d", "e"]
>>> columns = ["one", "two", "three", "four"]
>>> df1 = pd.DataFrame(np.arange(20).reshape(5, 4), index=index, columns=columns)
>>> df2 = pd.DataFrame(np.arange(16).reshape(4, 4), index=index[:4], columns=columns)
>>> df1.corrwith(df2)
one      1.0
two      1.0
three    1.0
four     1.0
dtype: float64

>>> df2.corrwith(df1, axis=1)
a    1.0
b    1.0
c    1.0
d    1.0
e    NaN
dtype: float64
        """
        pass
    def __getattr__(self, name: str) -> SeriesGroupBy[Any, ByT]:
        """
Make a histogram of the DataFrame's columns.

A `histogram`_ is a representation of the distribution of data.
This function calls :meth:`matplotlib.pyplot.hist`, on each series in
the DataFrame, resulting in one histogram per column.

.. _histogram: https://en.wikipedia.org/wiki/Histogram

Parameters
----------
data : DataFrame
    The pandas object holding the data.
column : str or sequence, optional
    If passed, will be used to limit data to a subset of columns.
by : object, optional
    If passed, then used to form histograms for separate groups.
grid : bool, default True
    Whether to show axis grid lines.
xlabelsize : int, default None
    If specified changes the x-axis label size.
xrot : float, default None
    Rotation of x axis labels. For example, a value of 90 displays the
    x labels rotated 90 degrees clockwise.
ylabelsize : int, default None
    If specified changes the y-axis label size.
yrot : float, default None
    Rotation of y axis labels. For example, a value of 90 displays the
    y labels rotated 90 degrees clockwise.
ax : Matplotlib axes object, default None
    The axes to plot the histogram on.
sharex : bool, default True if ax is None else False
    In case subplots=True, share x axis and set some x axis labels to
    invisible; defaults to True if ax is None otherwise False if an ax
    is passed in.
    Note that passing in both an ax and sharex=True will alter all x axis
    labels for all subplots in a figure.
sharey : bool, default False
    In case subplots=True, share y axis and set some y axis labels to
    invisible.
figsize : tuple, optional
    The size in inches of the figure to create. Uses the value in
    `matplotlib.rcParams` by default.
layout : tuple, optional
    Tuple of (rows, columns) for the layout of the histograms.
bins : int or sequence, default 10
    Number of histogram bins to be used. If an integer is given, bins + 1
    bin edges are calculated and returned. If bins is a sequence, gives
    bin edges, including left edge of first bin and right edge of last
    bin. In this case, bins is returned unmodified.

backend : str, default None
    Backend to use instead of the backend specified in the option
    ``plotting.backend``. For instance, 'matplotlib'. Alternatively, to
    specify the ``plotting.backend`` for the whole session, set
    ``pd.options.plotting.backend``.

legend : bool, default False
    Whether to show the legend.

**kwargs
    All other plotting keyword arguments to be passed to
    :meth:`matplotlib.pyplot.hist`.

Returns
-------
matplotlib.AxesSubplot or numpy.ndarray of them

See Also
--------
matplotlib.pyplot.hist : Plot a histogram using matplotlib.

Examples
--------
This example draws a histogram based on the length and width of
some animals, displayed in three bins

.. plot::
    :context: close-figs

    >>> data = {'length': [1.5, 0.5, 1.2, 0.9, 3],
    ...         'width': [0.7, 0.2, 0.15, 0.2, 1.1]}
    >>> index = ['pig', 'rabbit', 'duck', 'chicken', 'horse']
    >>> df = pd.DataFrame(data, index=index)
    >>> hist = df.hist(bins=3)
        """
        pass
    # Overrides that provide more precise return types over the GroupBy class
    @final  # type: ignore[misc]
    def __iter__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
    ) -> Iterator[tuple[ByT, DataFrame]]: ...
