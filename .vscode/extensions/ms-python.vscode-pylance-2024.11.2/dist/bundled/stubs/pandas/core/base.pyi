from collections.abc import (
    Hashable,
    Iterator,
)
from typing import (
    Any,
    Generic,
    Literal,
    final,
    overload,
)

import numpy as np
from pandas import (
    Index,
    Series,
)
from pandas.core.arraylike import OpsMixin
from pandas.core.arrays import ExtensionArray
from pandas.core.arrays.categorical import Categorical
from typing_extensions import Self

from pandas._typing import (
    S1,
    AxisIndex,
    NaPosition,
    NDFrameT,
    Scalar,
    npt,
)
from pandas.util._decorators import cache_readonly

class NoNewAttributesMixin:
    def __setattr__(self, key: str, value: Any) -> None: ...

class SelectionMixin(Generic[NDFrameT]):
    obj: NDFrameT
    exclusions: frozenset[Hashable]
    @final
    @cache_readonly
    def ndim(self) -> int: ...
    def __getitem__(self, key): ...
    def aggregate(self, func, *args, **kwargs): ...

class IndexOpsMixin(OpsMixin, Generic[S1]):
    __array_priority__: int = ...
    def transpose(self, *args, **kwargs) -> Self: ...
    @property
    def T(self) -> Self: ...
    @property
    def shape(self) -> tuple: ...
    @property
    def ndim(self) -> int: ...
    def item(self) -> S1: ...
    @property
    def nbytes(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def array(self) -> ExtensionArray: ...
    def to_numpy(
        self,
        dtype: npt.DTypeLike | None = ...,
        copy: bool = ...,
        na_value: Scalar = ...,
        **kwargs,
    ) -> np.ndarray: ...
    @property
    def empty(self) -> bool: ...
    def max(self, axis=..., skipna: bool = ..., **kwargs): ...
    def min(self, axis=..., skipna: bool = ..., **kwargs): ...
    def argmax(
        self, axis: AxisIndex | None = ..., skipna: bool = ..., *args, **kwargs
    ) -> np.int64:
        """
Return int position of the largest value in the Series.

If the maximum is achieved in multiple locations,
the first row position is returned.

Parameters
----------
axis : {None}
    Unused. Parameter needed for compatibility with DataFrame.
skipna : bool, default True
    Exclude NA/null values when showing the result.
*args, **kwargs
    Additional arguments and keywords for compatibility with NumPy.

Returns
-------
int
    Row position of the maximum value.

See Also
--------
Series.argmax : Return position of the maximum value.
Series.argmin : Return position of the minimum value.
numpy.ndarray.argmax : Equivalent method for numpy arrays.
Series.idxmax : Return index label of the maximum values.
Series.idxmin : Return index label of the minimum values.

Examples
--------
Consider dataset containing cereal calories

>>> s = pd.Series({'Corn Flakes': 100.0, 'Almond Delight': 110.0,
...                'Cinnamon Toast Crunch': 120.0, 'Cocoa Puff': 110.0})
>>> s
Corn Flakes              100.0
Almond Delight           110.0
Cinnamon Toast Crunch    120.0
Cocoa Puff               110.0
dtype: float64

>>> s.argmax()
2
>>> s.argmin()
0

The maximum cereal calories is the third element and
the minimum cereal calories is the first element,
since series is zero-indexed.
        """
        pass
    def argmin(
        self, axis: AxisIndex | None = ..., skipna: bool = ..., *args, **kwargs
    ) -> np.int64:
        """
Return int position of the smallest value in the Series.

If the minimum is achieved in multiple locations,
the first row position is returned.

Parameters
----------
axis : {None}
    Unused. Parameter needed for compatibility with DataFrame.
skipna : bool, default True
    Exclude NA/null values when showing the result.
*args, **kwargs
    Additional arguments and keywords for compatibility with NumPy.

Returns
-------
int
    Row position of the minimum value.

See Also
--------
Series.argmin : Return position of the minimum value.
Series.argmax : Return position of the maximum value.
numpy.ndarray.argmin : Equivalent method for numpy arrays.
Series.idxmax : Return index label of the maximum values.
Series.idxmin : Return index label of the minimum values.

Examples
--------
Consider dataset containing cereal calories

>>> s = pd.Series({'Corn Flakes': 100.0, 'Almond Delight': 110.0,
...                'Cinnamon Toast Crunch': 120.0, 'Cocoa Puff': 110.0})
>>> s
Corn Flakes              100.0
Almond Delight           110.0
Cinnamon Toast Crunch    120.0
Cocoa Puff               110.0
dtype: float64

>>> s.argmax()
2
>>> s.argmin()
0

The maximum cereal calories is the third element and
the minimum cereal calories is the first element,
since series is zero-indexed.
        """
        pass
    def tolist(self) -> list[S1]: ...
    def to_list(self) -> list[S1]: ...
    def __iter__(self) -> Iterator[S1]: ...
    @property
    def hasnans(self) -> bool: ...
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
    def nunique(self, dropna: bool = ...) -> int: ...
    @property
    def is_unique(self) -> bool: ...
    @property
    def is_monotonic_decreasing(self) -> bool: ...
    @property
    def is_monotonic_increasing(self) -> bool: ...
    def factorize(
        self, sort: bool = ...
    ) -> tuple[np.ndarray, np.ndarray | Index | Categorical]:
        """
Encode the object as an enumerated type or categorical variable.

This method is useful for obtaining a numeric representation of an
array when all that matters is identifying distinct values. `factorize`
is available as both a top-level function :func:`pandas.factorize`,
and as a method :meth:`Series.factorize` and :meth:`Index.factorize`.

Parameters
----------
sort : bool, default False
    Sort `uniques` and shuffle `codes` to maintain the
    relationship.

use_na_sentinel : bool, default True
    If True, the sentinel -1 will be used for NaN values. If False,
    NaN values will be encoded as non-negative integers and will not drop the
    NaN from the uniques of the values.

    .. versionadded:: 1.5.0

Returns
-------
codes : ndarray
    An integer ndarray that's an indexer into `uniques`.
    ``uniques.take(codes)`` will have the same values as `values`.
uniques : ndarray, Index, or Categorical
    The unique valid values. When `values` is Categorical, `uniques`
    is a Categorical. When `values` is some other pandas object, an
    `Index` is returned. Otherwise, a 1-D ndarray is returned.

    .. note::

       Even if there's a missing value in `values`, `uniques` will
       *not* contain an entry for it.

See Also
--------
cut : Discretize continuous-valued array.
unique : Find the unique value in an array.

Notes
-----
Reference :ref:`the user guide <reshaping.factorize>` for more examples.

Examples
--------
These examples all show factorize as a top-level method like
``pd.factorize(values)``. The results are identical for methods like
:meth:`Series.factorize`.

>>> codes, uniques = pd.factorize(np.array(['b', 'b', 'a', 'c', 'b'], dtype="O"))
>>> codes
array([0, 0, 1, 2, 0])
>>> uniques
array(['b', 'a', 'c'], dtype=object)

With ``sort=True``, the `uniques` will be sorted, and `codes` will be
shuffled so that the relationship is the maintained.

>>> codes, uniques = pd.factorize(np.array(['b', 'b', 'a', 'c', 'b'], dtype="O"),
...                               sort=True)
>>> codes
array([1, 1, 0, 2, 1])
>>> uniques
array(['a', 'b', 'c'], dtype=object)

When ``use_na_sentinel=True`` (the default), missing values are indicated in
the `codes` with the sentinel value ``-1`` and missing values are not
included in `uniques`.

>>> codes, uniques = pd.factorize(np.array(['b', None, 'a', 'c', 'b'], dtype="O"))
>>> codes
array([ 0, -1,  1,  2,  0])
>>> uniques
array(['b', 'a', 'c'], dtype=object)

Thus far, we've only factorized lists (which are internally coerced to
NumPy arrays). When factorizing pandas objects, the type of `uniques`
will differ. For Categoricals, a `Categorical` is returned.

>>> cat = pd.Categorical(['a', 'a', 'c'], categories=['a', 'b', 'c'])
>>> codes, uniques = pd.factorize(cat)
>>> codes
array([0, 0, 1])
>>> uniques
['a', 'c']
Categories (3, object): ['a', 'b', 'c']

Notice that ``'b'`` is in ``uniques.categories``, despite not being
present in ``cat.values``.

For all other pandas objects, an Index of the appropriate type is
returned.

>>> cat = pd.Series(['a', 'a', 'c'])
>>> codes, uniques = pd.factorize(cat)
>>> codes
array([0, 0, 1])
>>> uniques
Index(['a', 'c'], dtype='object')

If NaN is in the values, and we want to include NaN in the uniques of the
values, it can be achieved by setting ``use_na_sentinel=False``.

>>> values = np.array([1, 2, 1, np.nan])
>>> codes, uniques = pd.factorize(values)  # default: use_na_sentinel=True
>>> codes
array([ 0,  1,  0, -1])
>>> uniques
array([1., 2.])

>>> codes, uniques = pd.factorize(values, use_na_sentinel=False)
>>> codes
array([0, 1, 0, 2])
>>> uniques
array([ 1.,  2., nan])
        """
        pass
    def searchsorted(
        self, value, side: Literal["left", "right"] = ..., sorter=...
    ) -> int | list[int]:
        """
Find indices where elements should be inserted to maintain order.

Find the indices into a sorted Index `self` such that, if the
corresponding elements in `value` were inserted before the indices,
the order of `self` would be preserved.

.. note::

    The Index *must* be monotonically sorted, otherwise
    wrong locations will likely be returned. Pandas does *not*
    check this for you.

Parameters
----------
value : array-like or scalar
    Values to insert into `self`.
side : {'left', 'right'}, optional
    If 'left', the index of the first suitable location found is given.
    If 'right', return the last such index.  If there is no suitable
    index, return either 0 or N (where N is the length of `self`).
sorter : 1-D array-like, optional
    Optional array of integer indices that sort `self` into ascending
    order. They are typically the result of ``np.argsort``.

Returns
-------
int or array of int
    A scalar or array of insertion points with the
    same shape as `value`.

See Also
--------
sort_values : Sort by the values along either axis.
numpy.searchsorted : Similar method from NumPy.

Notes
-----
Binary search is used to find the required insertion points.

Examples
--------
>>> ser = pd.Series([1, 2, 3])
>>> ser
0    1
1    2
2    3
dtype: int64

>>> ser.searchsorted(4)
3

>>> ser.searchsorted([0, 4])
array([0, 3])

>>> ser.searchsorted([1, 3], side='left')
array([0, 2])

>>> ser.searchsorted([1, 3], side='right')
array([1, 3])

>>> ser = pd.Series(pd.to_datetime(['3/11/2000', '3/12/2000', '3/13/2000']))
>>> ser
0   2000-03-11
1   2000-03-12
2   2000-03-13
dtype: datetime64[ns]

>>> ser.searchsorted('3/14/2000')
3

>>> ser = pd.Categorical(
...     ['apple', 'bread', 'bread', 'cheese', 'milk'], ordered=True
... )
>>> ser
['apple', 'bread', 'bread', 'cheese', 'milk']
Categories (4, object): ['apple' < 'bread' < 'cheese' < 'milk']

>>> ser.searchsorted('bread')
1

>>> ser.searchsorted(['bread'], side='right')
array([3])

If the values are not monotonically sorted, wrong locations
may be returned:

>>> ser = pd.Series([2, 1, 3])
>>> ser
0    2
1    1
2    3
dtype: int64

>>> ser.searchsorted(1)  # doctest: +SKIP
0  # wrong result, correct would be 1
        """
        pass
    def drop_duplicates(self, *, keep: NaPosition | Literal[False] = ...) -> Self: ...
