from collections import abc
from collections.abc import Mapping
from types import TracebackType
from typing import (
    Generic,
    Literal,
    overload,
)

from pandas.core.frame import DataFrame
from pandas.core.series import Series

from pandas._libs.lib import NoDefault
from pandas._typing import (
    CompressionOptions,
    DtypeArg,
    DtypeBackend,
    FilePath,
    HashableT,
    JsonFrameOrient,
    JsonSeriesOrient,
    NDFrameT,
    ReadBuffer,
    StorageOptions,
    TimeUnit,
)

@overload
def read_json(
    path_or_buf: FilePath | ReadBuffer[str] | ReadBuffer[bytes],
    *,
    orient: JsonSeriesOrient | None = ...,
    typ: Literal["series"],
    dtype: bool | Mapping[HashableT, DtypeArg] | None = ...,
    convert_axes: bool | None = ...,
    convert_dates: bool | list[str] = ...,
    keep_default_dates: bool = ...,
    precise_float: bool = ...,
    date_unit: TimeUnit | None = ...,
    encoding: str | None = ...,
    encoding_errors: (
        Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape"]
        | None
    ) = ...,
    lines: Literal[True],
    chunksize: int,
    compression: CompressionOptions = ...,
    nrows: int | None = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> JsonReader[Series]:
    """
Convert a JSON string to pandas object.

Parameters
----------
path_or_buf : a valid JSON str, path object or file-like object
    Any valid string path is acceptable. The string could be a URL. Valid
    URL schemes include http, ftp, s3, and file. For file URLs, a host is
    expected. A local file could be:
    ``file://localhost/path/to/table.json``.

    If you want to pass in a path object, pandas accepts any
    ``os.PathLike``.

    By file-like object, we refer to objects with a ``read()`` method,
    such as a file handle (e.g. via builtin ``open`` function)
    or ``StringIO``.

    .. deprecated:: 2.1.0
        Passing json literal strings is deprecated.

orient : str, optional
    Indication of expected JSON string format.
    Compatible JSON strings can be produced by ``to_json()`` with a
    corresponding orient value.
    The set of possible orients is:

    - ``'split'`` : dict like
      ``{index -> [index], columns -> [columns], data -> [values]}``
    - ``'records'`` : list like
      ``[{column -> value}, ... , {column -> value}]``
    - ``'index'`` : dict like ``{index -> {column -> value}}``
    - ``'columns'`` : dict like ``{column -> {index -> value}}``
    - ``'values'`` : just the values array
    - ``'table'`` : dict like ``{'schema': {schema}, 'data': {data}}``

    The allowed and default values depend on the value
    of the `typ` parameter.

    * when ``typ == 'series'``,

      - allowed orients are ``{'split','records','index'}``
      - default is ``'index'``
      - The Series index must be unique for orient ``'index'``.

    * when ``typ == 'frame'``,

      - allowed orients are ``{'split','records','index',
        'columns','values', 'table'}``
      - default is ``'columns'``
      - The DataFrame index must be unique for orients ``'index'`` and
        ``'columns'``.
      - The DataFrame columns must be unique for orients ``'index'``,
        ``'columns'``, and ``'records'``.

typ : {'frame', 'series'}, default 'frame'
    The type of object to recover.

dtype : bool or dict, default None
    If True, infer dtypes; if a dict of column to dtype, then use those;
    if False, then don't infer dtypes at all, applies only to the data.

    For all ``orient`` values except ``'table'``, default is True.

convert_axes : bool, default None
    Try to convert the axes to the proper dtypes.

    For all ``orient`` values except ``'table'``, default is True.

convert_dates : bool or list of str, default True
    If True then default datelike columns may be converted (depending on
    keep_default_dates).
    If False, no dates will be converted.
    If a list of column names, then those columns will be converted and
    default datelike columns may also be converted (depending on
    keep_default_dates).

keep_default_dates : bool, default True
    If parsing dates (convert_dates is not False), then try to parse the
    default datelike columns.
    A column label is datelike if

    * it ends with ``'_at'``,

    * it ends with ``'_time'``,

    * it begins with ``'timestamp'``,

    * it is ``'modified'``, or

    * it is ``'date'``.

precise_float : bool, default False
    Set to enable usage of higher precision (strtod) function when
    decoding string to double values. Default (False) is to use fast but
    less precise builtin functionality.

date_unit : str, default None
    The timestamp unit to detect if converting dates. The default behaviour
    is to try and detect the correct precision, but if this is not desired
    then pass one of 's', 'ms', 'us' or 'ns' to force parsing only seconds,
    milliseconds, microseconds or nanoseconds respectively.

encoding : str, default is 'utf-8'
    The encoding to use to decode py3 bytes.

encoding_errors : str, optional, default "strict"
    How encoding errors are treated. `List of possible values
    <https://docs.python.org/3/library/codecs.html#error-handlers>`_ .

    .. versionadded:: 1.3.0

lines : bool, default False
    Read the file as a json object per line.

chunksize : int, optional
    Return JsonReader object for iteration.
    See the `line-delimited json docs
    <https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#line-delimited-json>`_
    for more information on ``chunksize``.
    This can only be passed if `lines=True`.
    If this is None, the file will be read into memory all at once.
compression : str or dict, default 'infer'
    For on-the-fly decompression of on-disk data. If 'infer' and 'path_or_buf' is
    path-like, then detect compression from the following extensions: '.gz',
    '.bz2', '.zip', '.xz', '.zst', '.tar', '.tar.gz', '.tar.xz' or '.tar.bz2'
    (otherwise no compression).
    If using 'zip' or 'tar', the ZIP file must contain only one data file to be read in.
    Set to ``None`` for no decompression.
    Can also be a dict with key ``'method'`` set
    to one of {``'zip'``, ``'gzip'``, ``'bz2'``, ``'zstd'``, ``'xz'``, ``'tar'``} and
    other key-value pairs are forwarded to
    ``zipfile.ZipFile``, ``gzip.GzipFile``,
    ``bz2.BZ2File``, ``zstandard.ZstdDecompressor``, ``lzma.LZMAFile`` or
    ``tarfile.TarFile``, respectively.
    As an example, the following could be passed for Zstandard decompression using a
    custom compression dictionary:
    ``compression={'method': 'zstd', 'dict_data': my_compression_dict}``.

    .. versionadded:: 1.5.0
        Added support for `.tar` files.

    .. versionchanged:: 1.4.0 Zstandard support.

nrows : int, optional
    The number of lines from the line-delimited jsonfile that has to be read.
    This can only be passed if `lines=True`.
    If this is None, all the rows will be returned.

storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

dtype_backend : {'numpy_nullable', 'pyarrow'}, default 'numpy_nullable'
    Back-end data type applied to the resultant :class:`DataFrame`
    (still experimental). Behaviour is as follows:

    * ``"numpy_nullable"``: returns nullable-dtype-backed :class:`DataFrame`
      (default).
    * ``"pyarrow"``: returns pyarrow-backed nullable :class:`ArrowDtype`
      DataFrame.

    .. versionadded:: 2.0

engine : {"ujson", "pyarrow"}, default "ujson"
    Parser engine to use. The ``"pyarrow"`` engine is only available when
    ``lines=True``.

    .. versionadded:: 2.0

Returns
-------
Series, DataFrame, or pandas.api.typing.JsonReader
    A JsonReader is returned when ``chunksize`` is not ``0`` or ``None``.
    Otherwise, the type returned depends on the value of ``typ``.

See Also
--------
DataFrame.to_json : Convert a DataFrame to a JSON string.
Series.to_json : Convert a Series to a JSON string.
json_normalize : Normalize semi-structured JSON data into a flat table.

Notes
-----
Specific to ``orient='table'``, if a :class:`DataFrame` with a literal
:class:`Index` name of `index` gets written with :func:`to_json`, the
subsequent read operation will incorrectly set the :class:`Index` name to
``None``. This is because `index` is also used by :func:`DataFrame.to_json`
to denote a missing :class:`Index` name, and the subsequent
:func:`read_json` operation cannot distinguish between the two. The same
limitation is encountered with a :class:`MultiIndex` and any names
beginning with ``'level_'``.

Examples
--------
>>> from io import StringIO
>>> df = pd.DataFrame([['a', 'b'], ['c', 'd']],
...                   index=['row 1', 'row 2'],
...                   columns=['col 1', 'col 2'])

Encoding/decoding a Dataframe using ``'split'`` formatted JSON:

>>> df.to_json(orient='split')
    '{"columns":["col 1","col 2"],"index":["row 1","row 2"],"data":[["a","b"],["c","d"]]}'
>>> pd.read_json(StringIO(_), orient='split')
      col 1 col 2
row 1     a     b
row 2     c     d

Encoding/decoding a Dataframe using ``'index'`` formatted JSON:

>>> df.to_json(orient='index')
'{"row 1":{"col 1":"a","col 2":"b"},"row 2":{"col 1":"c","col 2":"d"}}'

>>> pd.read_json(StringIO(_), orient='index')
      col 1 col 2
row 1     a     b
row 2     c     d

Encoding/decoding a Dataframe using ``'records'`` formatted JSON.
Note that index labels are not preserved with this encoding.

>>> df.to_json(orient='records')
'[{"col 1":"a","col 2":"b"},{"col 1":"c","col 2":"d"}]'
>>> pd.read_json(StringIO(_), orient='records')
  col 1 col 2
0     a     b
1     c     d

Encoding with Table Schema

>>> df.to_json(orient='table')
    '{"schema":{"fields":[{"name":"index","type":"string"},{"name":"col 1","type":"string"},{"name":"col 2","type":"string"}],"primaryKey":["index"],"pandas_version":"1.4.0"},"data":[{"index":"row 1","col 1":"a","col 2":"b"},{"index":"row 2","col 1":"c","col 2":"d"}]}'

The following example uses ``dtype_backend="numpy_nullable"``

>>> data = '''{"index": {"0": 0, "1": 1},
...        "a": {"0": 1, "1": null},
...        "b": {"0": 2.5, "1": 4.5},
...        "c": {"0": true, "1": false},
...        "d": {"0": "a", "1": "b"},
...        "e": {"0": 1577.2, "1": 1577.1}}'''
>>> pd.read_json(StringIO(data), dtype_backend="numpy_nullable")
   index     a    b      c  d       e
0      0     1  2.5   True  a  1577.2
1      1  <NA>  4.5  False  b  1577.1
    """
    pass
@overload
def read_json(
    path_or_buf: FilePath | ReadBuffer[str] | ReadBuffer[bytes],
    *,
    orient: JsonFrameOrient | None = ...,
    typ: Literal["frame"] = ...,
    dtype: bool | Mapping[HashableT, DtypeArg] | None = ...,
    convert_axes: bool | None = ...,
    convert_dates: bool | list[str] = ...,
    keep_default_dates: bool = ...,
    precise_float: bool = ...,
    date_unit: TimeUnit | None = ...,
    encoding: str | None = ...,
    encoding_errors: (
        Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape"]
        | None
    ) = ...,
    lines: Literal[True],
    chunksize: int,
    compression: CompressionOptions = ...,
    nrows: int | None = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> JsonReader[DataFrame]: ...
@overload
def read_json(
    path_or_buf: FilePath | ReadBuffer[str] | ReadBuffer[bytes],
    *,
    orient: JsonSeriesOrient | None = ...,
    typ: Literal["series"],
    dtype: bool | Mapping[HashableT, DtypeArg] | None = ...,
    convert_axes: bool | None = ...,
    convert_dates: bool | list[str] = ...,
    keep_default_dates: bool = ...,
    precise_float: bool = ...,
    date_unit: TimeUnit | None = ...,
    encoding: str | None = ...,
    encoding_errors: (
        Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape"]
        | None
    ) = ...,
    lines: bool = ...,
    chunksize: None = ...,
    compression: CompressionOptions = ...,
    nrows: int | None = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> Series: ...
@overload
def read_json(
    path_or_buf: FilePath | ReadBuffer[str] | ReadBuffer[bytes],
    *,
    orient: JsonFrameOrient | None = ...,
    typ: Literal["frame"] = ...,
    dtype: bool | Mapping[HashableT, DtypeArg] | None = ...,
    convert_axes: bool | None = ...,
    convert_dates: bool | list[str] = ...,
    keep_default_dates: bool = ...,
    precise_float: bool = ...,
    date_unit: TimeUnit | None = ...,
    encoding: str | None = ...,
    encoding_errors: (
        Literal["strict", "ignore", "replace", "backslashreplace", "surrogateescape"]
        | None
    ) = ...,
    lines: bool = ...,
    chunksize: None = ...,
    compression: CompressionOptions = ...,
    nrows: int | None = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> DataFrame: ...

class JsonReader(abc.Iterator, Generic[NDFrameT]):
    def read(self) -> NDFrameT: ...
    def close(self) -> None: ...
    def __iter__(self) -> JsonReader[NDFrameT]: ...
    def __next__(self) -> NDFrameT: ...
    def __enter__(self) -> JsonReader[NDFrameT]: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
