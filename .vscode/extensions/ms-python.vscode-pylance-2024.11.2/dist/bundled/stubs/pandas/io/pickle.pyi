from typing import Any

from pandas._typing import (
    CompressionOptions,
    FilePath,
    ReadPickleBuffer,
    StorageOptions,
    WriteBuffer,
)

def to_pickle(
    obj: object,
    filepath_or_buffer: FilePath | WriteBuffer[bytes],
    compression: CompressionOptions = ...,
    protocol: int = ...,
    storage_options: StorageOptions = ...,
) -> None:
    """
Pickle (serialize) object to file.

Parameters
----------
obj : any object
    Any python object.
filepath_or_buffer : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``write()`` function.
    Also accepts URL. URL has to be of S3 or GCS.
compression : str or dict, default 'infer'
    For on-the-fly compression of the output data. If 'infer' and 'filepath_or_buffer' is
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

protocol : int
    Int which indicates which protocol should be used by the pickler,
    default HIGHEST_PROTOCOL (see [1], paragraph 12.1.2). The possible
    values for this parameter depend on the version of Python. For Python
    2.x, possible values are 0, 1, 2. For Python>=3.0, 3 is a valid value.
    For Python >= 3.4, 4 is a valid value. A negative value for the
    protocol parameter is equivalent to setting its value to
    HIGHEST_PROTOCOL.

storage_options : dict, optional
    Extra options that make sense for a particular storage connection, e.g.
    host, port, username, password, etc. For HTTP(S) URLs the key-value pairs
    are forwarded to ``urllib.request.Request`` as header options. For other
    URLs (e.g. starting with "s3://", and "gcs://") the key-value pairs are
    forwarded to ``fsspec.open``. Please see ``fsspec`` and ``urllib`` for more
    details, and for more examples on storage options refer `here
    <https://pandas.pydata.org/docs/user_guide/io.html?
    highlight=storage_options#reading-writing-remote-files>`_.

    .. [1] https://docs.python.org/3/library/pickle.html

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
>>> pd.to_pickle(original_df, "./dummy.pkl")  # doctest: +SKIP

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
def read_pickle(
    filepath_or_buffer: FilePath | ReadPickleBuffer,
    compression: CompressionOptions = ...,
    storage_options: StorageOptions = ...,
) -> Any:
    """
Load pickled pandas object (or any object) from file.

.. warning::

   Loading pickled data received from untrusted sources can be
   unsafe. See `here <https://docs.python.org/3/library/pickle.html>`__.

Parameters
----------
filepath_or_buffer : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a binary ``readlines()`` function.
    Also accepts URL. URL is not limited to S3 and GCS.

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
same type as object stored in file

See Also
--------
DataFrame.to_pickle : Pickle (serialize) DataFrame object to file.
Series.to_pickle : Pickle (serialize) Series object to file.
read_hdf : Read HDF5 file into a DataFrame.
read_sql : Read SQL query or database table into a DataFrame.
read_parquet : Load a parquet object, returning a DataFrame.

Notes
-----
read_pickle is only guaranteed to be backwards compatible to pandas 0.20.3
provided the object was serialized with to_pickle.

Examples
--------
>>> original_df = pd.DataFrame(
...     {"foo": range(5), "bar": range(5, 10)}
...    )  # doctest: +SKIP
>>> original_df  # doctest: +SKIP
   foo  bar
0    0    5
1    1    6
2    2    7
3    3    8
4    4    9
>>> pd.to_pickle(original_df, "./dummy.pkl")  # doctest: +SKIP

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
