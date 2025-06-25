from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
)
import datetime as dt
from re import Pattern
from typing import (
    Any,
    ClassVar,
    Literal,
    overload,
)

from matplotlib.axes import Axes as PlotAxes
import numpy as np
from pandas import (
    Period,
    Timedelta,
    Timestamp,
)
from pandas.core.arraylike import OpsMixin
from pandas.core.generic import NDFrame
from pandas.core.groupby.generic import DataFrameGroupBy
from pandas.core.groupby.grouper import Grouper
from pandas.core.indexers import BaseIndexer
from pandas.core.indexes.base import Index
from pandas.core.indexes.category import CategoricalIndex
from pandas.core.indexes.datetimes import DatetimeIndex
from pandas.core.indexes.interval import IntervalIndex
from pandas.core.indexes.multi import MultiIndex
from pandas.core.indexes.period import PeriodIndex
from pandas.core.indexes.timedeltas import TimedeltaIndex
from pandas.core.indexing import (
    _iLocIndexer,
    _IndexSliceTuple,
    _LocIndexer,
)
from pandas.core.interchange.dataframe_protocol import DataFrame as DataFrameXchg
from pandas.core.series import Series
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

from pandas._libs.lib import NoDefault
from pandas._libs.missing import NAType
from pandas._libs.tslibs import BaseOffset
from pandas._libs.tslibs.nattype import NaTType
from pandas._typing import (
    S1,
    AggFuncTypeBase,
    AggFuncTypeDictFrame,
    AggFuncTypeDictSeries,
    AggFuncTypeFrame,
    AnyArrayLike,
    ArrayLike,
    AstypeArg,
    Axes,
    Axis,
    AxisColumn,
    AxisIndex,
    CalculationMethod,
    ColspaceArgType,
    CompressionOptions,
    Dtype,
    FilePath,
    FillnaOptions,
    FormattersType,
    GroupByObjectNonScalar,
    HashableT,
    HashableT1,
    HashableT2,
    HashableT3,
    IgnoreRaise,
    IndexingInt,
    IndexLabel,
    IndexType,
    InterpolateOptions,
    IntervalClosedType,
    IntervalT,
    JoinHow,
    JsonFrameOrient,
    Label,
    Level,
    ListLike,
    ListLikeExceptSeriesAndStr,
    ListLikeU,
    MaskType,
    MergeHow,
    NaPosition,
    NDFrameT,
    ParquetEngine,
    QuantileInterpolation,
    RandomState,
    ReadBuffer,
    Renamer,
    ReplaceMethod,
    Scalar,
    ScalarT,
    SeriesByT,
    SortKind,
    StataDateFormat,
    StorageOptions,
    StrDtypeArg,
    StrLike,
    Suffixes,
    T as _T,
    TimestampConvention,
    TimeUnit,
    ValidationOptions,
    WriteBuffer,
    XMLParsers,
    npt,
    num,
)

from pandas.io.formats.style import Styler
from pandas.plotting import PlotAccessor

_str = str
_bool = bool

class _iLocIndexerFrame(_iLocIndexer):
    @overload
    def __getitem__(self, idx: tuple[int, int]) -> Scalar: ...
    @overload
    def __getitem__(self, idx: IndexingInt) -> Series: ...
    @overload
    def __getitem__(self, idx: tuple[IndexType | MaskType, int]) -> Series: ...
    @overload
    def __getitem__(self, idx: tuple[int, IndexType | MaskType]) -> Series: ...
    @overload
    def __getitem__(
        self,
        idx: (
            IndexType
            | MaskType
            | tuple[IndexType | MaskType, IndexType | MaskType]
            | tuple[slice]
        ),
    ) -> DataFrame: ...
    def __setitem__(
        self,
        idx: (
            int
            | IndexType
            | tuple[int, int]
            | tuple[IndexType, int]
            | tuple[IndexType, IndexType]
            | tuple[int, IndexType]
        ),
        value: Scalar | Series | DataFrame | np.ndarray | NAType | NaTType | None,
    ) -> None: ...

class _LocIndexerFrame(_LocIndexer):
    @overload
    def __getitem__(self, idx: Scalar) -> Series | DataFrame: ...
    @overload
    def __getitem__(
        self,
        idx: (
            IndexType
            | MaskType
            | Callable[[DataFrame], IndexType | MaskType | list[HashableT]]
            | list[HashableT]
            | tuple[
                IndexType
                | MaskType
                | list[HashableT]
                | slice
                | _IndexSliceTuple
                | Callable,
                MaskType | list[HashableT] | slice | Callable,
            ]
        ),
    ) -> DataFrame: ...
    @overload
    def __getitem__(  # pyright: ignore[reportOverlappingOverload]
        self,
        idx: tuple[
            int | StrLike | tuple[Scalar, ...] | Callable[[DataFrame], ScalarT],
            int | StrLike | tuple[Scalar, ...],
        ],
    ) -> Scalar: ...
    @overload
    def __getitem__(
        self,
        idx: (
            Callable[[DataFrame], ScalarT]
            | tuple[
                IndexType
                | MaskType
                | _IndexSliceTuple
                | Callable[
                    [DataFrame], ScalarT | list[HashableT] | IndexType | MaskType
                ],
                ScalarT | None,
            ]
            | None
        ),
    ) -> Series: ...
    @overload
    def __getitem__(self, idx: tuple[Scalar, slice]) -> Series | DataFrame: ...
    @overload
    def __setitem__(
        self,
        idx: MaskType | StrLike | _IndexSliceTuple | list[ScalarT] | IndexingInt,
        value: Scalar | NAType | NaTType | ArrayLike | Series | DataFrame | list | None,
    ) -> None: ...
    @overload
    def __setitem__(
        self,
        idx: tuple[_IndexSliceTuple, HashableT],
        value: Scalar | NAType | NaTType | ArrayLike | Series | list | None,
    ) -> None: ...

class DataFrame(NDFrame, OpsMixin):
    __hash__: ClassVar[None]  # type: ignore[assignment]

    @overload
    def __new__(
        cls,
        data: (
            ListLikeU
            | DataFrame
            | dict[Any, Any]
            | Iterable[ListLikeU | tuple[Hashable, ListLikeU] | dict[Any, Any]]
            | None
        ) = ...,
        index: Axes | None = ...,
        columns: Axes | None = ...,
        dtype=...,
        copy: _bool = ...,
    ) -> Self: ...
    @overload
    def __new__(
        cls,
        data: Scalar,
        index: Axes,
        columns: Axes,
        dtype=...,
        copy: _bool = ...,
    ) -> Self: ...
    def __dataframe__(
        self, nan_as_null: bool = ..., allow_copy: bool = ...
    ) -> DataFrameXchg: ...
    def __arrow_c_stream__(self, requested_schema: object | None = None) -> object: ...
    @property
    def axes(self) -> list[Index]: ...
    @property
    def shape(self) -> tuple[int, int]: ...
    @property
    def style(self) -> Styler: ...
    def items(self) -> Iterable[tuple[Hashable, Series]]:
        """
Iterate over (column name, Series) pairs.

Iterates over the DataFrame columns, returning a tuple with
the column name and the content as a Series.

Yields
------
label : object
    The column names for the DataFrame being iterated over.
content : Series
    The column entries belonging to each label, as a Series.

See Also
--------
DataFrame.iterrows : Iterate over DataFrame rows as
    (index, Series) pairs.
DataFrame.itertuples : Iterate over DataFrame rows as namedtuples
    of the values.

Examples
--------
>>> df = pd.DataFrame({'species': ['bear', 'bear', 'marsupial'],
...                   'population': [1864, 22000, 80000]},
...                   index=['panda', 'polar', 'koala'])
>>> df
        species   population
panda   bear      1864
polar   bear      22000
koala   marsupial 80000
>>> for label, content in df.items():
...     print(f'label: {label}')
...     print(f'content: {content}', sep='\n')
...
label: species
content:
panda         bear
polar         bear
koala    marsupial
Name: species, dtype: object
label: population
content:
panda     1864
polar    22000
koala    80000
Name: population, dtype: int64
        """
        pass
    def iterrows(self) -> Iterable[tuple[Hashable, Series]]: ...
    @overload
    def itertuples(
        self, index: _bool = ..., name: _str = ...
    ) -> Iterable[_PandasNamedTuple]: ...
    @overload
    def itertuples(
        self, index: _bool = ..., name: None = None
    ) -> Iterable[tuple[Any, ...]]: ...
    def __len__(self) -> int: ...
    @overload
    def dot(self, other: DataFrame | ArrayLike) -> DataFrame: ...
    @overload
    def dot(self, other: Series) -> Series: ...
    def __matmul__(self, other): ...
    def __rmatmul__(self, other): ...
    @overload
    @classmethod
    def from_dict(
        cls,
        data: dict[Any, Any],
        orient: Literal["index"],
        dtype: AstypeArg | None = ...,
        columns: Axes | None = ...,
    ) -> DataFrame: ...
    @overload
    @classmethod
    def from_dict(
        cls,
        data: dict[Any, Any],
        orient: Literal["columns", "tight"] = ...,
        dtype: AstypeArg | None = ...,
    ) -> DataFrame: ...
    def to_numpy(
        self,
        dtype: npt.DTypeLike | None = ...,
        copy: bool = ...,
        na_value: Scalar = ...,
    ) -> np.ndarray: ...
    @overload
    def to_dict(  # type: ignore[overload-overlap]
        self,
        orient: Literal["records"],
        *,
        into: MutableMapping | type[MutableMapping],
        index: Literal[True] = ...,
    ) -> list[MutableMapping[Hashable, Any]]: ...
    @overload
    def to_dict(
        self,
        orient: Literal["records"],
        *,
        into: type[dict] = ...,
        index: Literal[True] = ...,
    ) -> list[dict[Hashable, Any]]: ...
    @overload
    def to_dict(  # type: ignore[overload-overlap]
        self,
        orient: Literal["dict", "list", "series", "index"],
        *,
        into: MutableMapping | type[MutableMapping],
        index: Literal[True] = ...,
    ) -> MutableMapping[Hashable, Any]: ...
    @overload
    def to_dict(  # type: ignore[overload-overlap]
        self,
        orient: Literal["split", "tight"],
        *,
        into: MutableMapping | type[MutableMapping],
        index: bool = ...,
    ) -> MutableMapping[Hashable, Any]: ...
    @overload
    def to_dict(  # type: ignore[overload-overlap]
        self,
        orient: Literal["dict", "list", "series", "index"] = ...,
        *,
        into: MutableMapping | type[MutableMapping],
        index: Literal[True] = ...,
    ) -> MutableMapping[Hashable, Any]: ...
    @overload
    def to_dict(  # type: ignore[overload-overlap]
        self,
        orient: Literal["split", "tight"] = ...,
        *,
        into: MutableMapping | type[MutableMapping],
        index: bool = ...,
    ) -> MutableMapping[Hashable, Any]: ...
    @overload
    def to_dict(
        self,
        orient: Literal["dict", "list", "series", "index"] = ...,
        *,
        into: type[dict] = ...,
        index: Literal[True] = ...,
    ) -> dict[Hashable, Any]: ...
    @overload
    def to_dict(
        self,
        orient: Literal["split", "tight"] = ...,
        *,
        into: type[dict] = ...,
        index: bool = ...,
    ) -> dict[Hashable, Any]: ...
    def to_gbq(
        self,
        destination_table: str,
        project_id: str | None = ...,
        chunksize: int | None = ...,
        reauth: bool = ...,
        if_exists: Literal["fail", "replace", "append"] = ...,
        auth_local_webserver: bool = ...,
        table_schema: list[dict[str, str]] | None = ...,
        location: str | None = ...,
        progress_bar: bool = ...,
        # Google type, not available
        credentials: Any = ...,
    ) -> None: ...
    @classmethod
    def from_records(
        cls, data, index=..., exclude=..., columns=..., coerce_float=..., nrows=...
    ) -> DataFrame: ...
    def to_records(
        self,
        index: _bool = ...,
        column_dtypes: (
            _str | npt.DTypeLike | Mapping[HashableT1, npt.DTypeLike] | None
        ) = ...,
        index_dtypes: (
            _str | npt.DTypeLike | Mapping[HashableT2, npt.DTypeLike] | None
        ) = ...,
    ) -> np.recarray: ...
    def to_stata(
        self,
        path: FilePath | WriteBuffer[bytes],
        *,
        convert_dates: dict[HashableT1, StataDateFormat] | None = ...,
        write_index: _bool = ...,
        byteorder: Literal["<", ">", "little", "big"] | None = ...,
        time_stamp: dt.datetime | None = ...,
        data_label: _str | None = ...,
        variable_labels: dict[HashableT2, str] | None = ...,
        version: Literal[114, 117, 118, 119] | None = ...,
        convert_strl: list[HashableT3] | None = ...,
        compression: CompressionOptions = ...,
        storage_options: StorageOptions = ...,
        value_labels: dict[Hashable, dict[float, str]] | None = ...,
    ) -> None:
        """
Export DataFrame object to Stata dta format.

Writes the DataFrame to a Stata dataset file.
"dta" files contain a Stata dataset.

Parameters
----------
path : str, path object, or buffer
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``write()`` function.

convert_dates : dict
    Dictionary mapping columns containing datetime types to stata
    internal format to use when writing the dates. Options are 'tc',
    'td', 'tm', 'tw', 'th', 'tq', 'ty'. Column can be either an integer
    or a name. Datetime columns that do not have a conversion type
    specified will be converted to 'tc'. Raises NotImplementedError if
    a datetime column has timezone information.
write_index : bool
    Write the index to Stata dataset.
byteorder : str
    Can be ">", "<", "little", or "big". default is `sys.byteorder`.
time_stamp : datetime
    A datetime to use as file creation date.  Default is the current
    time.
data_label : str, optional
    A label for the data set.  Must be 80 characters or smaller.
variable_labels : dict
    Dictionary containing columns as keys and variable labels as
    values. Each label must be 80 characters or smaller.
version : {114, 117, 118, 119, None}, default 114
    Version to use in the output dta file. Set to None to let pandas
    decide between 118 or 119 formats depending on the number of
    columns in the frame. Version 114 can be read by Stata 10 and
    later. Version 117 can be read by Stata 13 or later. Version 118
    is supported in Stata 14 and later. Version 119 is supported in
    Stata 15 and later. Version 114 limits string variables to 244
    characters or fewer while versions 117 and later allow strings
    with lengths up to 2,000,000 characters. Versions 118 and 119
    support Unicode characters, and version 119 supports more than
    32,767 variables.

    Version 119 should usually only be used when the number of
    variables exceeds the capacity of dta format 118. Exporting
    smaller datasets in format 119 may have unintended consequences,
    and, as of November 2020, Stata SE cannot read version 119 files.

convert_strl : list, optional
    List of column names to convert to string columns to Stata StrL
    format. Only available if version is 117.  Storing strings in the
    StrL format can produce smaller dta files if strings have more than
    8 characters and values are repeated.
compression : str or dict, default 'infer'
    For on-the-fly compression of the output data. If 'infer' and 'path' is
    path-like, then detect compression from the following extensions: '.gz',
    '.bz2', '.zip', '.xz', '.zst', '.tar', '.tar.gz', '.tar.xz' or '.tar.bz2'
    (otherwise no compression).
    Set to ``None`` for no compression.
    Can also be a dict with key ``'method'`` set
    to one of {``'zip'``, ``'gzip'``, ``'bz2'``, ``'zstd'``, ``'xz'``, ``'tar'``} and
    other key-value pairs are forwarded to
    ``zipfile.ZipFile``, ``gzip.GzipFile``,
    ``bz2.BZ2File``, ``zstandard.ZstdCompressor``, ``lzma.LZMAFile`` or
    ``tarfile.TarFile``, respectively.
    As an example, the following could be passed for faster compression and to create
    a reproducible gzip archive:
    ``compression={'method': 'gzip', 'compresslevel': 1, 'mtime': 1}``.

    .. versionadded:: 1.5.0
        Added support for `.tar` files.

    .. versionchanged:: 1.4.0 Zstandard support.

storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

value_labels : dict of dicts
    Dictionary containing columns as keys and dictionaries of column value
    to labels as values. Labels for a single variable must be 32,000
    characters or smaller.

    .. versionadded:: 1.4.0

Raises
------
NotImplementedError
    * If datetimes contain timezone information
    * Column dtype is not representable in Stata
ValueError
    * Columns listed in convert_dates are neither datetime64[ns]
      or datetime.datetime
    * Column listed in convert_dates is not in DataFrame
    * Categorical label contains more than 32,000 characters

See Also
--------
read_stata : Import Stata data files.
io.stata.StataWriter : Low-level writer for Stata data files.
io.stata.StataWriter117 : Low-level writer for version 117 files.

Examples
--------
>>> df = pd.DataFrame({'animal': ['falcon', 'parrot', 'falcon',
...                               'parrot'],
...                    'speed': [350, 18, 361, 15]})
>>> df.to_stata('animals.dta')  # doctest: +SKIP
        """
        pass
    def to_feather(self, path: FilePath | WriteBuffer[bytes], **kwargs) -> None: ...
    @overload
    def to_parquet(
        self,
        path: FilePath | WriteBuffer[bytes],
        engine: ParquetEngine = ...,
        compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"] | None = ...,
        index: bool | None = ...,
        partition_cols: list[HashableT] | None = ...,
        storage_options: StorageOptions = ...,
        **kwargs: Any,
    ) -> None:
        """
Write a DataFrame to the binary parquet format.

This function writes the dataframe as a `parquet file
<https://parquet.apache.org/>`_. You can choose different parquet
backends, and have the option of compression. See
:ref:`the user guide <io.parquet>` for more details.

Parameters
----------
path : str, path object, file-like object, or None, default None
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``write()`` function. If None, the result is
    returned as bytes. If a string or path, it will be used as Root Directory
    path when writing a partitioned dataset.
engine : {'auto', 'pyarrow', 'fastparquet'}, default 'auto'
    Parquet library to use. If 'auto', then the option
    ``io.parquet.engine`` is used. The default ``io.parquet.engine``
    behavior is to try 'pyarrow', falling back to 'fastparquet' if
    'pyarrow' is unavailable.
compression : str or None, default 'snappy'
    Name of the compression to use. Use ``None`` for no compression.
    Supported options: 'snappy', 'gzip', 'brotli', 'lz4', 'zstd'.
index : bool, default None
    If ``True``, include the dataframe's index(es) in the file output.
    If ``False``, they will not be written to the file.
    If ``None``, similar to ``True`` the dataframe's index(es)
    will be saved. However, instead of being saved as values,
    the RangeIndex will be stored as a range in the metadata so it
    doesn't require much space and is faster. Other indexes will
    be included as columns in the file output.
partition_cols : list, optional, default None
    Column names by which to partition the dataset.
    Columns are partitioned in the order they are given.
    Must be None if path is not a string.
storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

**kwargs
    Additional arguments passed to the parquet library. See
    :ref:`pandas io <io.parquet>` for more details.

Returns
-------
bytes if no path argument is provided else None

See Also
--------
read_parquet : Read a parquet file.
DataFrame.to_orc : Write an orc file.
DataFrame.to_csv : Write a csv file.
DataFrame.to_sql : Write to a sql table.
DataFrame.to_hdf : Write to hdf.

Notes
-----
This function requires either the `fastparquet
<https://pypi.org/project/fastparquet>`_ or `pyarrow
<https://arrow.apache.org/docs/python/>`_ library.

Examples
--------
>>> df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
>>> df.to_parquet('df.parquet.gzip',
...               compression='gzip')  # doctest: +SKIP
>>> pd.read_parquet('df.parquet.gzip')  # doctest: +SKIP
   col1  col2
0     1     3
1     2     4

If you want to get a buffer to the parquet content you can use a io.BytesIO
object, as long as you don't use partition_cols, which creates multiple files.

>>> import io
>>> f = io.BytesIO()
>>> df.to_parquet(f)
>>> f.seek(0)
0
>>> content = f.read()
        """
        pass
    @overload
    def to_parquet(
        self,
        path: None = ...,
        engine: ParquetEngine = ...,
        compression: Literal["snappy", "gzip", "brotli", "lz4", "zstd"] | None = ...,
        index: bool | None = ...,
        partition_cols: list[HashableT] | None = ...,
        storage_options: StorageOptions = ...,
        **kwargs: Any,
    ) -> bytes: ...
    @overload
    def to_orc(
        self,
        path: FilePath | WriteBuffer[bytes],
        *,
        engine: Literal["pyarrow"] = ...,
        index: bool | None = ...,
        engine_kwargs: dict[str, Any] | None = ...,
    ) -> None: ...
    @overload
    def to_orc(
        self,
        path: None = ...,
        *,
        engine: Literal["pyarrow"] = ...,
        index: bool | None = ...,
        engine_kwargs: dict[str, Any] | None = ...,
    ) -> bytes: ...
    @overload
    def to_html(
        self,
        buf: FilePath | WriteBuffer[str],
        columns: list[HashableT] | Index | Series | None = ...,
        col_space: ColspaceArgType | None = ...,
        header: _bool = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters: (
            list[Callable[[object], str]]
            | tuple[Callable[[object], str], ...]
            | Mapping[Hashable, Callable[[object], str]]
            | None
        ) = ...,
        float_format: Callable[[float], str] | None = ...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        justify: (
            Literal[
                "left",
                "right",
                "center",
                "justify",
                "justify-all",
                "start",
                "end",
                "inherit",
                "match-parent",
                "initial",
                "unset",
            ]
            | None
        ) = ...,
        max_rows: int | None = ...,
        max_cols: int | None = ...,
        show_dimensions: _bool = ...,
        decimal: _str = ...,
        bold_rows: _bool = ...,
        classes: Sequence[str] | None = ...,
        escape: _bool = ...,
        notebook: _bool = ...,
        border: int | None = ...,
        table_id: _str | None = ...,
        render_links: _bool = ...,
        encoding: _str | None = ...,
    ) -> None: ...
    @overload
    def to_html(
        self,
        buf: None = ...,
        columns: Sequence[HashableT] | None = ...,
        col_space: ColspaceArgType | None = ...,
        header: _bool = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters: (
            list[Callable[[object], str]]
            | tuple[Callable[[object], str], ...]
            | Mapping[Hashable, Callable[[object], str]]
            | None
        ) = ...,
        float_format: Callable[[float], str] | None = ...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        justify: (
            Literal[
                "left",
                "right",
                "center",
                "justify",
                "justify-all",
                "start",
                "end",
                "inherit",
                "match-parent",
                "initial",
                "unset",
            ]
            | None
        ) = ...,
        max_rows: int | None = ...,
        max_cols: int | None = ...,
        show_dimensions: _bool = ...,
        decimal: _str = ...,
        bold_rows: _bool = ...,
        classes: Sequence[str] | None = ...,
        escape: _bool = ...,
        notebook: _bool = ...,
        border: int | None = ...,
        table_id: _str | None = ...,
        render_links: _bool = ...,
        encoding: _str | None = ...,
    ) -> _str: ...
    @overload
    def to_xml(
        self,
        path_or_buffer: FilePath | WriteBuffer[bytes] | WriteBuffer[str],
        index: bool = ...,
        root_name: str = ...,
        row_name: str = ...,
        na_rep: str | None = ...,
        attr_cols: list[HashableT1] | None = ...,
        elem_cols: list[HashableT2] | None = ...,
        namespaces: dict[str | None, str] | None = ...,
        prefix: str | None = ...,
        encoding: str = ...,
        xml_declaration: bool = ...,
        pretty_print: bool = ...,
        parser: XMLParsers = ...,
        stylesheet: FilePath | ReadBuffer[str] | ReadBuffer[bytes] | None = ...,
        compression: CompressionOptions = ...,
        storage_options: StorageOptions = ...,
    ) -> None:
        """
Render a DataFrame to an XML document.

.. versionadded:: 1.3.0

Parameters
----------
path_or_buffer : str, path object, file-like object, or None, default None
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a ``write()`` function. If None, the result is returned
    as a string.
index : bool, default True
    Whether to include index in XML document.
root_name : str, default 'data'
    The name of root element in XML document.
row_name : str, default 'row'
    The name of row element in XML document.
na_rep : str, optional
    Missing data representation.
attr_cols : list-like, optional
    List of columns to write as attributes in row element.
    Hierarchical columns will be flattened with underscore
    delimiting the different levels.
elem_cols : list-like, optional
    List of columns to write as children in row element. By default,
    all columns output as children of row element. Hierarchical
    columns will be flattened with underscore delimiting the
    different levels.
namespaces : dict, optional
    All namespaces to be defined in root element. Keys of dict
    should be prefix names and values of dict corresponding URIs.
    Default namespaces should be given empty string key. For
    example, ::

        namespaces = {"": "https://example.com"}

prefix : str, optional
    Namespace prefix to be used for every element and/or attribute
    in document. This should be one of the keys in ``namespaces``
    dict.
encoding : str, default 'utf-8'
    Encoding of the resulting document.
xml_declaration : bool, default True
    Whether to include the XML declaration at start of document.
pretty_print : bool, default True
    Whether output should be pretty printed with indentation and
    line breaks.
parser : {'lxml','etree'}, default 'lxml'
    Parser module to use for building of tree. Only 'lxml' and
    'etree' are supported. With 'lxml', the ability to use XSLT
    stylesheet is supported.
stylesheet : str, path object or file-like object, optional
    A URL, file-like object, or a raw string containing an XSLT
    script used to transform the raw XML output. Script should use
    layout of elements and attributes from original output. This
    argument requires ``lxml`` to be installed. Only XSLT 1.0
    scripts and not later versions is currently supported.
compression : str or dict, default 'infer'
    For on-the-fly compression of the output data. If 'infer' and 'path_or_buffer' is
    path-like, then detect compression from the following extensions: '.gz',
    '.bz2', '.zip', '.xz', '.zst', '.tar', '.tar.gz', '.tar.xz' or '.tar.bz2'
    (otherwise no compression).
    Set to ``None`` for no compression.
    Can also be a dict with key ``'method'`` set
    to one of {``'zip'``, ``'gzip'``, ``'bz2'``, ``'zstd'``, ``'xz'``, ``'tar'``} and
    other key-value pairs are forwarded to
    ``zipfile.ZipFile``, ``gzip.GzipFile``,
    ``bz2.BZ2File``, ``zstandard.ZstdCompressor``, ``lzma.LZMAFile`` or
    ``tarfile.TarFile``, respectively.
    As an example, the following could be passed for faster compression and to create
    a reproducible gzip archive:
    ``compression={'method': 'gzip', 'compresslevel': 1, 'mtime': 1}``.

    .. versionadded:: 1.5.0
        Added support for `.tar` files.

    .. versionchanged:: 1.4.0 Zstandard support.

storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

Returns
-------
None or str
    If ``io`` is None, returns the resulting XML format as a
    string. Otherwise returns None.

See Also
--------
to_json : Convert the pandas object to a JSON string.
to_html : Convert DataFrame to a html.

Examples
--------
>>> df = pd.DataFrame({'shape': ['square', 'circle', 'triangle'],
...                    'degrees': [360, 360, 180],
...                    'sides': [4, np.nan, 3]})

>>> df.to_xml()  # doctest: +SKIP
<?xml version='1.0' encoding='utf-8'?>
<data>
  <row>
    <index>0</index>
    <shape>square</shape>
    <degrees>360</degrees>
    <sides>4.0</sides>
  </row>
  <row>
    <index>1</index>
    <shape>circle</shape>
    <degrees>360</degrees>
    <sides/>
  </row>
  <row>
    <index>2</index>
    <shape>triangle</shape>
    <degrees>180</degrees>
    <sides>3.0</sides>
  </row>
</data>

>>> df.to_xml(attr_cols=[
...           'index', 'shape', 'degrees', 'sides'
...           ])  # doctest: +SKIP
<?xml version='1.0' encoding='utf-8'?>
<data>
  <row index="0" shape="square" degrees="360" sides="4.0"/>
  <row index="1" shape="circle" degrees="360"/>
  <row index="2" shape="triangle" degrees="180" sides="3.0"/>
</data>

>>> df.to_xml(namespaces={"doc": "https://example.com"},
...           prefix="doc")  # doctest: +SKIP
<?xml version='1.0' encoding='utf-8'?>
<doc:data xmlns:doc="https://example.com">
  <doc:row>
    <doc:index>0</doc:index>
    <doc:shape>square</doc:shape>
    <doc:degrees>360</doc:degrees>
    <doc:sides>4.0</doc:sides>
  </doc:row>
  <doc:row>
    <doc:index>1</doc:index>
    <doc:shape>circle</doc:shape>
    <doc:degrees>360</doc:degrees>
    <doc:sides/>
  </doc:row>
  <doc:row>
    <doc:index>2</doc:index>
    <doc:shape>triangle</doc:shape>
    <doc:degrees>180</doc:degrees>
    <doc:sides>3.0</doc:sides>
  </doc:row>
</doc:data>
        """
        pass
    @overload
    def to_xml(
        self,
        path_or_buffer: Literal[None] = ...,
        index: bool = ...,
        root_name: str | None = ...,
        row_name: str | None = ...,
        na_rep: str | None = ...,
        attr_cols: list[HashableT1] | None = ...,
        elem_cols: list[HashableT2] | None = ...,
        namespaces: dict[str | None, str] | None = ...,
        prefix: str | None = ...,
        encoding: str = ...,
        xml_declaration: bool | None = ...,
        pretty_print: bool | None = ...,
        parser: str | None = ...,
        stylesheet: FilePath | ReadBuffer[str] | ReadBuffer[bytes] | None = ...,
        compression: CompressionOptions = ...,
        storage_options: StorageOptions = ...,
    ) -> str: ...
    def info(
        self,
        verbose: bool | None = ...,
        buf: WriteBuffer[str] = ...,
        max_cols: int | None = ...,
        memory_usage: bool | Literal["deep"] | None = ...,
        show_counts: bool | None = ...,
    ) -> None:
        """
Print a concise summary of a DataFrame.

This method prints information about a DataFrame including
the index dtype and columns, non-null values and memory usage.

Parameters
----------
verbose : bool, optional
    Whether to print the full summary. By default, the setting in
    ``pandas.options.display.max_info_columns`` is followed.
buf : writable buffer, defaults to sys.stdout
    Where to send the output. By default, the output is printed to
    sys.stdout. Pass a writable buffer if you need to further process
    the output.
max_cols : int, optional
    When to switch from the verbose to the truncated output. If the
    DataFrame has more than `max_cols` columns, the truncated output
    is used. By default, the setting in
    ``pandas.options.display.max_info_columns`` is used.
memory_usage : bool, str, optional
    Specifies whether total memory usage of the DataFrame
    elements (including the index) should be displayed. By default,
    this follows the ``pandas.options.display.memory_usage`` setting.

    True always show memory usage. False never shows memory usage.
    A value of 'deep' is equivalent to "True with deep introspection".
    Memory usage is shown in human-readable units (base-2
    representation). Without deep introspection a memory estimation is
    made based in column dtype and number of rows assuming values
    consume the same memory amount for corresponding dtypes. With deep
    memory introspection, a real memory usage calculation is performed
    at the cost of computational resources. See the
    :ref:`Frequently Asked Questions <df-memory-usage>` for more
    details.
show_counts : bool, optional
    Whether to show the non-null counts. By default, this is shown
    only if the DataFrame is smaller than
    ``pandas.options.display.max_info_rows`` and
    ``pandas.options.display.max_info_columns``. A value of True always
    shows the counts, and False never shows the counts.

Returns
-------
None
    This method prints a summary of a DataFrame and returns None.

See Also
--------
DataFrame.describe: Generate descriptive statistics of DataFrame
    columns.
DataFrame.memory_usage: Memory usage of DataFrame columns.

Examples
--------
>>> int_values = [1, 2, 3, 4, 5]
>>> text_values = ['alpha', 'beta', 'gamma', 'delta', 'epsilon']
>>> float_values = [0.0, 0.25, 0.5, 0.75, 1.0]
>>> df = pd.DataFrame({"int_col": int_values, "text_col": text_values,
...                   "float_col": float_values})
>>> df
    int_col text_col  float_col
0        1    alpha       0.00
1        2     beta       0.25
2        3    gamma       0.50
3        4    delta       0.75
4        5  epsilon       1.00

Prints information of all columns:

>>> df.info(verbose=True)
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 5 entries, 0 to 4
Data columns (total 3 columns):
 #   Column     Non-Null Count  Dtype
---  ------     --------------  -----
 0   int_col    5 non-null      int64
 1   text_col   5 non-null      object
 2   float_col  5 non-null      float64
dtypes: float64(1), int64(1), object(1)
memory usage: 248.0+ bytes

Prints a summary of columns count and its dtypes but not per column
information:

>>> df.info(verbose=False)
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 5 entries, 0 to 4
Columns: 3 entries, int_col to float_col
dtypes: float64(1), int64(1), object(1)
memory usage: 248.0+ bytes

Pipe output of DataFrame.info to buffer instead of sys.stdout, get
buffer content and writes to a text file:

>>> import io
>>> buffer = io.StringIO()
>>> df.info(buf=buffer)
>>> s = buffer.getvalue()
>>> with open("df_info.txt", "w",
...           encoding="utf-8") as f:  # doctest: +SKIP
...     f.write(s)
260

The `memory_usage` parameter allows deep introspection mode, specially
useful for big DataFrames and fine-tune memory optimization:

>>> random_strings_array = np.random.choice(['a', 'b', 'c'], 10 ** 6)
>>> df = pd.DataFrame({
...     'column_1': np.random.choice(['a', 'b', 'c'], 10 ** 6),
...     'column_2': np.random.choice(['a', 'b', 'c'], 10 ** 6),
...     'column_3': np.random.choice(['a', 'b', 'c'], 10 ** 6)
... })
>>> df.info()
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1000000 entries, 0 to 999999
Data columns (total 3 columns):
 #   Column    Non-Null Count    Dtype
---  ------    --------------    -----
 0   column_1  1000000 non-null  object
 1   column_2  1000000 non-null  object
 2   column_3  1000000 non-null  object
dtypes: object(3)
memory usage: 22.9+ MB

>>> df.info(memory_usage='deep')
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 1000000 entries, 0 to 999999
Data columns (total 3 columns):
 #   Column    Non-Null Count    Dtype
---  ------    --------------    -----
 0   column_1  1000000 non-null  object
 1   column_2  1000000 non-null  object
 2   column_3  1000000 non-null  object
dtypes: object(3)
memory usage: 165.9 MB
        """
        pass
    def memory_usage(self, index: _bool = ..., deep: _bool = ...) -> Series: ...
    def transpose(self, *args, copy: _bool = ...) -> DataFrame: ...
    @property
    def T(self) -> DataFrame: ...
    def __getattr__(self, name: str) -> Series: ...
    @overload
    def __getitem__(self, key: Scalar | tuple[Hashable, ...]) -> Series: ...  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
    @overload
    def __getitem__(self, key: Iterable[Hashable] | slice) -> DataFrame: ...
    @overload
    def __getitem__(self, key: Hashable) -> Series: ...
    def isetitem(
        self, loc: int | Sequence[int], value: Scalar | ArrayLike | list[Any]
    ) -> None: ...
    def __setitem__(self, key, value) -> None: ...
    @overload
    def query(self, expr: _str, *, inplace: Literal[True], **kwargs) -> None: ...
    @overload
    def query(
        self, expr: _str, *, inplace: Literal[False] = ..., **kwargs
    ) -> DataFrame: ...
    def eval(self, expr: _str, *, inplace: _bool = ..., **kwargs): ...
    AstypeArgExt: TypeAlias = (
        AstypeArg
        | Literal[
            "number",
            "datetime64",
            "datetime",
            "integer",
            "timedelta",
            "timedelta64",
            "datetimetz",
            "datetime64[ns]",
        ]
    )
    AstypeArgExtList: TypeAlias = AstypeArgExt | list[AstypeArgExt]
    @overload
    def select_dtypes(
        self, include: StrDtypeArg, exclude: AstypeArgExtList | None = ...
    ) -> Never: ...
    @overload
    def select_dtypes(
        self, include: AstypeArgExtList | None, exclude: StrDtypeArg
    ) -> Never: ...
    @overload
    def select_dtypes(self, exclude: StrDtypeArg) -> Never: ...
    @overload
    def select_dtypes(self, include: list[Never], exclude: list[Never]) -> Never: ...
    @overload
    def select_dtypes(
        self,
        include: AstypeArgExtList,
        exclude: AstypeArgExtList | None = ...,
    ) -> DataFrame: ...
    @overload
    def select_dtypes(
        self,
        include: AstypeArgExtList | None,
        exclude: AstypeArgExtList,
    ) -> DataFrame: ...
    @overload
    def select_dtypes(
        self,
        exclude: AstypeArgExtList,
    ) -> DataFrame: ...
    def insert(
        self,
        loc: int,
        column,
        value: Scalar | ListLikeU | None,
        allow_duplicates: _bool = ...,
    ) -> None: ...
    def assign(self, **kwargs) -> DataFrame: ...
    def align(
        self,
        other: NDFrameT,
        join: JoinHow = ...,
        axis: Axis | None = ...,
        level: Level | None = ...,
        copy: _bool = ...,
        fill_value=...,
        method: FillnaOptions | None = ...,
        limit: int | None = ...,
        fill_axis: Axis = ...,
        broadcast_axis: Axis | None = ...,
    ) -> tuple[DataFrame, NDFrameT]: ...
    def reindex(
        self,
        labels: Axes | None = ...,
        index: Axes | None = ...,
        columns: Axes | None = ...,
        axis: Axis | None = ...,
        method: FillnaOptions | Literal["nearest"] | None = ...,
        copy: bool = ...,
        level: int | _str = ...,
        fill_value: Scalar | None = ...,
        limit: int | None = ...,
        tolerance: float | None = ...,
    ) -> DataFrame:
        """
Conform DataFrame to new index with optional filling logic.

Places NA/NaN in locations having no value in the previous index. A new object
is produced unless the new index is equivalent to the current one and
``copy=False``.

Parameters
----------

labels : array-like, optional
    New labels / index to conform the axis specified by 'axis' to.
index : array-like, optional
    New labels for the index. Preferably an Index object to avoid
    duplicating data.
columns : array-like, optional
    New labels for the columns. Preferably an Index object to avoid
    duplicating data.
axis : int or str, optional
    Axis to target. Can be either the axis name ('index', 'columns')
    or number (0, 1).
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
DataFrame with changed index.

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
    @overload
    def rename(
        self,
        mapper: Renamer | None = ...,
        *,
        index: Renamer | None = ...,
        columns: Renamer | None = ...,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: Literal[True],
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def rename(
        self,
        mapper: Renamer | None = ...,
        *,
        index: Renamer | None = ...,
        columns: Renamer | None = ...,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: Literal[False] = ...,
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> DataFrame: ...
    @overload
    def rename(
        self,
        mapper: Renamer | None = ...,
        *,
        index: Renamer | None = ...,
        columns: Renamer | None = ...,
        axis: Axis | None = ...,
        copy: bool = ...,
        inplace: bool = ...,
        level: Level | None = ...,
        errors: IgnoreRaise = ...,
    ) -> DataFrame | None: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series | DataFrame | None = ...,
        *,
        axis: Axis | None = ...,
        limit: int = ...,
        downcast: dict | None = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series | DataFrame | None = ...,
        *,
        axis: Axis | None = ...,
        limit: int = ...,
        downcast: dict | None = ...,
        inplace: Literal[False] = ...,
    ) -> DataFrame: ...
    @overload
    def fillna(
        self,
        value: Scalar | NAType | dict | Series | DataFrame | None = ...,
        *,
        axis: Axis | None = ...,
        inplace: _bool | None = ...,
        limit: int = ...,
        downcast: dict | None = ...,
    ) -> DataFrame | None: ...
    @overload
    def replace(
        self,
        to_replace=...,
        value: Scalar | NAType | Sequence | Mapping | Pattern | None = ...,
        *,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def replace(
        self,
        to_replace=...,
        value: Scalar | NAType | Sequence | Mapping | Pattern | None = ...,
        *,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
    ) -> DataFrame: ...
    @overload
    def replace(
        self,
        to_replace=...,
        value: Scalar | NAType | Sequence | Mapping | Pattern | None = ...,
        *,
        inplace: _bool | None = ...,
        limit: int | None = ...,
        regex=...,
        method: ReplaceMethod = ...,
    ) -> DataFrame | None: ...
    def shift(
        self,
        periods: int = ...,
        freq=...,
        axis: Axis = ...,
        fill_value: Hashable | None = ...,
    ) -> DataFrame:
        """
Shift index by desired number of periods with an optional time `freq`.

When `freq` is not passed, shift the index without realigning the data.
If `freq` is passed (in this case, the index must be date or datetime,
or it will raise a `NotImplementedError`), the index will be
increased using the periods and the `freq`. `freq` can be inferred
when specified as "infer" as long as either freq or inferred_freq
attribute is set in the index.

Parameters
----------
periods : int or Sequence
    Number of periods to shift. Can be positive or negative.
    If an iterable of ints, the data will be shifted once by each int.
    This is equivalent to shifting by one value at a time and
    concatenating all resulting frames. The resulting columns will have
    the shift suffixed to their column names. For multiple periods,
    axis must not be 1.
freq : DateOffset, tseries.offsets, timedelta, or str, optional
    Offset to use from the tseries module or time rule (e.g. 'EOM').
    If `freq` is specified then the index values are shifted but the
    data is not realigned. That is, use `freq` if you would like to
    extend the index when shifting and preserve the original data.
    If `freq` is specified as "infer" then it will be inferred from
    the freq or inferred_freq attributes of the index. If neither of
    those attributes exist, a ValueError is thrown.
axis : {0 or 'index', 1 or 'columns', None}, default None
    Shift direction. For `Series` this parameter is unused and defaults to 0.
fill_value : object, optional
    The scalar value to use for newly introduced missing values.
    the default depends on the dtype of `self`.
    For numeric data, ``np.nan`` is used.
    For datetime, timedelta, or period data, etc. :attr:`NaT` is used.
    For extension dtypes, ``self.dtype.na_value`` is used.
suffix : str, optional
    If str and periods is an iterable, this is added after the column
    name and before the shift value for each shifted column name.

Returns
-------
DataFrame
    Copy of input object, shifted.

See Also
--------
Index.shift : Shift values of Index.
DatetimeIndex.shift : Shift values of DatetimeIndex.
PeriodIndex.shift : Shift values of PeriodIndex.

Examples
--------
>>> df = pd.DataFrame({"Col1": [10, 20, 15, 30, 45],
...                    "Col2": [13, 23, 18, 33, 48],
...                    "Col3": [17, 27, 22, 37, 52]},
...                   index=pd.date_range("2020-01-01", "2020-01-05"))
>>> df
            Col1  Col2  Col3
2020-01-01    10    13    17
2020-01-02    20    23    27
2020-01-03    15    18    22
2020-01-04    30    33    37
2020-01-05    45    48    52

>>> df.shift(periods=3)
            Col1  Col2  Col3
2020-01-01   NaN   NaN   NaN
2020-01-02   NaN   NaN   NaN
2020-01-03   NaN   NaN   NaN
2020-01-04  10.0  13.0  17.0
2020-01-05  20.0  23.0  27.0

>>> df.shift(periods=1, axis="columns")
            Col1  Col2  Col3
2020-01-01   NaN    10    13
2020-01-02   NaN    20    23
2020-01-03   NaN    15    18
2020-01-04   NaN    30    33
2020-01-05   NaN    45    48

>>> df.shift(periods=3, fill_value=0)
            Col1  Col2  Col3
2020-01-01     0     0     0
2020-01-02     0     0     0
2020-01-03     0     0     0
2020-01-04    10    13    17
2020-01-05    20    23    27

>>> df.shift(periods=3, freq="D")
            Col1  Col2  Col3
2020-01-04    10    13    17
2020-01-05    20    23    27
2020-01-06    15    18    22
2020-01-07    30    33    37
2020-01-08    45    48    52

>>> df.shift(periods=3, freq="infer")
            Col1  Col2  Col3
2020-01-04    10    13    17
2020-01-05    20    23    27
2020-01-06    15    18    22
2020-01-07    30    33    37
2020-01-08    45    48    52

>>> df['Col1'].shift(periods=[0, 1, 2])
            Col1_0  Col1_1  Col1_2
2020-01-01      10     NaN     NaN
2020-01-02      20    10.0     NaN
2020-01-03      15    20.0    10.0
2020-01-04      30    15.0    20.0
2020-01-05      45    30.0    15.0
        """
        pass
    @overload
    def set_index(
        self,
        keys: (
            Label | Series | Index | np.ndarray | Iterator[HashableT] | list[HashableT]
        ),
        *,
        drop: _bool = ...,
        append: _bool = ...,
        verify_integrity: _bool = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def set_index(
        self,
        keys: (
            Label | Series | Index | np.ndarray | Iterator[HashableT] | list[HashableT]
        ),
        *,
        drop: _bool = ...,
        append: _bool = ...,
        verify_integrity: _bool = ...,
        inplace: Literal[False] = ...,
    ) -> DataFrame: ...
    @overload
    def reset_index(
        self,
        level: Level | Sequence[Level] = ...,
        *,
        drop: _bool = ...,
        col_level: int | _str = ...,
        col_fill: Hashable = ...,
        inplace: Literal[True],
        allow_duplicates: _bool = ...,
        names: Hashable | list[HashableT] = ...,
    ) -> None: ...
    @overload
    def reset_index(
        self,
        level: Level | Sequence[Level] = ...,
        *,
        col_level: int | _str = ...,
        col_fill: Hashable = ...,
        drop: _bool = ...,
        inplace: Literal[False] = ...,
        allow_duplicates: _bool = ...,
        names: Hashable | list[HashableT] = ...,
    ) -> DataFrame: ...
    @overload
    def reset_index(
        self,
        level: Level | Sequence[Level] = ...,
        *,
        drop: _bool = ...,
        inplace: _bool | None = ...,
        col_level: int | _str = ...,
        col_fill: Hashable = ...,
        allow_duplicates: _bool = ...,
        names: Hashable | list[HashableT] = ...,
    ) -> DataFrame | None: ...
    def isna(self) -> DataFrame:
        """
Detect missing values.

Return a boolean same-sized object indicating if the values are NA.
NA values, such as None or :attr:`numpy.NaN`, gets mapped to True
values.
Everything else gets mapped to False values. Characters such as empty
strings ``''`` or :attr:`numpy.inf` are not considered NA values
(unless you set ``pandas.options.mode.use_inf_as_na = True``).

Returns
-------
DataFrame
    Mask of bool values for each element in DataFrame that
    indicates whether an element is an NA value.

See Also
--------
DataFrame.isnull : Alias of isna.
DataFrame.notna : Boolean inverse of isna.
DataFrame.dropna : Omit axes labels with missing values.
isna : Top-level isna.

Examples
--------
Show which entries in a DataFrame are NA.

>>> df = pd.DataFrame(dict(age=[5, 6, np.nan],
...                        born=[pd.NaT, pd.Timestamp('1939-05-27'),
...                              pd.Timestamp('1940-04-25')],
...                        name=['Alfred', 'Batman', ''],
...                        toy=[None, 'Batmobile', 'Joker']))
>>> df
   age       born    name        toy
0  5.0        NaT  Alfred       None
1  6.0 1939-05-27  Batman  Batmobile
2  NaN 1940-04-25              Joker

>>> df.isna()
     age   born   name    toy
0  False   True  False   True
1  False  False  False  False
2   True  False  False  False

Show which entries in a Series are NA.

>>> ser = pd.Series([5, 6, np.nan])
>>> ser
0    5.0
1    6.0
2    NaN
dtype: float64

>>> ser.isna()
0    False
1    False
2     True
dtype: bool
        """
        pass
    def isnull(self) -> DataFrame:
        """
DataFrame.isnull is an alias for DataFrame.isna.

Detect missing values.

Return a boolean same-sized object indicating if the values are NA.
NA values, such as None or :attr:`numpy.NaN`, gets mapped to True
values.
Everything else gets mapped to False values. Characters such as empty
strings ``''`` or :attr:`numpy.inf` are not considered NA values
(unless you set ``pandas.options.mode.use_inf_as_na = True``).

Returns
-------
DataFrame
    Mask of bool values for each element in DataFrame that
    indicates whether an element is an NA value.

See Also
--------
DataFrame.isnull : Alias of isna.
DataFrame.notna : Boolean inverse of isna.
DataFrame.dropna : Omit axes labels with missing values.
isna : Top-level isna.

Examples
--------
Show which entries in a DataFrame are NA.

>>> df = pd.DataFrame(dict(age=[5, 6, np.nan],
...                        born=[pd.NaT, pd.Timestamp('1939-05-27'),
...                              pd.Timestamp('1940-04-25')],
...                        name=['Alfred', 'Batman', ''],
...                        toy=[None, 'Batmobile', 'Joker']))
>>> df
   age       born    name        toy
0  5.0        NaT  Alfred       None
1  6.0 1939-05-27  Batman  Batmobile
2  NaN 1940-04-25              Joker

>>> df.isna()
     age   born   name    toy
0  False   True  False   True
1  False  False  False  False
2   True  False  False  False

Show which entries in a Series are NA.

>>> ser = pd.Series([5, 6, np.nan])
>>> ser
0    5.0
1    6.0
2    NaN
dtype: float64

>>> ser.isna()
0    False
1    False
2     True
dtype: bool
        """
        pass
    def notna(self) -> DataFrame:
        """
Detect existing (non-missing) values.

Return a boolean same-sized object indicating if the values are not NA.
Non-missing values get mapped to True. Characters such as empty
strings ``''`` or :attr:`numpy.inf` are not considered NA values
(unless you set ``pandas.options.mode.use_inf_as_na = True``).
NA values, such as None or :attr:`numpy.NaN`, get mapped to False
values.

Returns
-------
DataFrame
    Mask of bool values for each element in DataFrame that
    indicates whether an element is not an NA value.

See Also
--------
DataFrame.notnull : Alias of notna.
DataFrame.isna : Boolean inverse of notna.
DataFrame.dropna : Omit axes labels with missing values.
notna : Top-level notna.

Examples
--------
Show which entries in a DataFrame are not NA.

>>> df = pd.DataFrame(dict(age=[5, 6, np.nan],
...                        born=[pd.NaT, pd.Timestamp('1939-05-27'),
...                              pd.Timestamp('1940-04-25')],
...                        name=['Alfred', 'Batman', ''],
...                        toy=[None, 'Batmobile', 'Joker']))
>>> df
   age       born    name        toy
0  5.0        NaT  Alfred       None
1  6.0 1939-05-27  Batman  Batmobile
2  NaN 1940-04-25              Joker

>>> df.notna()
     age   born  name    toy
0   True  False  True  False
1   True   True  True   True
2  False   True  True   True

Show which entries in a Series are not NA.

>>> ser = pd.Series([5, 6, np.nan])
>>> ser
0    5.0
1    6.0
2    NaN
dtype: float64

>>> ser.notna()
0     True
1     True
2    False
dtype: bool
        """
        pass
    def notnull(self) -> DataFrame:
        """
DataFrame.notnull is an alias for DataFrame.notna.

Detect existing (non-missing) values.

Return a boolean same-sized object indicating if the values are not NA.
Non-missing values get mapped to True. Characters such as empty
strings ``''`` or :attr:`numpy.inf` are not considered NA values
(unless you set ``pandas.options.mode.use_inf_as_na = True``).
NA values, such as None or :attr:`numpy.NaN`, get mapped to False
values.

Returns
-------
DataFrame
    Mask of bool values for each element in DataFrame that
    indicates whether an element is not an NA value.

See Also
--------
DataFrame.notnull : Alias of notna.
DataFrame.isna : Boolean inverse of notna.
DataFrame.dropna : Omit axes labels with missing values.
notna : Top-level notna.

Examples
--------
Show which entries in a DataFrame are not NA.

>>> df = pd.DataFrame(dict(age=[5, 6, np.nan],
...                        born=[pd.NaT, pd.Timestamp('1939-05-27'),
...                              pd.Timestamp('1940-04-25')],
...                        name=['Alfred', 'Batman', ''],
...                        toy=[None, 'Batmobile', 'Joker']))
>>> df
   age       born    name        toy
0  5.0        NaT  Alfred       None
1  6.0 1939-05-27  Batman  Batmobile
2  NaN 1940-04-25              Joker

>>> df.notna()
     age   born  name    toy
0   True  False  True  False
1   True   True  True   True
2  False   True  True   True

Show which entries in a Series are not NA.

>>> ser = pd.Series([5, 6, np.nan])
>>> ser
0    5.0
1    6.0
2    NaN
dtype: float64

>>> ser.notna()
0     True
1     True
2    False
dtype: bool
        """
        pass
    @overload
    def dropna(
        self,
        *,
        axis: Axis = ...,
        how: Literal["any", "all"] = ...,
        thresh: int | None = ...,
        subset: ListLikeU | Scalar | None = ...,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def dropna(
        self,
        *,
        axis: Axis = ...,
        how: Literal["any", "all"] = ...,
        thresh: int | None = ...,
        subset: ListLikeU | Scalar | None = ...,
        inplace: Literal[False] = ...,
    ) -> DataFrame: ...
    @overload
    def dropna(
        self,
        *,
        axis: Axis = ...,
        how: Literal["any", "all"] = ...,
        thresh: int | None = ...,
        subset: ListLikeU | Scalar | None = ...,
        inplace: _bool | None = ...,
    ) -> DataFrame | None: ...
    def drop_duplicates(
        self,
        subset: Hashable | Iterable[Hashable] | None = ...,
        *,
        keep: NaPosition | _bool = ...,
        inplace: _bool = ...,
        ignore_index: _bool = ...,
    ) -> DataFrame: ...
    def duplicated(
        self,
        subset: Hashable | Iterable[Hashable] | None = ...,
        keep: NaPosition | _bool = ...,
    ) -> Series: ...
    @overload
    def sort_values(
        self,
        by: _str | Sequence[_str],
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
        by: _str | Sequence[_str],
        *,
        axis: Axis = ...,
        ascending: _bool | Sequence[_bool] = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        ignore_index: _bool = ...,
        inplace: Literal[False] = ...,
        key: Callable | None = ...,
    ) -> DataFrame: ...
    @overload
    def sort_values(
        self,
        by: _str | Sequence[_str],
        *,
        axis: Axis = ...,
        ascending: _bool | Sequence[_bool] = ...,
        inplace: _bool | None = ...,
        kind: SortKind = ...,
        na_position: NaPosition = ...,
        ignore_index: _bool = ...,
        key: Callable | None = ...,
    ) -> DataFrame | None: ...
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
    ) -> DataFrame: ...
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
    ) -> DataFrame | None: ...
    @overload
    def value_counts(
        self,
        subset: Sequence[Hashable] | None = ...,
        normalize: Literal[False] = ...,
        sort: _bool = ...,
        ascending: _bool = ...,
        dropna: _bool = ...,
    ) -> Series[int]: ...
    @overload
    def value_counts(
        self,
        normalize: Literal[True],
        subset: Sequence[Hashable] | None = ...,
        sort: _bool = ...,
        ascending: _bool = ...,
        dropna: _bool = ...,
    ) -> Series[float]: ...
    def nlargest(
        self,
        n: int,
        columns: _str | list[_str],
        keep: NaPosition | Literal["all"] = ...,
    ) -> DataFrame: ...
    def nsmallest(
        self,
        n: int,
        columns: _str | list[_str],
        keep: NaPosition | Literal["all"] = ...,
    ) -> DataFrame: ...
    def swaplevel(
        self, i: Level = ..., j: Level = ..., axis: Axis = ...
    ) -> DataFrame:
        """
Swap levels i and j in a :class:`MultiIndex`.

Default is to swap the two innermost levels of the index.

Parameters
----------
i, j : int or str
    Levels of the indices to be swapped. Can pass level name as string.
axis : {0 or 'index', 1 or 'columns'}, default 0
            The axis to swap levels on. 0 or 'index' for row-wise, 1 or
            'columns' for column-wise.

Returns
-------
DataFrame
    DataFrame with levels swapped in MultiIndex.

Examples
--------
>>> df = pd.DataFrame(
...     {"Grade": ["A", "B", "A", "C"]},
...     index=[
...         ["Final exam", "Final exam", "Coursework", "Coursework"],
...         ["History", "Geography", "History", "Geography"],
...         ["January", "February", "March", "April"],
...     ],
... )
>>> df
                                    Grade
Final exam  History     January      A
            Geography   February     B
Coursework  History     March        A
            Geography   April        C

In the following example, we will swap the levels of the indices.
Here, we will swap the levels column-wise, but levels can be swapped row-wise
in a similar manner. Note that column-wise is the default behaviour.
By not supplying any arguments for i and j, we swap the last and second to
last indices.

>>> df.swaplevel()
                                    Grade
Final exam  January     History         A
            February    Geography       B
Coursework  March       History         A
            April       Geography       C

By supplying one argument, we can choose which index to swap the last
index with. We can for example swap the first index with the last one as
follows.

>>> df.swaplevel(0)
                                    Grade
January     History     Final exam      A
February    Geography   Final exam      B
March       History     Coursework      A
April       Geography   Coursework      C

We can also define explicitly which indices we want to swap by supplying values
for both i and j. Here, we for example swap the first and second indices.

>>> df.swaplevel(0, 1)
                                    Grade
History     Final exam  January         A
Geography   Final exam  February        B
History     Coursework  March           A
Geography   Coursework  April           C
        """
        pass
    def reorder_levels(self, order: list, axis: Axis = ...) -> DataFrame: ...
    def compare(
        self,
        other: DataFrame,
        align_axis: Axis = ...,
        keep_shape: bool = ...,
        keep_equal: bool = ...,
        result_names: Suffixes = ...,
    ) -> DataFrame:
        """
Compare to another DataFrame and show the differences.

Parameters
----------
other : DataFrame
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
DataFrame
    DataFrame that shows the differences stacked side by side.

    The resulting index will be a MultiIndex with 'self' and 'other'
    stacked alternately at the inner level.

Raises
------
ValueError
    When the two DataFrames don't have identical labels or shape.

See Also
--------
Series.compare : Compare with another Series and show differences.
DataFrame.equals : Test whether two objects contain the same elements.

Notes
-----
Matching NaNs will not appear as a difference.

Can only compare identically-labeled
(i.e. same shape, identical row and column labels) DataFrames

Examples
--------
>>> df = pd.DataFrame(
...     {
...         "col1": ["a", "a", "b", "b", "a"],
...         "col2": [1.0, 2.0, 3.0, np.nan, 5.0],
...         "col3": [1.0, 2.0, 3.0, 4.0, 5.0]
...     },
...     columns=["col1", "col2", "col3"],
... )
>>> df
  col1  col2  col3
0    a   1.0   1.0
1    a   2.0   2.0
2    b   3.0   3.0
3    b   NaN   4.0
4    a   5.0   5.0

>>> df2 = df.copy()
>>> df2.loc[0, 'col1'] = 'c'
>>> df2.loc[2, 'col3'] = 4.0
>>> df2
  col1  col2  col3
0    c   1.0   1.0
1    a   2.0   2.0
2    b   3.0   4.0
3    b   NaN   4.0
4    a   5.0   5.0

Align the differences on columns

>>> df.compare(df2)
  col1       col3
  self other self other
0    a     c  NaN   NaN
2  NaN   NaN  3.0   4.0

Assign result_names

>>> df.compare(df2, result_names=("left", "right"))
  col1       col3
  left right left right
0    a     c  NaN   NaN
2  NaN   NaN  3.0   4.0

Stack the differences on rows

>>> df.compare(df2, align_axis=0)
        col1  col3
0 self     a   NaN
  other    c   NaN
2 self   NaN   3.0
  other  NaN   4.0

Keep the equal values

>>> df.compare(df2, keep_equal=True)
  col1       col3
  self other self other
0    a     c  1.0   1.0
2    b     b  3.0   4.0

Keep all original rows and columns

>>> df.compare(df2, keep_shape=True)
  col1       col2       col3
  self other self other self other
0    a     c  NaN   NaN  NaN   NaN
1  NaN   NaN  NaN   NaN  NaN   NaN
2  NaN   NaN  NaN   NaN  3.0   4.0
3  NaN   NaN  NaN   NaN  NaN   NaN
4  NaN   NaN  NaN   NaN  NaN   NaN

Keep all original rows and columns and also all original values

>>> df.compare(df2, keep_shape=True, keep_equal=True)
  col1       col2       col3
  self other self other self other
0    a     c  1.0   1.0  1.0   1.0
1    a     a  2.0   2.0  2.0   2.0
2    b     b  3.0   3.0  3.0   4.0
3    b     b  NaN   NaN  4.0   4.0
4    a     a  5.0   5.0  5.0   5.0
        """
        pass
    def combine(
        self,
        other: DataFrame,
        func: Callable,
        fill_value=...,
        overwrite: _bool = ...,
    ) -> DataFrame: ...
    def combine_first(self, other: DataFrame) -> DataFrame: ...
    def update(
        self,
        other: DataFrame | Series,
        join: _str = ...,
        overwrite: _bool = ...,
        filter_func: Callable | None = ...,
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def groupby(
        self,
        by: Scalar,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[Scalar]:
        """
Group DataFrame using a mapper or by a Series of columns.

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
pandas.api.typing.DataFrameGroupBy
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
>>> df = pd.DataFrame({'Animal': ['Falcon', 'Falcon',
...                               'Parrot', 'Parrot'],
...                    'Max Speed': [380., 370., 24., 26.]})
>>> df
   Animal  Max Speed
0  Falcon      380.0
1  Falcon      370.0
2  Parrot       24.0
3  Parrot       26.0
>>> df.groupby(['Animal']).mean()
        Max Speed
Animal
Falcon      375.0
Parrot       25.0

**Hierarchical Indexes**

We can groupby different levels of a hierarchical index
using the `level` parameter:

>>> arrays = [['Falcon', 'Falcon', 'Parrot', 'Parrot'],
...           ['Captive', 'Wild', 'Captive', 'Wild']]
>>> index = pd.MultiIndex.from_arrays(arrays, names=('Animal', 'Type'))
>>> df = pd.DataFrame({'Max Speed': [390., 350., 30., 20.]},
...                   index=index)
>>> df
                Max Speed
Animal Type
Falcon Captive      390.0
       Wild         350.0
Parrot Captive       30.0
       Wild          20.0
>>> df.groupby(level=0).mean()
        Max Speed
Animal
Falcon      370.0
Parrot       25.0
>>> df.groupby(level="Type").mean()
         Max Speed
Type
Captive      210.0
Wild         185.0

We can also choose to include NA in group keys or not by setting
`dropna` parameter, the default setting is `True`.

>>> l = [[1, 2, 3], [1, None, 4], [2, 1, 3], [1, 2, 2]]
>>> df = pd.DataFrame(l, columns=["a", "b", "c"])

>>> df.groupby(by=["b"]).sum()
    a   c
b
1.0 2   3
2.0 2   5

>>> df.groupby(by=["b"], dropna=False).sum()
    a   c
b
1.0 2   3
2.0 2   5
NaN 1   4

>>> l = [["a", 12, 12], [None, 12.3, 33.], ["b", 12.3, 123], ["a", 1, 1]]
>>> df = pd.DataFrame(l, columns=["a", "b", "c"])

>>> df.groupby(by="a").sum()
    b     c
a
a   13.0   13.0
b   12.3  123.0

>>> df.groupby(by="a", dropna=False).sum()
    b     c
a
a   13.0   13.0
b   12.3  123.0
NaN 12.3   33.0

When using ``.apply()``, use ``group_keys`` to include or exclude the
group keys. The ``group_keys`` argument defaults to ``True`` (include).

>>> df = pd.DataFrame({'Animal': ['Falcon', 'Falcon',
...                               'Parrot', 'Parrot'],
...                    'Max Speed': [380., 370., 24., 26.]})
>>> df.groupby("Animal", group_keys=True)[['Max Speed']].apply(lambda x: x)
          Max Speed
Animal
Falcon 0      380.0
       1      370.0
Parrot 2       24.0
       3       26.0

>>> df.groupby("Animal", group_keys=False)[['Max Speed']].apply(lambda x: x)
   Max Speed
0      380.0
1      370.0
2       24.0
3       26.0
        """
        pass
    @overload
    def groupby(
        self,
        by: DatetimeIndex,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[Timestamp]: ...
    @overload
    def groupby(
        self,
        by: TimedeltaIndex,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[Timedelta]: ...
    @overload
    def groupby(
        self,
        by: PeriodIndex,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[Period]: ...
    @overload
    def groupby(
        self,
        by: IntervalIndex[IntervalT],
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[IntervalT]: ...
    @overload
    def groupby(
        self,
        by: MultiIndex | GroupByObjectNonScalar | None = ...,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[tuple]: ...
    @overload
    def groupby(
        self,
        by: Series[SeriesByT],
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[SeriesByT]: ...
    @overload
    def groupby(
        self,
        by: CategoricalIndex | Index | Series,
        axis: AxisIndex | NoDefault = ...,
        level: IndexLabel | None = ...,
        as_index: _bool = ...,
        sort: _bool = ...,
        group_keys: _bool = ...,
        observed: _bool | NoDefault = ...,
        dropna: _bool = ...,
    ) -> DataFrameGroupBy[Any]: ...
    def pivot(
        self,
        *,
        index: IndexLabel = ...,
        columns: IndexLabel = ...,
        values: IndexLabel = ...,
    ) -> DataFrame:
        """
Return reshaped DataFrame organized by given index / column values.

Reshape data (produce a "pivot" table) based on column values. Uses
unique values from specified `index` / `columns` to form axes of the
resulting DataFrame. This function does not support data
aggregation, multiple values will result in a MultiIndex in the
columns. See the :ref:`User Guide <reshaping>` for more on reshaping.

Parameters
----------
columns : str or object or a list of str
    Column to use to make new frame's columns.
index : str or object or a list of str, optional
    Column to use to make new frame's index. If not given, uses existing index.
values : str, object or a list of the previous, optional
    Column(s) to use for populating new frame's values. If not
    specified, all remaining columns will be used and the result will
    have hierarchically indexed columns.

Returns
-------
DataFrame
    Returns reshaped DataFrame.

Raises
------
ValueError:
    When there are any `index`, `columns` combinations with multiple
    values. `DataFrame.pivot_table` when you need to aggregate.

See Also
--------
DataFrame.pivot_table : Generalization of pivot that can handle
    duplicate values for one index/column pair.
DataFrame.unstack : Pivot based on the index values instead of a
    column.
wide_to_long : Wide panel to long format. Less flexible but more
    user-friendly than melt.

Notes
-----
For finer-tuned control, see hierarchical indexing documentation along
with the related stack/unstack methods.

Reference :ref:`the user guide <reshaping.pivot>` for more examples.

Examples
--------
>>> df = pd.DataFrame({'foo': ['one', 'one', 'one', 'two', 'two',
...                            'two'],
...                    'bar': ['A', 'B', 'C', 'A', 'B', 'C'],
...                    'baz': [1, 2, 3, 4, 5, 6],
...                    'zoo': ['x', 'y', 'z', 'q', 'w', 't']})
>>> df
    foo   bar  baz  zoo
0   one   A    1    x
1   one   B    2    y
2   one   C    3    z
3   two   A    4    q
4   two   B    5    w
5   two   C    6    t

>>> df.pivot(index='foo', columns='bar', values='baz')
bar  A   B   C
foo
one  1   2   3
two  4   5   6

>>> df.pivot(index='foo', columns='bar')['baz']
bar  A   B   C
foo
one  1   2   3
two  4   5   6

>>> df.pivot(index='foo', columns='bar', values=['baz', 'zoo'])
      baz       zoo
bar   A  B  C   A  B  C
foo
one   1  2  3   x  y  z
two   4  5  6   q  w  t

You could also assign a list of column names or a list of index names.

>>> df = pd.DataFrame({
...        "lev1": [1, 1, 1, 2, 2, 2],
...        "lev2": [1, 1, 2, 1, 1, 2],
...        "lev3": [1, 2, 1, 2, 1, 2],
...        "lev4": [1, 2, 3, 4, 5, 6],
...        "values": [0, 1, 2, 3, 4, 5]})
>>> df
    lev1 lev2 lev3 lev4 values
0   1    1    1    1    0
1   1    1    2    2    1
2   1    2    1    3    2
3   2    1    2    4    3
4   2    1    1    5    4
5   2    2    2    6    5

>>> df.pivot(index="lev1", columns=["lev2", "lev3"], values="values")
lev2    1         2
lev3    1    2    1    2
lev1
1     0.0  1.0  2.0  NaN
2     4.0  3.0  NaN  5.0

>>> df.pivot(index=["lev1", "lev2"], columns=["lev3"], values="values")
      lev3    1    2
lev1  lev2
   1     1  0.0  1.0
         2  2.0  NaN
   2     1  4.0  3.0
         2  NaN  5.0

A ValueError is raised if there are any duplicates.

>>> df = pd.DataFrame({"foo": ['one', 'one', 'two', 'two'],
...                    "bar": ['A', 'A', 'B', 'C'],
...                    "baz": [1, 2, 3, 4]})
>>> df
   foo bar  baz
0  one   A    1
1  one   A    2
2  two   B    3
3  two   C    4

Notice that the first two rows are the same for our `index`
and `columns` arguments.

>>> df.pivot(index='foo', columns='bar', values='baz')
Traceback (most recent call last):
   ...
ValueError: Index contains duplicate entries, cannot reshape
        """
        pass
    def pivot_table(
        self,
        values: _str | None | Sequence[_str] = ...,
        index: _str | Grouper | Sequence | None = ...,
        columns: _str | Grouper | Sequence | None = ...,
        aggfunc=...,
        fill_value: Scalar | None = ...,
        margins: _bool = ...,
        dropna: _bool = ...,
        margins_name: _str = ...,
        observed: _bool = ...,
    ) -> DataFrame:
        """
Create a spreadsheet-style pivot table as a DataFrame.

The levels in the pivot table will be stored in MultiIndex objects
(hierarchical indexes) on the index and columns of the result DataFrame.

Parameters
----------
values : list-like or scalar, optional
    Column or columns to aggregate.
index : column, Grouper, array, or list of the previous
    Keys to group by on the pivot table index. If a list is passed,
    it can contain any of the other types (except list). If an array is
    passed, it must be the same length as the data and will be used in
    the same manner as column values.
columns : column, Grouper, array, or list of the previous
    Keys to group by on the pivot table column. If a list is passed,
    it can contain any of the other types (except list). If an array is
    passed, it must be the same length as the data and will be used in
    the same manner as column values.
aggfunc : function, list of functions, dict, default "mean"
    If a list of functions is passed, the resulting pivot table will have
    hierarchical columns whose top level are the function names
    (inferred from the function objects themselves).
    If a dict is passed, the key is column to aggregate and the value is
    function or list of functions. If ``margin=True``, aggfunc will be
    used to calculate the partial aggregates.
fill_value : scalar, default None
    Value to replace missing values with (in the resulting pivot table,
    after aggregation).
margins : bool, default False
    If ``margins=True``, special ``All`` columns and rows
    will be added with partial group aggregates across the categories
    on the rows and columns.
dropna : bool, default True
    Do not include columns whose entries are all NaN. If True,
    rows with a NaN value in any column will be omitted before
    computing margins.
margins_name : str, default 'All'
    Name of the row / column that will contain the totals
    when margins is True.
observed : bool, default False
    This only applies if any of the groupers are Categoricals.
    If True: only show observed values for categorical groupers.
    If False: show all values for categorical groupers.

    .. deprecated:: 2.2.0

        The default value of ``False`` is deprecated and will change to
        ``True`` in a future version of pandas.

sort : bool, default True
    Specifies if the result should be sorted.

    .. versionadded:: 1.3.0

Returns
-------
DataFrame
    An Excel style pivot table.

See Also
--------
DataFrame.pivot : Pivot without aggregation that can handle
    non-numeric data.
DataFrame.melt: Unpivot a DataFrame from wide to long format,
    optionally leaving identifiers set.
wide_to_long : Wide panel to long format. Less flexible but more
    user-friendly than melt.

Notes
-----
Reference :ref:`the user guide <reshaping.pivot>` for more examples.

Examples
--------
>>> df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
...                          "bar", "bar", "bar", "bar"],
...                    "B": ["one", "one", "one", "two", "two",
...                          "one", "one", "two", "two"],
...                    "C": ["small", "large", "large", "small",
...                          "small", "large", "small", "small",
...                          "large"],
...                    "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
...                    "E": [2, 4, 5, 5, 6, 6, 8, 9, 9]})
>>> df
     A    B      C  D  E
0  foo  one  small  1  2
1  foo  one  large  2  4
2  foo  one  large  2  5
3  foo  two  small  3  5
4  foo  two  small  3  6
5  bar  one  large  4  6
6  bar  one  small  5  8
7  bar  two  small  6  9
8  bar  two  large  7  9

This first example aggregates values by taking the sum.

>>> table = pd.pivot_table(df, values='D', index=['A', 'B'],
...                        columns=['C'], aggfunc="sum")
>>> table
C        large  small
A   B
bar one    4.0    5.0
    two    7.0    6.0
foo one    4.0    1.0
    two    NaN    6.0

We can also fill missing values using the `fill_value` parameter.

>>> table = pd.pivot_table(df, values='D', index=['A', 'B'],
...                        columns=['C'], aggfunc="sum", fill_value=0)
>>> table
C        large  small
A   B
bar one      4      5
    two      7      6
foo one      4      1
    two      0      6

The next example aggregates by taking the mean across multiple columns.

>>> table = pd.pivot_table(df, values=['D', 'E'], index=['A', 'C'],
...                        aggfunc={'D': "mean", 'E': "mean"})
>>> table
                D         E
A   C
bar large  5.500000  7.500000
    small  5.500000  8.500000
foo large  2.000000  4.500000
    small  2.333333  4.333333

We can also calculate multiple types of aggregations for any given
value column.

>>> table = pd.pivot_table(df, values=['D', 'E'], index=['A', 'C'],
...                        aggfunc={'D': "mean",
...                                 'E': ["min", "max", "mean"]})
>>> table
                  D   E
               mean max      mean  min
A   C
bar large  5.500000   9  7.500000    6
    small  5.500000   9  8.500000    8
foo large  2.000000   5  4.500000    4
    small  2.333333   6  4.333333    2
        """
        pass
    @overload
    def stack(
        self, level: Level | list[Level] = ..., dropna: _bool = ..., sort: _bool = ...
    ) -> DataFrame | Series[Any]: ...
    @overload
    def stack(
        self, level: Level | list[Level] = ..., future_stack: _bool = ...
    ) -> DataFrame | Series[Any]: ...
    def explode(
        self, column: Sequence[Hashable], ignore_index: _bool = ...
    ) -> DataFrame: ...
    def unstack(
        self,
        level: Level = ...,
        fill_value: int | _str | dict | None = ...,
    ) -> DataFrame | Series: ...
    def melt(
        self,
        id_vars: tuple | Sequence | np.ndarray | None = ...,
        value_vars: tuple | Sequence | np.ndarray | None = ...,
        var_name: Scalar | None = ...,
        value_name: Scalar = ...,
        col_level: int | _str | None = ...,
        ignore_index: _bool = ...,
    ) -> DataFrame:
        """
Unpivot a DataFrame from wide to long format, optionally leaving identifiers set.

This function is useful to massage a DataFrame into a format where one
or more columns are identifier variables (`id_vars`), while all other
columns, considered measured variables (`value_vars`), are "unpivoted" to
the row axis, leaving just two non-identifier columns, 'variable' and
'value'.

Parameters
----------
id_vars : scalar, tuple, list, or ndarray, optional
    Column(s) to use as identifier variables.
value_vars : scalar, tuple, list, or ndarray, optional
    Column(s) to unpivot. If not specified, uses all columns that
    are not set as `id_vars`.
var_name : scalar, default None
    Name to use for the 'variable' column. If None it uses
    ``frame.columns.name`` or 'variable'.
value_name : scalar, default 'value'
    Name to use for the 'value' column, can't be an existing column label.
col_level : scalar, optional
    If columns are a MultiIndex then use this level to melt.
ignore_index : bool, default True
    If True, original index is ignored. If False, the original index is retained.
    Index labels will be repeated as necessary.

Returns
-------
DataFrame
    Unpivoted DataFrame.

See Also
--------
melt : Identical method.
pivot_table : Create a spreadsheet-style pivot table as a DataFrame.
DataFrame.pivot : Return reshaped DataFrame organized
    by given index / column values.
DataFrame.explode : Explode a DataFrame from list-like
        columns to long format.

Notes
-----
Reference :ref:`the user guide <reshaping.melt>` for more examples.

Examples
--------
>>> df = pd.DataFrame({'A': {0: 'a', 1: 'b', 2: 'c'},
...                    'B': {0: 1, 1: 3, 2: 5},
...                    'C': {0: 2, 1: 4, 2: 6}})
>>> df
   A  B  C
0  a  1  2
1  b  3  4
2  c  5  6

>>> df.melt(id_vars=['A'], value_vars=['B'])
   A variable  value
0  a        B      1
1  b        B      3
2  c        B      5

>>> df.melt(id_vars=['A'], value_vars=['B', 'C'])
   A variable  value
0  a        B      1
1  b        B      3
2  c        B      5
3  a        C      2
4  b        C      4
5  c        C      6

The names of 'variable' and 'value' columns can be customized:

>>> df.melt(id_vars=['A'], value_vars=['B'],
...         var_name='myVarname', value_name='myValname')
   A myVarname  myValname
0  a         B          1
1  b         B          3
2  c         B          5

Original index values can be kept around:

>>> df.melt(id_vars=['A'], value_vars=['B', 'C'], ignore_index=False)
   A variable  value
0  a        B      1
1  b        B      3
2  c        B      5
0  a        C      2
1  b        C      4
2  c        C      6

If you have multi-index columns:

>>> df.columns = [list('ABC'), list('DEF')]
>>> df
   A  B  C
   D  E  F
0  a  1  2
1  b  3  4
2  c  5  6

>>> df.melt(col_level=0, id_vars=['A'], value_vars=['B'])
   A variable  value
0  a        B      1
1  b        B      3
2  c        B      5

>>> df.melt(id_vars=[('A', 'D')], value_vars=[('B', 'E')])
  (A, D) variable_0 variable_1  value
0      a          B          E      1
1      b          B          E      3
2      c          B          E      5
        """
        pass
    def diff(self, periods: int = ..., axis: Axis = ...) -> DataFrame:
        """
First discrete difference of element.

Calculates the difference of a DataFrame element compared with another
element in the DataFrame (default is element in previous row).

Parameters
----------
periods : int, default 1
    Periods to shift for calculating difference, accepts negative
    values.
axis : {0 or 'index', 1 or 'columns'}, default 0
    Take difference over rows (0) or columns (1).

Returns
-------
DataFrame
    First differences of the Series.

See Also
--------
DataFrame.pct_change: Percent change over given number of periods.
DataFrame.shift: Shift index by desired number of periods with an
    optional time freq.
Series.diff: First discrete difference of object.

Notes
-----
For boolean dtypes, this uses :meth:`operator.xor` rather than
:meth:`operator.sub`.
The result is calculated according to current dtype in DataFrame,
however dtype of the result is always float64.

Examples
--------

Difference with previous row

>>> df = pd.DataFrame({'a': [1, 2, 3, 4, 5, 6],
...                    'b': [1, 1, 2, 3, 5, 8],
...                    'c': [1, 4, 9, 16, 25, 36]})
>>> df
   a  b   c
0  1  1   1
1  2  1   4
2  3  2   9
3  4  3  16
4  5  5  25
5  6  8  36

>>> df.diff()
     a    b     c
0  NaN  NaN   NaN
1  1.0  0.0   3.0
2  1.0  1.0   5.0
3  1.0  1.0   7.0
4  1.0  2.0   9.0
5  1.0  3.0  11.0

Difference with previous column

>>> df.diff(axis=1)
    a  b   c
0 NaN  0   0
1 NaN -1   3
2 NaN -1   7
3 NaN -1  13
4 NaN  0  20
5 NaN  2  28

Difference with 3rd previous row

>>> df.diff(periods=3)
     a    b     c
0  NaN  NaN   NaN
1  NaN  NaN   NaN
2  NaN  NaN   NaN
3  3.0  2.0  15.0
4  3.0  4.0  21.0
5  3.0  6.0  27.0

Difference with following row

>>> df.diff(periods=-1)
     a    b     c
0 -1.0  0.0  -3.0
1 -1.0 -1.0  -5.0
2 -1.0 -1.0  -7.0
3 -1.0 -2.0  -9.0
4 -1.0 -3.0 -11.0
5  NaN  NaN   NaN

Overflow in input dtype

>>> df = pd.DataFrame({'a': [1, 0]}, dtype=np.uint8)
>>> df.diff()
       a
0    NaN
1  255.0
        """
        pass
    @overload
    def agg(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, func: AggFuncTypeBase | AggFuncTypeDictSeries, axis: Axis = ..., **kwargs
    ) -> Series:
        """
Aggregate using one or more operations over the specified axis.

Parameters
----------
func : function, str, list or dict
    Function to use for aggregating the data. If a function, must either
    work when passed a DataFrame or when passed to DataFrame.apply.

    Accepted combinations are:

    - function
    - string function name
    - list of functions and/or function names, e.g. ``[np.sum, 'mean']``
    - dict of axis labels -> functions, function names or list of such.
axis : {0 or 'index', 1 or 'columns'}, default 0
        If 0 or 'index': apply function to each column.
        If 1 or 'columns': apply function to each row.
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
DataFrame.apply : Perform any type of operations.
DataFrame.transform : Perform transformation type operations.
pandas.DataFrame.groupby : Perform operations over groups.
pandas.DataFrame.resample : Perform operations over resampled bins.
pandas.DataFrame.rolling : Perform operations over rolling window.
pandas.DataFrame.expanding : Perform operations over expanding window.
pandas.core.window.ewm.ExponentialMovingWindow : Perform operation over exponential
    weighted window.

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
>>> df = pd.DataFrame([[1, 2, 3],
...                    [4, 5, 6],
...                    [7, 8, 9],
...                    [np.nan, np.nan, np.nan]],
...                   columns=['A', 'B', 'C'])

Aggregate these functions over the rows.

>>> df.agg(['sum', 'min'])
        A     B     C
sum  12.0  15.0  18.0
min   1.0   2.0   3.0

Different aggregations per column.

>>> df.agg({'A' : ['sum', 'min'], 'B' : ['min', 'max']})
        A    B
sum  12.0  NaN
min   1.0  2.0
max   NaN  8.0

Aggregate different functions over the columns and rename the index of the resulting
DataFrame.

>>> df.agg(x=('A', 'max'), y=('B', 'min'), z=('C', 'mean'))
     A    B    C
x  7.0  NaN  NaN
y  NaN  2.0  NaN
z  NaN  NaN  6.0

Aggregate over the columns.

>>> df.agg("mean", axis="columns")
0    2.0
1    5.0
2    8.0
3    NaN
dtype: float64
        """
        pass
    @overload
    def agg(
        self,
        func: list[AggFuncTypeBase] | AggFuncTypeDictFrame = ...,
        axis: Axis = ...,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def aggregate(  # type: ignore[overload-overlap] # pyright: ignore[reportOverlappingOverload]
        self, func: AggFuncTypeBase | AggFuncTypeDictSeries, axis: Axis = ..., **kwargs
    ) -> Series:
        """
Aggregate using one or more operations over the specified axis.

Parameters
----------
func : function, str, list or dict
    Function to use for aggregating the data. If a function, must either
    work when passed a DataFrame or when passed to DataFrame.apply.

    Accepted combinations are:

    - function
    - string function name
    - list of functions and/or function names, e.g. ``[np.sum, 'mean']``
    - dict of axis labels -> functions, function names or list of such.
axis : {0 or 'index', 1 or 'columns'}, default 0
        If 0 or 'index': apply function to each column.
        If 1 or 'columns': apply function to each row.
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
DataFrame.apply : Perform any type of operations.
DataFrame.transform : Perform transformation type operations.
pandas.DataFrame.groupby : Perform operations over groups.
pandas.DataFrame.resample : Perform operations over resampled bins.
pandas.DataFrame.rolling : Perform operations over rolling window.
pandas.DataFrame.expanding : Perform operations over expanding window.
pandas.core.window.ewm.ExponentialMovingWindow : Perform operation over exponential
    weighted window.

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
>>> df = pd.DataFrame([[1, 2, 3],
...                    [4, 5, 6],
...                    [7, 8, 9],
...                    [np.nan, np.nan, np.nan]],
...                   columns=['A', 'B', 'C'])

Aggregate these functions over the rows.

>>> df.agg(['sum', 'min'])
        A     B     C
sum  12.0  15.0  18.0
min   1.0   2.0   3.0

Different aggregations per column.

>>> df.agg({'A' : ['sum', 'min'], 'B' : ['min', 'max']})
        A    B
sum  12.0  NaN
min   1.0  2.0
max   NaN  8.0

Aggregate different functions over the columns and rename the index of the resulting
DataFrame.

>>> df.agg(x=('A', 'max'), y=('B', 'min'), z=('C', 'mean'))
     A    B    C
x  7.0  NaN  NaN
y  NaN  2.0  NaN
z  NaN  NaN  6.0

Aggregate over the columns.

>>> df.agg("mean", axis="columns")
0    2.0
1    5.0
2    8.0
3    NaN
dtype: float64
        """
        pass
    @overload
    def aggregate(
        self,
        func: list[AggFuncTypeBase] | AggFuncTypeDictFrame,
        axis: Axis = ...,
        **kwargs,
    ) -> DataFrame: ...
    def transform(
        self,
        func: AggFuncTypeFrame,
        axis: Axis = ...,
        *args,
        **kwargs,
    ) -> DataFrame:
        """
Call ``func`` on self producing a DataFrame with the same axis shape as self.

Parameters
----------
func : function, str, list-like or dict-like
    Function to use for transforming the data. If a function, must either
    work when passed a DataFrame or when passed to DataFrame.apply. If func
    is both list-like and dict-like, dict-like behavior takes precedence.

    Accepted combinations are:

    - function
    - string function name
    - list-like of functions and/or function names, e.g. ``[np.exp, 'sqrt']``
    - dict-like of axis labels -> functions, function names or list-like of such.
axis : {0 or 'index', 1 or 'columns'}, default 0
        If 0 or 'index': apply function to each column.
        If 1 or 'columns': apply function to each row.
*args
    Positional arguments to pass to `func`.
**kwargs
    Keyword arguments to pass to `func`.

Returns
-------
DataFrame
    A DataFrame that must have the same length as self.

Raises
------
ValueError : If the returned DataFrame has a different length than self.

See Also
--------
DataFrame.agg : Only perform aggregating type operations.
DataFrame.apply : Invoke function on a DataFrame.

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

Even though the resulting DataFrame must have the same length as the
input DataFrame, it is possible to provide several input functions:

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

    # apply() overloads with default result_type of None, and is indifferent to axis
    @overload
    def apply(
        self,
        f: Callable[..., ListLikeExceptSeriesAndStr | Series[Any]],
        axis: AxisIndex = ...,
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        **kwargs: Any,
    ) -> DataFrame: ...
    @overload
    def apply(
        self,
        f: Callable[..., S1 | NAType],
        axis: AxisIndex = ...,
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        **kwargs: Any,
    ) -> Series[S1]: ...
    # Since non-scalar type T is not supported in Series[T],
    # we separate this overload from the above one
    @overload
    def apply(
        self,
        f: Callable[..., Mapping[Any, Any]],
        axis: AxisIndex = ...,
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        **kwargs: Any,
    ) -> Series[Any]: ...

    # apply() overloads with keyword result_type, and axis does not matter
    @overload
    def apply(
        self,
        f: Callable[..., S1 | NAType],
        axis: Axis = ...,
        raw: _bool = ...,
        args: Any = ...,
        *,
        result_type: Literal["expand", "reduce"],
        **kwargs: Any,
    ) -> Series[S1]: ...
    @overload
    def apply(
        self,
        f: Callable[..., ListLikeExceptSeriesAndStr | Series[Any] | Mapping[Any, Any]],
        axis: Axis = ...,
        raw: _bool = ...,
        args: Any = ...,
        *,
        result_type: Literal["expand"],
        **kwargs: Any,
    ) -> DataFrame: ...
    @overload
    def apply(
        self,
        f: Callable[..., ListLikeExceptSeriesAndStr | Mapping[Any, Any]],
        axis: Axis = ...,
        raw: _bool = ...,
        args: Any = ...,
        *,
        result_type: Literal["reduce"],
        **kwargs: Any,
    ) -> Series[Any]: ...
    @overload
    def apply(
        self,
        f: Callable[
            ..., ListLikeExceptSeriesAndStr | Series[Any] | Scalar | Mapping[Any, Any]
        ],
        axis: Axis = ...,
        raw: _bool = ...,
        args: Any = ...,
        *,
        result_type: Literal["broadcast"],
        **kwargs: Any,
    ) -> DataFrame: ...

    # apply() overloads with keyword result_type, and axis does matter
    @overload
    def apply(
        self,
        f: Callable[..., Series[Any]],
        axis: AxisIndex = ...,
        raw: _bool = ...,
        args: Any = ...,
        *,
        result_type: Literal["reduce"],
        **kwargs: Any,
    ) -> Series[Any]: ...

    # apply() overloads with default result_type of None, and keyword axis=1 matters
    @overload
    def apply(
        self,
        f: Callable[..., S1 | NAType],
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        *,
        axis: AxisColumn,
        **kwargs: Any,
    ) -> Series[S1]: ...
    @overload
    def apply(
        self,
        f: Callable[..., ListLikeExceptSeriesAndStr | Mapping[Any, Any]],
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        *,
        axis: AxisColumn,
        **kwargs: Any,
    ) -> Series[Any]: ...
    @overload
    def apply(
        self,
        f: Callable[..., Series[Any]],
        raw: _bool = ...,
        result_type: None = ...,
        args: Any = ...,
        *,
        axis: AxisColumn,
        **kwargs: Any,
    ) -> DataFrame: ...

    # apply() overloads with keyword axis=1 and keyword result_type
    @overload
    def apply(
        self,
        f: Callable[..., Series[Any]],
        raw: _bool = ...,
        args: Any = ...,
        *,
        axis: AxisColumn,
        result_type: Literal["reduce"],
        **kwargs: Any,
    ) -> DataFrame: ...

    # Add spacing between apply() overloads and remaining annotations
    def map(
        self, func: Callable, na_action: Literal["ignore"] | None = ..., **kwargs
    ) -> DataFrame: ...
    def join(
        self,
        other: DataFrame | Series | list[DataFrame | Series],
        on: _str | list[_str] | None = ...,
        how: JoinHow = ...,
        lsuffix: _str = ...,
        rsuffix: _str = ...,
        sort: _bool = ...,
        validate: ValidationOptions | None = ...,
    ) -> DataFrame: ...
    def merge(
        self,
        right: DataFrame | Series[Any],
        how: MergeHow = ...,
        on: IndexLabel | AnyArrayLike | None = ...,
        left_on: IndexLabel | AnyArrayLike | None = ...,
        right_on: IndexLabel | AnyArrayLike | None = ...,
        left_index: _bool = ...,
        right_index: _bool = ...,
        sort: _bool = ...,
        suffixes: tuple[_str | None, _str | None] = ...,
        copy: _bool = ...,
        indicator: _bool | _str = ...,
        validate: _str | None = ...,
    ) -> DataFrame:
        """
Merge DataFrame or named Series objects with a database-style join.

A named Series object is treated as a DataFrame with a single named column.

The join is done on columns or indexes. If joining columns on
columns, the DataFrame indexes *will be ignored*. Otherwise if joining indexes
on indexes or indexes on a column or columns, the index will be passed on.
When performing a cross merge, no column specifications to merge on are
allowed.

.. warning::

    If both key columns contain rows where the key is a null value, those
    rows will be matched against each other. This is different from usual SQL
    join behaviour and can lead to unexpected results.

Parameters
----------
right : DataFrame or named Series
    Object to merge with.
how : {'left', 'right', 'outer', 'inner', 'cross'}, default 'inner'
    Type of merge to be performed.

    * left: use only keys from left frame, similar to a SQL left outer join;
      preserve key order.
    * right: use only keys from right frame, similar to a SQL right outer join;
      preserve key order.
    * outer: use union of keys from both frames, similar to a SQL full outer
      join; sort keys lexicographically.
    * inner: use intersection of keys from both frames, similar to a SQL inner
      join; preserve the order of the left keys.
    * cross: creates the cartesian product from both frames, preserves the order
      of the left keys.
on : label or list
    Column or index level names to join on. These must be found in both
    DataFrames. If `on` is None and not merging on indexes then this defaults
    to the intersection of the columns in both DataFrames.
left_on : label or list, or array-like
    Column or index level names to join on in the left DataFrame. Can also
    be an array or list of arrays of the length of the left DataFrame.
    These arrays are treated as if they are columns.
right_on : label or list, or array-like
    Column or index level names to join on in the right DataFrame. Can also
    be an array or list of arrays of the length of the right DataFrame.
    These arrays are treated as if they are columns.
left_index : bool, default False
    Use the index from the left DataFrame as the join key(s). If it is a
    MultiIndex, the number of keys in the other DataFrame (either the index
    or a number of columns) must match the number of levels.
right_index : bool, default False
    Use the index from the right DataFrame as the join key. Same caveats as
    left_index.
sort : bool, default False
    Sort the join keys lexicographically in the result DataFrame. If False,
    the order of the join keys depends on the join type (how keyword).
suffixes : list-like, default is ("_x", "_y")
    A length-2 sequence where each element is optionally a string
    indicating the suffix to add to overlapping column names in
    `left` and `right` respectively. Pass a value of `None` instead
    of a string to indicate that the column name from `left` or
    `right` should be left as-is, with no suffix. At least one of the
    values must not be None.
copy : bool, default True
    If False, avoid copy if possible.

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
indicator : bool or str, default False
    If True, adds a column to the output DataFrame called "_merge" with
    information on the source of each row. The column can be given a different
    name by providing a string argument. The column will have a Categorical
    type with the value of "left_only" for observations whose merge key only
    appears in the left DataFrame, "right_only" for observations
    whose merge key only appears in the right DataFrame, and "both"
    if the observation's merge key is found in both DataFrames.

validate : str, optional
    If specified, checks if merge is of specified type.

    * "one_to_one" or "1:1": check if merge keys are unique in both
      left and right datasets.
    * "one_to_many" or "1:m": check if merge keys are unique in left
      dataset.
    * "many_to_one" or "m:1": check if merge keys are unique in right
      dataset.
    * "many_to_many" or "m:m": allowed, but does not result in checks.

Returns
-------
DataFrame
    A DataFrame of the two merged objects.

See Also
--------
merge_ordered : Merge with optional filling/interpolation.
merge_asof : Merge on nearest keys.
DataFrame.join : Similar method using indices.

Examples
--------
>>> df1 = pd.DataFrame({'lkey': ['foo', 'bar', 'baz', 'foo'],
...                     'value': [1, 2, 3, 5]})
>>> df2 = pd.DataFrame({'rkey': ['foo', 'bar', 'baz', 'foo'],
...                     'value': [5, 6, 7, 8]})
>>> df1
    lkey value
0   foo      1
1   bar      2
2   baz      3
3   foo      5
>>> df2
    rkey value
0   foo      5
1   bar      6
2   baz      7
3   foo      8

Merge df1 and df2 on the lkey and rkey columns. The value columns have
the default suffixes, _x and _y, appended.

>>> df1.merge(df2, left_on='lkey', right_on='rkey')
  lkey  value_x rkey  value_y
0  foo        1  foo        5
1  foo        1  foo        8
2  bar        2  bar        6
3  baz        3  baz        7
4  foo        5  foo        5
5  foo        5  foo        8

Merge DataFrames df1 and df2 with specified left and right suffixes
appended to any overlapping columns.

>>> df1.merge(df2, left_on='lkey', right_on='rkey',
...           suffixes=('_left', '_right'))
  lkey  value_left rkey  value_right
0  foo           1  foo            5
1  foo           1  foo            8
2  bar           2  bar            6
3  baz           3  baz            7
4  foo           5  foo            5
5  foo           5  foo            8

Merge DataFrames df1 and df2, but raise an exception if the DataFrames have
any overlapping columns.

>>> df1.merge(df2, left_on='lkey', right_on='rkey', suffixes=(False, False))
Traceback (most recent call last):
...
ValueError: columns overlap but no suffix specified:
    Index(['value'], dtype='object')

>>> df1 = pd.DataFrame({'a': ['foo', 'bar'], 'b': [1, 2]})
>>> df2 = pd.DataFrame({'a': ['foo', 'baz'], 'c': [3, 4]})
>>> df1
      a  b
0   foo  1
1   bar  2
>>> df2
      a  c
0   foo  3
1   baz  4

>>> df1.merge(df2, how='inner', on='a')
      a  b  c
0   foo  1  3

>>> df1.merge(df2, how='left', on='a')
      a  b  c
0   foo  1  3.0
1   bar  2  NaN

>>> df1 = pd.DataFrame({'left': ['foo', 'bar']})
>>> df2 = pd.DataFrame({'right': [7, 8]})
>>> df1
    left
0   foo
1   bar
>>> df2
    right
0   7
1   8

>>> df1.merge(df2, how='cross')
   left  right
0   foo      7
1   foo      8
2   bar      7
3   bar      8
        """
        pass
    def round(
        self, decimals: int | dict | Series = ..., *args, **kwargs
    ) -> DataFrame: ...
    def corr(
        self,
        method: Literal["pearson", "kendall", "spearman"] = ...,
        min_periods: int = ...,
        numeric_only: _bool = ...,
    ) -> DataFrame: ...
    def cov(
        self, min_periods: int | None = ..., ddof: int = ..., numeric_only: _bool = ...
    ) -> DataFrame: ...
    def corrwith(
        self,
        other: DataFrame | Series,
        axis: Axis | None = ...,
        drop: _bool = ...,
        method: Literal["pearson", "kendall", "spearman"] = ...,
        numeric_only: _bool = ...,
    ) -> Series: ...
    @overload
    def count(
        self, axis: Axis = ..., numeric_only: _bool = ..., *, level: Level
    ) -> DataFrame: ...
    @overload
    def count(
        self, axis: Axis = ..., level: None = ..., numeric_only: _bool = ...
    ) -> Series: ...
    def nunique(self, axis: Axis = ..., dropna: bool = ...) -> Series: ...
    def idxmax(
        self, axis: Axis = ..., skipna: _bool = ..., numeric_only: _bool = ...
    ) -> Series:
        """
Return index of first occurrence of maximum over requested axis.

NA/null values are excluded.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to use. 0 or 'index' for row-wise, 1 or 'columns' for column-wise.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
numeric_only : bool, default False
    Include only `float`, `int` or `boolean` data.

    .. versionadded:: 1.5.0

Returns
-------
Series
    Indexes of maxima along the specified axis.

Raises
------
ValueError
    * If the row/column is empty

See Also
--------
Series.idxmax : Return index of the maximum element.

Notes
-----
This method is the DataFrame version of ``ndarray.argmax``.

Examples
--------
Consider a dataset containing food consumption in Argentina.

>>> df = pd.DataFrame({'consumption': [10.51, 103.11, 55.48],
...                     'co2_emissions': [37.2, 19.66, 1712]},
...                   index=['Pork', 'Wheat Products', 'Beef'])

>>> df
                consumption  co2_emissions
Pork                  10.51         37.20
Wheat Products       103.11         19.66
Beef                  55.48       1712.00

By default, it returns the index for the maximum value in each column.

>>> df.idxmax()
consumption     Wheat Products
co2_emissions             Beef
dtype: object

To return the index for the maximum value in each row, use ``axis="columns"``.

>>> df.idxmax(axis="columns")
Pork              co2_emissions
Wheat Products     consumption
Beef              co2_emissions
dtype: object
        """
        pass
    def idxmin(
        self, axis: Axis = ..., skipna: _bool = ..., numeric_only: _bool = ...
    ) -> Series:
        """
Return index of first occurrence of minimum over requested axis.

NA/null values are excluded.

Parameters
----------
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to use. 0 or 'index' for row-wise, 1 or 'columns' for column-wise.
skipna : bool, default True
    Exclude NA/null values. If an entire row/column is NA, the result
    will be NA.
numeric_only : bool, default False
    Include only `float`, `int` or `boolean` data.

    .. versionadded:: 1.5.0

Returns
-------
Series
    Indexes of minima along the specified axis.

Raises
------
ValueError
    * If the row/column is empty

See Also
--------
Series.idxmin : Return index of the minimum element.

Notes
-----
This method is the DataFrame version of ``ndarray.argmin``.

Examples
--------
Consider a dataset containing food consumption in Argentina.

>>> df = pd.DataFrame({'consumption': [10.51, 103.11, 55.48],
...                     'co2_emissions': [37.2, 19.66, 1712]},
...                   index=['Pork', 'Wheat Products', 'Beef'])

>>> df
                consumption  co2_emissions
Pork                  10.51         37.20
Wheat Products       103.11         19.66
Beef                  55.48       1712.00

By default, it returns the index for the minimum value in each column.

>>> df.idxmin()
consumption                Pork
co2_emissions    Wheat Products
dtype: object

To return the index for the minimum value in each row, use ``axis="columns"``.

>>> df.idxmin(axis="columns")
Pork                consumption
Wheat Products    co2_emissions
Beef                consumption
dtype: object
        """
        pass
    @overload
    def mode(
        self,
        axis: Axis = ...,
        skipna: _bool = ...,
        numeric_only: _bool = ...,
        *,
        level: Level,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def mode(
        self,
        axis: Axis = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series: ...
    @overload
    def quantile(
        self,
        q: float = ...,
        axis: Axis = ...,
        numeric_only: _bool = ...,
        interpolation: QuantileInterpolation = ...,
        method: CalculationMethod = ...,
    ) -> Series: ...
    @overload
    def quantile(
        self,
        q: list[float] | np.ndarray,
        axis: Axis = ...,
        numeric_only: _bool = ...,
        interpolation: QuantileInterpolation = ...,
        method: CalculationMethod = ...,
    ) -> DataFrame: ...
    def to_timestamp(
        self,
        freq=...,
        how: TimestampConvention = ...,
        axis: Axis = ...,
        copy: _bool = ...,
    ) -> DataFrame: ...
    def to_period(
        self, freq: _str | None = ..., axis: Axis = ..., copy: _bool = ...
    ) -> DataFrame: ...
    def isin(self, values: Iterable | Series | DataFrame | dict) -> DataFrame: ...
    @property
    def plot(self) -> PlotAccessor: ...
    def hist(
        self,
        column: _str | list[_str] | None = ...,
        by: _str | ListLike | None = ...,
        grid: _bool = ...,
        xlabelsize: float | str | None = ...,
        xrot: float | None = ...,
        ylabelsize: float | str | None = ...,
        yrot: float | None = ...,
        ax: PlotAxes | None = ...,
        sharex: _bool = ...,
        sharey: _bool = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        bins: int | list = ...,
        backend: _str | None = ...,
        **kwargs,
    ): ...
    def boxplot(
        self,
        column: _str | list[_str] | None = ...,
        by: _str | ListLike | None = ...,
        ax: PlotAxes | None = ...,
        fontsize: float | _str | None = ...,
        rot: float = ...,
        grid: _bool = ...,
        figsize: tuple[float, float] | None = ...,
        layout: tuple[int, int] | None = ...,
        return_type: Literal["axes", "dict", "both"] | None = ...,
        backend: _str | None = ...,
        **kwargs,
    ): ...
    sparse = ...

    # The rest of these are remnants from the
    # stubs shipped at preview. They may belong in
    # base classes, or stubgen just failed to generate
    # these.

    Name: _str
    #
    # dunder methods
    def __iter__(self) -> Iterator[Hashable]: ...
    # properties
    @property
    def at(self): ...  # Not sure what to do with this yet; look at source
    @property
    def columns(self) -> Index[str]: ...
    @columns.setter  # setter needs to be right next to getter; otherwise mypy complains
    def columns(
        self, cols: AnyArrayLike | list[HashableT] | tuple[HashableT, ...]
    ) -> None: ...
    @property
    def dtypes(self) -> Series: ...
    @property
    def empty(self) -> _bool: ...
    @property
    def iat(self): ...  # Not sure what to do with this yet; look at source
    @property
    def iloc(self) -> _iLocIndexerFrame: ...
    @property
    def index(self) -> Index: ...
    @index.setter
    def index(self, idx: Index) -> None: ...
    @property
    def loc(self) -> _LocIndexerFrame: ...
    @property
    def ndim(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def values(self) -> np.ndarray: ...
    # methods
    def abs(self) -> DataFrame: ...
    def add(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Addition of dataframe and other, element-wise (binary operator `add`).

Equivalent to ``dataframe + other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `radd`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def add_prefix(self, prefix: _str, axis: Axis | None = None) -> DataFrame: ...
    def add_suffix(self, suffix: _str, axis: Axis | None = None) -> DataFrame: ...
    @overload
    def all(
        self,
        axis: None,
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
Series or DataFrame
    If level is specified, then, DataFrame is returned; otherwise, Series
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
    @overload
    def all(
        self,
        axis: Axis = ...,
        bool_only: _bool | None = ...,
        skipna: _bool = ...,
        **kwargs,
    ) -> Series[_bool]: ...
    @overload
    def any(
        self,
        *,
        axis: None,
        bool_only: _bool | None = ...,
        skipna: _bool = ...,
        **kwargs,
    ) -> _bool: ...
    @overload
    def any(
        self,
        *,
        axis: Axis = ...,
        bool_only: _bool | None = ...,
        skipna: _bool = ...,
        **kwargs,
    ) -> Series[_bool]: ...
    def asof(self, where, subset: _str | list[_str] | None = ...) -> DataFrame: ...
    def asfreq(
        self,
        freq,
        method: FillnaOptions | None = ...,
        how: Literal["start", "end"] | None = ...,
        normalize: _bool = ...,
        fill_value: Scalar | None = ...,
    ) -> DataFrame: ...
    def astype(
        self,
        dtype: AstypeArg | Mapping[Any, Dtype] | Series,
        copy: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> DataFrame: ...
    def at_time(
        self,
        time: _str | dt.time,
        asof: _bool = ...,
        axis: Axis | None = ...,
    ) -> DataFrame: ...
    def between_time(
        self,
        start_time: _str | dt.time,
        end_time: _str | dt.time,
        axis: Axis | None = ...,
    ) -> DataFrame: ...
    @overload
    def bfill(
        self,
        *,
        axis: Axis | None = ...,
        inplace: Literal[True],
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> None: ...
    @overload
    def bfill(
        self,
        *,
        axis: Axis | None = ...,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> DataFrame: ...
    def clip(
        self,
        lower: float | AnyArrayLike | None = ...,
        upper: float | AnyArrayLike | None = ...,
        *,
        axis: Axis | None = ...,
        inplace: _bool = ...,
        **kwargs,
    ) -> DataFrame: ...
    def copy(self, deep: _bool = ...) -> DataFrame: ...
    def cummax(
        self, axis: Axis | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> DataFrame:
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
Series or DataFrame
    Return cumulative maximum of Series or DataFrame.

See Also
--------
core.window.expanding.Expanding.max : Similar functionality
    but ignores ``NaN`` values.
DataFrame.max : Return the maximum over
    DataFrame axis.
DataFrame.cummax : Return cumulative maximum over DataFrame axis.
DataFrame.cummin : Return cumulative minimum over DataFrame axis.
DataFrame.cumsum : Return cumulative sum over DataFrame axis.
DataFrame.cumprod : Return cumulative product over DataFrame axis.

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
        self, axis: Axis | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> DataFrame:
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
Series or DataFrame
    Return cumulative minimum of Series or DataFrame.

See Also
--------
core.window.expanding.Expanding.min : Similar functionality
    but ignores ``NaN`` values.
DataFrame.min : Return the minimum over
    DataFrame axis.
DataFrame.cummax : Return cumulative maximum over DataFrame axis.
DataFrame.cummin : Return cumulative minimum over DataFrame axis.
DataFrame.cumsum : Return cumulative sum over DataFrame axis.
DataFrame.cumprod : Return cumulative product over DataFrame axis.

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
        self, axis: Axis | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> DataFrame:
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
Series or DataFrame
    Return cumulative product of Series or DataFrame.

See Also
--------
core.window.expanding.Expanding.prod : Similar functionality
    but ignores ``NaN`` values.
DataFrame.prod : Return the product over
    DataFrame axis.
DataFrame.cummax : Return cumulative maximum over DataFrame axis.
DataFrame.cummin : Return cumulative minimum over DataFrame axis.
DataFrame.cumsum : Return cumulative sum over DataFrame axis.
DataFrame.cumprod : Return cumulative product over DataFrame axis.

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
        self, axis: Axis | None = ..., skipna: _bool = ..., *args, **kwargs
    ) -> DataFrame:
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
Series or DataFrame
    Return cumulative sum of Series or DataFrame.

See Also
--------
core.window.expanding.Expanding.sum : Similar functionality
    but ignores ``NaN`` values.
DataFrame.sum : Return the sum over
    DataFrame axis.
DataFrame.cummax : Return cumulative maximum over DataFrame axis.
DataFrame.cummin : Return cumulative minimum over DataFrame axis.
DataFrame.cumsum : Return cumulative sum over DataFrame axis.
DataFrame.cumprod : Return cumulative product over DataFrame axis.

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
    def describe(
        self,
        percentiles: list[float] | None = ...,
        include: Literal["all"] | list[Dtype] | None = ...,
        exclude: list[Dtype] | None = ...,
    ) -> DataFrame: ...
    def div(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Floating division of dataframe and other, element-wise (binary operator `truediv`).

Equivalent to ``dataframe / other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rtruediv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def divide(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Floating division of dataframe and other, element-wise (binary operator `truediv`).

Equivalent to ``dataframe / other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rtruediv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def droplevel(self, level: Level | list[Level], axis: Axis = ...) -> DataFrame: ...
    def eq(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Equal to of dataframe and other, element-wise (binary operator `eq`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    def equals(self, other: Series | DataFrame) -> _bool: ...
    def ewm(
        self,
        com: float | None = ...,
        span: float | None = ...,
        halflife: float | None = ...,
        alpha: float | None = ...,
        min_periods: int = ...,
        adjust: _bool = ...,
        ignore_na: _bool = ...,
        axis: Axis = ...,
    ) -> ExponentialMovingWindow[DataFrame]: ...
    def expanding(
        self,
        min_periods: int = ...,
        axis: AxisIndex = ...,
        method: CalculationMethod = ...,
    ) -> Expanding[DataFrame]: ...
    @overload
    def ffill(
        self,
        *,
        axis: Axis | None = ...,
        inplace: Literal[True],
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> None: ...
    @overload
    def ffill(
        self,
        *,
        axis: Axis | None = ...,
        inplace: Literal[False] = ...,
        limit: int | None = ...,
        downcast: dict | None = ...,
    ) -> DataFrame: ...
    def filter(
        self,
        items: ListLike | None = ...,
        like: _str | None = ...,
        regex: _str | None = ...,
        axis: Axis | None = ...,
    ) -> DataFrame: ...
    def first(self, offset) -> DataFrame: ...
    def first_valid_index(self) -> Scalar: ...
    def floordiv(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Integer division of dataframe and other, element-wise (binary operator `floordiv`).

Equivalent to ``dataframe // other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rfloordiv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    # def from_dict
    # def from_records
    def ge(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Greater than or equal to of dataframe and other, element-wise (binary operator `ge`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    @overload
    def get(self, key: Hashable, default: None = ...) -> Series | None: ...
    @overload
    def get(self, key: Hashable, default: _T) -> Series | _T: ...
    @overload
    def get(self, key: list[Hashable], default: None = ...) -> DataFrame | None: ...
    @overload
    def get(self, key: list[Hashable], default: _T) -> DataFrame | _T: ...
    def gt(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Greater than of dataframe and other, element-wise (binary operator `gt`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    def head(self, n: int = ...) -> DataFrame: ...
    def infer_objects(self) -> DataFrame: ...
    # def info
    @overload
    def interpolate(
        self,
        method: InterpolateOptions = ...,
        *,
        axis: Axis = ...,
        limit: int | None = ...,
        limit_direction: Literal["forward", "backward", "both"] = ...,
        limit_area: Literal["inside", "outside"] | None = ...,
        downcast: Literal["infer"] | None = ...,
        inplace: Literal[True],
        **kwargs,
    ) -> None: ...
    @overload
    def interpolate(
        self,
        method: InterpolateOptions = ...,
        *,
        axis: Axis = ...,
        limit: int | None = ...,
        limit_direction: Literal["forward", "backward", "both"] = ...,
        limit_area: Literal["inside", "outside"] | None = ...,
        downcast: Literal["infer"] | None = ...,
        inplace: Literal[False] = ...,
        **kwargs,
    ) -> DataFrame: ...
    @overload
    def interpolate(
        self,
        method: InterpolateOptions = ...,
        *,
        axis: Axis = ...,
        limit: int | None = ...,
        inplace: _bool | None = ...,
        limit_direction: Literal["forward", "backward", "both"] = ...,
        limit_area: Literal["inside", "outside"] | None = ...,
        downcast: Literal["infer"] | None = ...,
        **kwargs,
    ) -> DataFrame | None: ...
    def keys(self) -> Index: ...
    def kurt(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return unbiased kurtosis over requested axis.

Kurtosis obtained using Fisher's definition of
kurtosis (kurtosis of normal == 0.0). Normalized by N-1.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return unbiased kurtosis over requested axis.

Kurtosis obtained using Fisher's definition of
kurtosis (kurtosis of normal == 0.0). Normalized by N-1.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
    def last(self, offset) -> DataFrame: ...
    def last_valid_index(self) -> Scalar: ...
    def le(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Less than or equal to of dataframe and other, element-wise (binary operator `le`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    def lt(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Less than of dataframe and other, element-wise (binary operator `lt`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    def mask(
        self,
        cond: (
            Series
            | DataFrame
            | np.ndarray
            | Callable[[DataFrame], DataFrame]
            | Callable[[Any], _bool]
        ),
        other=...,
        *,
        inplace: _bool = ...,
        axis: Axis | None = ...,
        level: Level | None = ...,
    ) -> DataFrame: ...
    def max(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return the maximum of the values over the requested axis.

If you want the *index* of the maximum, use ``idxmax``. This is the equivalent of the ``numpy.ndarray`` method ``argmax``.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return the mean of the values over the requested axis.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return the median of the values over the requested axis.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return the minimum of the values over the requested axis.

If you want the *index* of the minimum, use ``idxmin``. This is the equivalent of the ``numpy.ndarray`` method ``argmin``.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Modulo of dataframe and other, element-wise (binary operator `mod`).

Equivalent to ``dataframe % other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rmod`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def mul(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Multiplication of dataframe and other, element-wise (binary operator `mul`).

Equivalent to ``dataframe * other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rmul`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def multiply(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Multiplication of dataframe and other, element-wise (binary operator `mul`).

Equivalent to ``dataframe * other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rmul`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def ne(self, other, axis: Axis = ..., level: Level | None = ...) -> DataFrame:
        """
Get Not equal to of dataframe and other, element-wise (binary operator `ne`).

Among flexible wrappers (`eq`, `ne`, `le`, `lt`, `ge`, `gt`) to comparison
operators.

Equivalent to `==`, `!=`, `<=`, `<`, `>=`, `>` with support to choose axis
(rows or columns) and level for comparison.

Parameters
----------
other : scalar, sequence, Series, or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}, default 'columns'
    Whether to compare by the index (0 or 'index') or columns
    (1 or 'columns').
level : int or label
    Broadcast across a level, matching Index values on the passed
    MultiIndex level.

Returns
-------
DataFrame of bool
    Result of the comparison.

See Also
--------
DataFrame.eq : Compare DataFrames for equality elementwise.
DataFrame.ne : Compare DataFrames for inequality elementwise.
DataFrame.le : Compare DataFrames for less than inequality
    or equality elementwise.
DataFrame.lt : Compare DataFrames for strictly less than
    inequality elementwise.
DataFrame.ge : Compare DataFrames for greater than inequality
    or equality elementwise.
DataFrame.gt : Compare DataFrames for strictly greater than
    inequality elementwise.

Notes
-----
Mismatched indices will be unioned together.
`NaN` values are considered different (i.e. `NaN` != `NaN`).

Examples
--------
>>> df = pd.DataFrame({'cost': [250, 150, 100],
...                    'revenue': [100, 250, 300]},
...                   index=['A', 'B', 'C'])
>>> df
   cost  revenue
A   250      100
B   150      250
C   100      300

Comparison with a scalar, using either the operator or method:

>>> df == 100
    cost  revenue
A  False     True
B  False    False
C   True    False

>>> df.eq(100)
    cost  revenue
A  False     True
B  False    False
C   True    False

When `other` is a :class:`Series`, the columns of a DataFrame are aligned
with the index of `other` and broadcast:

>>> df != pd.Series([100, 250], index=["cost", "revenue"])
    cost  revenue
A   True     True
B   True    False
C  False     True

Use the method to control the broadcast axis:

>>> df.ne(pd.Series([100, 300], index=["A", "D"]), axis='index')
   cost  revenue
A  True    False
B  True     True
C  True     True
D  True     True

When comparing to an arbitrary sequence, the number of columns must
match the number elements in `other`:

>>> df == [250, 100]
    cost  revenue
A   True     True
B  False    False
C  False    False

Use the method to control the axis:

>>> df.eq([250, 250, 100], axis='index')
    cost  revenue
A   True    False
B  False     True
C   True    False

Compare to a DataFrame of different shape.

>>> other = pd.DataFrame({'revenue': [300, 250, 100, 150]},
...                      index=['A', 'B', 'C', 'D'])
>>> other
   revenue
A      300
B      250
C      100
D      150

>>> df.gt(other)
    cost  revenue
A  False    False
B  False    False
C  False     True
D  False    False

Compare to a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'cost': [250, 150, 100, 150, 300, 220],
...                              'revenue': [100, 250, 300, 200, 175, 225]},
...                             index=[['Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2'],
...                                    ['A', 'B', 'C', 'A', 'B', 'C']])
>>> df_multindex
      cost  revenue
Q1 A   250      100
   B   150      250
   C   100      300
Q2 A   150      200
   B   300      175
   C   220      225

>>> df.le(df_multindex, level=1)
       cost  revenue
Q1 A   True     True
   B   True     True
   C   True     True
Q2 A  False     True
   B   True    False
   C   True    False
        """
        pass
    def pct_change(
        self,
        periods: int = ...,
        fill_method: None = ...,
        limit: int | None = ...,
        freq=...,
        **kwargs,
    ) -> DataFrame: ...
    def pop(self, item: _str) -> Series: ...
    def pow(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Exponential power of dataframe and other, element-wise (binary operator `pow`).

Equivalent to ``dataframe ** other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rpow`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def prod(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Series:
        """
Return the product of the values over the requested axis.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        axis: Axis | None = ...,
        skipna: _bool = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Series:
        """
Return the product of the values over the requested axis.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Addition of dataframe and other, element-wise (binary operator `radd`).

Equivalent to ``other + dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `add`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def rank(
        self,
        axis: Axis = ...,
        method: Literal["average", "min", "max", "first", "dense"] = ...,
        numeric_only: _bool = ...,
        na_option: Literal["keep", "top", "bottom"] = ...,
        ascending: _bool = ...,
        pct: _bool = ...,
    ) -> DataFrame: ...
    def rdiv(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Floating division of dataframe and other, element-wise (binary operator `rtruediv`).

Equivalent to ``other / dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `truediv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def reindex_like(
        self,
        other: DataFrame,
        method: _str | FillnaOptions | Literal["nearest"] | None = ...,
        copy: _bool = ...,
        limit: int | None = ...,
        tolerance=...,
    ) -> DataFrame: ...
    @overload
    def rename_axis(
        self,
        mapper=...,
        axis: Axis | None = ...,
        copy: _bool = ...,
        *,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def rename_axis(
        self,
        mapper=...,
        axis: Axis | None = ...,
        copy: _bool = ...,
        *,
        inplace: Literal[False] = ...,
    ) -> DataFrame: ...
    @overload
    def rename_axis(
        self,
        index: _str | Sequence[_str] | dict[_str | int, _str] | Callable | None = ...,
        columns: _str | Sequence[_str] | dict[_str | int, _str] | Callable | None = ...,
        copy: _bool = ...,
        *,
        inplace: Literal[True],
    ) -> None: ...
    @overload
    def rename_axis(
        self,
        index: _str | Sequence[_str] | dict[_str | int, _str] | Callable | None = ...,
        columns: _str | Sequence[_str] | dict[_str | int, _str] | Callable | None = ...,
        copy: _bool = ...,
        *,
        inplace: Literal[False] = ...,
    ) -> DataFrame: ...
    def rfloordiv(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Integer division of dataframe and other, element-wise (binary operator `rfloordiv`).

Equivalent to ``other // dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `floordiv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def rmod(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Modulo of dataframe and other, element-wise (binary operator `rmod`).

Equivalent to ``other % dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `mod`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def rmul(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Multiplication of dataframe and other, element-wise (binary operator `rmul`).

Equivalent to ``other * dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `mul`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    @overload
    def rolling(
        self,
        window: int | str | dt.timedelta | BaseOffset | BaseIndexer,
        min_periods: int | None = ...,
        center: _bool = ...,
        on: Hashable | None = ...,
        axis: AxisIndex = ...,
        closed: IntervalClosedType | None = ...,
        step: int | None = ...,
        method: CalculationMethod = ...,
        *,
        win_type: _str,
    ) -> Window[DataFrame]: ...
    @overload
    def rolling(
        self,
        window: int | str | dt.timedelta | BaseOffset | BaseIndexer,
        min_periods: int | None = ...,
        center: _bool = ...,
        on: Hashable | None = ...,
        axis: AxisIndex = ...,
        closed: IntervalClosedType | None = ...,
        step: int | None = ...,
        method: CalculationMethod = ...,
        *,
        win_type: None = ...,
    ) -> Rolling[DataFrame]: ...
    def rpow(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Exponential power of dataframe and other, element-wise (binary operator `rpow`).

Equivalent to ``other ** dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `pow`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def rsub(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Subtraction of dataframe and other, element-wise (binary operator `rsub`).

Equivalent to ``other - dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `sub`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def rtruediv(
        self,
        other,
        axis: Axis = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Floating division of dataframe and other, element-wise (binary operator `rtruediv`).

Equivalent to ``other / dataframe``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `truediv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    # sample is missing a weights arg
    def sample(
        self,
        n: int | None = ...,
        frac: float | None = ...,
        replace: _bool = ...,
        weights: _str | ListLike | None = ...,
        random_state: RandomState | None = ...,
        axis: AxisIndex | None = ...,
        ignore_index: _bool = ...,
    ) -> DataFrame: ...
    def sem(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return unbiased standard error of the mean over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument

Parameters
----------
axis : {index (0), columns (1)}
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
Series or DataFrame (if level specified) 

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
    # Not actually positional, but used to handle removal of deprecated
    def set_axis(self, labels, *, axis: Axis, copy: _bool = ...) -> DataFrame:
        """
Assign desired index to given axis.

Indexes for column or row labels can be changed by assigning
a list-like or Index.

Parameters
----------
labels : list-like, Index
    The values for the new index.

axis : {0 or 'index', 1 or 'columns'}, default 0
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
DataFrame
    An object of type DataFrame.

See Also
--------
DataFrame.rename_axis : Alter the name of the index or columns.

        Examples
        --------
        >>> df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        Change the row labels.

        >>> df.set_axis(['a', 'b', 'c'], axis='index')
           A  B
        a  1  4
        b  2  5
        c  3  6

        Change the column labels.

        >>> df.set_axis(['I', 'II'], axis='columns')
           I  II
        0  1   4
        1  2   5
        2  3   6
        """
        pass
    def skew(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return unbiased skew over requested axis.

Normalized by N-1.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
    def squeeze(self, axis: Axis | None = ...): ...
    def std(
        self,
        axis: Axis = ...,
        skipna: _bool = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return sample standard deviation over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or DataFrame (if level specified) 

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
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Subtraction of dataframe and other, element-wise (binary operator `sub`).

Equivalent to ``dataframe - other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rsub`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def subtract(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Subtraction of dataframe and other, element-wise (binary operator `sub`).

Equivalent to ``dataframe - other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rsub`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def sum(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        numeric_only: _bool = ...,
        min_count: int = ...,
        **kwargs,
    ) -> Series:
        """
Return the sum of the values over the requested axis.

This is equivalent to the method ``numpy.sum``.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or scalar

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
    def swapaxes(self, axis1: Axis, axis2: Axis, copy: _bool = ...) -> DataFrame: ...
    def tail(self, n: int = ...) -> DataFrame: ...
    def take(self, indices: list, axis: Axis = ..., **kwargs) -> DataFrame: ...
    def to_clipboard(
        self, excel: _bool = ..., sep: _str | None = ..., **kwargs
    ) -> None: ...
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
        path_or_buf: None = ...,
        orient: JsonFrameOrient | None = ...,
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
    @overload
    def to_json(
        self,
        path_or_buf: FilePath | WriteBuffer[str],
        orient: JsonFrameOrient | None = ...,
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
    def to_string(
        self,
        buf: FilePath | WriteBuffer[str],
        columns: list[HashableT1] | Index | Series | None = ...,
        col_space: int | list[int] | dict[HashableT2, int] | None = ...,
        header: _bool | list[_str] | tuple[str, ...] = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters: FormattersType | None = ...,
        float_format: Callable[[float], str] | None = ...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        justify: _str | None = ...,
        max_rows: int | None = ...,
        max_cols: int | None = ...,
        show_dimensions: _bool = ...,
        decimal: _str = ...,
        line_width: int | None = ...,
        min_rows: int | None = ...,
        max_colwidth: int | None = ...,
        encoding: _str | None = ...,
    ) -> None: ...
    @overload
    def to_string(
        self,
        buf: None = ...,
        columns: list[HashableT] | Index | Series | None = ...,
        col_space: int | list[int] | dict[Hashable, int] | None = ...,
        header: _bool | Sequence[_str] = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters: FormattersType | None = ...,
        float_format: Callable[[float], str] | None = ...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        justify: _str | None = ...,
        max_rows: int | None = ...,
        max_cols: int | None = ...,
        show_dimensions: _bool = ...,
        decimal: _str = ...,
        line_width: int | None = ...,
        min_rows: int | None = ...,
        max_colwidth: int | None = ...,
        encoding: _str | None = ...,
    ) -> _str: ...
    def to_xarray(self) -> xr.Dataset: ...
    def truediv(
        self,
        other: num | ListLike | DataFrame,
        axis: Axis | None = ...,
        level: Level | None = ...,
        fill_value: float | None = ...,
    ) -> DataFrame:
        """
Get Floating division of dataframe and other, element-wise (binary operator `truediv`).

Equivalent to ``dataframe / other``, but with support to substitute a fill_value
for missing data in one of the inputs. With reverse version, `rtruediv`.

Among flexible wrappers (`add`, `sub`, `mul`, `div`, `floordiv`, `mod`, `pow`) to
arithmetic operators: `+`, `-`, `*`, `/`, `//`, `%`, `**`.

Parameters
----------
other : scalar, sequence, Series, dict or DataFrame
    Any single or multiple element data structure, or list-like object.
axis : {0 or 'index', 1 or 'columns'}
    Whether to compare by the index (0 or 'index') or columns.
    (1 or 'columns'). For Series input, axis to match Series index on.
level : int or label
    Broadcast across a level, matching Index values on the
    passed MultiIndex level.
fill_value : float or None, default None
    Fill existing missing (NaN) values, and any new element needed for
    successful DataFrame alignment, with this value before computation.
    If data in both corresponding DataFrame locations is missing
    the result will be missing.

Returns
-------
DataFrame
    Result of the arithmetic operation.

See Also
--------
DataFrame.add : Add DataFrames.
DataFrame.sub : Subtract DataFrames.
DataFrame.mul : Multiply DataFrames.
DataFrame.div : Divide DataFrames (float division).
DataFrame.truediv : Divide DataFrames (float division).
DataFrame.floordiv : Divide DataFrames (integer division).
DataFrame.mod : Calculate modulo (remainder after division).
DataFrame.pow : Calculate exponential power.

Notes
-----
Mismatched indices will be unioned together.

Examples
--------
>>> df = pd.DataFrame({'angles': [0, 3, 4],
...                    'degrees': [360, 180, 360]},
...                   index=['circle', 'triangle', 'rectangle'])
>>> df
           angles  degrees
circle          0      360
triangle        3      180
rectangle       4      360

Add a scalar with operator version which return the same
results.

>>> df + 1
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

>>> df.add(1)
           angles  degrees
circle          1      361
triangle        4      181
rectangle       5      361

Divide by constant with reverse version.

>>> df.div(10)
           angles  degrees
circle        0.0     36.0
triangle      0.3     18.0
rectangle     0.4     36.0

>>> df.rdiv(10)
             angles   degrees
circle          inf  0.027778
triangle   3.333333  0.055556
rectangle  2.500000  0.027778

Subtract a list and Series by axis with operator version.

>>> df - [1, 2]
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub([1, 2], axis='columns')
           angles  degrees
circle         -1      358
triangle        2      178
rectangle       3      358

>>> df.sub(pd.Series([1, 1, 1], index=['circle', 'triangle', 'rectangle']),
...        axis='index')
           angles  degrees
circle         -1      359
triangle        2      179
rectangle       3      359

Multiply a dictionary by axis.

>>> df.mul({'angles': 0, 'degrees': 2})
            angles  degrees
circle           0      720
triangle         0      360
rectangle        0      720

>>> df.mul({'circle': 0, 'triangle': 2, 'rectangle': 3}, axis='index')
            angles  degrees
circle           0        0
triangle         6      360
rectangle       12     1080

Multiply a DataFrame of different shape with operator version.

>>> other = pd.DataFrame({'angles': [0, 3, 4]},
...                      index=['circle', 'triangle', 'rectangle'])
>>> other
           angles
circle          0
triangle        3
rectangle       4

>>> df * other
           angles  degrees
circle          0      NaN
triangle        9      NaN
rectangle      16      NaN

>>> df.mul(other, fill_value=0)
           angles  degrees
circle          0      0.0
triangle        9      0.0
rectangle      16      0.0

Divide by a MultiIndex by level.

>>> df_multindex = pd.DataFrame({'angles': [0, 3, 4, 4, 5, 6],
...                              'degrees': [360, 180, 360, 360, 540, 720]},
...                             index=[['A', 'A', 'A', 'B', 'B', 'B'],
...                                    ['circle', 'triangle', 'rectangle',
...                                     'square', 'pentagon', 'hexagon']])
>>> df_multindex
             angles  degrees
A circle          0      360
  triangle        3      180
  rectangle       4      360
B square          4      360
  pentagon        5      540
  hexagon         6      720

>>> df.div(df_multindex, level=1, fill_value=0)
             angles  degrees
A circle        NaN      1.0
  triangle      1.0      1.0
  rectangle     1.0      1.0
B square        0.0      0.0
  pentagon      0.0      0.0
  hexagon       0.0      0.0
        """
        pass
    def truncate(
        self,
        before: dt.date | _str | int | None = ...,
        after: dt.date | _str | int | None = ...,
        axis: Axis | None = ...,
        copy: _bool = ...,
    ) -> DataFrame: ...
    def tz_convert(
        self,
        tz,
        axis: Axis = ...,
        level: Level | None = ...,
        copy: _bool = ...,
    ) -> DataFrame: ...
    def tz_localize(
        self,
        tz,
        axis: Axis = ...,
        level: Level | None = ...,
        copy: _bool = ...,
        ambiguous=...,
        nonexistent: _str = ...,
    ) -> DataFrame: ...
    def var(
        self,
        axis: Axis | None = ...,
        skipna: _bool | None = ...,
        level: None = ...,
        ddof: int = ...,
        numeric_only: _bool = ...,
        **kwargs,
    ) -> Series:
        """
Return unbiased variance over requested axis.

Normalized by N-1 by default. This can be changed using the ddof argument.

Parameters
----------
axis : {index (0), columns (1)}
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
Series or DataFrame (if level specified) 

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
    def where(
        self,
        cond: (
            Series
            | DataFrame
            | np.ndarray
            | Callable[[DataFrame], DataFrame]
            | Callable[[Any], _bool]
        ),
        other=...,
        *,
        inplace: _bool = ...,
        axis: Axis | None = ...,
        level: Level | None = ...,
    ) -> DataFrame: ...
    # Move from generic because Series is Generic and it returns Series[bool] there
    def __invert__(self) -> DataFrame: ...
    def xs(
        self,
        key: Hashable,
        axis: Axis = ...,
        level: Level | None = ...,
        drop_level: _bool = ...,
    ) -> DataFrame | Series: ...
    # floordiv overload
    def __floordiv__(
        self, other: float | DataFrame | Series[int] | Series[float] | Sequence[float]
    ) -> Self: ...
    def __rfloordiv__(
        self, other: float | DataFrame | Series[int] | Series[float] | Sequence[float]
    ) -> Self: ...
    def __truediv__(self, other: float | DataFrame | Series | Sequence) -> Self: ...
    def __rtruediv__(self, other: float | DataFrame | Series | Sequence) -> Self: ...

class _PandasNamedTuple(tuple[Any, ...]):
    def __getattr__(self, field: str) -> Scalar: ...
