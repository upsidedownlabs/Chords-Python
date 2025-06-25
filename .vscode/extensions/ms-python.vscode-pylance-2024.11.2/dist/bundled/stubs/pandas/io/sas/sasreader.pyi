from abc import (
    ABCMeta,
    abstractmethod,
)
from collections.abc import Hashable
from typing import (
    Literal,
    overload,
)

from pandas import DataFrame
from typing_extensions import Self

from pandas._typing import (
    CompressionOptions as CompressionOptions,
    FilePath as FilePath,
    ReadBuffer,
)

from pandas.io.sas.sas7bdat import SAS7BDATReader
from pandas.io.sas.sas_xport import XportReader

class ReaderBase(metaclass=ABCMeta):
    @abstractmethod
    def read(self, nrows: int | None = ...) -> DataFrame: ...
    @abstractmethod
    def close(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...

@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: Literal["sas7bdat"],
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int,
    iterator: bool = ...,
    compression: CompressionOptions = ...,
) -> SAS7BDATReader:
    """
Read SAS files stored as either XPORT or SAS7BDAT format files.

Parameters
----------
filepath_or_buffer : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``read()`` function. The string could be a URL.
    Valid URL schemes include http, ftp, s3, and file. For file URLs, a host is
    expected. A local file could be:
    ``file://localhost/path/to/table.sas7bdat``.
format : str {'xport', 'sas7bdat'} or None
    If None, file format is inferred from file extension. If 'xport' or
    'sas7bdat', uses the corresponding format.
index : identifier of index column, defaults to None
    Identifier of column that should be used as index of the DataFrame.
encoding : str, default is None
    Encoding for text data.  If None, text data are stored as raw bytes.
chunksize : int
    Read file `chunksize` lines at a time, returns iterator.
iterator : bool, defaults to False
    If True, returns an iterator for reading the file incrementally.
compression : str or dict, default 'infer'
    For on-the-fly decompression of on-disk data. If 'infer' and 'filepath_or_buffer' is
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

Returns
-------
DataFrame if iterator=False and chunksize=None, else SAS7BDATReader
or XportReader

Examples
--------
>>> df = pd.read_sas("sas_data.sas7bdat")  # doctest: +SKIP
    """
    pass
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: Literal["xport"],
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int,
    iterator: bool = ...,
    compression: CompressionOptions = ...,
) -> XportReader: ...
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: None = ...,
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int,
    iterator: bool = ...,
    compression: CompressionOptions = ...,
) -> XportReader | SAS7BDATReader: ...
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: Literal["sas7bdat"],
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int | None = ...,
    iterator: Literal[True],
    compression: CompressionOptions = ...,
) -> SAS7BDATReader: ...
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: Literal["xport"],
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int | None = ...,
    iterator: Literal[True],
    compression: CompressionOptions = ...,
) -> XportReader: ...
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: None = ...,
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: int | None = ...,
    iterator: Literal[True],
    compression: CompressionOptions = ...,
) -> XportReader | SAS7BDATReader: ...
@overload
def read_sas(
    filepath_or_buffer: FilePath | ReadBuffer[bytes],
    *,
    format: Literal["xport", "sas7bdat"] | None = ...,
    index: Hashable | None = ...,
    encoding: str | None = ...,
    chunksize: None = ...,
    iterator: Literal[False] = ...,
    compression: CompressionOptions = ...,
) -> DataFrame: ...
