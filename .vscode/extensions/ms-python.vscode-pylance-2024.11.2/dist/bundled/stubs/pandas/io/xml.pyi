from collections.abc import Sequence

from pandas.core.frame import DataFrame

from pandas._libs.lib import NoDefault
from pandas._typing import (
    CompressionOptions,
    ConvertersArg,
    DtypeArg,
    DtypeBackend,
    FilePath,
    ParseDatesArg,
    ReadBuffer,
    StorageOptions,
    XMLParsers,
)

def read_xml(
    path_or_buffer: FilePath | ReadBuffer[bytes] | ReadBuffer[str],
    *,
    xpath: str = ...,
    namespaces: dict[str, str] | None = ...,
    elems_only: bool = ...,
    attrs_only: bool = ...,
    names: Sequence[str] | None = ...,
    dtype: DtypeArg | None = ...,
    converters: ConvertersArg | None = ...,
    parse_dates: ParseDatesArg | None = ...,
    # encoding can not be None for lxml and StringIO input
    encoding: str | None = ...,
    parser: XMLParsers = ...,
    stylesheet: FilePath | ReadBuffer[bytes] | ReadBuffer[str] | None = ...,
    iterparse: dict[str, list[str]] | None = ...,
    compression: CompressionOptions = ...,
    storage_options: StorageOptions = ...,
    dtype_backend: DtypeBackend | NoDefault = ...,
) -> DataFrame:
    """
Read XML document into a :class:`~pandas.DataFrame` object.

.. versionadded:: 1.3.0

Parameters
----------
path_or_buffer : str, path object, or file-like object
    String, path object (implementing ``os.PathLike[str]``), or file-like
    object implementing a ``read()`` function. The string can be any valid XML
    string or a path. The string can further be a URL. Valid URL schemes
    include http, ftp, s3, and file.

    .. deprecated:: 2.1.0
        Passing xml literal strings is deprecated.
        Wrap literal xml input in ``io.StringIO`` or ``io.BytesIO`` instead.

xpath : str, optional, default './\*'
    The ``XPath`` to parse required set of nodes for migration to
    :class:`~pandas.DataFrame`.``XPath`` should return a collection of elements
    and not a single element. Note: The ``etree`` parser supports limited ``XPath``
    expressions. For more complex ``XPath``, use ``lxml`` which requires
    installation.

namespaces : dict, optional
    The namespaces defined in XML document as dicts with key being
    namespace prefix and value the URI. There is no need to include all
    namespaces in XML, only the ones used in ``xpath`` expression.
    Note: if XML document uses default namespace denoted as
    `xmlns='<URI>'` without a prefix, you must assign any temporary
    namespace prefix such as 'doc' to the URI in order to parse
    underlying nodes and/or attributes. For example, ::

        namespaces = {"doc": "https://example.com"}

elems_only : bool, optional, default False
    Parse only the child elements at the specified ``xpath``. By default,
    all child elements and non-empty text nodes are returned.

attrs_only :  bool, optional, default False
    Parse only the attributes at the specified ``xpath``.
    By default, all attributes are returned.

names :  list-like, optional
    Column names for DataFrame of parsed XML data. Use this parameter to
    rename original element names and distinguish same named elements and
    attributes.

dtype : Type name or dict of column -> type, optional
    Data type for data or columns. E.g. {'a': np.float64, 'b': np.int32,
    'c': 'Int64'}
    Use `str` or `object` together with suitable `na_values` settings
    to preserve and not interpret dtype.
    If converters are specified, they will be applied INSTEAD
    of dtype conversion.

    .. versionadded:: 1.5.0

converters : dict, optional
    Dict of functions for converting values in certain columns. Keys can either
    be integers or column labels.

    .. versionadded:: 1.5.0

parse_dates : bool or list of int or names or list of lists or dict, default False
    Identifiers to parse index or columns to datetime. The behavior is as follows:

    * boolean. If True -> try parsing the index.
    * list of int or names. e.g. If [1, 2, 3] -> try parsing columns 1, 2, 3
      each as a separate date column.
    * list of lists. e.g.  If [[1, 3]] -> combine columns 1 and 3 and parse as
      a single date column.
    * dict, e.g. {'foo' : [1, 3]} -> parse columns 1, 3 as date and call
      result 'foo'

    .. versionadded:: 1.5.0

encoding : str, optional, default 'utf-8'
    Encoding of XML document.

parser : {'lxml','etree'}, default 'lxml'
    Parser module to use for retrieval of data. Only 'lxml' and
    'etree' are supported. With 'lxml' more complex ``XPath`` searches
    and ability to use XSLT stylesheet are supported.

stylesheet : str, path object or file-like object
    A URL, file-like object, or a raw string containing an XSLT script.
    This stylesheet should flatten complex, deeply nested XML documents
    for easier parsing. To use this feature you must have ``lxml`` module
    installed and specify 'lxml' as ``parser``. The ``xpath`` must
    reference nodes of transformed XML document generated after XSLT
    transformation and not the original XML document. Only XSLT 1.0
    scripts and not later versions is currently supported.

iterparse : dict, optional
    The nodes or attributes to retrieve in iterparsing of XML document
    as a dict with key being the name of repeating element and value being
    list of elements or attribute names that are descendants of the repeated
    element. Note: If this option is used, it will replace ``xpath`` parsing
    and unlike ``xpath``, descendants do not need to relate to each other but can
    exist any where in document under the repeating element. This memory-
    efficient method should be used for very large XML files (500MB, 1GB, or 5GB+).
    For example, ::

        iterparse = {"row_element": ["child_elem", "attr", "grandchild_elem"]}

    .. versionadded:: 1.5.0

compression : str or dict, default 'infer'
    For on-the-fly decompression of on-disk data. If 'infer' and 'path_or_buffer' is
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
df
    A DataFrame.

See Also
--------
read_json : Convert a JSON string to pandas object.
read_html : Read HTML tables into a list of DataFrame objects.

Notes
-----
This method is best designed to import shallow XML documents in
following format which is the ideal fit for the two-dimensions of a
``DataFrame`` (row by column). ::

        <root>
            <row>
              <column1>data</column1>
              <column2>data</column2>
              <column3>data</column3>
              ...
           </row>
           <row>
              ...
           </row>
           ...
        </root>

As a file format, XML documents can be designed any way including
layout of elements and attributes as long as it conforms to W3C
specifications. Therefore, this method is a convenience handler for
a specific flatter design and not all possible XML structures.

However, for more complex XML documents, ``stylesheet`` allows you to
temporarily redesign original document with XSLT (a special purpose
language) for a flatter version for migration to a DataFrame.

This function will *always* return a single :class:`DataFrame` or raise
exceptions due to issues with XML document, ``xpath``, or other
parameters.

See the :ref:`read_xml documentation in the IO section of the docs
<io.read_xml>` for more information in using this method to parse XML
files to DataFrames.

Examples
--------
>>> from io import StringIO
>>> xml = '''<?xml version='1.0' encoding='utf-8'?>
... <data xmlns="http://example.com">
...  <row>
...    <shape>square</shape>
...    <degrees>360</degrees>
...    <sides>4.0</sides>
...  </row>
...  <row>
...    <shape>circle</shape>
...    <degrees>360</degrees>
...    <sides/>
...  </row>
...  <row>
...    <shape>triangle</shape>
...    <degrees>180</degrees>
...    <sides>3.0</sides>
...  </row>
... </data>'''

>>> df = pd.read_xml(StringIO(xml))
>>> df
      shape  degrees  sides
0    square      360    4.0
1    circle      360    NaN
2  triangle      180    3.0

>>> xml = '''<?xml version='1.0' encoding='utf-8'?>
... <data>
...   <row shape="square" degrees="360" sides="4.0"/>
...   <row shape="circle" degrees="360"/>
...   <row shape="triangle" degrees="180" sides="3.0"/>
... </data>'''

>>> df = pd.read_xml(StringIO(xml), xpath=".//row")
>>> df
      shape  degrees  sides
0    square      360    4.0
1    circle      360    NaN
2  triangle      180    3.0

>>> xml = '''<?xml version='1.0' encoding='utf-8'?>
... <doc:data xmlns:doc="https://example.com">
...   <doc:row>
...     <doc:shape>square</doc:shape>
...     <doc:degrees>360</doc:degrees>
...     <doc:sides>4.0</doc:sides>
...   </doc:row>
...   <doc:row>
...     <doc:shape>circle</doc:shape>
...     <doc:degrees>360</doc:degrees>
...     <doc:sides/>
...   </doc:row>
...   <doc:row>
...     <doc:shape>triangle</doc:shape>
...     <doc:degrees>180</doc:degrees>
...     <doc:sides>3.0</doc:sides>
...   </doc:row>
... </doc:data>'''

>>> df = pd.read_xml(StringIO(xml),
...                  xpath="//doc:row",
...                  namespaces={"doc": "https://example.com"})
>>> df
      shape  degrees  sides
0    square      360    4.0
1    circle      360    NaN
2  triangle      180    3.0

>>> xml_data = '''
...         <data>
...            <row>
...               <index>0</index>
...               <a>1</a>
...               <b>2.5</b>
...               <c>True</c>
...               <d>a</d>
...               <e>2019-12-31 00:00:00</e>
...            </row>
...            <row>
...               <index>1</index>
...               <b>4.5</b>
...               <c>False</c>
...               <d>b</d>
...               <e>2019-12-31 00:00:00</e>
...            </row>
...         </data>
...         '''

>>> df = pd.read_xml(StringIO(xml_data),
...                  dtype_backend="numpy_nullable",
...                  parse_dates=["e"])
>>> df
   index     a    b      c  d          e
0      0     1  2.5   True  a 2019-12-31
1      1  <NA>  4.5  False  b 2019-12-31
    """
    pass
