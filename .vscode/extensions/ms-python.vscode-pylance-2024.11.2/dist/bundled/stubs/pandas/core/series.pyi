from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
from typing import (
    Any,
    ClassVar,
    Generic,
    Literal,
    overload,
)

from matplotlib.axes import (
    Axes as PlotAxes,
    SubplotBase,
)
import numpy as np
from pandas import (
    Period,
    PeriodDtype,
    Timedelta,
    Timestamp,
)
from pandas.core.api import (
    Int8Dtype as Int8Dtype,
    Int16Dtype as Int16Dtype,
    Int32Dtype as Int32Dtype,
    Int64Dtype as Int64Dtype,
)
from pandas.core.arrays.base import ExtensionArray
from pandas.core.arrays.categorical import CategoricalAccessor
from pandas.core.arrays.interval import IntervalArray
from pandas.core.base import IndexOpsMixin
from pandas.core.frame import DataFrame
from pandas.core.generic import NDFrame
from pandas.core.groupby.generic import SeriesGroupBy
from pandas.core.groupby.groupby import BaseGroupBy
from pandas.core.indexers import BaseIndexer
from pandas.core.indexes.accessors import (
    CombinedDatetimelikeProperties,
    PeriodProperties,
    TimedeltaProperties,
    TimestampProperties,
)
from pandas.core.indexes.base import Index
from pandas.core.indexes.category import CategoricalIndex
from pandas.core.indexes.datetimes import DatetimeIndex
from pandas.core.indexes.interval import IntervalIndex
from pandas.core.indexes.multi import MultiIndex
from pandas.core.indexes.period import PeriodIndex
from pandas.core.indexes.timedeltas import TimedeltaIndex
from pandas.core.indexing import (
    _AtIndexer,
    _iAtIndexer,
    _iLocIndexer,
    _IndexSliceTuple,
    _LocIndexer,
)
from pandas.core.strings import StringMethods
from pandas.core.window import (
    Expanding,
    ExponentialMovingWindow,
)
from pandas.core.window.rolling import (
    Rolling,
    Window,
)
from typing_extensions import (
    Never,
    Self,
    TypeAlias,
)
import xarray as xr

from pandas._libs.interval import (
    Interval,
    _OrderableT,
)
from pandas._libs.lib import NoDefault
from pandas._libs.missing import NAType
from pandas._libs.tslibs import BaseOffset
from pandas._libs.tslibs.nattype import NaTType
from pandas._typing import (
    S1,
    S2,
    AggFuncTypeBase,
    AggFuncTypeDictFrame,
    AggFuncTypeSeriesToFrame,
    AnyArrayLike,
    ArrayLike,
    Axes,
    Axis,
    AxisColumn,
    AxisIndex,
    BooleanDtypeArg,
    BytesDtypeArg,
    CalculationMethod,
    CategoryDtypeArg,
    ComplexDtypeArg,
    CompressionOptions,
    Dtype,
    DtypeObj,
    FilePath,
    FillnaOptions,
    FloatDtypeArg,
    GroupByObjectNonScalar,
    HashableT1,
    IgnoreRaise,
    IndexingInt,
    IndexLabel,
    IntDtypeArg,
    InterpolateOptions,
    IntervalClosedType,
    IntervalT,
    JoinHow,
    JsonSeriesOrient,
    Level,
    ListLike,
    ListLikeU,
    MaskType,
    NaPosition,
    ObjectDtypeArg,
    QuantileInterpolation,
    RandomState,
    Renamer,
    ReplaceMethod,
    Scalar,
    ScalarT,
    SeriesByT,
    SortKind,
    StrDtypeArg,
    StrLike,
    T,
    TimedeltaDtypeArg,
    TimestampConvention,
    TimestampDtypeArg,
    TimeUnit,
    UIntDtypeArg,
    VoidDtypeArg,
    WriteBuffer,
    np_ndarray_anyint,
    np_ndarray_bool,
    npt,
    num,
)

from pandas.core.dtypes.base import ExtensionDtype
from pandas.core.dtypes.dtypes import CategoricalDtype

from pandas.plotting import PlotAccessor

_bool = bool
_str = str

class _iLocIndexerSeries(_iLocIndexer, Generic[S1]):
    # get item
    @overload
    def __getitem__(self, idx: IndexingInt) -> S1: ...
    @overload
    def __getitem__(self, idx: Index | slice | np_ndarray_anyint) -> Series[S1]: ...
    # set item
    @overload
    def __setitem__(self, idx: int, value: S1 | None) -> None: ...
    @overload
    def __setitem__(
        self,
        idx: Index | slice | np_ndarray_anyint | list[int],
        value: S1 | Series[S1] | None,
    ) -> None: ...

class _LocIndexerSeries(_LocIndexer, Generic[S1]):
    # ignore needed because of mypy.  Overlapping, but we want to distinguish
    # having a tuple of just scalars, versus tuples that include slices or Index
    @overload
    def __getitem__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self,
        idx: Scalar | tuple[Scalar, ...],
        # tuple case is for getting a specific element when using a MultiIndex
    ) -> S1: ...
    @overload
    def __getitem__(
        self,
        idx: (
            MaskType
            | Index
            | Sequence[float]
            | list[str]
            | slice
            | _IndexSliceTuple
            | Sequence[_IndexSliceTuple]
            | Callable
        ),
        # _IndexSliceTuple is when having a tuple that includes a slice.  Could just
        # be s.loc[1, :], or s.loc[pd.IndexSlice[1, :]]
    ) -> Series[S1]: ...
    @overload
    def __setitem__(
        self,
        idx: Index | MaskType,
        value: S1 | ArrayLike | Series[S1] | None,
    ) -> None: ...
    @overload
    def __setitem__(
        self,
        idx: str,
        value: S1 | None,
    ) -> None: ...
    @overload
    def __setitem__(
        self,
        idx: MaskType | StrLike | _IndexSliceTuple | list[ScalarT],
        value: S1 | ArrayLike | Series[S1] | None,
    ) -> None: ...

_ListLike: TypeAlias = (
    ArrayLike | dict[_str, np.ndarray] | Sequence[S1] | IndexOpsMixin[S1]
)

class Series(IndexOpsMixin[S1], NDFrame):
    __hash__: ClassVar[None]

    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: npt.NDArray[np.float64],
        index: Axes | None = ...,
        *,
        dtype: Dtype = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> Series[float]: ...
    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: (
            DatetimeIndex
            | Sequence[np.datetime64 | datetime | date]
            | dict[HashableT1, np.datetime64 | datetime | date]
            | np.datetime64
            | datetime
            | date
        ),
        index: Axes | None = ...,
        *,
        dtype: TimestampDtypeArg = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> TimestampSeries: ...
    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: _ListLike,
        index: Axes | None = ...,
        *,
        dtype: TimestampDtypeArg,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> TimestampSeries: ...
    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: PeriodIndex | Sequence[Period],
        index: Axes | None = ...,
        *,
        dtype: PeriodDtype = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> PeriodSeries: ...
    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: (
            TimedeltaIndex
            | Sequence[np.timedelta64 | timedelta]
            | dict[HashableT1, np.timedelta64 | timedelta]
            | np.timedelta64
            | timedelta
        ),
        index: Axes | None = ...,
        *,
        dtype: TimedeltaDtypeArg = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> TimedeltaSeries: ...
    @overload
    def __new__(  # type: ignore[overload-overlap]
        cls,
        data: (
            IntervalIndex[Interval[_OrderableT]]
            | Interval[_OrderableT]
            | Sequence[Interval[_OrderableT]]
            | dict[HashableT1, Interval[_OrderableT]]
        ),
        index: Axes | None = ...,
        *,
        dtype: Literal["Interval"] = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> IntervalSeries[_OrderableT]: ...
    @overload
    def __new__(
        cls,
        data: Scalar | _ListLike | dict[HashableT1, Any] | None,
        index: Axes | None = ...,
        *,
        dtype: type[S1],
        name: Hashable = ...,
        copy: bool = ...,
    ) -> Self: ...
    @overload
    def __new__(
        cls,
        data: S1 | _ListLike[S1] | dict[HashableT1, S1],
        index: Axes | None = ...,
        *,
        dtype: Dtype = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> Self: ...
    @overload
    def __new__(
        cls,
        data: (
            Scalar
            | _ListLike
            | Mapping[HashableT1, Any]
            | BaseGroupBy
            | NaTType
            | NAType
            | None
        ) = ...,
        index: Axes | None = ...,
        *,
        dtype: Dtype = ...,
        name: Hashable = ...,
        copy: bool = ...,
    ) -> Series: ...
    @property
    def hasnans(self) -> bool: ...
    def div(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[float]:
        """
Return Floating division of series and other, element-wise (binary operator `truediv`).

Equivalent to ``series / other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rtruediv : Reverse of the Floating division operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divide(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def rdiv(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Floating division of series and other, element-wise (binary operator `rtruediv`).

Equivalent to ``other / series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.truediv : Element-wise Floating division, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divide(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    @property
    def dtype(self) -> DtypeObj: ...
    @property
    def dtypes(self) -> DtypeObj: ...
    @property
    def name(self) -> Hashable | None: ...
    @name.setter
    def name(self, value: Hashable | None) -> None: ...
    @property
    def values(self) -> ArrayLike: ...
    @property
    def array(self) -> ExtensionArray: ...
    def ravel(self, order: _str = ...) -> np.ndarray: ...
    def __len__(self) -> int: ...
    def view(self, dtype=...) -> Series[S1]:
        """
Create a new view of the Series.

.. deprecated:: 2.2.0
    ``Series.view`` is deprecated and will be removed in a future version.
    Use :meth:`Series.astype` as an alternative to change the dtype.

This function will return a new Series with a view of the same
underlying values in memory, optionally reinterpreted with a new data
type. The new data type must preserve the same size in bytes as to not
cause index misalignment.

Parameters
----------
dtype : data type
    Data type object or one of their string representations.

Returns
-------
Series
    A new Series object as a view of the same data in memory.

See Also
--------
numpy.ndarray.view : Equivalent numpy function to create a new view of
    the same data in memory.

Notes
-----
Series are instantiated with ``dtype=float64`` by default. While
``numpy.ndarray.view()`` will return a view with the same data type as
the original array, ``Series.view()`` (without specified dtype)
will try using ``float64`` and may fail if the original data type size
in bytes is not the same.

Examples
--------
Use ``astype`` to change the dtype instead.
        """
        pass
    def __array_ufunc__(self, ufunc: Callable, method: _str, *inputs, **kwargs): ...
    def __array__(self, dtype=...) -> np.ndarray: ...
    @property
    def axes(self) -> list: ...
    def take(
        self, indices: Sequence, axis: AxisIndex = ..., **kwargs
    ) -> Series[S1]: ...
    def __getattr__(self, name: _str) -> S1: ...
    @overload
    def __getitem__(
        self,
        idx: (
            list[_str]
            | Index
            | Series[S1]
            | slice
            | MaskType
            | tuple[Hashable | slice, ...]
        ),
    ) -> Self: ...
    @overload
    def __getitem__(self, idx: Scalar) -> S1: ...
    def __setitem__(self, key, value) -> None: ...
    @overload
    def get(self, key: Hashable, default: None = ...) -> S1 | None: ...
    @overload
    def get(self, key: Hashable, default: S1) -> S1: ...
    @overload
    def get(self, key: Hashable, default: T) -> S1 | T: ...
    def repeat(
        self, repeats: int | list[int], axis: AxisIndex | None = ...
    ) -> Series[S1]: ...
    @property
    def index(self) -> Index | MultiIndex: ...
    @index.setter
    def index(self, idx: Index) -> None: ...
    # TODO: combine Level | Sequence[Level] github.com/python/mypy/issues/14311
    @overload
    def reset_index(
        self,
        level: Sequence[Level] = ...,
        *,
        drop: Literal[False] = ...,
        name: Level = ...,
        inplace: Literal[False] = ...,
        allow_duplicates: bool = ...,
    ) -> DataFrame: ...
    @overload
    def reset_index(
        self,
        level: Sequence[Level] = ...,
        *,
        drop: Literal[True],
        name: Level = ...,
        inplace: Literal[False] = ...,
        allow_duplicates: bool = ...,
    ) -> Series[S1]: ...
    @overload
    def reset_index(
        self,
        level: Sequence[Level] = ...,
        *,
        drop: bool = ...,
        name: Level = ...,
        inplace: Literal[True],
        allow_duplicates: bool = ...,
    ) -> None: ...
    @overload
    def reset_index(
        self,
        level: Level | None = ...,
        *,
        drop: Literal[False] = ...,
        name: Level = ...,
        inplace: Literal[False] = ...,
        allow_duplicates: bool = ...,
    ) -> DataFrame: ...
    @overload
    def reset_index(
        self,
        level: Level | None = ...,
        *,
        drop: Literal[True],
        name: Level = ...,
        inplace: Literal[False] = ...,
        allow_duplicates: bool = ...,
    ) -> Series[S1]: ...
    @overload
    def reset_index(
        self,
        level: Level | None = ...,
        *,
        drop: bool = ...,
        name: Level = ...,
        inplace: Literal[True],
        allow_duplicates: bool = ...,
    ) -> None: ...
    @overload
    def to_string(
        self,
        buf: FilePath | WriteBuffer[str],
        na_rep: _str = ...,
        float_format: Callable[[float], str] = ...,
        header: _bool = ...,
        index: _bool = ...,
        length: _bool = ...,
        dtype: _bool = ...,
        name: _bool = ...,
        max_rows: int | None = ...,
        min_rows: int | None = ...,
    ) -> None: ...
    @overload
    def to_string(
        self,
        buf: None = ...,
        na_rep: _str = ...,
        float_format: Callable[[float], str] = ...,
        header: _bool = ...,
        index: _bool = ...,
        length: _bool = ...,
        dtype: _bool = ...,
        name: _bool = ...,
        max_rows: int | None = ...,
        min_rows: int | None = ...,
    ) -> _str: ...
    @overload
    def to_json(
        self,
        path_or_buf: FilePath | WriteBuffer[str],
        *,
        orient: Literal["records"],
        date_format: Literal["epoch", "iso"] | None = ...,
        double_precision: int = ...,
        force_ascii: _bool = ...,
        date_unit: TimeUnit = ...,
        default_handler: (
            Callable[[Any], _str | float | _bool | list | dict] | None
        ) = ...,
        lines: Literal[True],
        compression: CompressionOptions = ...,
        index: _bool = ...,
        indent: int | None = ...,
        mode: Literal["a"],
    ) -> None: ...
    @overload
    def to_json(
        self,
        path_or_buf: None = ...,
        *,
        orient: Literal["records"],
        date_format: Literal["epoch", "iso"] | None = ...,
        double_precision: int = ...,
        force_ascii: _bool = ...,
        date_unit: TimeUnit = ...,
        default_handler: (
            Callable[[Any], _str | float | _bool | list | dict] | None
        ) = ...,
        lines: Literal[True],
        compression: CompressionOptions = ...,
        index: _bool = ...,
        indent: int | None = ...,
        mode: Literal["a"],
    ) -> _str: ...
    @overload
    def to_json(
        self,
        path_or_buf: FilePath | WriteBuffer[str],
        orient: JsonSeriesOrient | None = ...,
        date_format: Literal["epoch", "iso"] | None = ...,
        double_precision: int = ...,
        force_ascii: _bool = ...,
        date_unit: TimeUnit = ...,
        default_handler: (
            Callable[[Any], _str | float | _bool | list | dict] | None
        ) = ...,
        lines: _bool = ...,
        compression: CompressionOptions = ...,
        index: _bool = ...,
        indent: int | None = ...,
        mode: Literal["w"] = ...,
    ) -> None: ...
    @overload
    def to_json(
        self,
        path_or_buf: None = ...,
        orient: JsonSeriesOrient | None = ...,
        date_format: Literal["epoch", "iso"] | None = ...,
        double_precision: int = ...,
        force_ascii: _bool = ...,
        date_unit: TimeUnit = ...,
        default_handler: (
            Callable[[Any], _str | float | _bool | list | dict] | None
        ) = ...,
        lines: _bool = ...,
        compression: CompressionOptions = ...,
        index: _bool = ...,
        indent: int | None = ...,
        mode: Literal["w"] = ...,
    ) -> _str: ...
    def to_xarray(self) -> xr.DataArray: ...
    def items(self) -> Iterable[tuple[Hashable, S1]]: ...
    def keys(self) -> list: ...
    @overload
    def to_dict(self, *, into: type[dict] = ...) -> dict[Any, S1]: ...
    @overload
    def to_dict(
        self, *, into: type[MutableMapping] | MutableMapping
    ) -> MutableMapping[Hashable, S1]: ...
    def to_frame(self, name: object | None = ...) -> DataFrame: ...
    @overload
    def groupby(
        self,
        by: Scalar,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Scalar]:
        """
Group Series using a mapper or by a Series of columns.

A groupby operation involves some combination of splitting the
object, applying a function, and combining the results. This can be
used to group large amounts of data and compute operations on these
groups.

Parameters
----------
by : mapping, function, label, pd.Grouper or list of such
    Used to determine the groups for the groupby.
    If ``by`` is a function, it's called on each value of the object's
    index. If a dict or Series is passed, the Series or dict VALUES
    will be used to determine the groups (the Series' values are first
    aligned; see ``.align()`` method). If a list or ndarray of length
    equal to the selected axis is passed (see the `groupby user guide
    <https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#splitting-an-object-into-groups>`_),
    the values are used as-is to determine the groups. A label or list
    of labels may be passed to group by the columns in ``self``.
    Notice that a tuple is interpreted as a (single) key.
axis : {0 or 'index', 1 or 'columns'}, default 0
    Split along rows (0) or columns (1). For `Series` this parameter
    is unused and defaults to 0.

    .. deprecated:: 2.1.0

        Will be removed and behave like axis=0 in a future version.
        For ``axis=1``, do ``frame.T.groupby(...)`` instead.

level : int, level name, or sequence of such, default None
    If the axis is a MultiIndex (hierarchical), group by a particular
    level or levels. Do not specify both ``by`` and ``level``.
as_index : bool, default True
    Return object with group labels as the
    index. Only relevant for DataFrame input. as_index=False is
    effectively "SQL-style" grouped output. This argument has no effect
    on filtrations (see the `filtrations in the user guide
    <https://pandas.pydata.org/docs/dev/user_guide/groupby.html#filtration>`_),
    such as ``head()``, ``tail()``, ``nth()`` and in transformations
    (see the `transformations in the user guide
    <https://pandas.pydata.org/docs/dev/user_guide/groupby.html#transformation>`_).
sort : bool, default True
    Sort group keys. Get better performance by turning this off.
    Note this does not influence the order of observations within each
    group. Groupby preserves the order of rows within each group. If False,
    the groups will appear in the same order as they did in the original DataFrame.
    This argument has no effect on filtrations (see the `filtrations in the user guide
    <https://pandas.pydata.org/docs/dev/user_guide/groupby.html#filtration>`_),
    such as ``head()``, ``tail()``, ``nth()`` and in transformations
    (see the `transformations in the user guide
    <https://pandas.pydata.org/docs/dev/user_guide/groupby.html#transformation>`_).

    .. versionchanged:: 2.0.0

        Specifying ``sort=False`` with an ordered categorical grouper will no
        longer sort the values.

group_keys : bool, default True
    When calling apply and the ``by`` argument produces a like-indexed
    (i.e. :ref:`a transform <groupby.transform>`) result, add group keys to
    index to identify pieces. By default group keys are not included
    when the result's index (and column) labels match the inputs, and
    are included otherwise.

    .. versionchanged:: 1.5.0

       Warns that ``group_keys`` will no longer be ignored when the
       result from ``apply`` is a like-indexed Series or DataFrame.
       Specify ``group_keys`` explicitly to include the group keys or
       not.

    .. versionchanged:: 2.0.0

       ``group_keys`` now defaults to ``True``.

observed : bool, default False
    This only applies if any of the groupers are Categoricals.
    If True: only show observed values for categorical groupers.
    If False: show all values for categorical groupers.

    .. deprecated:: 2.1.0

        The default value will change to True in a future version of pandas.

dropna : bool, default True
    If True, and if group keys contain NA values, NA values together
    with row/column will be dropped.
    If False, NA values will also be treated as the key in groups.

Returns
-------
pandas.api.typing.SeriesGroupBy
    Returns a groupby object that contains information about the groups.

See Also
--------
resample : Convenience method for frequency conversion and resampling
    of time series.

Notes
-----
See the `user guide
<https://pandas.pydata.org/pandas-docs/stable/groupby.html>`__ for more
detailed usage and examples, including splitting an object into groups,
iterating through groups, selecting a group, aggregation, and more.

Examples
--------
>>> ser = pd.Series([390., 350., 30., 20.],
...                 index=['Falcon', 'Falcon', 'Parrot', 'Parrot'],
...                 name="Max Speed")
>>> ser
Falcon    390.0
Falcon    350.0
Parrot     30.0
Parrot     20.0
Name: Max Speed, dtype: float64
>>> ser.groupby(["a", "b", "a", "b"]).mean()
a    210.0
b    185.0
Name: Max Speed, dtype: float64
>>> ser.groupby(level=0).mean()
Falcon    370.0
Parrot     25.0
Name: Max Speed, dtype: float64
>>> ser.groupby(ser > 100).mean()
Max Speed
False     25.0
True     370.0
Name: Max Speed, dtype: float64

**Grouping by Indexes**

We can groupby different levels of a hierarchical index
using the `level` parameter:

>>> arrays = [['Falcon', 'Falcon', 'Parrot', 'Parrot'],
...           ['Captive', 'Wild', 'Captive', 'Wild']]
>>> index = pd.MultiIndex.from_arrays(arrays, names=('Animal', 'Type'))
>>> ser = pd.Series([390., 350., 30., 20.], index=index, name="Max Speed")
>>> ser
Animal  Type
Falcon  Captive    390.0
        Wild       350.0
Parrot  Captive     30.0
        Wild        20.0
Name: Max Speed, dtype: float64
>>> ser.groupby(level=0).mean()
Animal
Falcon    370.0
Parrot     25.0
Name: Max Speed, dtype: float64
>>> ser.groupby(level="Type").mean()
Type
Captive    210.0
Wild       185.0
Name: Max Speed, dtype: float64

We can also choose to include `NA` in group keys or not by defining
`dropna` parameter, the default setting is `True`.

>>> ser = pd.Series([1, 2, 3, 3], index=["a", 'a', 'b', np.nan])
>>> ser.groupby(level=0).sum()
a    3
b    3
dtype: int64

>>> ser.groupby(level=0, dropna=False).sum()
a    3
b    3
NaN  3
dtype: int64

>>> arrays = ['Falcon', 'Falcon', 'Parrot', 'Parrot']
>>> ser = pd.Series([390., 350., 30., 20.], index=arrays, name="Max Speed")
>>> ser.groupby(["a", "b", "a", np.nan]).mean()
a    210.0
b    350.0
Name: Max Speed, dtype: float64

>>> ser.groupby(["a", "b", "a", np.nan], dropna=False).mean()
a    210.0
b    350.0
NaN   20.0
Name: Max Speed, dtype: float64
        """
        pass
    @overload
    def groupby(
        self,
        by: DatetimeIndex,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Timestamp]: ...
    @overload
    def groupby(
        self,
        by: TimedeltaIndex,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Timedelta]: ...
    @overload
    def groupby(
        self,
        by: PeriodIndex,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Period]: ...
    @overload
    def groupby(
        self,
        by: IntervalIndex[IntervalT],
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, IntervalT]: ...
    @overload
    def groupby(
        self,
        by: MultiIndex | GroupByObjectNonScalar,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, tuple]: ...
    @overload
    def groupby(
        self,
        by: None,
        axis: AxisIndex,
        level: IndexLabel,  # level is required when by=None (passed as positional)
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Scalar]: ...
    @overload
    def groupby(
        self,
        by: None = ...,
        axis: AxisIndex = ...,
        *,
        level: IndexLabel,  # level is required when by=None (passed as keyword)
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Scalar]: ...
    @overload
    def groupby(
        self,
        by: Series[SeriesByT],
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, SeriesByT]: ...
    @overload
    def groupby(
        self,
        by: CategoricalIndex | Index | Series,
        axis: AxisIndex = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> SeriesGroupBy[S1, Any]: ...
    # need the ignore because None is Hashable
    @overload
    def count(self, level: None = ...) -> int: ...  # type: ignore[overload-overlap]
    @overload
    def count(self, level: Hashable) -> Series[S1]: ...
    def mode(self, dropna=...) -> Series[S1]: ...
    def unique(self) -> np.ndarray: ...
    @overload
    def drop_duplicates(
        self, *, keep: NaPosition | Literal[False] = ..., inplace: Literal[False] = ...
    ) -> Series[S1]: ...
    @overload
    def drop_duplicates(
        self, *, keep: NaPosition | Literal[False] = ..., inplace: Literal[True]
    ) -> None: ...
    @overload
    def drop_duplicates(
        self, *, keep: NaPosition | Literal[False] = ..., inplace: bool = ...
    ) -> Series[S1] | None: ...
    def duplicated(self, keep: NaPosition | Literal[False] = ...) -> Series[_bool]: ...
    def idxmax(
        self, axis: AxisIndex = ..., skipna: _bool = ..., *args, **kwargs
    ) -> int | _str: ...
    def idxmin(
        self, axis: AxisIndex = ..., skipna: _bool = ..., *args, **kwargs
    ) -> int | _str: ...
    def round(self, decimals: int = ..., *args, **kwargs) -> Series[S1]: ...
    @overload
    def quantile(
        self,
        q: float = ...,
        interpolation: QuantileInterpolation = ...,
    ) -> float: ...
    @overload
    def quantile(
        self,
        q: _ListLike,
        interpolation: QuantileInterpolation = ...,
    ) -> Series[S1]: ...
    def corr(
        self,
        other: Series[S1],
        method: Literal["pearson", "kendall", "spearman"] = ...,
        min_periods: int = ...,
    ) -> float: ...
    def cov(
        self, other: Series[S1], min_periods: int | None = ..., ddof: int = ...
    ) -> float: ...
    @overload
    def diff(self: Series[_bool], periods: int = ...) -> Series[type[object]]: ...  # type: ignore[overload-overlap]
    @overload
    def diff(self: Series[complex], periods: int = ...) -> Series[complex]: ...  # type: ignore[overload-overlap]
    @overload
    def diff(self: Series[bytes], periods: int = ...) -> Never:
        """
First discrete difference of element.

Calculates the difference of a Series element compared with another
element in the Series (default is element in previous row).

Parameters
----------
periods : int, default 1
    Periods to shift for calculating difference, accepts negative
    values.

Returns
-------
Series
    First differences of the Series.

See Also
--------
Series.pct_change: Percent change over given number of periods.
Series.shift: Shift index by desired number of periods with an
    optional time freq.
DataFrame.diff: First discrete difference of object.

Notes
-----
For boolean dtypes, this uses :meth:`operator.xor` rather than
:meth:`operator.sub`.
The result is calculated according to current dtype in Series,
however dtype of the result is always float64.

Examples
--------

Difference with previous row

>>> s = pd.Series([1, 1, 2, 3, 5, 8])
>>> s.diff()
0    NaN
1    0.0
2    1.0
3    1.0
4    2.0
5    3.0
dtype: float64

Difference with 3rd previous row

>>> s.diff(periods=3)
0    NaN
1    NaN
2    NaN
3    2.0
4    4.0
5    6.0
dtype: float64

Difference with following row

>>> s.diff(periods=-1)
0    0.0
1   -1.0
2   -1.0
3   -2.0
4   -3.0
5    NaN
dtype: float64

Overflow in input dtype

>>> s = pd.Series([1, 0], dtype=np.uint8)
>>> s.diff()
0      NaN
1    255.0
dtype: float64
        """
        pass
    @overload
    def diff(self: Series[type], periods: int = ...) -> Never: ...
    @overload
    def diff(self: Series[str], periods: int = ...) -> Never: ...
    @overload
    def diff(self, periods: int = ...) -> Series[float]: ...
    def autocorr(self, lag: int = ...) -> float: ...
    @overload
    def dot(self, other: Series[S1]) -> Scalar: ...
    @overload
    def dot(self, other: DataFrame) -> Series[S1]: ...
    @overload
    def dot(
        self, other: ArrayLike | dict[_str, np.ndarray] | Sequence[S1] | Index[S1]
    ) -> np.ndarray: ...
    def __matmul__(self, other): ...
    def __rmatmul__(self, other): ...
    @overload
    def searchsorted(  # type: ignore[overload-overlap]
        self,
        value: _ListLike,
        side: Literal["left", "right"] = ...,
        sorter: _ListLike | None = ...,
    ) -> list[int]: ...
    @overload
    def searchsorted(
        self,
        value: Scalar,
        side: Literal["left", "right"] = ...,
        sorter: _ListLike | None = ...,
    ) -> int: ...
    @overload
    def compare(
        self,
        other: Series,
        align_axis: AxisIndex,
        keep_shape: bool = ...,
        keep_equal: bool = ...,
    ) -> Series:
        """
Compare to another Series and show the differences.

Parameters
----------
other : Series
    Object to compare with.

align_axis : {0 or 'index', 1 or 'columns'}, default 1
    Determine which axis to align the comparison on.

    * 0, or 'index' : Resulting differences are stacked vertically
        with rows drawn alternately from self and other.
    * 1, or 'columns' : Resulting differences are aligned horizontally
        with columns drawn alternately from self and other.

keep_shape : bool, default False
    If true, all rows and columns are kept.
    Otherwise, only the ones with different values are kept.

keep_equal : bool, default False
    If true, the result keeps values that are equal.
    Otherwise, equal values are shown as NaNs.

result_names : tuple, default ('self', 'other')
    Set the dataframes names in the comparison.

    .. versionadded:: 1.5.0

Returns
-------
Series or DataFrame
    If axis is 0 or 'index' the result will be a Series.
    The resulting index will be a MultiIndex with 'self' and 'other'
    stacked alternately at the inner level.

    If axis is 1 or 'columns' the result will be a DataFrame.
    It will have two columns namely 'self' and 'other'.

See Also
--------
DataFrame.compare : Compare with another DataFrame and show differences.

Notes
-----
Matching NaNs will not appear as a difference.

Examples
--------
>>> s1 = pd.Series(["a", "b", "c", "d", "e"])
>>> s2 = pd.Series(["a", "a", "c", "b", "e"])

Align the differences on columns

>>> s1.compare(s2)
  self other
1    b     a
3    d     b

Stack the differences on indices

>>> s1.compare(s2, align_axis=0)
1  self     b
   other    a
3  self     d
   other    b
dtype: object

Keep all original rows

>>> s1.compare(s2, keep_shape=True)
  self other
0  NaN   NaN
1    b     a
2  NaN   NaN
3    d     b
4  NaN   NaN

Keep all original rows and also all original values

>>> s1.compare(s2, keep_shape=True, keep_equal=True)
  self other
0    a     a
1    b     a
2    c     c
3    d     b
4    e     e
        """
        pass
    @overload
    def compare(
        self,
        other: Series,
        align_axis: AxisColumn = ...,
        keep_shape: bool = ...,
        keep_equal: bool = ...,
    ) -> DataFrame: ...
    def combine(
        self, other: Series[S1], func: Callable, fill_value: Scalar | None = ...
    ) -> Series[S1]: ...
    def combine_first(self, other: Series[S1]) -> Series[S1]: ...
    def update(self, other: Series[S1] | Sequence[S1] | Mapping[int, S1]) -> None: ...
    @overload
    def sort_values(
        self,
        *,
        axis: Axis = ...,
        ascending: _bool | Sequence[_bool] = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        ignore_index: _bool = ...,
        inplace: Literal[True],
        key: Callable | None = ...,
    ) -> None: ...
    @overload
    def sort_values(
        self,
        *,
        axis: Axis = ...,
        ascending: _bool | Sequence[_bool] = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        ignore_index: _bool = ...,
        inplace: Literal[False] = ...,
        key: Callable | None = ...,
    ) -> Series[S1]: ...
    @overload
    def sort_values(
        self,
        *,
        axis: Axis = ...,
        ascending: _bool | Sequence[_bool] = ...,
        inplace: _bool | None = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        ignore_index: _bool = ...,
        key: Callable | None = ...,
    ) -> Series[S1] | None: ...
    @overload
    def sort_index(
        self,
        *,
        axis: Axis = ...,
        level: Level | None = ...,
        ascending: _bool | Sequence[_bool] = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        sort_remaining: _bool = ...,
        ignore_index: _bool = ...,
        inplace: Literal[True],
        key: Callable | None = ...,
    ) -> None: ...
    @overload
    def sort_index(
        self,
        *,
        axis: Axis = ...,
        level: Level | list[int] | list[_str] | None = ...,
        ascending: _bool | Sequence[_bool] = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        sort_remaining: _bool = ...,
        ignore_index: _bool = ...,
        inplace: Literal[False] = ...,
        key: Callable | None = ...,
    ) -> Self: ...
    @overload
    def sort_index(
        self,
        *,
        axis: Axis = ...,
        level: Level | list[int] | list[_str] | None = ...,
        ascending: _bool | Sequence[_bool] = ...,
        inplace: _bool | None = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        sort_remaining: _bool = ...,
        ignore_index: _bool = ...,
        key: Callable | None = ...,
    ) -> Series | None: ...
    def argsort(
        self,
        axis: AxisIndex = ...,
        kind: SortKind = ...,
        order: None = ...,
    ) -> Series[int]: ...
    def nlargest(
        self, n: int = ..., keep: NaPosition | Literal["all"] = ...
    ) -> Series[S1]: ...
    def nsmallest(
        self, n: int = ..., keep: NaPosition | Literal["all"] = ...
    ) -> Series[S1]: ...
    def swaplevel(
        self, i: Level = ..., j: Level = ..., copy: _bool = ...
    ) -> Series[S1]:
        """
Swap levels i and j in a :class:`MultiIndex`.

Default is to swap the two innermost levels of the index.

Parameters
----------
i, j : int or str
    Levels of the indices to be swapped. Can pass level name as string.
copy : bool, default True
            Whether to copy underlying data.

            .. note::
                The `copy` keyword will change behavior in pandas 3.0.
                `Copy-on-Write
                <https://pandas.pydata.org/docs/dev/user_guide/copy_on_write.html>`__
                will be enabled by default, which means that all methods with a
                `copy` keyword will use a lazy copy mechanism to defer the copy and
                ignore the `copy` keyword. The `copy` keyword will be removed in a
                future version of pandas.

                You can already get the future behavior and improvements through
                enabling copy on write ``pd.options.mode.copy_on_write = True``

Returns
-------
Series
    Series with levels swapped in MultiIndex.

Examples
--------
>>> s = pd.Series(
...     ["A", "B", "A", "C"],
...     index=[
...         ["Final exam", "Final exam", "Coursework", "Coursework"],
...         ["History", "Geography", "History", "Geography"],
...         ["January", "February", "March", "April"],
...     ],
... )
>>> s
Final exam  History     January      A
            Geography   February     B
Coursework  History     March        A
            Geography   April        C
dtype: object

In the following example, we will swap the levels of the indices.
Here, we will swap the levels column-wise, but levels can be swapped row-wise
in a similar manner. Note that column-wise is the default behaviour.
By not supplying any arguments for i and j, we swap the last and second to
last indices.

>>> s.swaplevel()
Final exam  January     History         A
            February    Geography       B
Coursework  March       History         A
            April       Geography       C
dtype: object

By supplying one argument, we can choose which index to swap the last
index with. We can for example swap the first index with the last one as
follows.

>>> s.swaplevel(0)
January     History     Final exam      A
February    Geography   Final exam      B
March       History     Coursework      A
April       Geography   Coursework      C
dtype: object

We can also define explicitly which indices we want to swap by supplying values
for both i and j. Here, we for example swap the first and second indices.

>>> s.swaplevel(0, 1)
History     Final exam  January         A
Geography   Final exam  February        B
History     Coursework  March           A
Geography   Coursework  April           C
dtype: object
        """
        pass
    def reorder_levels(self, order: list) -> Series[S1]: ...
    def explode(self) -> Series[S1]: ...
    def unstack(
        self,
        level: Level = ...,
        fill_value: int | _str | dict | None = ...,
    ) -> DataFrame: ...
    @overload
    def map(
        self,
        arg: Callable[[S1], S2 | NAType] | Mapping[S1, S2] | Series[S2],
        na_action: Literal["ignore"] = ...,
    ) -> Series[S2]: ...
    @overload
    def map(
        self,
        arg: Callable[[S1 | NAType], S2 | NAType] | Mapping[S1, S2] | Series[S2],
        na_action: None = ...,
    ) -> Series[S2]: ...
    @overload
    def aggregate(  # type: ignore[overload-overlap]
        self: Series[int],
        func: Literal["mean"],
        axis: AxisIndex = ...,
        *args,
        **kwargs,
    ) -> float:
        """
Aggregate using one or more operations over the specified axis.

Parameters
----------
func : function, str, list or dict
    Function to use for aggregating the data. If a function, must either
    work when passed a Series or when passed to Series.apply.

    Accepted combinations are:

    - function
    - string function name
    - list of functions and/or function names, e.g. ``[np.sum, 'mean']``
    - dict of axis labels -> functions, function names or list of such.
axis : {0 or 'index'}
        Unused. Parameter needed for compatibility with DataFrame.
*args
    Positional arguments to pass to `func`.
**kwargs
    Keyword arguments to pass to `func`.

Returns
-------
scalar, Series or DataFrame

    The return can be:

    * scalar : when Series.agg is called with single function
    * Series : when DataFrame.agg is called with a single function
    * DataFrame : when DataFrame.agg is called with several functions

See Also
--------
Series.apply : Invoke function on a Series.
Series.transform : Transform function producing a Series with like indexes.

Notes
-----
The aggregation operations are always performed over an axis, either the
index (default) or the column axis. This behavior is different from
`numpy` aggregation functions (`mean`, `median`, `prod`, `sum`, `std`,
`var`), where the default is to compute the aggregation of the flattened
array, e.g., ``numpy.mean(arr_2d)`` as opposed to
``numpy.mean(arr_2d, axis=0)``.

`agg` is an alias for `aggregate`. Use the alias.

Functions that mutate the passed object can produce unexpected
behavior or errors and are not supported. See :ref:`gotchas.udf-mutation`
for more details.

A passed user-defined-function will be passed a Series for evaluation.

Examples
--------
>>> s = pd.Series([1, 2, 3, 4])
>>> s
0    1
1    2
2    3
3    4
dtype: int64

>>> s.agg('min')
1

>>> s.agg(['min', 'max'])
min   1
max   4
dtype: int64
        """
        pass
    @overload
    def aggregate(
        self,
        func: AggFuncTypeBase,
        axis: AxisIndex = ...,
        *args,
        **kwargs,
    ) -> S1: ...
    @overload
    def aggregate(
        self,
        func: AggFuncTypeSeriesToFrame = ...,
        axis: AxisIndex = ...,
        *args,
        **kwargs,
    ) -> Series: ...
    agg = aggregate
    @overload
    def transform(
        self,
        func: AggFuncTypeBase,
        axis: AxisIndex = ...,
        *args,
        **kwargs,
    ) -> Series[S1]:
        """
Call ``func`` on self producing a Series with the same axis shape as self.

Parameters
----------
func : function, str, list-like or dict-like
    Function to use for transforming the data. If a function, must either
    work when passed a Series or when passed to Series.apply. If func
    is both list-like and dict-like, dict-like behavior takes precedence.

    Accepted combinations are:

    - function
    - string function name
    - list-like of functions and/or function names, e.g. ``[np.exp, 'sqrt']``
    - dict-like of axis labels -> functions, function names or list-like of such.
axis : {0 or 'index'}
        Unused. Parameter needed for compatibility with DataFrame.
*args
    Positional arguments to pass to `func`.
**kwargs
    Keyword arguments to pass to `func`.

Returns
-------
Series
    A Series that must have the same length as self.

Raises
------
ValueError : If the returned Series has a different length than self.

See Also
--------
Series.agg : Only perform aggregating type operations.
Series.apply : Invoke function on a Series.

Notes
-----
Functions that mutate the passed object can produce unexpected
behavior or errors and are not supported. See :ref:`gotchas.udf-mutation`
for more details.

Examples
--------
>>> df = pd.DataFrame({'A': range(3), 'B': range(1, 4)})
>>> df
   A  B
0  0  1
1  1  2
2  2  3
>>> df.transform(lambda x: x + 1)
   A  B
0  1  2
1  2  3
2  3  4

Even though the resulting Series must have the same length as the
input Series, it is possible to provide several input functions:

>>> s = pd.Series(range(3))
>>> s
0    0
1    1
2    2
dtype: int64
>>> s.transform([np.sqrt, np.exp])
       sqrt        exp
0  0.000000   1.000000
1  1.000000   2.718282
2  1.414214   7.389056

You can call transform on a GroupBy object:

>>> df = pd.DataFrame({
...     "Date": [
...         "2015-05-08", "2015-05-07", "2015-05-06", "2015-05-05",
...         "2015-05-08", "2015-05-07", "2015-05-06", "2015-05-05"],
...     "Data": [5, 8, 6, 1, 50, 100, 60, 120],
... })
>>> df
         Date  Data
0  2015-05-08     5
1  2015-05-07     8
2  2015-05-06     6
3  2015-05-05     1
4  2015-05-08    50
5  2015-05-07   100
6  2015-05-06    60
7  2015-05-05   120
>>> df.groupby('Date')['Data'].transform('sum')
0     55
1    108
2     66
3    121
4     55
5    108
6     66
7    121
Name: Data, dtype: int64

>>> df = pd.DataFrame({
...     "c": [1, 1, 1, 2, 2, 2, 2],
...     "type": ["m", "n", "o", "m", "m", "n", "n"]
... })
>>> df
   c type
0  1    m
1  1    n
2  1    o
3  2    m
4  2    m
5  2    n
6  2    n
>>> df['size'] = df.groupby('c')['type'].transform(len)
>>> df
   c type size
0  1    m    3
1  1    n    3
2  1    o    3
3  2    m    4
4  2    m    4
5  2    n    4
6  2    n    4
        """
        pass
    @overload
    def transform(
        self,
        func: list[AggFuncTypeBase] | AggFuncTypeDictFrame,
        axis: AxisIndex = ...,
        *args,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def apply(
        self,
        func: Callable[
            ..., Scalar | Sequence | set | Mapping | NAType | frozenset | None
        ],
        convertDType: _bool = ...,
        args: tuple = ...,
        **kwds,
    ) -> Series: ...
    @overload
    def apply(
        self,
        func: Callable[..., Series],
        convertDType: _bool = ...,
        args: tuple = ...,
        **kwds,
    ) -> DataFrame: ...
    def align(
        self,
        other: DataFrame | Series,
        join: JoinHow = ...,
        axis: Axis | None = ...,
        level: Level | None = ...,
        copy: _bool = ...,
        fill_value=...,
        method: FillnaOptions | None = ...,
        limit: int | None = ...,
        fill_axis: AxisIndex = ...,
        broadcast_axis: AxisIndex | None = ...,
    ) -> tuple[Series, Series]: ...
    @overload
    def rename(
        self,
        index: Renamer | Hashable | None = ...,
        *,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: Literal[True],
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def rename(
        self,
        index: Renamer | None = ...,
        *,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: Literal[False] = ...,
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> Self: ...
    @overload
    def rename(
        self,
        index: Hashable | None = ...,
        *,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: Literal[False] = ...,
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> Self: ...
    @overload
    def rename(
        self,
        index: Renamer | Hashable | None = ...,
        *,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: bool = ...,
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> Series | None: ...
    def reindex_like(
        self,
        other: Series[S1],
        method: _str | FillnaOptions | Literal["nearest"] | None = ...,
        copy: _bool = ...,
        limit: int | None = ...,
        tolerance: float | None = ...,
    ) -> Self: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series[S1] | DataFrame | None = ...,
        *,
        axis: AxisIndex = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series[S1] | DataFrame | None = ...,
        *,
        axis: AxisIndex = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
        inplace: Literal[False] = ...,
    ) -> Series[S1]: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series[S1] | DataFrame | None = ...,
        *,
        axis: AxisIndex = ...,
        inplace: _bool = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> Series[S1] | None: ...
    @overload
    def replace(
        self,
        to_replace: _str | list | dict | Series[S1] | float | None = ...,
        value: Scalar | NAType | dict | list | _str | None = ...,
        *,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
    ) -> Series[S1]: ...
    @overload
    def replace(
        self,
        to_replace: _str | list | dict | Series[S1] | float | None = ...,
        value: Scalar | NAType | dict | list | _str | None = ...,
        *,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def replace(
        self,
        to_replace: _str | list | dict | Series[S1] | float | None = ...,
        value: Scalar | NAType | dict | list | _str | None = ...,
        *,
        inplace: _bool = ...,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
    ) -> Series[S1] | None: ...
    def shift(
        self,
        periods: int = ...,
        freq=...,
        axis: AxisIndex = ...,
        fill_value: object | None = ...,
    ) -> Series[S1]: ...
    def memory_usage(self, index: _bool = ..., deep: _bool = ...) -> int: ...
    def isin(self, values: Iterable | Series[S1] | dict) -> Series[_bool]: ...
    def between(
        self,
        left: Scalar | ListLikeU,
        right: Scalar | ListLikeU,
        inclusive: Literal["both", "neither", "left", "right"] = ...,
    ) -> Series[_bool]: ...
    def isna(self) -> Series[_bool]: ...
    def isnull(self) -> Series[_bool]: ...
    def notna(self) -> Series[_bool]: ...
    def notnull(self) -> Series[_bool]: ...
    @overload
    def dropna(
        self,
        *,
        axis: AxisIndex = ...,
        inplace: Literal[True],
        how: Literal["any", "all"] | None = ...,
    ) -> None: ...
    @overload
    def dropna(
        self,
        *,
        axis: AxisIndex = ...,
        inplace: Literal[False] = ...,
        how: Literal["any", "all"] | None = ...,
    ) -> Series[S1]: ...
    @overload
    def dropna(
        self,
        *,
        axis: AxisIndex = ...,
        inplace: _bool = ...,
        how: Literal["any", "all"] | None = ...,
    ) -> Series[S1] | None: ...
    def to_timestamp(
        self,
        freq=...,
        how: TimestampConvention = ...,
        copy: _bool = ...,
    ) -> Series[S1]: ...
    def to_period(self, freq: _str | None = ..., copy: _bool = ...) -> DataFrame: ...
    @property
    def str(self) -> StringMethods[Series, DataFrame, Series[bool]]: ...
    @property
    def dt(self) -> CombinedDatetimelikeProperties: ...
    @property
    def plot(self) -> PlotAccessor: ...
    sparse = ...
    def hist(
        self,
        by: object | None = ...,
        ax: PlotAxes | None = ...,
        grid: _bool = ...,
        xlabelsize: float | _str | None = ...,
        xrot: float | None = ...,
        ylabelsize: float | _str | None = ...,
        yrot: float | None = ...,
        figsize: tuple[float, float] | None = ...,
        bins: int | Sequence = ...,
        backend: _str | None = ...,
        **kwargs,
    ) -> SubplotBase: ...
    def swapaxes(
        self, axis1: AxisIndex, axis2: AxisIndex, copy: _bool = ...
    ) -> Series[S1]: ...
    def droplevel(self, level: Level | list[Level], axis: AxisIndex = ...) -> Self: ...
    def pop(self, item: Hashable) -> S1: ...
    def squeeze(self, axis: AxisIndex | None = ...) -> Scalar: ...
    def __abs__(self) -> Series[S1]: ...
    def add_prefix(self, prefix: _str, axis: AxisIndex | None = ...) -> Series[S1]: ...
    def add_suffix(self, suffix: _str, axis: AxisIndex | None = ...) -> Series[S1]: ...
    def reindex(
        self,
        index: Axes | None = ...,
        method: FillnaOptions | Literal["nearest"] | None = ...,
        copy: bool = ...,
        level: int | _str = ...,
        fill_value: Scalar | None = ...,
        limit: int | None = ...,
        tolerance: float | None = ...,
    ) -> Series[S1]:
        """
Conform Series to new index with optional filling logic.

Places NA/NaN in locations having no value in the previous index. A new object
is produced unless the new index is equivalent to the current one and
``copy=False``.

Parameters
----------

index : array-like, optional
    New labels for the index. Preferably an Index object to avoid
    duplicating data.
axis : int or str, optional
    Unused.
method : {None, 'backfill'/'bfill', 'pad'/'ffill', 'nearest'}
    Method to use for filling holes in reindexed DataFrame.
    Please note: this is only applicable to DataFrames/Series with a
    monotonically increasing/decreasing index.

    * None (default): don't fill gaps
    * pad / ffill: Propagate last valid observation forward to next
      valid.
    * backfill / bfill: Use next valid observation to fill gap.
    * nearest: Use nearest valid observations to fill gap.

copy : bool, default True
    Return a new object, even if the passed indexes are the same.

    .. note::
        The `copy` keyword will change behavior in pandas 3.0.
        `Copy-on-Write
        <https://pandas.pydata.org/docs/dev/user_guide/copy_on_write.html>`__
        will be enabled by default, which means that all methods with a
        `copy` keyword will use a lazy copy mechanism to defer the copy and
        ignore the `copy` keyword. The `copy` keyword will be removed in a
        future version of pandas.

        You can already get the future behavior and improvements through
        enabling copy on write ``pd.options.mode.copy_on_write = True``
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : scalar, default np.nan
    Value to use for missing values. Defaults to NaN, but can be any
    "compatible" value.
limit : int, default None
    Maximum number of consecutive elements to forward or backward fill.
tolerance : optional
    Maximum distance between original and new labels for inexact
    matches. The values of the index at the matching locations most
    satisfy the equation ``abs(index[indexer] - target) <= tolerance``.

    Tolerance may be a scalar value, which applies the same tolerance
    to all values, or list-like, which applies variable tolerance per
    element. List-like includes list, tuple, array, Series, and must be
    the same size as the index and its dtype must exactly match the
    index's type.

Returns
-------
Series with changed index.

See Also
--------
DataFrame.set_index : Set row labels.
DataFrame.reset_index : Remove row labels or move them to new columns.
DataFrame.reindex_like : Change to same indices as other DataFrame.

Examples
--------
``DataFrame.reindex`` supports two calling conventions

* ``(index=index_labels, columns=column_labels, ...)``
* ``(labels, axis={'index', 'columns'}, ...)``

We *highly* recommend using keyword arguments to clarify your
intent.

Create a dataframe with some fictional data.

>>> index = ['Firefox', 'Chrome', 'Safari', 'IE10', 'Konqueror']
>>> df = pd.DataFrame({'http_status': [200, 200, 404, 404, 301],
...                   'response_time': [0.04, 0.02, 0.07, 0.08, 1.0]},
...                   index=index)
>>> df
           http_status  response_time
Firefox            200           0.04
Chrome             200           0.02
Safari             404           0.07
IE10               404           0.08
Konqueror          301           1.00

Create a new index and reindex the dataframe. By default
values in the new index that do not have corresponding
records in the dataframe are assigned ``NaN``.

>>> new_index = ['Safari', 'Iceweasel', 'Comodo Dragon', 'IE10',
...              'Chrome']
>>> df.reindex(new_index)
               http_status  response_time
Safari               404.0           0.07
Iceweasel              NaN            NaN
Comodo Dragon          NaN            NaN
IE10                 404.0           0.08
Chrome               200.0           0.02

We can fill in the missing values by passing a value to
the keyword ``fill_value``. Because the index is not monotonically
increasing or decreasing, we cannot use arguments to the keyword
``method`` to fill the ``NaN`` values.

>>> df.reindex(new_index, fill_value=0)
               http_status  response_time
Safari                 404           0.07
Iceweasel                0           0.00
Comodo Dragon            0           0.00
IE10                   404           0.08
Chrome                 200           0.02

>>> df.reindex(new_index, fill_value='missing')
              http_status response_time
Safari                404          0.07
Iceweasel         missing       missing
Comodo Dragon     missing       missing
IE10                  404          0.08
Chrome                200          0.02

We can also reindex the columns.

>>> df.reindex(columns=['http_status', 'user_agent'])
           http_status  user_agent
Firefox            200         NaN
Chrome             200         NaN
Safari             404         NaN
IE10               404         NaN
Konqueror          301         NaN

Or we can use "axis-style" keyword arguments

>>> df.reindex(['http_status', 'user_agent'], axis="columns")
           http_status  user_agent
Firefox            200         NaN
Chrome             200         NaN
Safari             404         NaN
IE10               404         NaN
Konqueror          301         NaN

To further illustrate the filling functionality in
``reindex``, we will create a dataframe with a
monotonically increasing index (for example, a sequence
of dates).

>>> date_index = pd.date_range('1/1/2010', periods=6, freq='D')
>>> df2 = pd.DataFrame({"prices": [100, 101, np.nan, 100, 89, 88]},
...                    index=date_index)
>>> df2
            prices
2010-01-01   100.0
2010-01-02   101.0
2010-01-03     NaN
2010-01-04   100.0
2010-01-05    89.0
2010-01-06    88.0

Suppose we decide to expand the dataframe to cover a wider
date range.

>>> date_index2 = pd.date_range('12/29/2009', periods=10, freq='D')
>>> df2.reindex(date_index2)
            prices
2009-12-29     NaN
2009-12-30     NaN
2009-12-31     NaN
2010-01-01   100.0
2010-01-02   101.0
2010-01-03     NaN
2010-01-04   100.0
2010-01-05    89.0
2010-01-06    88.0
2010-01-07     NaN

The index entries that did not have a value in the original data frame
(for example, '2009-12-29') are by default filled with ``NaN``.
If desired, we can fill in the missing values using one of several
options.

For example, to back-propagate the last valid value to fill the ``NaN``
values, pass ``bfill`` as an argument to the ``method`` keyword.

>>> df2.reindex(date_index2, method='bfill')
            prices
2009-12-29   100.0
2009-12-30   100.0
2009-12-31   100.0
2010-01-01   100.0
2010-01-02   101.0
2010-01-03     NaN
2010-01-04   100.0
2010-01-05    89.0
2010-01-06    88.0
2010-01-07     NaN

Please note that the ``NaN`` value present in the original dataframe
(at index value 2010-01-03) will not be filled by any of the
value propagation schemes. This is because filling while reindexing
does not look at dataframe values, but only compares the original and
desired indexes. If you do want to fill in the ``NaN`` values present
in the original dataframe, use the ``fillna()`` method.

See the :ref:`user guide <basics.reindexing>` for more.
        """
        pass
    def filter(
        self,
        items: _ListLike | None = ...,
        like: _str | None = ...,
        regex: _str | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]: ...
    def head(self, n: int = ...) -> Series[S1]: ...
    def tail(self, n: int = ...) -> Series[S1]: ...
    def sample(
        self,
        n: int | None = ...,
        frac: float | None = ...,
        replace: _bool = ...,
        weights: _str | _ListLike | np.ndarray | None = ...,
        random_state: RandomState | None = ...,
        axis: AxisIndex | None = ...,
        ignore_index: _bool = ...,
    ) -> Series[S1]: ...
    @overload
    def astype(  # type: ignore[overload-overlap]
        self,
        dtype: BooleanDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[bool]: ...
    @overload
    def astype(
        self,
        dtype: IntDtypeArg | UIntDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[int]: ...
    @overload
    def astype(
        self,
        dtype: StrDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[_str]: ...
    @overload
    def astype(
        self,
        dtype: BytesDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[bytes]: ...
    @overload
    def astype(
        self,
        dtype: FloatDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[float]: ...
    @overload
    def astype(
        self,
        dtype: ComplexDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[complex]: ...
    @overload
    def astype(
        self,
        dtype: TimedeltaDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> TimedeltaSeries: ...
    @overload
    def astype(
        self,
        dtype: TimestampDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> TimestampSeries: ...
    @overload
    def astype(
        self,
        dtype: CategoryDtypeArg,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[CategoricalDtype]: ...
    @overload
    def astype(
        self,
        dtype: ObjectDtypeArg | VoidDtypeArg | ExtensionDtype | DtypeObj,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Series[Any]: ...
    def copy(self, deep: _bool = ...) -> Series[S1]: ...
    def infer_objects(self) -> Series[S1]: ...
    @overload
    def ffill(
        self,
        *,
        axis: AxisIndex | None = ...,
        inplace: Literal[True],
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> None: ...
    @overload
    def ffill(
        self,
        *,
        axis: AxisIndex | None = ...,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> Series[S1]: ...
    @overload
    def bfill(
        self,
        *,
        axis: AxisIndex | None = ...,
        inplace: Literal[True],
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> None: ...
    @overload
    def bfill(
        self,
        *,
        axis: AxisIndex | None = ...,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> Series[S1]: ...
    @overload
    def bfill(
        self,
        *,
        value: S1 | dict | Series[S1] | DataFrame,
        axis: AxisIndex = ...,
        inplace: _bool = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> Series[S1] | None: ...
    def interpolate(
        self,
        method: InterpolateOptions = ...,
        *,
        axis: AxisIndex | None = ...,
        limit: int | None = ...,
        inplace: _bool = ...,
        limit_direction: Literal["forward", "backward", "both"] | None = ...,
        limit_area: Literal["inside", "outside"] | None = ...,
        downcast: Literal["infer"] | None = ...,
        **kwargs,
    ) -> Series[S1]: ...
    def asof(
        self,
        where: Scalar | Sequence[Scalar],
        subset: _str | Sequence[_str] | None = ...,
    ) -> Scalar | Series[S1]: ...
    def clip(
        self,
        lower: AnyArrayLike | float | None = ...,
        upper: AnyArrayLike | float | None = ...,
        *,
        axis: AxisIndex | None = ...,
        inplace: _bool = ...,
        **kwargs,
    ) -> Series[S1]: ...
    def asfreq(
        self,
        freq,
        method: FillnaOptions | None = ...,
        how: Literal["start", "end"] | None = ...,
        normalize: _bool = ...,
        fill_value: Scalar | None = ...,
    ) -> Series[S1]: ...
    def at_time(
        self,
        time: _str | time,
        asof: _bool = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]: ...
    def between_time(
        self,
        start_time: _str | time,
        end_time: _str | time,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]: ...
    def first(self, offset) -> Series[S1]: ...
    def last(self, offset) -> Series[S1]: ...
    def rank(
        self,
        axis: AxisIndex = ...,
        method: Literal["average", "min", "max", "first", "dense"] = ...,
        numeric_only: _bool = ...,
        na_option: Literal["keep", "top", "bottom"] = ...,
        ascending: _bool = ...,
        pct: _bool = ...,
    ) -> Series[float]: ...
    def where(
        self,
        cond: (
            Series[S1]
            | Series[_bool]
            | np.ndarray
            | Callable[[Series[S1]], Series[bool]]
            | Callable[[S1], bool]
        ),
        other=...,
        *,
        inplace: _bool = ...,
        axis: AxisIndex | None = ...,
        level: Level | None = ...,
    ) -> Series[S1]: ...
    def mask(
        self,
        cond: (
            Series[S1]
            | Series[_bool]
            | np.ndarray
            | Callable[[Series[S1]], Series[bool]]
            | Callable[[S1], bool]
        ),
        other: Scalar | Series[S1] | DataFrame | Callable | NAType | None = ...,
        *,
        inplace: _bool = ...,
        axis: AxisIndex | None = ...,
        level: Level | None = ...,
    ) -> Series[S1]: ...
    def case_when(
        self,
        caselist: list[
            tuple[
                Sequence[bool]
                | Series[bool]
                | Callable[[Series], Series | np.ndarray | Sequence[bool]],
                ListLikeU | Scalar | Callable[[Series], Series | np.ndarray],
            ],
        ],
    ) -> Series: ...
    def truncate(
        self,
        before: date | _str | int | None = ...,
        after: date | _str | int | None = ...,
        axis: AxisIndex | None = ...,
        copy: _bool = ...,
    ) -> Series[S1]: ...
    def tz_convert(
        self,
        tz,
        axis: AxisIndex = ...,
        level: Level | None = ...,
        copy: _bool = ...,
    ) -> Series[S1]: ...
    def tz_localize(
        self,
        tz,
        axis: AxisIndex = ...,
        level: Level | None = ...,
        copy: _bool = ...,
        ambiguous=...,
        nonexistent: _str = ...,
    ) -> Series[S1]: ...
    def abs(self) -> Series[S1]: ...
    def describe(
        self,
        percentiles: list[float] | None = ...,
        include: Literal["all"] | list[S1] | None = ...,
        exclude: S1 | list[S1] | None = ...,
    ) -> Series[S1]: ...
    def pct_change(
        self,
        periods: int = ...,
        fill_method: _str = ...,
        limit: int | None = ...,
        freq=...,
        **kwargs,
    ) -> Series[S1]: ...
    def first_valid_index(self) -> Scalar: ...
    def last_valid_index(self) -> Scalar: ...
    @overload
    def value_counts(
        self,
        normalize: Literal[False] = ...,
        sort: _bool = ...,
        ascending: _bool = ...,
        bins: int | None = ...,
        dropna: _bool = ...,
    ) -> Series[int]: ...
    @overload
    def value_counts(
        self,
        normalize: Literal[True],
        sort: _bool = ...,
        ascending: _bool = ...,
        bins: int | None = ...,
        dropna: _bool = ...,
    ) -> Series[float]: ...
    def transpose(self, *args, **kwargs) -> Series[S1]: ...
    @property
    def T(self) -> Self: ...
    # The rest of these were left over from the old
    # stubs we shipped in preview. They may belong in
    # the base classes in some cases; I expect stubgen
    # just failed to generate these so I couldn't match
    # them up.
    @overload
    def __add__(self, other: S1 | Self) -> Self: ...
    @overload
    def __add__(
        self,
        other: num | _str | timedelta | Timedelta | _ListLike | Series | np.timedelta64,
    ) -> Series: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __and__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __and__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: int | np_ndarray_anyint | Series[int]
    ) -> Series[int]: ...
    # def __array__(self, dtype: Optional[_bool] = ...) -> _np_ndarray
    def __div__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    def __eq__(self, other: object) -> Series[_bool]: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __floordiv__(self, other: num | _ListLike | Series[S1]) -> Series[int]: ...
    def __ge__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: S1 | _ListLike | Series[S1] | datetime | timedelta | date
    ) -> Series[_bool]: ...
    def __gt__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: S1 | _ListLike | Series[S1] | datetime | timedelta | date
    ) -> Series[_bool]: ...
    def __le__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: S1 | _ListLike | Series[S1] | datetime | timedelta | date
    ) -> Series[_bool]: ...
    def __lt__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: S1 | _ListLike | Series[S1] | datetime | timedelta | date
    ) -> Series[_bool]: ...
    @overload
    def __mul__(
        self, other: timedelta | Timedelta | TimedeltaSeries | np.timedelta64
    ) -> TimedeltaSeries: ...
    @overload
    def __mul__(self, other: num | _ListLike | Series) -> Series: ...
    def __mod__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    def __ne__(self, other: object) -> Series[_bool]: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __pow__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __or__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __or__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: int | np_ndarray_anyint | Series[int]
    ) -> Series[int]: ...
    @overload
    def __radd__(self, other: S1 | Series[S1]) -> Self: ...
    @overload
    def __radd__(self, other: num | _str | _ListLike | Series) -> Series: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __rand__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __rand__(self, other: int | np_ndarray_anyint | Series[int]) -> Series[int]: ...  # type: ignore[misc] # pyright: ignore[reportIncompatibleMethodOverride]
    def __rdiv__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    def __rdivmod__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __rfloordiv__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    def __rmod__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    @overload
    def __rmul__(
        self, other: timedelta | Timedelta | TimedeltaSeries | np.timedelta64
    ) -> TimedeltaSeries: ...
    @overload
    def __rmul__(self, other: num | _ListLike | Series) -> Series: ...
    def __rnatmul__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    def __rpow__(self, other: num | _ListLike | Series[S1]) -> Series[S1]: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __ror__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __ror__(self, other: int | np_ndarray_anyint | Series[int]) -> Series[int]: ...  # type: ignore[misc] # pyright: ignore[reportIncompatibleMethodOverride]
    def __rsub__(self, other: num | _ListLike | Series[S1]) -> Series: ...
    def __rtruediv__(self, other: num | _ListLike | Series[S1]) -> Series: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __rxor__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __rxor__(self, other: int | np_ndarray_anyint | Series[int]) -> Series[int]: ...  # type: ignore[misc] # pyright: ignore[reportIncompatibleMethodOverride]
    @overload
    def __sub__(
        self: Series[Timestamp],
        other: Timedelta | TimedeltaSeries | TimedeltaIndex | np.timedelta64,
    ) -> TimestampSeries: ...
    @overload
    def __sub__(
        self: Series[Timedelta],
        other: Timedelta | TimedeltaSeries | TimedeltaIndex | np.timedelta64,
    ) -> TimedeltaSeries: ...
    @overload
    def __sub__(
        self, other: Timestamp | datetime | TimestampSeries
    ) -> TimedeltaSeries: ...
    @overload
    def __sub__(self, other: num | _ListLike | Series) -> Series: ...
    def __truediv__(self, other: num | _ListLike | Series[S1]) -> Series: ...
    # ignore needed for mypy as we want different results based on the arguments
    @overload  # type: ignore[override]
    def __xor__(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, other: bool | list[bool] | list[int] | np_ndarray_bool | Series[bool]
    ) -> Series[bool]: ...
    @overload
    def __xor__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: int | np_ndarray_anyint | Series[int]
    ) -> Series[int]: ...
    def __invert__(self) -> Series[bool]: ...
    # properties
    # @property
    # def array(self) -> _npndarray
    @property
    def at(self) -> _AtIndexer: ...
    @property
    def cat(self) -> CategoricalAccessor: ...
    @property
    def iat(self) -> _iAtIndexer: ...
    @property
    def iloc(self) -> _iLocIndexerSeries[S1]: ...
    @property
    def loc(self) -> _LocIndexerSeries[S1]: ...
    # Methods
    def add(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: int = ...,
    ) -> Series[S1]:
        """
Return Addition of series and other, element-wise (binary operator `add`).

Equivalent to ``series + other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.radd : Reverse of the Addition operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.add(b, fill_value=0)
a    2.0
b    1.0
c    1.0
d    1.0
e    NaN
dtype: float64
        """
        pass
    def all(
        self,
        axis: AxisIndex = ...,
        bool_only: _bool | None = ...,
        skipna: _bool = ...,
        **kwargs,
    ) -> _bool:
        """
Return whether all elements are True, potentially over an axis.

Returns True unless there at least one element within a series or
along a Dataframe axis that is False or equivalent (e.g. zero or
empty).

Parameters
----------
axis : {0 or 'index', 1 or 'columns', None}, default 0
    Indicate which axis or axes should be reduced. For `Series` this parameter
    is unused and defaults to 0.

    * 0 / 'index' : reduce the index, return a Series whose index is the
      original column labels.
    * 1 / 'columns' : reduce the columns, return a Series whose index is the
      original index.
    * None : reduce all axes, return a scalar.

bool_only : bool, default False
    Include only boolean columns. Not implemented for Series.
skipna : bool, default True
    Exclude NA/null values. If the entire row/column is NA and skipna is
    True, then the result will be True, as for an empty row/column.
    If skipna is False, then NA are treated as True, because these are not
    equal to zero.
**kwargs : any, default None
    Additional keywords have no effect but might be accepted for
    compatibility with NumPy.

Returns
-------
scalar or Series
    If level is specified, then, Series is returned; otherwise, scalar
    is returned.

See Also
--------
Series.all : Return True if all elements are True.
DataFrame.any : Return True if one (or more) elements are True.

Examples
--------
**Series**

>>> pd.Series([True, True]).all()
True
>>> pd.Series([True, False]).all()
False
>>> pd.Series([], dtype="float64").all()
True
>>> pd.Series([np.nan]).all()
True
>>> pd.Series([np.nan]).all(skipna=False)
True

**DataFrames**

Create a dataframe from a dictionary.

>>> df = pd.DataFrame({'col1': [True, True], 'col2': [True, False]})
>>> df
   col1   col2
0  True   True
1  True  False

Default behaviour checks if values in each column all return True.

>>> df.all()
col1     True
col2    False
dtype: bool

Specify ``axis='columns'`` to check if values in each row all return True.

>>> df.all(axis='columns')
0     True
1    False
dtype: bool

Or ``axis=None`` for whether every value is True.

>>> df.all(axis=None)
False
        """
        pass
    def any(
        self,
        *,
        axis: AxisIndex = ...,
        bool_only: _bool | None = ...,
        skipna: _bool = ...,
        **kwargs,
    ) -> _bool: ...
    def cummax(
        self, axis: AxisIndex | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> Series[S1]:
        """
Return cumulative maximum over a DataFrame or Series axis.

Returns a DataFrame or Series of the same size containing the cumulative
maximum.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The index or the name of the axis. 0 is equivalent to None or 'index'.
    For `Series` this parameter is unused and defaults to 0.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
*args, **kwargs
    Additional keywords have no effect but might be accepted for
    compatibility with NumPy.

Returns
-------
scalar or Series
    Return cumulative maximum of scalar or Series.

See Also
--------
core.window.expanding.Expanding.max : Similar functionality
    but ignores ``NaN`` values.
Series.max : Return the maximum over
    Series axis.
Series.cummax : Return cumulative maximum over Series axis.
Series.cummin : Return cumulative minimum over Series axis.
Series.cumsum : Return cumulative sum over Series axis.
Series.cumprod : Return cumulative product over Series axis.

Examples
--------
**Series**

>>> s = pd.Series([2, np.nan, 5, -1, 0])
>>> s
0    2.0
1    NaN
2    5.0
3   -1.0
4    0.0
dtype: float64

By default, NA values are ignored.

>>> s.cummax()
0    2.0
1    NaN
2    5.0
3    5.0
4    5.0
dtype: float64

To include NA values in the operation, use ``skipna=False``

>>> s.cummax(skipna=False)
0    2.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

**DataFrame**

>>> df = pd.DataFrame([[2.0, 1.0],
...                    [3.0, np.nan],
...                    [1.0, 0.0]],
...                   columns=list('AB'))
>>> df
     A    B
0  2.0  1.0
1  3.0  NaN
2  1.0  0.0

By default, iterates over rows and finds the maximum
in each column. This is equivalent to ``axis=None`` or ``axis='index'``.

>>> df.cummax()
     A    B
0  2.0  1.0
1  3.0  NaN
2  3.0  1.0

To iterate over columns and find the maximum in each row,
use ``axis=1``

>>> df.cummax(axis=1)
     A    B
0  2.0  2.0
1  3.0  NaN
2  1.0  1.0
        """
        pass
    def cummin(
        self, axis: AxisIndex | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> Series[S1]:
        """
Return cumulative minimum over a DataFrame or Series axis.

Returns a DataFrame or Series of the same size containing the cumulative
minimum.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The index or the name of the axis. 0 is equivalent to None or 'index'.
    For `Series` this parameter is unused and defaults to 0.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
*args, **kwargs
    Additional keywords have no effect but might be accepted for
    compatibility with NumPy.

Returns
-------
scalar or Series
    Return cumulative minimum of scalar or Series.

See Also
--------
core.window.expanding.Expanding.min : Similar functionality
    but ignores ``NaN`` values.
Series.min : Return the minimum over
    Series axis.
Series.cummax : Return cumulative maximum over Series axis.
Series.cummin : Return cumulative minimum over Series axis.
Series.cumsum : Return cumulative sum over Series axis.
Series.cumprod : Return cumulative product over Series axis.

Examples
--------
**Series**

>>> s = pd.Series([2, np.nan, 5, -1, 0])
>>> s
0    2.0
1    NaN
2    5.0
3   -1.0
4    0.0
dtype: float64

By default, NA values are ignored.

>>> s.cummin()
0    2.0
1    NaN
2    2.0
3   -1.0
4   -1.0
dtype: float64

To include NA values in the operation, use ``skipna=False``

>>> s.cummin(skipna=False)
0    2.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

**DataFrame**

>>> df = pd.DataFrame([[2.0, 1.0],
...                    [3.0, np.nan],
...                    [1.0, 0.0]],
...                   columns=list('AB'))
>>> df
     A    B
0  2.0  1.0
1  3.0  NaN
2  1.0  0.0

By default, iterates over rows and finds the minimum
in each column. This is equivalent to ``axis=None`` or ``axis='index'``.

>>> df.cummin()
     A    B
0  2.0  1.0
1  2.0  NaN
2  1.0  0.0

To iterate over columns and find the minimum in each row,
use ``axis=1``

>>> df.cummin(axis=1)
     A    B
0  2.0  1.0
1  3.0  NaN
2  1.0  0.0
        """
        pass
    def cumprod(
        self, axis: AxisIndex | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> Series[S1]:
        """
Return cumulative product over a DataFrame or Series axis.

Returns a DataFrame or Series of the same size containing the cumulative
product.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The index or the name of the axis. 0 is equivalent to None or 'index'.
    For `Series` this parameter is unused and defaults to 0.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
*args, **kwargs
    Additional keywords have no effect but might be accepted for
    compatibility with NumPy.

Returns
-------
scalar or Series
    Return cumulative product of scalar or Series.

See Also
--------
core.window.expanding.Expanding.prod : Similar functionality
    but ignores ``NaN`` values.
Series.prod : Return the product over
    Series axis.
Series.cummax : Return cumulative maximum over Series axis.
Series.cummin : Return cumulative minimum over Series axis.
Series.cumsum : Return cumulative sum over Series axis.
Series.cumprod : Return cumulative product over Series axis.

Examples
--------
**Series**

>>> s = pd.Series([2, np.nan, 5, -1, 0])
>>> s
0    2.0
1    NaN
2    5.0
3   -1.0
4    0.0
dtype: float64

By default, NA values are ignored.

>>> s.cumprod()
0     2.0
1     NaN
2    10.0
3   -10.0
4    -0.0
dtype: float64

To include NA values in the operation, use ``skipna=False``

>>> s.cumprod(skipna=False)
0    2.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

**DataFrame**

>>> df = pd.DataFrame([[2.0, 1.0],
...                    [3.0, np.nan],
...                    [1.0, 0.0]],
...                   columns=list('AB'))
>>> df
     A    B
0  2.0  1.0
1  3.0  NaN
2  1.0  0.0

By default, iterates over rows and finds the product
in each column. This is equivalent to ``axis=None`` or ``axis='index'``.

>>> df.cumprod()
     A    B
0  2.0  1.0
1  6.0  NaN
2  6.0  0.0

To iterate over columns and find the product in each row,
use ``axis=1``

>>> df.cumprod(axis=1)
     A    B
0  2.0  2.0
1  3.0  NaN
2  1.0  0.0
        """
        pass
    def cumsum(
        self, axis: AxisIndex | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> Series[S1]:
        """
Return cumulative sum over a DataFrame or Series axis.

Returns a DataFrame or Series of the same size containing the cumulative
sum.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The index or the name of the axis. 0 is equivalent to None or 'index'.
    For `Series` this parameter is unused and defaults to 0.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
*args, **kwargs
    Additional keywords have no effect but might be accepted for
    compatibility with NumPy.

Returns
-------
scalar or Series
    Return cumulative sum of scalar or Series.

See Also
--------
core.window.expanding.Expanding.sum : Similar functionality
    but ignores ``NaN`` values.
Series.sum : Return the sum over
    Series axis.
Series.cummax : Return cumulative maximum over Series axis.
Series.cummin : Return cumulative minimum over Series axis.
Series.cumsum : Return cumulative sum over Series axis.
Series.cumprod : Return cumulative product over Series axis.

Examples
--------
**Series**

>>> s = pd.Series([2, np.nan, 5, -1, 0])
>>> s
0    2.0
1    NaN
2    5.0
3   -1.0
4    0.0
dtype: float64

By default, NA values are ignored.

>>> s.cumsum()
0    2.0
1    NaN
2    7.0
3    6.0
4    6.0
dtype: float64

To include NA values in the operation, use ``skipna=False``

>>> s.cumsum(skipna=False)
0    2.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

**DataFrame**

>>> df = pd.DataFrame([[2.0, 1.0],
...                    [3.0, np.nan],
...                    [1.0, 0.0]],
...                   columns=list('AB'))
>>> df
     A    B
0  2.0  1.0
1  3.0  NaN
2  1.0  0.0

By default, iterates over rows and finds the sum
in each column. This is equivalent to ``axis=None`` or ``axis='index'``.

>>> df.cumsum()
     A    B
0  2.0  1.0
1  5.0  NaN
2  6.0  1.0

To iterate over columns and find the sum in each row,
use ``axis=1``

>>> df.cumsum(axis=1)
     A    B
0  2.0  3.0
1  3.0  NaN
2  1.0  1.0
        """
        pass
    def divide(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[float]:
        """
Return Floating division of series and other, element-wise (binary operator `truediv`).

Equivalent to ``series / other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rtruediv : Reverse of the Floating division operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divide(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def divmod(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Integer division and modulo of series and other, element-wise (binary operator `divmod`).

Equivalent to ``divmod(series, other)``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
2-Tuple of Series
    The result of the operation.

See Also
--------
Series.rdivmod : Reverse of the Integer division and modulo operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divmod(b, fill_value=0)
(a    1.0
 b    inf
 c    inf
 d    0.0
 e    NaN
 dtype: float64,
 a    0.0
 b    NaN
 c    NaN
 d    0.0
 e    NaN
 dtype: float64)
        """
        pass
    def eq(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Equal to of series and other, element-wise (binary operator `eq`).

Equivalent to ``series == other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.eq(b, fill_value=0)
a     True
b    False
c    False
d    False
e    False
dtype: bool
        """
        pass
    def ewm(
        self,
        com: float | None = ...,
        span: float | None = ...,
        halflife: float | None = ...,
        alpha: float | None = ...,
        min_periods: int = ...,
        adjust: _bool = ...,
        ignore_na: _bool = ...,
    ) -> ExponentialMovingWindow[Series]: ...
    def expanding(
        self,
        min_periods: int = ...,
        method: CalculationMethod = ...,
    ) -> Expanding[Series]: ...
    def floordiv(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[int]:
        """
Return Integer division of series and other, element-wise (binary operator `floordiv`).

Equivalent to ``series // other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rfloordiv : Reverse of the Integer division operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.floordiv(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def ge(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Greater than or equal to of series and other, element-wise (binary operator `ge`).

Equivalent to ``series >= other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan, 1], index=['a', 'b', 'c', 'd', 'e'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
e    1.0
dtype: float64
>>> b = pd.Series([0, 1, 2, np.nan, 1], index=['a', 'b', 'c', 'd', 'f'])
>>> b
a    0.0
b    1.0
c    2.0
d    NaN
f    1.0
dtype: float64
>>> a.ge(b, fill_value=0)
a     True
b     True
c    False
d    False
e     True
f    False
dtype: bool
        """
        pass
    def gt(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Greater than of series and other, element-wise (binary operator `gt`).

Equivalent to ``series > other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan, 1], index=['a', 'b', 'c', 'd', 'e'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
e    1.0
dtype: float64
>>> b = pd.Series([0, 1, 2, np.nan, 1], index=['a', 'b', 'c', 'd', 'f'])
>>> b
a    0.0
b    1.0
c    2.0
d    NaN
f    1.0
dtype: float64
>>> a.gt(b, fill_value=0)
a     True
b    False
c    False
d    False
e     True
f    False
dtype: bool
        """
        pass
    def item(self) -> S1: ...
    def kurt(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Scalar:
        """
Return unbiased kurtosis over requested axis.

Kurtosis obtained using Fisher's definition of
kurtosis (kurtosis of normal == 0.0). Normalized by N-1.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

            Examples
            --------
            >>> s = pd.Series([1, 2, 2, 3], index=['cat', 'dog', 'dog', 'mouse'])
            >>> s
            cat    1
            dog    2
            dog    2
            mouse  3
            dtype: int64
            >>> s.kurt()
            1.5

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2, 2, 3], 'b': [3, 4, 4, 4]},
            ...                   index=['cat', 'dog', 'dog', 'mouse'])
            >>> df
                   a   b
              cat  1   3
              dog  2   4
              dog  2   4
            mouse  3   4
            >>> df.kurt()
            a   1.5
            b   4.0
            dtype: float64

            With axis=None

            >>> df.kurt(axis=None).round(6)
            -0.988693

            Using axis=1

            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [3, 4], 'd': [1, 2]},
            ...                   index=['cat', 'dog'])
            >>> df.kurt(axis=1)
            cat   -6.0
            dog   -6.0
            dtype: float64
        """
        pass
    def kurtosis(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Scalar:
        """
Return unbiased kurtosis over requested axis.

Kurtosis obtained using Fisher's definition of
kurtosis (kurtosis of normal == 0.0). Normalized by N-1.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

            Examples
            --------
            >>> s = pd.Series([1, 2, 2, 3], index=['cat', 'dog', 'dog', 'mouse'])
            >>> s
            cat    1
            dog    2
            dog    2
            mouse  3
            dtype: int64
            >>> s.kurt()
            1.5

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2, 2, 3], 'b': [3, 4, 4, 4]},
            ...                   index=['cat', 'dog', 'dog', 'mouse'])
            >>> df
                   a   b
              cat  1   3
              dog  2   4
              dog  2   4
            mouse  3   4
            >>> df.kurt()
            a   1.5
            b   4.0
            dtype: float64

            With axis=None

            >>> df.kurt(axis=None).round(6)
            -0.988693

            Using axis=1

            >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [3, 4], 'd': [1, 2]},
            ...                   index=['cat', 'dog'])
            >>> df.kurt(axis=1)
            cat   -6.0
            dog   -6.0
            dtype: float64
        """
        pass
    def le(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Less than or equal to of series and other, element-wise (binary operator `le`).

Equivalent to ``series <= other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan, 1], index=['a', 'b', 'c', 'd', 'e'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
e    1.0
dtype: float64
>>> b = pd.Series([0, 1, 2, np.nan, 1], index=['a', 'b', 'c', 'd', 'f'])
>>> b
a    0.0
b    1.0
c    2.0
d    NaN
f    1.0
dtype: float64
>>> a.le(b, fill_value=0)
a    False
b     True
c     True
d    False
e    False
f     True
dtype: bool
        """
        pass
    def lt(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Less than of series and other, element-wise (binary operator `lt`).

Equivalent to ``series < other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan, 1], index=['a', 'b', 'c', 'd', 'e'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
e    1.0
dtype: float64
>>> b = pd.Series([0, 1, 2, np.nan, 1], index=['a', 'b', 'c', 'd', 'f'])
>>> b
a    0.0
b    1.0
c    2.0
d    NaN
f    1.0
dtype: float64
>>> a.lt(b, fill_value=0)
a    False
b    False
c     True
d    False
e    False
f     True
dtype: bool
        """
        pass
    def max(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> S1:
        """
Return the maximum of the values over the requested axis.

If you want the *index* of the maximum, use ``idxmax``. This is the equivalent of the ``numpy.ndarray`` method ``argmax``.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

See Also
--------
Series.sum : Return the sum.
Series.min : Return the minimum.
Series.max : Return the maximum.
Series.idxmin : Return the index of the minimum.
Series.idxmax : Return the index of the maximum.
DataFrame.sum : Return the sum over the requested axis.
DataFrame.min : Return the minimum over the requested axis.
DataFrame.max : Return the maximum over the requested axis.
DataFrame.idxmin : Return the index of the minimum over the requested axis.
DataFrame.idxmax : Return the index of the maximum over the requested axis.

Examples
--------
>>> idx = pd.MultiIndex.from_arrays([
...     ['warm', 'warm', 'cold', 'cold'],
...     ['dog', 'falcon', 'fish', 'spider']],
...     names=['blooded', 'animal'])
>>> s = pd.Series([4, 2, 0, 8], name='legs', index=idx)
>>> s
blooded  animal
warm     dog       4
         falcon    2
cold     fish      0
         spider    8
Name: legs, dtype: int64

>>> s.max()
8
        """
        pass
    def mean(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> float:
        """
Return the mean of the values over the requested axis.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

            Examples
            --------
            >>> s = pd.Series([1, 2, 3])
            >>> s.mean()
            2.0

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2], 'b': [2, 3]}, index=['tiger', 'zebra'])
            >>> df
                   a   b
            tiger  1   2
            zebra  2   3
            >>> df.mean()
            a   1.5
            b   2.5
            dtype: float64

            Using axis=1

            >>> df.mean(axis=1)
            tiger   1.5
            zebra   2.5
            dtype: float64

            In this case, `numeric_only` should be set to `True` to avoid
            getting an error.

            >>> df = pd.DataFrame({'a': [1, 2], 'b': ['T', 'Z']},
            ...                   index=['tiger', 'zebra'])
            >>> df.mean(numeric_only=True)
            a   1.5
            dtype: float64
        """
        pass
    def median(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> float:
        """
Return the median of the values over the requested axis.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

            Examples
            --------
            >>> s = pd.Series([1, 2, 3])
            >>> s.median()
            2.0

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2], 'b': [2, 3]}, index=['tiger', 'zebra'])
            >>> df
                   a   b
            tiger  1   2
            zebra  2   3
            >>> df.median()
            a   1.5
            b   2.5
            dtype: float64

            Using axis=1

            >>> df.median(axis=1)
            tiger   1.5
            zebra   2.5
            dtype: float64

            In this case, `numeric_only` should be set to `True`
            to avoid getting an error.

            >>> df = pd.DataFrame({'a': [1, 2], 'b': ['T', 'Z']},
            ...                   index=['tiger', 'zebra'])
            >>> df.median(numeric_only=True)
            a   1.5
            dtype: float64
        """
        pass
    def min(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> S1:
        """
Return the minimum of the values over the requested axis.

If you want the *index* of the minimum, use ``idxmin``. This is the equivalent of the ``numpy.ndarray`` method ``argmin``.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

See Also
--------
Series.sum : Return the sum.
Series.min : Return the minimum.
Series.max : Return the maximum.
Series.idxmin : Return the index of the minimum.
Series.idxmax : Return the index of the maximum.
DataFrame.sum : Return the sum over the requested axis.
DataFrame.min : Return the minimum over the requested axis.
DataFrame.max : Return the maximum over the requested axis.
DataFrame.idxmin : Return the index of the minimum over the requested axis.
DataFrame.idxmax : Return the index of the maximum over the requested axis.

Examples
--------
>>> idx = pd.MultiIndex.from_arrays([
...     ['warm', 'warm', 'cold', 'cold'],
...     ['dog', 'falcon', 'fish', 'spider']],
...     names=['blooded', 'animal'])
>>> s = pd.Series([4, 2, 0, 8], name='legs', index=idx)
>>> s
blooded  animal
warm     dog       4
         falcon    2
cold     fish      0
         spider    8
Name: legs, dtype: int64

>>> s.min()
0
        """
        pass
    def mod(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]:
        """
Return Modulo of series and other, element-wise (binary operator `mod`).

Equivalent to ``series % other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rmod : Reverse of the Modulo operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.mod(b, fill_value=0)
a    0.0
b    NaN
c    NaN
d    0.0
e    NaN
dtype: float64
        """
        pass
    @overload
    def mul(
        self,
        other: timedelta | Timedelta | TimedeltaSeries | np.timedelta64,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> TimedeltaSeries:
        """
Return Multiplication of series and other, element-wise (binary operator `mul`).

Equivalent to ``series * other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rmul : Reverse of the Multiplication operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.multiply(b, fill_value=0)
a    1.0
b    0.0
c    0.0
d    0.0
e    NaN
dtype: float64
        """
        pass
    @overload
    def mul(
        self,
        other: num | _ListLike | Series,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series: ...
    def multiply(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]:
        """
Return Multiplication of series and other, element-wise (binary operator `mul`).

Equivalent to ``series * other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rmul : Reverse of the Multiplication operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.multiply(b, fill_value=0)
a    1.0
b    0.0
c    0.0
d    0.0
e    NaN
dtype: float64
        """
        pass
    def ne(
        self,
        other: Scalar | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[_bool]:
        """
Return Not equal to of series and other, element-wise (binary operator `ne`).

Equivalent to ``series != other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.ne(b, fill_value=0)
a    False
b     True
c     True
d     True
e     True
dtype: bool
        """
        pass
    def nunique(self, dropna: _bool = ...) -> int: ...
    def pow(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]:
        """
Return Exponential power of series and other, element-wise (binary operator `pow`).

Equivalent to ``series ** other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rpow : Reverse of the Exponential power operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.pow(b, fill_value=0)
a    1.0
b    1.0
c    1.0
d    0.0
e    NaN
dtype: float64
        """
        pass
    def prod(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Scalar:
        """
Return the product of the values over the requested axis.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.prod with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

min_count : int, default 0
    The required number of valid values to perform the operation. If fewer than
    ``min_count`` non-NA values are present the result will be NA.
**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

See Also
--------
Series.sum : Return the sum.
Series.min : Return the minimum.
Series.max : Return the maximum.
Series.idxmin : Return the index of the minimum.
Series.idxmax : Return the index of the maximum.
DataFrame.sum : Return the sum over the requested axis.
DataFrame.min : Return the minimum over the requested axis.
DataFrame.max : Return the maximum over the requested axis.
DataFrame.idxmin : Return the index of the minimum over the requested axis.
DataFrame.idxmax : Return the index of the maximum over the requested axis.

Examples
--------
By default, the product of an empty or all-NA Series is ``1``

>>> pd.Series([], dtype="float64").prod()
1.0

This can be controlled with the ``min_count`` parameter

>>> pd.Series([], dtype="float64").prod(min_count=1)
nan

Thanks to the ``skipna`` parameter, ``min_count`` handles all-NA and
empty series identically.

>>> pd.Series([np.nan]).prod()
1.0

>>> pd.Series([np.nan]).prod(min_count=1)
nan
        """
        pass
    def product(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Scalar:
        """
Return the product of the values over the requested axis.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.prod with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

min_count : int, default 0
    The required number of valid values to perform the operation. If fewer than
    ``min_count`` non-NA values are present the result will be NA.
**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

See Also
--------
Series.sum : Return the sum.
Series.min : Return the minimum.
Series.max : Return the maximum.
Series.idxmin : Return the index of the minimum.
Series.idxmax : Return the index of the maximum.
DataFrame.sum : Return the sum over the requested axis.
DataFrame.min : Return the minimum over the requested axis.
DataFrame.max : Return the maximum over the requested axis.
DataFrame.idxmin : Return the index of the minimum over the requested axis.
DataFrame.idxmax : Return the index of the maximum over the requested axis.

Examples
--------
By default, the product of an empty or all-NA Series is ``1``

>>> pd.Series([], dtype="float64").prod()
1.0

This can be controlled with the ``min_count`` parameter

>>> pd.Series([], dtype="float64").prod(min_count=1)
nan

Thanks to the ``skipna`` parameter, ``min_count`` handles all-NA and
empty series identically.

>>> pd.Series([np.nan]).prod()
1.0

>>> pd.Series([np.nan]).prod(min_count=1)
nan
        """
        pass
    def radd(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Addition of series and other, element-wise (binary operator `radd`).

Equivalent to ``other + series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.add : Element-wise Addition, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.add(b, fill_value=0)
a    2.0
b    1.0
c    1.0
d    1.0
e    NaN
dtype: float64
        """
        pass
    def rdivmod(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Integer division and modulo of series and other, element-wise (binary operator `rdivmod`).

Equivalent to ``other divmod series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
2-Tuple of Series
    The result of the operation.

See Also
--------
Series.divmod : Element-wise Integer division and modulo, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divmod(b, fill_value=0)
(a    1.0
 b    inf
 c    inf
 d    0.0
 e    NaN
 dtype: float64,
 a    0.0
 b    NaN
 c    NaN
 d    0.0
 e    NaN
 dtype: float64)
        """
        pass
    def rfloordiv(
        self,
        other,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Integer division of series and other, element-wise (binary operator `rfloordiv`).

Equivalent to ``other // series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.floordiv : Element-wise Integer division, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.floordiv(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def rmod(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Modulo of series and other, element-wise (binary operator `rmod`).

Equivalent to ``other % series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.mod : Element-wise Modulo, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.mod(b, fill_value=0)
a    0.0
b    NaN
c    NaN
d    0.0
e    NaN
dtype: float64
        """
        pass
    @overload
    def rmul(
        self,
        other: timedelta | Timedelta | TimedeltaSeries | np.timedelta64,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> TimedeltaSeries:
        """
Return Multiplication of series and other, element-wise (binary operator `rmul`).

Equivalent to ``other * series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.mul : Element-wise Multiplication, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.multiply(b, fill_value=0)
a    1.0
b    0.0
c    0.0
d    0.0
e    NaN
dtype: float64
        """
        pass
    @overload
    def rmul(
        self,
        other: num | _ListLike | Series,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series: ...
    @overload
    def rolling(
        self,
        window: int | _str | timedelta | BaseOffset | BaseIndexer,
        min_periods: int | None = ...,
        center: _bool = ...,
        on: _str | None = ...,
        closed: IntervalClosedType | None = ...,
        step: int | None = ...,
        method: CalculationMethod = ...,
        *,
        win_type: _str,
    ) -> Window[Series]: ...
    @overload
    def rolling(
        self,
        window: int | _str | timedelta | BaseOffset | BaseIndexer,
        min_periods: int | None = ...,
        center: _bool = ...,
        on: _str | None = ...,
        closed: IntervalClosedType | None = ...,
        step: int | None = ...,
        method: CalculationMethod = ...,
        *,
        win_type: None = ...,
    ) -> Rolling[Series]: ...
    def rpow(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Exponential power of series and other, element-wise (binary operator `rpow`).

Equivalent to ``other ** series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.pow : Element-wise Exponential power, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.pow(b, fill_value=0)
a    1.0
b    1.0
c    1.0
d    0.0
e    NaN
dtype: float64
        """
        pass
    def rsub(
        self,
        other: Series[S1] | Scalar,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Subtraction of series and other, element-wise (binary operator `rsub`).

Equivalent to ``other - series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.sub : Element-wise Subtraction, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.subtract(b, fill_value=0)
a    0.0
b    1.0
c    1.0
d   -1.0
e    NaN
dtype: float64
        """
        pass
    def rtruediv(
        self,
        other,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[S1]:
        """
Return Floating division of series and other, element-wise (binary operator `rtruediv`).

Equivalent to ``other / series``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.truediv : Element-wise Floating division, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divide(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def sem(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Scalar:
        """
Return unbiased standard error of the mean over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument

Parameters
----------
axis : {index (0)}
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.sem with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
ddof : int, default 1
    Delta Degrees of Freedom. The divisor used in calculations is N - ddof,
    where N represents the number of elements.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

Returns
-------
scalar or Series (if level specified) 

            Examples
            --------
            >>> s = pd.Series([1, 2, 3])
            >>> s.sem().round(6)
            0.57735

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2], 'b': [2, 3]}, index=['tiger', 'zebra'])
            >>> df
                   a   b
            tiger  1   2
            zebra  2   3
            >>> df.sem()
            a   0.5
            b   0.5
            dtype: float64

            Using axis=1

            >>> df.sem(axis=1)
            tiger   0.5
            zebra   0.5
            dtype: float64

            In this case, `numeric_only` should be set to `True`
            to avoid getting an error.

            >>> df = pd.DataFrame({'a': [1, 2], 'b': ['T', 'Z']},
            ...                   index=['tiger', 'zebra'])
            >>> df.sem(numeric_only=True)
            a   0.5
            dtype: float64
        """
        pass
    def skew(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Scalar:
        """
Return unbiased skew over requested axis.

Normalized by N-1.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    For DataFrames, specifying ``axis=None`` will apply the aggregation
    across both axes.

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

            Examples
            --------
            >>> s = pd.Series([1, 2, 3])
            >>> s.skew()
            0.0

            With a DataFrame

            >>> df = pd.DataFrame({'a': [1, 2, 3], 'b': [2, 3, 4], 'c': [1, 3, 5]},
            ...                   index=['tiger', 'zebra', 'cow'])
            >>> df
                    a   b   c
            tiger   1   2   1
            zebra   2   3   3
            cow     3   4   5
            >>> df.skew()
            a   0.0
            b   0.0
            c   0.0
            dtype: float64

            Using axis=1

            >>> df.skew(axis=1)
            tiger   1.732051
            zebra  -1.732051
            cow     0.000000
            dtype: float64

            In this case, `numeric_only` should be set to `True` to avoid
            getting an error.

            >>> df = pd.DataFrame({'a': [1, 2, 3], 'b': ['T', 'Z', 'X']},
            ...                   index=['tiger', 'zebra', 'cow'])
            >>> df.skew(numeric_only=True)
            a   0.0
            dtype: float64
        """
        pass
    def std(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> float:
        """
Return sample standard deviation over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument.

Parameters
----------
axis : {index (0)}
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.std with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
ddof : int, default 1
    Delta Degrees of Freedom. The divisor used in calculations is N - ddof,
    where N represents the number of elements.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

Returns
-------
scalar or Series (if level specified) 

Notes
-----
To have the same behaviour as `numpy.std`, use `ddof=0` (instead of the
default `ddof=1`)

Examples
--------
>>> df = pd.DataFrame({'person_id': [0, 1, 2, 3],
...                    'age': [21, 25, 62, 43],
...                    'height': [1.61, 1.87, 1.49, 2.01]}
...                   ).set_index('person_id')
>>> df
           age  height
person_id
0           21    1.61
1           25    1.87
2           62    1.49
3           43    2.01

The standard deviation of the columns can be found as follows:

>>> df.std()
age       18.786076
height     0.237417
dtype: float64

Alternatively, `ddof=0` can be set to normalize by N instead of N-1:

>>> df.std(ddof=0)
age       16.269219
height     0.205609
dtype: float64
        """
        pass
    def sub(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]:
        """
Return Subtraction of series and other, element-wise (binary operator `sub`).

Equivalent to ``series - other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rsub : Reverse of the Subtraction operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.subtract(b, fill_value=0)
a    0.0
b    1.0
c    1.0
d   -1.0
e    NaN
dtype: float64
        """
        pass
    def subtract(
        self,
        other: num | _ListLike | Series[S1],
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex | None = ...,
    ) -> Series[S1]:
        """
Return Subtraction of series and other, element-wise (binary operator `sub`).

Equivalent to ``series - other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rsub : Reverse of the Subtraction operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.subtract(b, fill_value=0)
a    0.0
b    1.0
c    1.0
d   -1.0
e    NaN
dtype: float64
        """
        pass
    # ignore needed because of mypy, for using `Never` as type-var.
    @overload
    def sum(
        self: Series[Never],
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Any:
        """
Return the sum of the values over the requested axis.

This is equivalent to the method ``numpy.sum``.

Parameters
----------
axis : {index (0)}
    Axis for the function to be applied on.
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.sum with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

    .. versionadded:: 2.0.0

skipna : bool, default True
    Exclude NA/null values when computing the result.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

min_count : int, default 0
    The required number of valid values to perform the operation. If fewer than
    ``min_count`` non-NA values are present the result will be NA.
**kwargs
    Additional keyword arguments to be passed to the function.

Returns
-------
scalar or scalar

See Also
--------
Series.sum : Return the sum.
Series.min : Return the minimum.
Series.max : Return the maximum.
Series.idxmin : Return the index of the minimum.
Series.idxmax : Return the index of the maximum.
DataFrame.sum : Return the sum over the requested axis.
DataFrame.min : Return the minimum over the requested axis.
DataFrame.max : Return the maximum over the requested axis.
DataFrame.idxmin : Return the index of the minimum over the requested axis.
DataFrame.idxmax : Return the index of the maximum over the requested axis.

Examples
--------
>>> idx = pd.MultiIndex.from_arrays([
...     ['warm', 'warm', 'cold', 'cold'],
...     ['dog', 'falcon', 'fish', 'spider']],
...     names=['blooded', 'animal'])
>>> s = pd.Series([4, 2, 0, 8], name='legs', index=idx)
>>> s
blooded  animal
warm     dog       4
         falcon    2
cold     fish      0
         spider    8
Name: legs, dtype: int64

>>> s.sum()
14

By default, the sum of an empty or all-NA Series is ``0``.

>>> pd.Series([], dtype="float64").sum()  # min_count=0 is the default
0.0

This can be controlled with the ``min_count`` parameter. For example, if
you'd like the sum of an empty series to be NaN, pass ``min_count=1``.

>>> pd.Series([], dtype="float64").sum(min_count=1)
nan

Thanks to the ``skipna`` parameter, ``min_count`` handles all-NA and
empty series identically.

>>> pd.Series([np.nan]).sum()
0.0

>>> pd.Series([np.nan]).sum(min_count=1)
nan
        """
        pass
    # ignore needed because of mypy, for overlapping overloads
    # between `Series[bool]` and `Series[int]`.
    @overload
    def sum(  # type: ignore[overload-overlap]
        self: Series[bool],
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> int: ...
    @overload
    def sum(
        self: Series[S1],
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> S1: ...
    def to_list(self) -> list[S1]: ...
    def to_numpy(
        self,
        dtype: npt.DTypeLike | None = ...,
        copy: bool = ...,
        na_value: Scalar = ...,
        **kwargs,
    ) -> np.ndarray: ...
    def tolist(self) -> list[S1]: ...
    def truediv(
        self,
        other,
        level: Level | None = ...,
        fill_value: float | None = ...,
        axis: AxisIndex = ...,
    ) -> Series[float]:
        """
Return Floating division of series and other, element-wise (binary operator `truediv`).

Equivalent to ``series / other``, but with support to substitute a fill_value for
missing data in either one of the inputs.

Parameters
----------
other : Series or scalar value
level : int or name
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : None or float value, default None (NaN)
    Fill existing missing (NaN) values, and any new element needed for
    successful Series alignment, with this value before computation.
    If data in both corresponding Series locations is missing
    the result of filling (at that location) will be missing.
axis : {0 or 'index'}
    Unused. Parameter needed for compatibility with DataFrame.

Returns
-------
Series
    The result of the operation.

See Also
--------
Series.rtruediv : Reverse of the Floating division operator, see
    `Python documentation
    <https://docs.python.org/3/reference/datamodel.html#emulating-numeric-types>`_
    for more details.

Examples
--------
>>> a = pd.Series([1, 1, 1, np.nan], index=['a', 'b', 'c', 'd'])
>>> a
a    1.0
b    1.0
c    1.0
d    NaN
dtype: float64
>>> b = pd.Series([1, np.nan, 1, np.nan], index=['a', 'b', 'd', 'e'])
>>> b
a    1.0
b    NaN
d    1.0
e    NaN
dtype: float64
>>> a.divide(b, fill_value=0)
a    1.0
b    inf
c    inf
d    0.0
e    NaN
dtype: float64
        """
        pass
    def var(
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Scalar:
        """
Return unbiased variance over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument.

Parameters
----------
axis : {index (0)}
    For `Series` this parameter is unused and defaults to 0.

    .. warning::

        The behavior of DataFrame.var with ``axis=None`` is deprecated,
        in a future version this will reduce over both axes and return a scalar
        To retain the old behavior, pass axis=0 (or do not pass axis).

skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
ddof : int, default 1
    Delta Degrees of Freedom. The divisor used in calculations is N - ddof,
    where N represents the number of elements.
numeric_only : bool, default False
    Include only float, int, boolean columns. Not implemented for Series.

Returns
-------
scalar or Series (if level specified) 

Examples
--------
>>> df = pd.DataFrame({'person_id': [0, 1, 2, 3],
...                    'age': [21, 25, 62, 43],
...                    'height': [1.61, 1.87, 1.49, 2.01]}
...                   ).set_index('person_id')
>>> df
           age  height
person_id
0           21    1.61
1           25    1.87
2           62    1.49
3           43    2.01

>>> df.var()
age       352.916667
height      0.056367
dtype: float64

Alternatively, ``ddof=0`` can be set to normalize by N instead of N-1:

>>> df.var(ddof=0)
age       264.687500
height      0.042275
dtype: float64
        """
        pass
    @overload
    def rename_axis(
        self,
        mapper: Scalar | ListLike = ...,
        index: Scalar | ListLike | Callable | dict | None = ...,
        columns: Scalar | ListLike | Callable | dict | None = ...,
        axis: AxisIndex | None = ...,
        copy: _bool = ...,
        *,
        inplace: Literal[True],
    ) -> None:
        """
Set the name of the axis for the index or columns.

Parameters
----------
mapper : scalar, list-like, optional
    Value to set the axis name attribute.
index, columns : scalar, list-like, dict-like or function, optional
    A scalar, list-like, dict-like or functions transformations to
    apply to that axis' values.
    Note that the ``columns`` parameter is not allowed if the
    object is a Series. This parameter only apply for DataFrame
    type objects.

    Use either ``mapper`` and ``axis`` to
    specify the axis to target with ``mapper``, or ``index``
    and/or ``columns``.
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to rename. For `Series` this parameter is unused and defaults to 0.
copy : bool, default None
    Also copy underlying data.

    .. note::
        The `copy` keyword will change behavior in pandas 3.0.
        `Copy-on-Write
        <https://pandas.pydata.org/docs/dev/user_guide/copy_on_write.html>`__
        will be enabled by default, which means that all methods with a
        `copy` keyword will use a lazy copy mechanism to defer the copy and
        ignore the `copy` keyword. The `copy` keyword will be removed in a
        future version of pandas.

        You can already get the future behavior and improvements through
        enabling copy on write ``pd.options.mode.copy_on_write = True``
inplace : bool, default False
    Modifies the object directly, instead of creating a new Series
    or DataFrame.

Returns
-------
Series, DataFrame, or None
    The same type as the caller or None if ``inplace=True``.

See Also
--------
Series.rename : Alter Series index labels or name.
DataFrame.rename : Alter DataFrame index labels or name.
Index.rename : Set new names on index.

Notes
-----
``DataFrame.rename_axis`` supports two calling conventions

* ``(index=index_mapper, columns=columns_mapper, ...)``
* ``(mapper, axis={'index', 'columns'}, ...)``

The first calling convention will only modify the names of
the index and/or the names of the Index object that is the columns.
In this case, the parameter ``copy`` is ignored.

The second calling convention will modify the names of the
corresponding index if mapper is a list or a scalar.
However, if mapper is dict-like or a function, it will use the
deprecated behavior of modifying the axis *labels*.

We *highly* recommend using keyword arguments to clarify your
intent.

Examples
--------
**Series**

>>> s = pd.Series(["dog", "cat", "monkey"])
>>> s
0       dog
1       cat
2    monkey
dtype: object
>>> s.rename_axis("animal")
animal
0    dog
1    cat
2    monkey
dtype: object

**DataFrame**

>>> df = pd.DataFrame({"num_legs": [4, 4, 2],
...                    "num_arms": [0, 0, 2]},
...                   ["dog", "cat", "monkey"])
>>> df
        num_legs  num_arms
dog            4         0
cat            4         0
monkey         2         2
>>> df = df.rename_axis("animal")
>>> df
        num_legs  num_arms
animal
dog            4         0
cat            4         0
monkey         2         2
>>> df = df.rename_axis("limbs", axis="columns")
>>> df
limbs   num_legs  num_arms
animal
dog            4         0
cat            4         0
monkey         2         2

**MultiIndex**

>>> df.index = pd.MultiIndex.from_product([['mammal'],
...                                        ['dog', 'cat', 'monkey']],
...                                       names=['type', 'name'])
>>> df
limbs          num_legs  num_arms
type   name
mammal dog            4         0
       cat            4         0
       monkey         2         2

>>> df.rename_axis(index={'type': 'class'})
limbs          num_legs  num_arms
class  name
mammal dog            4         0
       cat            4         0
       monkey         2         2

>>> df.rename_axis(columns=str.upper)
LIMBS          num_legs  num_arms
type   name
mammal dog            4         0
       cat            4         0
       monkey         2         2
        """
        pass
    @overload
    def rename_axis(
        self,
        mapper: Scalar | ListLike = ...,
        index: Scalar | ListLike | Callable | dict | None = ...,
        columns: Scalar | ListLike | Callable | dict | None = ...,
        axis: AxisIndex | None = ...,
        copy: _bool = ...,
        inplace: Literal[False] = ...,
    ) -> Self: ...
    def set_axis(self, labels, *, axis: Axis = ..., copy: _bool = ...) -> Self:
        """
Assign desired index to given axis.

Indexes for row labels can be changed by assigning
a list-like or Index.

Parameters
----------
labels : list-like, Index
    The values for the new index.

axis : {0 or 'index'}, default 0
    The axis to update. The value 0 identifies the rows. For `Series`
    this parameter is unused and defaults to 0.

copy : bool, default True
    Whether to make a copy of the underlying data.

    .. note::
        The `copy` keyword will change behavior in pandas 3.0.
        `Copy-on-Write
        <https://pandas.pydata.org/docs/dev/user_guide/copy_on_write.html>`__
        will be enabled by default, which means that all methods with a
        `copy` keyword will use a lazy copy mechanism to defer the copy and
        ignore the `copy` keyword. The `copy` keyword will be removed in a
        future version of pandas.

        You can already get the future behavior and improvements through
        enabling copy on write ``pd.options.mode.copy_on_write = True``

Returns
-------
Series
    An object of type Series.

See Also
--------
Series.rename_axis : Alter the name of the index.

        Examples
        --------
        >>> s = pd.Series([1, 2, 3])
        >>> s
        0    1
        1    2
        2    3
        dtype: int64

        >>> s.set_axis(['a', 'b', 'c'], axis=0)
        a    1
        b    2
        c    3
        dtype: int64
        """
        pass
    def __iter__(self) -> Iterator[S1]: ...
    def xs(
        self,
        key: Hashable,
        axis: AxisIndex = ...,
        level: Level | None = ...,
        drop_level: _bool = ...,
    ) -> Self: ...

class TimestampSeries(Series[Timestamp]):
    @property
    def dt(self) -> TimestampProperties: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __add__(self, other: TimedeltaSeries | np.timedelta64 | timedelta | BaseOffset) -> TimestampSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __radd__(self, other: TimedeltaSeries | np.timedelta64 | timedelta) -> TimestampSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    @overload  # type: ignore[override]
    def __sub__(
        self, other: Timestamp | datetime | TimestampSeries
    ) -> TimedeltaSeries: ...
    @overload
    def __sub__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta | TimedeltaSeries | TimedeltaIndex | np.timedelta64 | BaseOffset
        ),
    ) -> TimestampSeries: ...
    def __mul__(self, other: float | Series[int] | Series[float] | Sequence[float]) -> TimestampSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __truediv__(self, other: float | Series[int] | Series[float] | Sequence[float]) -> TimestampSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def mean(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timestamp: ...
    def median(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timestamp: ...
    def std(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timedelta: ...
    def diff(self, periods: int = ...) -> TimedeltaSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]

class TimedeltaSeries(Series[Timedelta]):
    # ignores needed because of mypy
    @overload  # type: ignore[override]
    def __add__(self, other: Period) -> PeriodSeries: ...
    @overload
    def __add__(
        self, other: datetime | Timestamp | TimestampSeries | DatetimeIndex
    ) -> TimestampSeries: ...
    @overload
    def __add__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: timedelta | Timedelta | np.timedelta64
    ) -> TimedeltaSeries: ...
    def __radd__(self, other: datetime | Timestamp | TimestampSeries) -> TimestampSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __mul__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: num | Sequence[num] | Series[int] | Series[float]
    ) -> TimedeltaSeries: ...
    def __sub__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta | Timedelta | TimedeltaSeries | TimedeltaIndex | np.timedelta64
        ),
    ) -> TimedeltaSeries: ...
    @overload  # type: ignore[override]
    def __truediv__(self, other: float | Sequence[float]) -> Self: ...
    @overload
    def __truediv__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta
            | TimedeltaSeries
            | np.timedelta64
            | TimedeltaIndex
            | Sequence[timedelta]
        ),
    ) -> Series[float]: ...
    def __rtruediv__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta
            | TimedeltaSeries
            | np.timedelta64
            | TimedeltaIndex
            | Sequence[timedelta]
        ),
    ) -> Series[float]: ...
    @overload  # type: ignore[override]
    def __floordiv__(self, other: float | Sequence[float]) -> Self: ...
    @overload
    def __floordiv__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta
            | TimedeltaSeries
            | np.timedelta64
            | TimedeltaIndex
            | Sequence[timedelta]
        ),
    ) -> Series[int]: ...
    def __rfloordiv__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        other: (
            timedelta
            | TimedeltaSeries
            | np.timedelta64
            | TimedeltaIndex
            | Sequence[timedelta]
        ),
    ) -> Series[int]: ...
    @property
    def dt(self) -> TimedeltaProperties: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def mean(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timedelta: ...
    def median(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timedelta: ...
    def std(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        axis: AxisIndex | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Timedelta: ...
    def diff(self, periods: int = ...) -> TimedeltaSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]

class PeriodSeries(Series[Period]):
    @property
    def dt(self) -> PeriodProperties: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def __sub__(self, other: PeriodSeries) -> OffsetSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
    def diff(self, periods: int = ...) -> OffsetSeries: ...  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]

class OffsetSeries(Series[BaseOffset]):
    @overload  # type: ignore[override]
    def __radd__(self, other: Period) -> PeriodSeries: ...
    @overload
    def __radd__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, other: BaseOffset
    ) -> OffsetSeries: ...

class IntervalSeries(Series[Interval[_OrderableT]], Generic[_OrderableT]):
    @property
    def array(self) -> IntervalArray: ...
    def diff(self, periods: int = ...) -> Never: ...
