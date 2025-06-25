from pandas import DataFrame

from pandas._libs.lib import NoDefault
from pandas._typing import (
    DtypeBackend,
    FilePath,
    HashableT,
    ReadBuffer,
    StorageOptions,
)

def read_feather(
    path: FilePath | ReadBuffer[bytes],
    columns: list[HashableT] | None = ...,
    use_threads: bool = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> DataFrame:
    """
Load a feather-format object from the file path.

Parameters
----------
path : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``read()`` function. The string could be a URL.
    Valid URL schemes include http, ftp, s3, and file. For file URLs, a host is
    expected. A local file could be: ``file://localhost/path/to/table.feather``.
columns : sequence, default None
    If not provided, all columns are read.
use_threads : bool, default True
    Whether to parallelize reading using multiple threads.
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

Returns
-------
type of object stored in file

Examples
--------
>>> df = pd.read_feather("path/to/file.feather")  # doctest: +SKIP
    """
    pass
