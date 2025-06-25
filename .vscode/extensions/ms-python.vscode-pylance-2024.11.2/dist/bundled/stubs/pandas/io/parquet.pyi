from typing import Any

from pandas import DataFrame

from pandas._typing import (
    FilePath,
    ParquetEngine,
    ReadBuffer,
    StorageOptions,
)

def read_parquet(
    path: FilePath | ReadBuffer[bytes],
    engine: ParquetEngine = ...,
    columns: list[str] | None = ...,
    storage_options: StorageOptions = ...,
    use_nullable_dtypes: bool = ...,
    **kwargs: Any,
) -> DataFrame:
    """
Load a parquet object from the file path, returning a DataFrame.

Parameters
----------
path : str, path object or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``read()`` function.
    The string could be a URL. Valid URL schemes include http, ftp, s3,
    gs, and file. For file URLs, a host is expected. A local file could be:
    ``file://localhost/path/to/table.parquet``.
    A file URL can also be a path to a directory that contains multiple
    partitioned parquet files. Both pyarrow and fastparquet support
    paths to directories as well as file URLs. A directory path could be:
    ``file://localhost/path/to/tables`` or ``s3://bucket/partition_dir``.
engine : {'auto', 'pyarrow', 'fastparquet'}, default 'auto'
    Parquet library to use. If 'auto', then the option
    ``io.parquet.engine`` is used. The default ``io.parquet.engine``
    behavior is to try 'pyarrow', falling back to 'fastparquet' if
    'pyarrow' is unavailable.

    When using the ``'pyarrow'`` engine and no storage options are provided
    and a filesystem is implemented by both ``pyarrow.fs`` and ``fsspec``
    (e.g. "s3://"), then the ``pyarrow.fs`` filesystem is attempted first.
    Use the filesystem keyword with an instantiated fsspec filesystem
    if you wish to use its implementation.
columns : list, default=None
    If not None, only these columns will be read from the file.
storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

    .. versionadded:: 1.3.0

use_nullable_dtypes : bool, default False
    If True, use dtypes that use ``pd.NA`` as missing value indicator
    for the resulting DataFrame. (only applicable for the ``pyarrow``
    engine)
    As new dtypes are added that support ``pd.NA`` in the future, the
    output with this option will change to use those dtypes.
    Note: this is an experimental option, and behaviour (e.g. additional
    support dtypes) may change without notice.

    .. deprecated:: 2.0

dtype_backend : {'numpy_nullable', 'pyarrow'}, default 'numpy_nullable'
    Back-end data type applied to the resultant :class:`DataFrame`
    (still experimental). Behaviour is as follows:

    * ``"numpy_nullable"``: returns nullable-dtype-backed :class:`DataFrame`
      (default).
    * ``"pyarrow"``: returns pyarrow-backed nullable :class:`ArrowDtype`
      DataFrame.

    .. versionadded:: 2.0

filesystem : fsspec or pyarrow filesystem, default None
    Filesystem object to use when reading the parquet file. Only implemented
    for ``engine="pyarrow"``.

    .. versionadded:: 2.1.0

filters : List[Tuple] or List[List[Tuple]], default None
    To filter out data.
    Filter syntax: [[(column, op, val), ...],...]
    where op is [==, =, >, >=, <, <=, !=, in, not in]
    The innermost tuples are transposed into a set of filters applied
    through an `AND` operation.
    The outer list combines these sets of filters through an `OR`
    operation.
    A single list of tuples can also be used, meaning that no `OR`
    operation between set of filters is to be conducted.

    Using this argument will NOT result in row-wise filtering of the final
    partitions unless ``engine="pyarrow"`` is also specified.  For
    other engines, filtering is only performed at the partition level, that is,
    to prevent the loading of some row-groups and/or files.

    .. versionadded:: 2.1.0

**kwargs
    Any additional kwargs are passed to the engine.

Returns
-------
DataFrame

See Also
--------
DataFrame.to_parquet : Create a parquet object that serializes a DataFrame.

Examples
--------
>>> original_df = pd.DataFrame(
...     {"foo": range(5), "bar": range(5, 10)}
...    )
>>> original_df
   foo  bar
0    0    5
1    1    6
2    2    7
3    3    8
4    4    9
>>> df_parquet_bytes = original_df.to_parquet()
>>> from io import BytesIO
>>> restored_df = pd.read_parquet(BytesIO(df_parquet_bytes))
>>> restored_df
   foo  bar
0    0    5
1    1    6
2    2    7
3    3    8
4    4    9
>>> restored_df.equals(original_df)
True
>>> restored_bar = pd.read_parquet(BytesIO(df_parquet_bytes), columns=["bar"])
>>> restored_bar
    bar
0    5
1    6
2    7
3    8
4    9
>>> restored_bar.equals(original_df[['bar']])
True

The function uses `kwargs` that are passed directly to the engine.
In the following example, we use the `filters` argument of the pyarrow
engine to filter the rows of the DataFrame.

Since `pyarrow` is the default engine, we can omit the `engine` argument.
Note that the `filters` argument is implemented by the `pyarrow` engine,
which can benefit from multithreading and also potentially be more
economical in terms of memory.

>>> sel = [("foo", ">", 2)]
>>> restored_part = pd.read_parquet(BytesIO(df_parquet_bytes), filters=sel)
>>> restored_part
    foo  bar
0    3    8
1    4    9
    """
    pass
