from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Mapping,
    Sequence,
)
import datetime as dt
import sqlite3
from typing import (
    Any,
    ClassVar,
    Literal,
    final,
    overload,
)

import numpy as np
from pandas import Index
import pandas.core.indexing as indexing
from pandas.core.resample import DatetimeIndexResampler
from pandas.core.series import Series
import sqlalchemy.engine
from typing_extensions import (
    Concatenate,
    Self,
)

from pandas._libs.lib import NoDefault
from pandas._typing import (
    S1,
    ArrayLike,
    Axis,
    AxisIndex,
    CompressionOptions,
    CSVQuoting,
    DtypeArg,
    DtypeBackend,
    FilePath,
    FileWriteMode,
    FillnaOptions,
    Frequency,
    HashableT1,
    HashableT2,
    HDFCompLib,
    IgnoreRaise,
    IndexLabel,
    Level,
    P,
    ReplaceMethod,
    SortKind,
    StorageOptions,
    T,
    TimedeltaConvertibleTypes,
    TimeGrouperOrigin,
    TimestampConvention,
    TimestampConvertibleTypes,
    WriteBuffer,
)

from pandas.io.pytables import HDFStore
from pandas.io.sql import SQLTable

_bool = bool
_str = str

class NDFrame(indexing.IndexingMixin):
    __hash__: ClassVar[None]  # type: ignore[assignment] # pyright: ignore[reportIncompatibleMethodOverride]

    def set_flags(
        self,
        *,
        copy: bool = ...,
        allows_duplicate_labels: bool | None = ...,
    ) -> Self: ...
    @property
    def attrs(self) -> dict[Hashable | None, Any]: ...
    @attrs.setter
    def attrs(self, value: Mapping[Hashable | None, Any]) -> None: ...
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def axes(self) -> list[Index]: ...
    @property
    def ndim(self) -> int: ...
    @property
    def size(self) -> int: ...
    def droplevel(self, level: Level, axis: AxisIndex = ...) -> Self:
        """
Return Series/DataFrame with requested index / column level(s) removed.

Parameters
----------
level : int, str, or list-like
    If a string is given, must be the name of a level
    If list-like, elements must be names or positional indexes
    of levels.

axis : {0 or 'index', 1 or 'columns'}, default 0
    Axis along which the level(s) is removed:

    * 0 or 'index': remove level(s) in column.
    * 1 or 'columns': remove level(s) in row.

    For `Series` this parameter is unused and defaults to 0.

Returns
-------
Series/DataFrame
    Series/DataFrame with requested index / column level(s) removed.

Examples
--------
>>> df = pd.DataFrame([
...     [1, 2, 3, 4],
...     [5, 6, 7, 8],
...     [9, 10, 11, 12]
... ]).set_index([0, 1]).rename_axis(['a', 'b'])

>>> df.columns = pd.MultiIndex.from_tuples([
...     ('c', 'e'), ('d', 'f')
... ], names=['level_1', 'level_2'])

>>> df
level_1   c   d
level_2   e   f
a b
1 2      3   4
5 6      7   8
9 10    11  12

>>> df.droplevel('a')
level_1   c   d
level_2   e   f
b
2        3   4
6        7   8
10      11  12

>>> df.droplevel('level_2', axis=1)
level_1   c   d
a b
1 2      3   4
5 6      7   8
9 10    11  12
        """
        pass
    def squeeze(self, axis=...): ...
    def equals(self, other: Series[S1]) -> _bool: ...
    def __neg__(self) -> Self: ...
    def __pos__(self) -> Self: ...
    def __nonzero__(self) -> None: ...
    @final
    def bool(self) -> _bool: ...
    def __abs__(self) -> Self: ...
    def __round__(self, decimals: int = ...) -> Self: ...
    def keys(self): ...
    def __len__(self) -> int: ...
    def __contains__(self, key) -> _bool: ...
    @property
    def empty(self) -> _bool: ...
    __array_priority__: int = ...
    def __array__(self, dtype=...) -> np.ndarray: ...
    def to_excel(
        self,
        excel_writer,
        sheet_name: _str = ...,
        na_rep: _str = ...,
        float_format: _str | None = ...,
        columns: _str | Sequence[_str] | None = ...,
        header: _bool | list[_str] = ...,
        index: _bool = ...,
        index_label: _str | Sequence[_str] | None = ...,
        startrow: int = ...,
        startcol: int = ...,
        engine: _str | None = ...,
        merge_cells: _bool = ...,
        inf_rep: _str = ...,
        freeze_panes: tuple[int, int] | None = ...,
    ) -> None:
        """
Write object to an Excel sheet.

To write a single object to an Excel .xlsx file it is only necessary to
specify a target file name. To write to multiple sheets it is necessary to
create an `ExcelWriter` object with a target file name, and specify a sheet
in the file to write to.

Multiple sheets may be written to by specifying unique `sheet_name`.
With all data written to the file it is necessary to save the changes.
Note that creating an `ExcelWriter` object with a file name that already
exists will result in the contents of the existing file being erased.

Parameters
----------
excel_writer : path-like, file-like, or ExcelWriter object
    File path or existing ExcelWriter.
sheet_name : str, default 'Sheet1'
    Name of sheet which will contain DataFrame.
na_rep : str, default ''
    Missing data representation.
float_format : str, optional
    Format string for floating point numbers. For example
    ``float_format="%.2f"`` will format 0.1234 to 0.12.
columns : sequence or list of str, optional
    Columns to write.
header : bool or list of str, default True
    Write out the column names. If a list of string is given it is
    assumed to be aliases for the column names.
index : bool, default True
    Write row names (index).
index_label : str or sequence, optional
    Column label for index column(s) if desired. If not specified, and
    `header` and `index` are True, then the index names are used. A
    sequence should be given if the DataFrame uses MultiIndex.
startrow : int, default 0
    Upper left cell row to dump data frame.
startcol : int, default 0
    Upper left cell column to dump data frame.
engine : str, optional
    Write engine to use, 'openpyxl' or 'xlsxwriter'. You can also set this
    via the options ``io.excel.xlsx.writer`` or
    ``io.excel.xlsm.writer``.

merge_cells : bool, default True
    Write MultiIndex and Hierarchical Rows as merged cells.
inf_rep : str, default 'inf'
    Representation for infinity (there is no native representation for
    infinity in Excel).
freeze_panes : tuple of int (length 2), optional
    Specifies the one-based bottommost row and rightmost column that
    is to be frozen.
storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

    .. versionadded:: 1.2.0
engine_kwargs : dict, optional
    Arbitrary keyword arguments passed to excel engine.

See Also
--------
to_csv : Write DataFrame to a comma-separated values (csv) file.
ExcelWriter : Class for writing DataFrame objects into excel sheets.
read_excel : Read an Excel file into a pandas DataFrame.
read_csv : Read a comma-separated values (csv) file into DataFrame.
io.formats.style.Styler.to_excel : Add styles to Excel sheet.

Notes
-----
For compatibility with :meth:`~DataFrame.to_csv`,
to_excel serializes lists and dicts to strings before writing.

Once a workbook has been saved it is not possible to write further
data without rewriting the whole workbook.

Examples
--------

Create, write to and save a workbook:

>>> df1 = pd.DataFrame([['a', 'b'], ['c', 'd']],
...                    index=['row 1', 'row 2'],
...                    columns=['col 1', 'col 2'])
>>> df1.to_excel("output.xlsx")  # doctest: +SKIP

To specify the sheet name:

>>> df1.to_excel("output.xlsx",
...              sheet_name='Sheet_name_1')  # doctest: +SKIP

If you wish to write to more than one sheet in the workbook, it is
necessary to specify an ExcelWriter object:

>>> df2 = df1.copy()
>>> with pd.ExcelWriter('output.xlsx') as writer:  # doctest: +SKIP
...     df1.to_excel(writer, sheet_name='Sheet_name_1')
...     df2.to_excel(writer, sheet_name='Sheet_name_2')

ExcelWriter can also be used to append to an existing Excel file:

>>> with pd.ExcelWriter('output.xlsx',
...                     mode='a') as writer:  # doctest: +SKIP
...     df1.to_excel(writer, sheet_name='Sheet_name_3')

To set the library that is used to write the Excel file,
you can pass the `engine` keyword (the default engine is
automatically chosen depending on the file extension):

>>> df1.to_excel('output1.xlsx', engine='xlsxwriter')  # doctest: +SKIP
        """
        pass
    def to_hdf(
        self,
        path_or_buf: FilePath | HDFStore,
        *,
        key: _str,
        mode: Literal["a", "w", "r+"] = ...,
        complevel: int | None = ...,
        complib: HDFCompLib | None = ...,
        append: _bool = ...,
        format: Literal["t", "table", "f", "fixed"] | None = ...,
        index: _bool = ...,
        min_itemsize: int | dict[HashableT1, int] | None = ...,
        nan_rep: _str | None = ...,
        dropna: _bool | None = ...,
        data_columns: Literal[True] | list[HashableT2] | None = ...,
        errors: Literal[
            "strict",
            "ignore",
            "replace",
            "surrogateescape",
            "xmlcharrefreplace",
            "backslashreplace",
            "namereplace",
        ] = ...,
        encoding: _str = ...,
    ) -> None: ...
    @overload
    def to_markdown(
        self,
        buf: FilePath | WriteBuffer[str],
        mode: FileWriteMode | None = ...,
        index: _bool = ...,
        storage_options: StorageOptions = ...,
        **kwargs: Any,
    ) -> None: ...
    @overload
    def to_markdown(
        self,
        buf: None = ...,
        mode: FileWriteMode | None = ...,
        index: _bool = ...,
        storage_options: StorageOptions = ...,
        **kwargs: Any,
    ) -> _str: ...
    def to_sql(
        self,
        name: _str,
        con: str | sqlalchemy.engine.Connectable | sqlite3.Connection,
        schema: _str | None = ...,
        if_exists: Literal["fail", "replace", "append"] = ...,
        index: _bool = ...,
        index_label: IndexLabel = ...,
        chunksize: int | None = ...,
        dtype: DtypeArg | None = ...,
        method: (
            Literal["multi"]
            | Callable[
                [SQLTable, Any, list[str], Iterable[tuple[Any, ...]]],
                int | None,
            ]
            | None
        ) = ...,
    ) -> int | None: ...
    def to_pickle(
        self,
        path: FilePath | WriteBuffer[bytes],
        compression: CompressionOptions = ...,
        protocol: int = ...,
        storage_options: StorageOptions = ...,
    ) -> None:
        """
Pickle (serialize) object to file.

Parameters
----------
path : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``write()`` function. File path where
    the pickled object will be stored.
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
protocol : int
    Int which indicates which protocol should be used by the pickler,
    default HIGHEST_PROTOCOL (see [1]_ paragraph 12.1.2). The possible
    values are 0, 1, 2, 3, 4, 5. A negative value for the protocol
    parameter is equivalent to setting its value to HIGHEST_PROTOCOL.

    .. [1] https://docs.python.org/3/library/pickle.html.

storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

See Also
--------
read_pickle : Load pickled pandas object (or any object) from file.
DataFrame.to_hdf : Write DataFrame to an HDF5 file.
DataFrame.to_sql : Write DataFrame to a SQL database.
DataFrame.to_parquet : Write a DataFrame to the binary parquet format.

Examples
--------
>>> original_df = pd.DataFrame({"foo": range(5), "bar": range(5, 10)})  # doctest: +SKIP
>>> original_df  # doctest: +SKIP
   foo  bar
0    0    5
1    1    6
2    2    7
3    3    8
4    4    9
>>> original_df.to_pickle("./dummy.pkl")  # doctest: +SKIP

>>> unpickled_df = pd.read_pickle("./dummy.pkl")  # doctest: +SKIP
>>> unpickled_df  # doctest: +SKIP
   foo  bar
0    0    5
1    1    6
2    2    7
3    3    8
4    4    9
        """
        pass
    def to_clipboard(
        self, excel: _bool = ..., sep: _str | None = ..., **kwargs
    ) -> None: ...
    @overload
    def to_latex(
        self,
        buf: FilePath | WriteBuffer[str],
        columns: list[_str] | None = ...,
        header: _bool | list[_str] = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters=...,
        float_format=...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        bold_rows: _bool = ...,
        column_format: _str | None = ...,
        longtable: _bool | None = ...,
        escape: _bool | None = ...,
        encoding: _str | None = ...,
        decimal: _str = ...,
        multicolumn: _bool | None = ...,
        multicolumn_format: _str | None = ...,
        multirow: _bool | None = ...,
        caption: _str | tuple[_str, _str] | None = ...,
        label: _str | None = ...,
        position: _str | None = ...,
    ) -> None: ...
    @overload
    def to_latex(
        self,
        buf: None = ...,
        columns: list[_str] | None = ...,
        header: _bool | list[_str] = ...,
        index: _bool = ...,
        na_rep: _str = ...,
        formatters=...,
        float_format=...,
        sparsify: _bool | None = ...,
        index_names: _bool = ...,
        bold_rows: _bool = ...,
        column_format: _str | None = ...,
        longtable: _bool | None = ...,
        escape: _bool | None = ...,
        encoding: _str | None = ...,
        decimal: _str = ...,
        multicolumn: _bool | None = ...,
        multicolumn_format: _str | None = ...,
        multirow: _bool | None = ...,
        caption: _str | tuple[_str, _str] | None = ...,
        label: _str | None = ...,
        position: _str | None = ...,
    ) -> _str: ...
    @overload
    def to_csv(
        self,
        path_or_buf: FilePath | WriteBuffer[bytes] | WriteBuffer[str],
        sep: _str = ...,
        na_rep: _str = ...,
        float_format: _str | Callable[[object], _str] | None = ...,
        columns: list[HashableT1] | None = ...,
        header: _bool | list[_str] = ...,
        index: _bool = ...,
        index_label: Literal[False] | _str | list[HashableT2] | None = ...,
        mode: FileWriteMode = ...,
        encoding: _str | None = ...,
        compression: CompressionOptions = ...,
        quoting: CSVQuoting = ...,
        quotechar: _str = ...,
        lineterminator: _str | None = ...,
        chunksize: int | None = ...,
        date_format: _str | None = ...,
        doublequote: _bool = ...,
        escapechar: _str | None = ...,
        decimal: _str = ...,
        errors: _str = ...,
        storage_options: StorageOptions = ...,
    ) -> None:
        """
Write object to a comma-separated values (csv) file.

Parameters
----------
path_or_buf : str, path object, file-like object, or None, default None
    String, path object (implementing os.PathLike[str]), or file-like
    object implementing a write() function. If None, the result is
    returned as a string. If a non-binary file object is passed, it should
    be opened with `newline=''`, disabling universal newlines. If a binary
    file object is passed, `mode` might need to contain a `'b'`.
sep : str, default ','
    String of length 1. Field delimiter for the output file.
na_rep : str, default ''
    Missing data representation.
float_format : str, Callable, default None
    Format string for floating point numbers. If a Callable is given, it takes
    precedence over other numeric formatting parameters, like decimal.
columns : sequence, optional
    Columns to write.
header : bool or list of str, default True
    Write out the column names. If a list of strings is given it is
    assumed to be aliases for the column names.
index : bool, default True
    Write row names (index).
index_label : str or sequence, or False, default None
    Column label for index column(s) if desired. If None is given, and
    `header` and `index` are True, then the index names are used. A
    sequence should be given if the object uses MultiIndex. If
    False do not print fields for index names. Use index_label=False
    for easier importing in R.
mode : {'w', 'x', 'a'}, default 'w'
    Forwarded to either `open(mode=)` or `fsspec.open(mode=)` to control
    the file opening. Typical values include:

    - 'w', truncate the file first.
    - 'x', exclusive creation, failing if the file already exists.
    - 'a', append to the end of file if it exists.

encoding : str, optional
    A string representing the encoding to use in the output file,
    defaults to 'utf-8'. `encoding` is not supported if `path_or_buf`
    is a non-binary file object.
compression : str or dict, default 'infer'
    For on-the-fly compression of the output data. If 'infer' and 'path_or_buf' is
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

       May be a dict with key 'method' as compression mode
       and other entries as additional compression options if
       compression mode is 'zip'.

       Passing compression options as keys in dict is
       supported for compression modes 'gzip', 'bz2', 'zstd', and 'zip'.
quoting : optional constant from csv module
    Defaults to csv.QUOTE_MINIMAL. If you have set a `float_format`
    then floats are converted to strings and thus csv.QUOTE_NONNUMERIC
    will treat them as non-numeric.
quotechar : str, default '\"'
    String of length 1. Character used to quote fields.
lineterminator : str, optional
    The newline character or character sequence to use in the output
    file. Defaults to `os.linesep`, which depends on the OS in which
    this method is called ('\\n' for linux, '\\r\\n' for Windows, i.e.).

    .. versionchanged:: 1.5.0

        Previously was line_terminator, changed for consistency with
        read_csv and the standard library 'csv' module.

chunksize : int or None
    Rows to write at a time.
date_format : str, default None
    Format string for datetime objects.
doublequote : bool, default True
    Control quoting of `quotechar` inside a field.
escapechar : str, default None
    String of length 1. Character used to escape `sep` and `quotechar`
    when appropriate.
decimal : str, default '.'
    Character recognized as decimal separator. E.g. use ',' for
    European data.
errors : str, default 'strict'
    Specifies how encoding and decoding errors are to be handled.
    See the errors argument for :func:`open` for a full list
    of options.

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
    If path_or_buf is None, returns the resulting csv format as a
    string. Otherwise returns None.

See Also
--------
read_csv : Load a CSV file into a DataFrame.
to_excel : Write DataFrame to an Excel file.

Examples
--------
Create 'out.csv' containing 'df' without indices

>>> df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
...                    'mask': ['red', 'purple'],
...                    'weapon': ['sai', 'bo staff']})
>>> df.to_csv('out.csv', index=False)  # doctest: +SKIP

Create 'out.zip' containing 'out.csv'

>>> df.to_csv(index=False)
'name,mask,weapon\nRaphael,red,sai\nDonatello,purple,bo staff\n'
>>> compression_opts = dict(method='zip',
...                         archive_name='out.csv')  # doctest: +SKIP
>>> df.to_csv('out.zip', index=False,
...           compression=compression_opts)  # doctest: +SKIP

To write a csv file to a new folder or nested folder you will first
need to create it using either Pathlib or os:

>>> from pathlib import Path  # doctest: +SKIP
>>> filepath = Path('folder/subfolder/out.csv')  # doctest: +SKIP
>>> filepath.parent.mkdir(parents=True, exist_ok=True)  # doctest: +SKIP
>>> df.to_csv(filepath)  # doctest: +SKIP

>>> import os  # doctest: +SKIP
>>> os.makedirs('folder/subfolder', exist_ok=True)  # doctest: +SKIP
>>> df.to_csv('folder/subfolder/out.csv')  # doctest: +SKIP
        """
        pass
    @overload
    def to_csv(
        self,
        path_or_buf: None = ...,
        sep: _str = ...,
        na_rep: _str = ...,
        float_format: _str | Callable[[object], _str] | None = ...,
        columns: list[HashableT1] | None = ...,
        header: _bool | list[_str] = ...,
        index: _bool = ...,
        index_label: Literal[False] | _str | list[HashableT2] | None = ...,
        mode: FileWriteMode = ...,
        encoding: _str | None = ...,
        compression: CompressionOptions = ...,
        quoting: CSVQuoting = ...,
        quotechar: _str = ...,
        lineterminator: _str | None = ...,
        chunksize: int | None = ...,
        date_format: _str | None = ...,
        doublequote: _bool = ...,
        escapechar: _str | None = ...,
        decimal: _str = ...,
        errors: _str = ...,
        storage_options: StorageOptions = ...,
    ) -> _str: ...
    def take(self, indices, axis=..., **kwargs) -> Self: ...
    def __delitem__(self, idx: Hashable) -> None: ...
    def reindex_like(
        self,
        other,
        method: _str | None = ...,
        copy: _bool = ...,
        limit=...,
        tolerance=...,
    ) -> Self: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any] = ...,
        columns: Hashable | Sequence[Hashable] | Index[Any],
        level: Level | None = ...,
        inplace: Literal[True],
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any],
        columns: Hashable | Sequence[Hashable] | Index[Any] = ...,
        level: Level | None = ...,
        inplace: Literal[True],
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def drop(
        self,
        labels: Hashable | Sequence[Hashable] | Index[Any],
        *,
        axis: Axis = ...,
        index: None = ...,
        columns: None = ...,
        level: Level | None = ...,
        inplace: Literal[True],
        errors: IgnoreRaise = ...,
    ) -> None: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any] = ...,
        columns: Hashable | Sequence[Hashable] | Index[Any],
        level: Level | None = ...,
        inplace: Literal[False] = ...,
        errors: IgnoreRaise = ...,
    ) -> Self: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any],
        columns: Hashable | Sequence[Hashable] | Index[Any] = ...,
        level: Level | None = ...,
        inplace: Literal[False] = ...,
        errors: IgnoreRaise = ...,
    ) -> Self: ...
    @overload
    def drop(
        self,
        labels: Hashable | Sequence[Hashable] | Index[Any],
        *,
        axis: Axis = ...,
        index: None = ...,
        columns: None = ...,
        level: Level | None = ...,
        inplace: Literal[False] = ...,
        errors: IgnoreRaise = ...,
    ) -> Self: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any] = ...,
        columns: Hashable | Sequence[Hashable] | Index[Any],
        level: Level | None = ...,
        inplace: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Self | None: ...
    @overload
    def drop(
        self,
        labels: None = ...,
        *,
        axis: Axis = ...,
        index: Hashable | Sequence[Hashable] | Index[Any],
        columns: Hashable | Sequence[Hashable] | Index[Any] = ...,
        level: Level | None = ...,
        inplace: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Self | None: ...
    @overload
    def drop(
        self,
        labels: Hashable | Sequence[Hashable] | Index[Any],
        *,
        axis: Axis = ...,
        index: None = ...,
        columns: None = ...,
        level: Level | None = ...,
        inplace: _bool = ...,
        errors: IgnoreRaise = ...,
    ) -> Self | None: ...
    def add_prefix(self, prefix: _str) -> Self: ...
    def add_suffix(self, suffix: _str) -> Self: ...
    def sort_index(
        self,
        *,
        axis: Axis = ...,
        level=...,
        ascending: _bool = ...,
        inplace: _bool = ...,
        kind: SortKind = ...,
        na_position: Literal["first", "last"] = ...,
        sort_remaining: _bool = ...,
        ignore_index: _bool = ...,
    ): ...
    def filter(
        self,
        items=...,
        like: _str | None = ...,
        regex: _str | None = ...,
        axis=...,
    ) -> Self: ...
    def head(self, n: int = ...) -> Self: ...
    def tail(self, n: int = ...) -> Self: ...
    @overload
    def pipe(
        self,
        func: Callable[Concatenate[Self, P], T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """
Apply chainable functions that expect Series or DataFrames.

Parameters
----------
func : function
    Function to apply to the Series/DataFrame.
    ``args``, and ``kwargs`` are passed into ``func``.
    Alternatively a ``(callable, data_keyword)`` tuple where
    ``data_keyword`` is a string indicating the keyword of
    ``callable`` that expects the Series/DataFrame.
*args : iterable, optional
    Positional arguments passed into ``func``.
**kwargs : mapping, optional
    A dictionary of keyword arguments passed into ``func``.

Returns
-------
the return type of ``func``.

See Also
--------
DataFrame.apply : Apply a function along input axis of DataFrame.
DataFrame.map : Apply a function elementwise on a whole DataFrame.
Series.map : Apply a mapping correspondence on a
    :class:`~pandas.Series`.

Notes
-----
Use ``.pipe`` when chaining together functions that expect
Series, DataFrames or GroupBy objects.

Examples
--------
Constructing a income DataFrame from a dictionary.

>>> data = [[8000, 1000], [9500, np.nan], [5000, 2000]]
>>> df = pd.DataFrame(data, columns=['Salary', 'Others'])
>>> df
   Salary  Others
0    8000  1000.0
1    9500     NaN
2    5000  2000.0

Functions that perform tax reductions on an income DataFrame.

>>> def subtract_federal_tax(df):
...     return df * 0.9
>>> def subtract_state_tax(df, rate):
...     return df * (1 - rate)
>>> def subtract_national_insurance(df, rate, rate_increase):
...     new_rate = rate + rate_increase
...     return df * (1 - new_rate)

Instead of writing

>>> subtract_national_insurance(
...     subtract_state_tax(subtract_federal_tax(df), rate=0.12),
...     rate=0.05,
...     rate_increase=0.02)  # doctest: +SKIP

You can write

>>> (
...     df.pipe(subtract_federal_tax)
...     .pipe(subtract_state_tax, rate=0.12)
...     .pipe(subtract_national_insurance, rate=0.05, rate_increase=0.02)
... )
    Salary   Others
0  5892.48   736.56
1  6997.32      NaN
2  3682.80  1473.12

If you have a function that takes the data as (say) the second
argument, pass a tuple indicating which keyword expects the
data. For example, suppose ``national_insurance`` takes its data as ``df``
in the second argument:

>>> def subtract_national_insurance(rate, df, rate_increase):
...     new_rate = rate + rate_increase
...     return df * (1 - new_rate)
>>> (
...     df.pipe(subtract_federal_tax)
...     .pipe(subtract_state_tax, rate=0.12)
...     .pipe(
...         (subtract_national_insurance, 'df'),
...         rate=0.05,
...         rate_increase=0.02
...     )
... )
    Salary   Others
0  5892.48   736.56
1  6997.32      NaN
2  3682.80  1473.12
        """
        pass
    @overload
    def pipe(
        self,
        func: tuple[Callable[..., T], str],
        *args: Any,
        **kwargs: Any,
    ) -> T: ...
    def __finalize__(self, other, method=..., **kwargs) -> Self: ...
    def __setattr__(self, name: _str, value) -> None: ...
    @property
    def values(self) -> ArrayLike: ...
    @property
    def dtypes(self): ...
    def copy(self, deep: _bool = ...) -> Self: ...
    def __copy__(self, deep: _bool = ...) -> Self: ...
    def __deepcopy__(self, memo=...) -> Self: ...
    def infer_objects(self) -> Self: ...
    def convert_dtypes(
        self,
        infer_objects: _bool = ...,
        convert_string: _bool = ...,
        convert_integer: _bool = ...,
        convert_boolean: _bool = ...,
        convert_floating: _bool = ...,
        dtype_backend: DtypeBackend = ...,
    ) -> Self: ...
    def fillna(
        self,
        value=...,
        *,
        axis=...,
        inplace: _bool = ...,
        limit=...,
        downcast=...,
    ) -> NDFrame | None:
        """
Fill NA/NaN values using the specified method.

Parameters
----------
value : scalar, dict, Series, or DataFrame
    Value to use to fill holes (e.g. 0), alternately a
    dict/Series/DataFrame of values specifying which value to use for
    each index (for a Series) or column (for a DataFrame).  Values not
    in the dict/Series/DataFrame will not be filled. This value cannot
    be a list.
method : {'backfill', 'bfill', 'ffill', None}, default None
    Method to use for filling holes in reindexed Series:

    * ffill: propagate last valid observation forward to next valid.
    * backfill / bfill: use next valid observation to fill gap.

    .. deprecated:: 2.1.0
        Use ffill or bfill instead.

axis : {0 or 'index'} for Series, {0 or 'index', 1 or 'columns'} for DataFrame
    Axis along which to fill missing values. For `Series`
    this parameter is unused and defaults to 0.
inplace : bool, default False
    If True, fill in-place. Note: this will modify any
    other views on this object (e.g., a no-copy slice for a column in a
    DataFrame).
limit : int, default None
    If method is specified, this is the maximum number of consecutive
    NaN values to forward/backward fill. In other words, if there is
    a gap with more than this number of consecutive NaNs, it will only
    be partially filled. If method is not specified, this is the
    maximum number of entries along the entire axis where NaNs will be
    filled. Must be greater than 0 if not None.
downcast : dict, default is None
    A dict of item->dtype of what to downcast if possible,
    or the string 'infer' which will try to downcast to an appropriate
    equal type (e.g. float64 to int64 if possible).

    .. deprecated:: 2.2.0

Returns
-------
Series/DataFrame or None
    Object with missing values filled or None if ``inplace=True``.

See Also
--------
ffill : Fill values by propagating the last valid observation to next valid.
bfill : Fill values by using the next valid observation to fill the gap.
interpolate : Fill NaN values using interpolation.
reindex : Conform object to new index.
asfreq : Convert TimeSeries to specified frequency.

Examples
--------
>>> df = pd.DataFrame([[np.nan, 2, np.nan, 0],
...                    [3, 4, np.nan, 1],
...                    [np.nan, np.nan, np.nan, np.nan],
...                    [np.nan, 3, np.nan, 4]],
...                   columns=list("ABCD"))
>>> df
     A    B   C    D
0  NaN  2.0 NaN  0.0
1  3.0  4.0 NaN  1.0
2  NaN  NaN NaN  NaN
3  NaN  3.0 NaN  4.0

Replace all NaN elements with 0s.

>>> df.fillna(0)
     A    B    C    D
0  0.0  2.0  0.0  0.0
1  3.0  4.0  0.0  1.0
2  0.0  0.0  0.0  0.0
3  0.0  3.0  0.0  4.0

Replace all NaN elements in column 'A', 'B', 'C', and 'D', with 0, 1,
2, and 3 respectively.

>>> values = {"A": 0, "B": 1, "C": 2, "D": 3}
>>> df.fillna(value=values)
     A    B    C    D
0  0.0  2.0  2.0  0.0
1  3.0  4.0  2.0  1.0
2  0.0  1.0  2.0  3.0
3  0.0  3.0  2.0  4.0

Only replace the first NaN element.

>>> df.fillna(value=values, limit=1)
     A    B    C    D
0  0.0  2.0  2.0  0.0
1  3.0  4.0  NaN  1.0
2  NaN  1.0  NaN  3.0
3  NaN  3.0  NaN  4.0

When filling using a DataFrame, replacement happens along
the same column names and same indices

>>> df2 = pd.DataFrame(np.zeros((4, 4)), columns=list("ABCE"))
>>> df.fillna(df2)
     A    B    C    D
0  0.0  2.0  0.0  0.0
1  3.0  4.0  0.0  1.0
2  0.0  0.0  0.0  NaN
3  0.0  3.0  0.0  4.0

Note that column D is not affected since it is not present in df2.
        """
        pass
    def replace(
        self,
        to_replace=...,
        value=...,
        *,
        inplace: _bool = ...,
        limit=...,
        regex: _bool = ...,
        method: ReplaceMethod = ...,
    ):
        """
Replace values given in `to_replace` with `value`.

Values of the Series/DataFrame are replaced with other values dynamically.
This differs from updating with ``.loc`` or ``.iloc``, which require
you to specify a location to update with some value.

Parameters
----------
to_replace : str, regex, list, dict, Series, int, float, or None
    How to find the values that will be replaced.

    * numeric, str or regex:

        - numeric: numeric values equal to `to_replace` will be
          replaced with `value`
        - str: string exactly matching `to_replace` will be replaced
          with `value`
        - regex: regexs matching `to_replace` will be replaced with
          `value`

    * list of str, regex, or numeric:

        - First, if `to_replace` and `value` are both lists, they
          **must** be the same length.
        - Second, if ``regex=True`` then all of the strings in **both**
          lists will be interpreted as regexs otherwise they will match
          directly. This doesn't matter much for `value` since there
          are only a few possible substitution regexes you can use.
        - str, regex and numeric rules apply as above.

    * dict:

        - Dicts can be used to specify different replacement values
          for different existing values. For example,
          ``{'a': 'b', 'y': 'z'}`` replaces the value 'a' with 'b' and
          'y' with 'z'. To use a dict in this way, the optional `value`
          parameter should not be given.
        - For a DataFrame a dict can specify that different values
          should be replaced in different columns. For example,
          ``{'a': 1, 'b': 'z'}`` looks for the value 1 in column 'a'
          and the value 'z' in column 'b' and replaces these values
          with whatever is specified in `value`. The `value` parameter
          should not be ``None`` in this case. You can treat this as a
          special case of passing two lists except that you are
          specifying the column to search in.
        - For a DataFrame nested dictionaries, e.g.,
          ``{'a': {'b': np.nan}}``, are read as follows: look in column
          'a' for the value 'b' and replace it with NaN. The optional `value`
          parameter should not be specified to use a nested dict in this
          way. You can nest regular expressions as well. Note that
          column names (the top-level dictionary keys in a nested
          dictionary) **cannot** be regular expressions.

    * None:

        - This means that the `regex` argument must be a string,
          compiled regular expression, or list, dict, ndarray or
          Series of such elements. If `value` is also ``None`` then
          this **must** be a nested dictionary or Series.

    See the examples section for examples of each of these.
value : scalar, dict, list, str, regex, default None
    Value to replace any values matching `to_replace` with.
    For a DataFrame a dict of values can be used to specify which
    value to use for each column (columns not in the dict will not be
    filled). Regular expressions, strings and lists or dicts of such
    objects are also allowed.

inplace : bool, default False
    If True, performs operation inplace and returns None.
limit : int, default None
    Maximum size gap to forward or backward fill.

    .. deprecated:: 2.1.0
regex : bool or same types as `to_replace`, default False
    Whether to interpret `to_replace` and/or `value` as regular
    expressions. Alternatively, this could be a regular expression or a
    list, dict, or array of regular expressions in which case
    `to_replace` must be ``None``.
method : {'pad', 'ffill', 'bfill'}
    The method to use when for replacement, when `to_replace` is a
    scalar, list or tuple and `value` is ``None``.

    .. deprecated:: 2.1.0

Returns
-------
Series/DataFrame
    Object after replacement.

Raises
------
AssertionError
    * If `regex` is not a ``bool`` and `to_replace` is not
      ``None``.

TypeError
    * If `to_replace` is not a scalar, array-like, ``dict``, or ``None``
    * If `to_replace` is a ``dict`` and `value` is not a ``list``,
      ``dict``, ``ndarray``, or ``Series``
    * If `to_replace` is ``None`` and `regex` is not compilable
      into a regular expression or is a list, dict, ndarray, or
      Series.
    * When replacing multiple ``bool`` or ``datetime64`` objects and
      the arguments to `to_replace` does not match the type of the
      value being replaced

ValueError
    * If a ``list`` or an ``ndarray`` is passed to `to_replace` and
      `value` but they are not the same length.

See Also
--------
Series.fillna : Fill NA values.
DataFrame.fillna : Fill NA values.
Series.where : Replace values based on boolean condition.
DataFrame.where : Replace values based on boolean condition.
DataFrame.map: Apply a function to a Dataframe elementwise.
Series.map: Map values of Series according to an input mapping or function.
Series.str.replace : Simple string replacement.

Notes
-----
* Regex substitution is performed under the hood with ``re.sub``. The
  rules for substitution for ``re.sub`` are the same.
* Regular expressions will only substitute on strings, meaning you
  cannot provide, for example, a regular expression matching floating
  point numbers and expect the columns in your frame that have a
  numeric dtype to be matched. However, if those floating point
  numbers *are* strings, then you can do this.
* This method has *a lot* of options. You are encouraged to experiment
  and play with this method to gain intuition about how it works.
* When dict is used as the `to_replace` value, it is like
  key(s) in the dict are the to_replace part and
  value(s) in the dict are the value parameter.

Examples
--------

**Scalar `to_replace` and `value`**

>>> s = pd.Series([1, 2, 3, 4, 5])
>>> s.replace(1, 5)
0    5
1    2
2    3
3    4
4    5
dtype: int64

>>> df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
...                    'B': [5, 6, 7, 8, 9],
...                    'C': ['a', 'b', 'c', 'd', 'e']})
>>> df.replace(0, 5)
    A  B  C
0  5  5  a
1  1  6  b
2  2  7  c
3  3  8  d
4  4  9  e

**List-like `to_replace`**

>>> df.replace([0, 1, 2, 3], 4)
    A  B  C
0  4  5  a
1  4  6  b
2  4  7  c
3  4  8  d
4  4  9  e

>>> df.replace([0, 1, 2, 3], [4, 3, 2, 1])
    A  B  C
0  4  5  a
1  3  6  b
2  2  7  c
3  1  8  d
4  4  9  e

>>> s.replace([1, 2], method='bfill')
0    3
1    3
2    3
3    4
4    5
dtype: int64

**dict-like `to_replace`**

>>> df.replace({0: 10, 1: 100})
        A  B  C
0   10  5  a
1  100  6  b
2    2  7  c
3    3  8  d
4    4  9  e

>>> df.replace({'A': 0, 'B': 5}, 100)
        A    B  C
0  100  100  a
1    1    6  b
2    2    7  c
3    3    8  d
4    4    9  e

>>> df.replace({'A': {0: 100, 4: 400}})
        A  B  C
0  100  5  a
1    1  6  b
2    2  7  c
3    3  8  d
4  400  9  e

**Regular expression `to_replace`**

>>> df = pd.DataFrame({'A': ['bat', 'foo', 'bait'],
...                    'B': ['abc', 'bar', 'xyz']})
>>> df.replace(to_replace=r'^ba.$', value='new', regex=True)
        A    B
0   new  abc
1   foo  new
2  bait  xyz

>>> df.replace({'A': r'^ba.$'}, {'A': 'new'}, regex=True)
        A    B
0   new  abc
1   foo  bar
2  bait  xyz

>>> df.replace(regex=r'^ba.$', value='new')
        A    B
0   new  abc
1   foo  new
2  bait  xyz

>>> df.replace(regex={r'^ba.$': 'new', 'foo': 'xyz'})
        A    B
0   new  abc
1   xyz  new
2  bait  xyz

>>> df.replace(regex=[r'^ba.$', 'foo'], value='new')
        A    B
0   new  abc
1   new  new
2  bait  xyz

Compare the behavior of ``s.replace({'a': None})`` and
``s.replace('a', None)`` to understand the peculiarities
of the `to_replace` parameter:

>>> s = pd.Series([10, 'a', 'a', 'b', 'a'])

When one uses a dict as the `to_replace` value, it is like the
value(s) in the dict are equal to the `value` parameter.
``s.replace({'a': None})`` is equivalent to
``s.replace(to_replace={'a': None}, value=None, method=None)``:

>>> s.replace({'a': None})
0      10
1    None
2    None
3       b
4    None
dtype: object

When ``value`` is not explicitly passed and `to_replace` is a scalar, list
or tuple, `replace` uses the method parameter (default 'pad') to do the
replacement. So this is why the 'a' values are being replaced by 10
in rows 1 and 2 and 'b' in row 4 in this case.

>>> s.replace('a')
0    10
1    10
2    10
3     b
4     b
dtype: object

    .. deprecated:: 2.1.0
        The 'method' parameter and padding behavior are deprecated.

On the other hand, if ``None`` is explicitly passed for ``value``, it will
be respected:

>>> s.replace('a', None)
0      10
1    None
2    None
3       b
4    None
dtype: object

    .. versionchanged:: 1.4.0
        Previously the explicit ``None`` was silently ignored.

When ``regex=True``, ``value`` is not ``None`` and `to_replace` is a string,
the replacement will be applied in all columns of the DataFrame.

>>> df = pd.DataFrame({'A': [0, 1, 2, 3, 4],
...                    'B': ['a', 'b', 'c', 'd', 'e'],
...                    'C': ['f', 'g', 'h', 'i', 'j']})

>>> df.replace(to_replace='^[a-g]', value='e', regex=True)
    A  B  C
0  0  e  e
1  1  e  e
2  2  e  h
3  3  e  i
4  4  e  j

If ``value`` is not ``None`` and `to_replace` is a dictionary, the dictionary
keys will be the DataFrame columns that the replacement will be applied.

>>> df.replace(to_replace={'B': '^[a-c]', 'C': '^[h-j]'}, value='e', regex=True)
    A  B  C
0  0  e  f
1  1  e  g
2  2  e  e
3  3  d  e
4  4  e  e
        """
        pass
    def asof(self, where, subset=...): ...
    def isna(self) -> NDFrame:
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
Series/DataFrame
    Mask of bool values for each element in Series/DataFrame that
    indicates whether an element is an NA value.

See Also
--------
Series/DataFrame.isnull : Alias of isna.
Series/DataFrame.notna : Boolean inverse of isna.
Series/DataFrame.dropna : Omit axes labels with missing values.
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
    def isnull(self) -> NDFrame:
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
Series/DataFrame
    Mask of bool values for each element in Series/DataFrame that
    indicates whether an element is an NA value.

See Also
--------
Series/DataFrame.isnull : Alias of isna.
Series/DataFrame.notna : Boolean inverse of isna.
Series/DataFrame.dropna : Omit axes labels with missing values.
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
    def notna(self) -> NDFrame:
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
Series/DataFrame
    Mask of bool values for each element in Series/DataFrame that
    indicates whether an element is not an NA value.

See Also
--------
Series/DataFrame.notnull : Alias of notna.
Series/DataFrame.isna : Boolean inverse of notna.
Series/DataFrame.dropna : Omit axes labels with missing values.
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
    def notnull(self) -> NDFrame:
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
Series/DataFrame
    Mask of bool values for each element in Series/DataFrame that
    indicates whether an element is not an NA value.

See Also
--------
Series/DataFrame.notnull : Alias of notna.
Series/DataFrame.isna : Boolean inverse of notna.
Series/DataFrame.dropna : Omit axes labels with missing values.
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
    def clip(
        self, lower=..., upper=..., *, axis=..., inplace: _bool = ..., **kwargs
    ) -> Self: ...
    def asfreq(
        self,
        freq,
        method: FillnaOptions | None = ...,
        how: Literal["start", "end"] | None = ...,
        normalize: _bool = ...,
        fill_value=...,
    ) -> Self:
        """
Convert time series to specified frequency.

Returns the original data conformed to a new index with the specified
frequency.

If the index of this Series/DataFrame is a :class:`~pandas.PeriodIndex`, the new index
is the result of transforming the original index with
:meth:`PeriodIndex.asfreq <pandas.PeriodIndex.asfreq>` (so the original index
will map one-to-one to the new index).

Otherwise, the new index will be equivalent to ``pd.date_range(start, end,
freq=freq)`` where ``start`` and ``end`` are, respectively, the first and
last entries in the original index (see :func:`pandas.date_range`). The
values corresponding to any timesteps in the new index which were not present
in the original index will be null (``NaN``), unless a method for filling
such unknowns is provided (see the ``method`` parameter below).

The :meth:`resample` method is more appropriate if an operation on each group of
timesteps (such as an aggregate) is necessary to represent the data at the new
frequency.

Parameters
----------
freq : DateOffset or str
    Frequency DateOffset or string.
method : {'backfill'/'bfill', 'pad'/'ffill'}, default None
    Method to use for filling holes in reindexed Series (note this
    does not fill NaNs that already were present):

    * 'pad' / 'ffill': propagate last valid observation forward to next
      valid
    * 'backfill' / 'bfill': use NEXT valid observation to fill.
how : {'start', 'end'}, default end
    For PeriodIndex only (see PeriodIndex.asfreq).
normalize : bool, default False
    Whether to reset output index to midnight.
fill_value : scalar, optional
    Value to use for missing values, applied during upsampling (note
    this does not fill NaNs that already were present).

Returns
-------
Series/DataFrame
    Series/DataFrame object reindexed to the specified frequency.

See Also
--------
reindex : Conform DataFrame to new index with optional filling logic.

Notes
-----
To learn more about the frequency strings, please see `this link
<https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`__.

Examples
--------
Start by creating a series with 4 one minute timestamps.

>>> index = pd.date_range('1/1/2000', periods=4, freq='min')
>>> series = pd.Series([0.0, None, 2.0, 3.0], index=index)
>>> df = pd.DataFrame({'s': series})
>>> df
                       s
2000-01-01 00:00:00    0.0
2000-01-01 00:01:00    NaN
2000-01-01 00:02:00    2.0
2000-01-01 00:03:00    3.0

Upsample the series into 30 second bins.

>>> df.asfreq(freq='30s')
                       s
2000-01-01 00:00:00    0.0
2000-01-01 00:00:30    NaN
2000-01-01 00:01:00    NaN
2000-01-01 00:01:30    NaN
2000-01-01 00:02:00    2.0
2000-01-01 00:02:30    NaN
2000-01-01 00:03:00    3.0

Upsample again, providing a ``fill value``.

>>> df.asfreq(freq='30s', fill_value=9.0)
                       s
2000-01-01 00:00:00    0.0
2000-01-01 00:00:30    9.0
2000-01-01 00:01:00    NaN
2000-01-01 00:01:30    9.0
2000-01-01 00:02:00    2.0
2000-01-01 00:02:30    9.0
2000-01-01 00:03:00    3.0

Upsample again, providing a ``method``.

>>> df.asfreq(freq='30s', method='bfill')
                       s
2000-01-01 00:00:00    0.0
2000-01-01 00:00:30    NaN
2000-01-01 00:01:00    NaN
2000-01-01 00:01:30    2.0
2000-01-01 00:02:00    2.0
2000-01-01 00:02:30    3.0
2000-01-01 00:03:00    3.0
        """
        pass
    def at_time(self, time, asof: _bool = ..., axis=...) -> Self: ...
    def between_time(
        self,
        start_time,
        end_time,
        axis=...,
    ) -> Self: ...
    @final
    def resample(
        self,
        rule: Frequency | dt.timedelta,
        axis: Axis | NoDefault = ...,
        closed: Literal["right", "left"] | None = ...,
        label: Literal["right", "left"] | None = ...,
        convention: TimestampConvention = ...,
        kind: Literal["period", "timestamp"] | None = ...,
        on: Level | None = ...,
        level: Level | None = ...,
        origin: TimeGrouperOrigin | TimestampConvertibleTypes = ...,
        offset: TimedeltaConvertibleTypes | None = ...,
        group_keys: _bool = ...,
    ) -> DatetimeIndexResampler[Self]:
        """
Resample time-series data.

Convenience method for frequency conversion and resampling of time series.
The object must have a datetime-like index (`DatetimeIndex`, `PeriodIndex`,
or `TimedeltaIndex`), or the caller must pass the label of a datetime-like
series/index to the ``on``/``level`` keyword parameter.

Parameters
----------
rule : DateOffset, Timedelta or str
    The offset string or object representing target conversion.
axis : {0 or 'index', 1 or 'columns'}, default 0
    Which axis to use for up- or down-sampling. For `Series` this parameter
    is unused and defaults to 0. Must be
    `DatetimeIndex`, `TimedeltaIndex` or `PeriodIndex`.

    .. deprecated:: 2.0.0
        Use frame.T.resample(...) instead.
closed : {'right', 'left'}, default None
    Which side of bin interval is closed. The default is 'left'
    for all frequency offsets except for 'ME', 'YE', 'QE', 'BME',
    'BA', 'BQE', and 'W' which all have a default of 'right'.
label : {'right', 'left'}, default None
    Which bin edge label to label bucket with. The default is 'left'
    for all frequency offsets except for 'ME', 'YE', 'QE', 'BME',
    'BA', 'BQE', and 'W' which all have a default of 'right'.
convention : {'start', 'end', 's', 'e'}, default 'start'
    For `PeriodIndex` only, controls whether to use the start or
    end of `rule`.

    .. deprecated:: 2.2.0
        Convert PeriodIndex to DatetimeIndex before resampling instead.
kind : {'timestamp', 'period'}, optional, default None
    Pass 'timestamp' to convert the resulting index to a
    `DateTimeIndex` or 'period' to convert it to a `PeriodIndex`.
    By default the input representation is retained.

    .. deprecated:: 2.2.0
        Convert index to desired type explicitly instead.

on : str, optional
    For a DataFrame, column to use instead of index for resampling.
    Column must be datetime-like.
level : str or int, optional
    For a MultiIndex, level (name or number) to use for
    resampling. `level` must be datetime-like.
origin : Timestamp or str, default 'start_day'
    The timestamp on which to adjust the grouping. The timezone of origin
    must match the timezone of the index.
    If string, must be one of the following:

    - 'epoch': `origin` is 1970-01-01
    - 'start': `origin` is the first value of the timeseries
    - 'start_day': `origin` is the first day at midnight of the timeseries

    - 'end': `origin` is the last value of the timeseries
    - 'end_day': `origin` is the ceiling midnight of the last day

    .. versionadded:: 1.3.0

    .. note::

        Only takes effect for Tick-frequencies (i.e. fixed frequencies like
        days, hours, and minutes, rather than months or quarters).
offset : Timedelta or str, default is None
    An offset timedelta added to the origin.

group_keys : bool, default False
    Whether to include the group keys in the result index when using
    ``.apply()`` on the resampled object.

    .. versionadded:: 1.5.0

        Not specifying ``group_keys`` will retain values-dependent behavior
        from pandas 1.4 and earlier (see :ref:`pandas 1.5.0 Release notes
        <whatsnew_150.enhancements.resample_group_keys>` for examples).

    .. versionchanged:: 2.0.0

        ``group_keys`` now defaults to ``False``.

Returns
-------
pandas.api.typing.Resampler
    :class:`~pandas.core.Resampler` object.

See Also
--------
Series.resample : Resample a Series.
DataFrame.resample : Resample a DataFrame.
groupby : Group Series/DataFrame by mapping, function, label, or list of labels.
asfreq : Reindex a Series/DataFrame with the given frequency without grouping.

Notes
-----
See the `user guide
<https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#resampling>`__
for more.

To learn more about the offset strings, please see `this link
<https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects>`__.

Examples
--------
Start by creating a series with 9 one minute timestamps.

>>> index = pd.date_range('1/1/2000', periods=9, freq='min')
>>> series = pd.Series(range(9), index=index)
>>> series
2000-01-01 00:00:00    0
2000-01-01 00:01:00    1
2000-01-01 00:02:00    2
2000-01-01 00:03:00    3
2000-01-01 00:04:00    4
2000-01-01 00:05:00    5
2000-01-01 00:06:00    6
2000-01-01 00:07:00    7
2000-01-01 00:08:00    8
Freq: min, dtype: int64

Downsample the series into 3 minute bins and sum the values
of the timestamps falling into a bin.

>>> series.resample('3min').sum()
2000-01-01 00:00:00     3
2000-01-01 00:03:00    12
2000-01-01 00:06:00    21
Freq: 3min, dtype: int64

Downsample the series into 3 minute bins as above, but label each
bin using the right edge instead of the left. Please note that the
value in the bucket used as the label is not included in the bucket,
which it labels. For example, in the original series the
bucket ``2000-01-01 00:03:00`` contains the value 3, but the summed
value in the resampled bucket with the label ``2000-01-01 00:03:00``
does not include 3 (if it did, the summed value would be 6, not 3).

>>> series.resample('3min', label='right').sum()
2000-01-01 00:03:00     3
2000-01-01 00:06:00    12
2000-01-01 00:09:00    21
Freq: 3min, dtype: int64

To include this value close the right side of the bin interval,
as shown below.

>>> series.resample('3min', label='right', closed='right').sum()
2000-01-01 00:00:00     0
2000-01-01 00:03:00     6
2000-01-01 00:06:00    15
2000-01-01 00:09:00    15
Freq: 3min, dtype: int64

Upsample the series into 30 second bins.

>>> series.resample('30s').asfreq()[0:5]   # Select first 5 rows
2000-01-01 00:00:00   0.0
2000-01-01 00:00:30   NaN
2000-01-01 00:01:00   1.0
2000-01-01 00:01:30   NaN
2000-01-01 00:02:00   2.0
Freq: 30s, dtype: float64

Upsample the series into 30 second bins and fill the ``NaN``
values using the ``ffill`` method.

>>> series.resample('30s').ffill()[0:5]
2000-01-01 00:00:00    0
2000-01-01 00:00:30    0
2000-01-01 00:01:00    1
2000-01-01 00:01:30    1
2000-01-01 00:02:00    2
Freq: 30s, dtype: int64

Upsample the series into 30 second bins and fill the
``NaN`` values using the ``bfill`` method.

>>> series.resample('30s').bfill()[0:5]
2000-01-01 00:00:00    0
2000-01-01 00:00:30    1
2000-01-01 00:01:00    1
2000-01-01 00:01:30    2
2000-01-01 00:02:00    2
Freq: 30s, dtype: int64

Pass a custom function via ``apply``

>>> def custom_resampler(arraylike):
...     return np.sum(arraylike) + 5
...
>>> series.resample('3min').apply(custom_resampler)
2000-01-01 00:00:00     8
2000-01-01 00:03:00    17
2000-01-01 00:06:00    26
Freq: 3min, dtype: int64

For DataFrame objects, the keyword `on` can be used to specify the
column instead of the index for resampling.

>>> d = {'price': [10, 11, 9, 13, 14, 18, 17, 19],
...      'volume': [50, 60, 40, 100, 50, 100, 40, 50]}
>>> df = pd.DataFrame(d)
>>> df['week_starting'] = pd.date_range('01/01/2018',
...                                     periods=8,
...                                     freq='W')
>>> df
   price  volume week_starting
0     10      50    2018-01-07
1     11      60    2018-01-14
2      9      40    2018-01-21
3     13     100    2018-01-28
4     14      50    2018-02-04
5     18     100    2018-02-11
6     17      40    2018-02-18
7     19      50    2018-02-25
>>> df.resample('ME', on='week_starting').mean()
               price  volume
week_starting
2018-01-31     10.75    62.5
2018-02-28     17.00    60.0

For a DataFrame with MultiIndex, the keyword `level` can be used to
specify on which level the resampling needs to take place.

>>> days = pd.date_range('1/1/2000', periods=4, freq='D')
>>> d2 = {'price': [10, 11, 9, 13, 14, 18, 17, 19],
...       'volume': [50, 60, 40, 100, 50, 100, 40, 50]}
>>> df2 = pd.DataFrame(
...     d2,
...     index=pd.MultiIndex.from_product(
...         [days, ['morning', 'afternoon']]
...     )
... )
>>> df2
                      price  volume
2000-01-01 morning       10      50
           afternoon     11      60
2000-01-02 morning        9      40
           afternoon     13     100
2000-01-03 morning       14      50
           afternoon     18     100
2000-01-04 morning       17      40
           afternoon     19      50
>>> df2.resample('D', level=0).sum()
            price  volume
2000-01-01     21     110
2000-01-02     22     140
2000-01-03     32     150
2000-01-04     36      90

If you want to adjust the start of the bins based on a fixed timestamp:

>>> start, end = '2000-10-01 23:30:00', '2000-10-02 00:30:00'
>>> rng = pd.date_range(start, end, freq='7min')
>>> ts = pd.Series(np.arange(len(rng)) * 3, index=rng)
>>> ts
2000-10-01 23:30:00     0
2000-10-01 23:37:00     3
2000-10-01 23:44:00     6
2000-10-01 23:51:00     9
2000-10-01 23:58:00    12
2000-10-02 00:05:00    15
2000-10-02 00:12:00    18
2000-10-02 00:19:00    21
2000-10-02 00:26:00    24
Freq: 7min, dtype: int64

>>> ts.resample('17min').sum()
2000-10-01 23:14:00     0
2000-10-01 23:31:00     9
2000-10-01 23:48:00    21
2000-10-02 00:05:00    54
2000-10-02 00:22:00    24
Freq: 17min, dtype: int64

>>> ts.resample('17min', origin='epoch').sum()
2000-10-01 23:18:00     0
2000-10-01 23:35:00    18
2000-10-01 23:52:00    27
2000-10-02 00:09:00    39
2000-10-02 00:26:00    24
Freq: 17min, dtype: int64

>>> ts.resample('17min', origin='2000-01-01').sum()
2000-10-01 23:24:00     3
2000-10-01 23:41:00    15
2000-10-01 23:58:00    45
2000-10-02 00:15:00    45
Freq: 17min, dtype: int64

If you want to adjust the start of the bins with an `offset` Timedelta, the two
following lines are equivalent:

>>> ts.resample('17min', origin='start').sum()
2000-10-01 23:30:00     9
2000-10-01 23:47:00    21
2000-10-02 00:04:00    54
2000-10-02 00:21:00    24
Freq: 17min, dtype: int64

>>> ts.resample('17min', offset='23h30min').sum()
2000-10-01 23:30:00     9
2000-10-01 23:47:00    21
2000-10-02 00:04:00    54
2000-10-02 00:21:00    24
Freq: 17min, dtype: int64

If you want to take the largest Timestamp as the end of the bins:

>>> ts.resample('17min', origin='end').sum()
2000-10-01 23:35:00     0
2000-10-01 23:52:00    18
2000-10-02 00:09:00    27
2000-10-02 00:26:00    63
Freq: 17min, dtype: int64

In contrast with the `start_day`, you can use `end_day` to take the ceiling
midnight of the largest Timestamp as the end of the bins and drop the bins
not containing data:

>>> ts.resample('17min', origin='end_day').sum()
2000-10-01 23:38:00     3
2000-10-01 23:55:00    15
2000-10-02 00:12:00    45
2000-10-02 00:29:00    45
Freq: 17min, dtype: int64
        """
        pass
    def first(self, offset) -> Self: ...
    def last(self, offset) -> Self: ...
    def rank(
        self,
        axis=...,
        method: Literal["average", "min", "max", "first", "dense"] = ...,
        numeric_only: _bool = ...,
        na_option: Literal["keep", "top", "bottom"] = ...,
        ascending: _bool = ...,
        pct: _bool = ...,
    ) -> NDFrame: ...
    def where(
        self,
        cond,
        other=...,
        *,
        inplace: _bool = ...,
        axis=...,
        level=...,
    ):
        """
Replace values where the condition is False.

Parameters
----------
cond : bool Series/DataFrame, array-like, or callable
    Where `cond` is True, keep the original value. Where
    False, replace with corresponding value from `other`.
    If `cond` is callable, it is computed on the Series/DataFrame and
    should return boolean Series/DataFrame or array. The callable must
    not change input Series/DataFrame (though pandas doesn't check it).
other : scalar, Series/DataFrame, or callable
    Entries where `cond` is False are replaced with
    corresponding value from `other`.
    If other is callable, it is computed on the Series/DataFrame and
    should return scalar or Series/DataFrame. The callable must not
    change input Series/DataFrame (though pandas doesn't check it).
    If not specified, entries will be filled with the corresponding
    NULL value (``np.nan`` for numpy dtypes, ``pd.NA`` for extension
    dtypes).
inplace : bool, default False
    Whether to perform the operation in place on the data.
axis : int, default None
    Alignment axis if needed. For `Series` this parameter is
    unused and defaults to 0.
level : int, default None
    Alignment level if needed.

Returns
-------
Same type as caller or None if ``inplace=True``.

See Also
--------
:func:`DataFrame.mask` : Return an object of same shape as
    self.

Notes
-----
The where method is an application of the if-then idiom. For each
element in the calling DataFrame, if ``cond`` is ``True`` the
element is used; otherwise the corresponding element from the DataFrame
``other`` is used. If the axis of ``other`` does not align with axis of
``cond`` Series/DataFrame, the misaligned index positions will be filled with
False.

The signature for :func:`DataFrame.where` differs from
:func:`numpy.where`. Roughly ``df1.where(m, df2)`` is equivalent to
``np.where(m, df1, df2)``.

For further details and examples see the ``where`` documentation in
:ref:`indexing <indexing.where_mask>`.

The dtype of the object takes precedence. The fill value is casted to
the object's dtype, if this can be done losslessly.

Examples
--------
>>> s = pd.Series(range(5))
>>> s.where(s > 0)
0    NaN
1    1.0
2    2.0
3    3.0
4    4.0
dtype: float64
>>> s.mask(s > 0)
0    0.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

>>> s = pd.Series(range(5))
>>> t = pd.Series([True, False])
>>> s.where(t, 99)
0     0
1    99
2    99
3    99
4    99
dtype: int64
>>> s.mask(t, 99)
0    99
1     1
2    99
3    99
4    99
dtype: int64

>>> s.where(s > 1, 10)
0    10
1    10
2    2
3    3
4    4
dtype: int64
>>> s.mask(s > 1, 10)
0     0
1     1
2    10
3    10
4    10
dtype: int64

>>> df = pd.DataFrame(np.arange(10).reshape(-1, 2), columns=['A', 'B'])
>>> df
   A  B
0  0  1
1  2  3
2  4  5
3  6  7
4  8  9
>>> m = df % 3 == 0
>>> df.where(m, -df)
   A  B
0  0 -1
1 -2  3
2 -4 -5
3  6 -7
4 -8  9
>>> df.where(m, -df) == np.where(m, df, -df)
      A     B
0  True  True
1  True  True
2  True  True
3  True  True
4  True  True
>>> df.where(m, -df) == df.mask(~m, -df)
      A     B
0  True  True
1  True  True
2  True  True
3  True  True
4  True  True
        """
        pass
    def mask(
        self,
        cond,
        other=...,
        *,
        inplace: _bool = ...,
        axis=...,
        level=...,
    ):
        """
Replace values where the condition is True.

Parameters
----------
cond : bool Series/DataFrame, array-like, or callable
    Where `cond` is False, keep the original value. Where
    True, replace with corresponding value from `other`.
    If `cond` is callable, it is computed on the Series/DataFrame and
    should return boolean Series/DataFrame or array. The callable must
    not change input Series/DataFrame (though pandas doesn't check it).
other : scalar, Series/DataFrame, or callable
    Entries where `cond` is True are replaced with
    corresponding value from `other`.
    If other is callable, it is computed on the Series/DataFrame and
    should return scalar or Series/DataFrame. The callable must not
    change input Series/DataFrame (though pandas doesn't check it).
    If not specified, entries will be filled with the corresponding
    NULL value (``np.nan`` for numpy dtypes, ``pd.NA`` for extension
    dtypes).
inplace : bool, default False
    Whether to perform the operation in place on the data.
axis : int, default None
    Alignment axis if needed. For `Series` this parameter is
    unused and defaults to 0.
level : int, default None
    Alignment level if needed.

Returns
-------
Same type as caller or None if ``inplace=True``.

See Also
--------
:func:`DataFrame.where` : Return an object of same shape as
    self.

Notes
-----
The mask method is an application of the if-then idiom. For each
element in the calling DataFrame, if ``cond`` is ``False`` the
element is used; otherwise the corresponding element from the DataFrame
``other`` is used. If the axis of ``other`` does not align with axis of
``cond`` Series/DataFrame, the misaligned index positions will be filled with
True.

The signature for :func:`DataFrame.where` differs from
:func:`numpy.where`. Roughly ``df1.where(m, df2)`` is equivalent to
``np.where(m, df1, df2)``.

For further details and examples see the ``mask`` documentation in
:ref:`indexing <indexing.where_mask>`.

The dtype of the object takes precedence. The fill value is casted to
the object's dtype, if this can be done losslessly.

Examples
--------
>>> s = pd.Series(range(5))
>>> s.where(s > 0)
0    NaN
1    1.0
2    2.0
3    3.0
4    4.0
dtype: float64
>>> s.mask(s > 0)
0    0.0
1    NaN
2    NaN
3    NaN
4    NaN
dtype: float64

>>> s = pd.Series(range(5))
>>> t = pd.Series([True, False])
>>> s.where(t, 99)
0     0
1    99
2    99
3    99
4    99
dtype: int64
>>> s.mask(t, 99)
0    99
1     1
2    99
3    99
4    99
dtype: int64

>>> s.where(s > 1, 10)
0    10
1    10
2    2
3    3
4    4
dtype: int64
>>> s.mask(s > 1, 10)
0     0
1     1
2    10
3    10
4    10
dtype: int64

>>> df = pd.DataFrame(np.arange(10).reshape(-1, 2), columns=['A', 'B'])
>>> df
   A  B
0  0  1
1  2  3
2  4  5
3  6  7
4  8  9
>>> m = df % 3 == 0
>>> df.where(m, -df)
   A  B
0  0 -1
1 -2  3
2 -4 -5
3  6 -7
4 -8  9
>>> df.where(m, -df) == np.where(m, df, -df)
      A     B
0  True  True
1  True  True
2  True  True
3  True  True
4  True  True
>>> df.where(m, -df) == df.mask(~m, -df)
      A     B
0  True  True
1  True  True
2  True  True
3  True  True
4  True  True
        """
        pass
    def shift(self, periods=..., freq=..., axis=..., fill_value=...) -> Self:
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
Series/DataFrame
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
    def truncate(self, before=..., after=..., axis=..., copy: _bool = ...) -> Self: ...
    def tz_convert(self, tz, axis=..., level=..., copy: _bool = ...) -> Self:
        """
Convert tz-aware axis to target time zone.

Parameters
----------
tz : str or tzinfo object or None
    Target time zone. Passing ``None`` will convert to
    UTC and remove the timezone information.
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to convert
level : int, str, default None
    If axis is a MultiIndex, convert a specific level. Otherwise
    must be None.
copy : bool, default True
    Also make a copy of the underlying data.

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
Series/DataFrame
    Object with time zone converted axis.

Raises
------
TypeError
    If the axis is tz-naive.

Examples
--------
Change to another time zone:

>>> s = pd.Series(
...     [1],
...     index=pd.DatetimeIndex(['2018-09-15 01:30:00+02:00']),
... )
>>> s.tz_convert('Asia/Shanghai')
2018-09-15 07:30:00+08:00    1
dtype: int64

Pass None to convert to UTC and get a tz-naive index:

>>> s = pd.Series([1],
...               index=pd.DatetimeIndex(['2018-09-15 01:30:00+02:00']))
>>> s.tz_convert(None)
2018-09-14 23:30:00    1
dtype: int64
        """
        pass
    def tz_localize(
        self,
        tz,
        axis=...,
        level=...,
        copy: _bool = ...,
        ambiguous=...,
        nonexistent: str = ...,
    ) -> Self:
        """
Localize tz-naive index of a Series or DataFrame to target time zone.

This operation localizes the Index. To localize the values in a
timezone-naive Series, use :meth:`Series.dt.tz_localize`.

Parameters
----------
tz : str or tzinfo or None
    Time zone to localize. Passing ``None`` will remove the
    time zone information and preserve local time.
axis : {0 or 'index', 1 or 'columns'}, default 0
    The axis to localize
level : int, str, default None
    If axis ia a MultiIndex, localize a specific level. Otherwise
    must be None.
copy : bool, default True
    Also make a copy of the underlying data.

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
ambiguous : 'infer', bool-ndarray, 'NaT', default 'raise'
    When clocks moved backward due to DST, ambiguous times may arise.
    For example in Central European Time (UTC+01), when going from
    03:00 DST to 02:00 non-DST, 02:30:00 local time occurs both at
    00:30:00 UTC and at 01:30:00 UTC. In such a situation, the
    `ambiguous` parameter dictates how ambiguous times should be
    handled.

    - 'infer' will attempt to infer fall dst-transition hours based on
      order
    - bool-ndarray where True signifies a DST time, False designates
      a non-DST time (note that this flag is only applicable for
      ambiguous times)
    - 'NaT' will return NaT where there are ambiguous times
    - 'raise' will raise an AmbiguousTimeError if there are ambiguous
      times.
nonexistent : str, default 'raise'
    A nonexistent time does not exist in a particular timezone
    where clocks moved forward due to DST. Valid values are:

    - 'shift_forward' will shift the nonexistent time forward to the
      closest existing time
    - 'shift_backward' will shift the nonexistent time backward to the
      closest existing time
    - 'NaT' will return NaT where there are nonexistent times
    - timedelta objects will shift nonexistent times by the timedelta
    - 'raise' will raise an NonExistentTimeError if there are
      nonexistent times.

Returns
-------
Series/DataFrame
    Same type as the input.

Raises
------
TypeError
    If the TimeSeries is tz-aware and tz is not None.

Examples
--------
Localize local times:

>>> s = pd.Series(
...     [1],
...     index=pd.DatetimeIndex(['2018-09-15 01:30:00']),
... )
>>> s.tz_localize('CET')
2018-09-15 01:30:00+02:00    1
dtype: int64

Pass None to convert to tz-naive index and preserve local time:

>>> s = pd.Series([1],
...               index=pd.DatetimeIndex(['2018-09-15 01:30:00+02:00']))
>>> s.tz_localize(None)
2018-09-15 01:30:00    1
dtype: int64

Be careful with DST changes. When there is sequential data, pandas
can infer the DST time:

>>> s = pd.Series(range(7),
...               index=pd.DatetimeIndex(['2018-10-28 01:30:00',
...                                       '2018-10-28 02:00:00',
...                                       '2018-10-28 02:30:00',
...                                       '2018-10-28 02:00:00',
...                                       '2018-10-28 02:30:00',
...                                       '2018-10-28 03:00:00',
...                                       '2018-10-28 03:30:00']))
>>> s.tz_localize('CET', ambiguous='infer')
2018-10-28 01:30:00+02:00    0
2018-10-28 02:00:00+02:00    1
2018-10-28 02:30:00+02:00    2
2018-10-28 02:00:00+01:00    3
2018-10-28 02:30:00+01:00    4
2018-10-28 03:00:00+01:00    5
2018-10-28 03:30:00+01:00    6
dtype: int64

In some cases, inferring the DST is impossible. In such cases, you can
pass an ndarray to the ambiguous parameter to set the DST explicitly

>>> s = pd.Series(range(3),
...               index=pd.DatetimeIndex(['2018-10-28 01:20:00',
...                                       '2018-10-28 02:36:00',
...                                       '2018-10-28 03:46:00']))
>>> s.tz_localize('CET', ambiguous=np.array([True, True, False]))
2018-10-28 01:20:00+02:00    0
2018-10-28 02:36:00+02:00    1
2018-10-28 03:46:00+01:00    2
dtype: int64

If the DST transition causes nonexistent times, you can shift these
dates forward or backward with a timedelta object or `'shift_forward'`
or `'shift_backward'`.

>>> s = pd.Series(range(2),
...               index=pd.DatetimeIndex(['2015-03-29 02:30:00',
...                                       '2015-03-29 03:30:00']))
>>> s.tz_localize('Europe/Warsaw', nonexistent='shift_forward')
2015-03-29 03:00:00+02:00    0
2015-03-29 03:30:00+02:00    1
dtype: int64
>>> s.tz_localize('Europe/Warsaw', nonexistent='shift_backward')
2015-03-29 01:59:59.999999999+01:00    0
2015-03-29 03:30:00+02:00              1
dtype: int64
>>> s.tz_localize('Europe/Warsaw', nonexistent=pd.Timedelta('1h'))
2015-03-29 03:30:00+02:00    0
2015-03-29 03:30:00+02:00    1
dtype: int64
        """
        pass
    def abs(self) -> Self: ...
    def describe(self, percentiles=..., include=..., exclude=...) -> NDFrame: ...
    def pct_change(
        self, periods=..., fill_method=..., limit=..., freq=..., **kwargs
    ) -> Self: ...
    def first_valid_index(self):
        """
Return index for first non-NA value or None, if no non-NA value is found.

Returns
-------
type of index

Examples
--------
For Series:

>>> s = pd.Series([None, 3, 4])
>>> s.first_valid_index()
1
>>> s.last_valid_index()
2

>>> s = pd.Series([None, None])
>>> print(s.first_valid_index())
None
>>> print(s.last_valid_index())
None

If all elements in Series are NA/null, returns None.

>>> s = pd.Series()
>>> print(s.first_valid_index())
None
>>> print(s.last_valid_index())
None

If Series is empty, returns None.

For DataFrame:

>>> df = pd.DataFrame({'A': [None, None, 2], 'B': [None, 3, 4]})
>>> df
     A      B
0  NaN    NaN
1  NaN    3.0
2  2.0    4.0
>>> df.first_valid_index()
1
>>> df.last_valid_index()
2

>>> df = pd.DataFrame({'A': [None, None, None], 'B': [None, None, None]})
>>> df
     A      B
0  None   None
1  None   None
2  None   None
>>> print(df.first_valid_index())
None
>>> print(df.last_valid_index())
None

If all elements in DataFrame are NA/null, returns None.

>>> df = pd.DataFrame()
>>> df
Empty DataFrame
Columns: []
Index: []
>>> print(df.first_valid_index())
None
>>> print(df.last_valid_index())
None

If DataFrame is empty, returns None.
        """
        pass
    def last_valid_index(self):
        """
Return index for last non-NA value or None, if no non-NA value is found.

Returns
-------
type of index

Examples
--------
For Series:

>>> s = pd.Series([None, 3, 4])
>>> s.first_valid_index()
1
>>> s.last_valid_index()
2

>>> s = pd.Series([None, None])
>>> print(s.first_valid_index())
None
>>> print(s.last_valid_index())
None

If all elements in Series are NA/null, returns None.

>>> s = pd.Series()
>>> print(s.first_valid_index())
None
>>> print(s.last_valid_index())
None

If Series is empty, returns None.

For DataFrame:

>>> df = pd.DataFrame({'A': [None, None, 2], 'B': [None, 3, 4]})
>>> df
     A      B
0  NaN    NaN
1  NaN    3.0
2  2.0    4.0
>>> df.first_valid_index()
1
>>> df.last_valid_index()
2

>>> df = pd.DataFrame({'A': [None, None, None], 'B': [None, None, None]})
>>> df
     A      B
0  None   None
1  None   None
2  None   None
>>> print(df.first_valid_index())
None
>>> print(df.last_valid_index())
None

If all elements in DataFrame are NA/null, returns None.

>>> df = pd.DataFrame()
>>> df
Empty DataFrame
Columns: []
Index: []
>>> print(df.first_valid_index())
None
>>> print(df.last_valid_index())
None

If DataFrame is empty, returns None.
        """
        pass
