from typing import overload

import numpy as np
from pandas import (
    Index,
    Series,
)
from pandas.core.arrays.base import ExtensionArray as ExtensionArray
from typing_extensions import Self

from pandas._libs.interval import (
    Interval as Interval,
    IntervalMixin as IntervalMixin,
)
from pandas._typing import (
    Axis,
    Scalar,
    TakeIndexer,
    np_ndarray_bool,
)

class IntervalArray(IntervalMixin, ExtensionArray):
    can_hold_na: bool = ...
    def __new__(
        cls, data, closed=..., dtype=..., copy: bool = ..., verify_integrity: bool = ...
    ): ...
    @classmethod
    def from_breaks(cls, breaks, closed: str = ..., copy: bool = ..., dtype=...):
        """
classmethod(function) -> method

Convert a function to be a class method.

A class method receives the class as implicit first argument,
just like an instance method receives the instance.
To declare a class method, use this idiom:

  class C:
      @classmethod
      def f(cls, arg1, arg2, ...):
          ...

It can be called either on the class (e.g. C.f()) or on an instance
(e.g. C().f()).  The instance is ignored except for its class.
If a class method is called for a derived class, the derived class
object is passed as the implied first argument.

Class methods are different than C++ or Java static methods.
If you want those, see the staticmethod builtin.
        """
        pass
    @classmethod
    def from_arrays(
        cls, left, right, closed: str = ..., copy: bool = ..., dtype=...
    ):
        """
classmethod(function) -> method

Convert a function to be a class method.

A class method receives the class as implicit first argument,
just like an instance method receives the instance.
To declare a class method, use this idiom:

  class C:
      @classmethod
      def f(cls, arg1, arg2, ...):
          ...

It can be called either on the class (e.g. C.f()) or on an instance
(e.g. C().f()).  The instance is ignored except for its class.
If a class method is called for a derived class, the derived class
object is passed as the implied first argument.

Class methods are different than C++ or Java static methods.
If you want those, see the staticmethod builtin.
        """
        pass
    @classmethod
    def from_tuples(cls, data, closed: str = ..., copy: bool = ..., dtype=...):
        """
classmethod(function) -> method

Convert a function to be a class method.

A class method receives the class as implicit first argument,
just like an instance method receives the instance.
To declare a class method, use this idiom:

  class C:
      @classmethod
      def f(cls, arg1, arg2, ...):
          ...

It can be called either on the class (e.g. C.f()) or on an instance
(e.g. C().f()).  The instance is ignored except for its class.
If a class method is called for a derived class, the derived class
object is passed as the implied first argument.

Class methods are different than C++ or Java static methods.
If you want those, see the staticmethod builtin.
        """
        pass
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def __getitem__(self, value): ...
    def __setitem__(self, key, value) -> None: ...
    def __eq__(self, other): ...
    def __ne__(self, other): ...
    def fillna(self, value=..., method=..., limit=...): ...
    @property
    def dtype(self): ...
    def astype(self, dtype, copy: bool = ...): ...
    def copy(self): ...
    def isna(self): ...
    @property
    def nbytes(self) -> int: ...
    @property
    def size(self) -> int: ...
    def shift(self, periods: int = ..., fill_value: object = ...) -> IntervalArray: ...
    def take(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self: Self,
        indices: TakeIndexer,
        *,
        allow_fill: bool = ...,
        fill_value=...,
        axis=...,
        **kwargs,
    ) -> Self: ...
    def value_counts(self, dropna: bool = ...): ...
    @property
    def left(self) -> Index: ...
    @property
    def right(self) -> Index: ...
    @property
    def closed(self) -> bool: ...
    def set_closed(self, closed):
        """
Return an identical IntervalArray closed on the specified side.

Parameters
----------
closed : {'left', 'right', 'both', 'neither'}
    Whether the intervals are closed on the left-side, right-side, both
    or neither.

Returns
-------
IntervalArray

Examples
--------
>>> index = pd.arrays.IntervalArray.from_breaks(range(4))
>>> index
<IntervalArray>
[(0, 1], (1, 2], (2, 3]]
Length: 3, dtype: interval[int64, right]
>>> index.set_closed('both')
<IntervalArray>
[[0, 1], [1, 2], [2, 3]]
Length: 3, dtype: interval[int64, both]
        """
        pass
    @property
    def length(self) -> Index: ...
    @property
    def mid(self) -> Index: ...
    @property
    def is_non_overlapping_monotonic(self) -> bool:
        """
Return a boolean whether the IntervalArray is non-overlapping and monotonic.

Non-overlapping means (no Intervals share points), and monotonic means
either monotonic increasing or monotonic decreasing.

Examples
--------
For arrays:

>>> interv_arr = pd.arrays.IntervalArray([pd.Interval(0, 1), pd.Interval(1, 5)])
>>> interv_arr
<IntervalArray>
[(0, 1], (1, 5]]
Length: 2, dtype: interval[int64, right]
>>> interv_arr.is_non_overlapping_monotonic
True

>>> interv_arr = pd.arrays.IntervalArray([pd.Interval(0, 1),
...                                       pd.Interval(-1, 0.1)])
>>> interv_arr
<IntervalArray>
[(0.0, 1.0], (-1.0, 0.1]]
Length: 2, dtype: interval[float64, right]
>>> interv_arr.is_non_overlapping_monotonic
False

For Interval Index:

>>> interv_idx = pd.interval_range(start=0, end=2)
>>> interv_idx
IntervalIndex([(0, 1], (1, 2]], dtype='interval[int64, right]')
>>> interv_idx.is_non_overlapping_monotonic
True

>>> interv_idx = pd.interval_range(start=0, end=2, closed='both')
>>> interv_idx
IntervalIndex([[0, 1], [1, 2]], dtype='interval[int64, both]')
>>> interv_idx.is_non_overlapping_monotonic
False
        """
        pass
    def __array__(self, dtype=...) -> np.ndarray: ...
    def __arrow_array__(self, type=...): ...
    def to_tuples(self, na_tuple: bool = ...):
        """
Return an ndarray (if self is IntervalArray) or Index (if self is IntervalIndex) of tuples of the form (left, right).

Parameters
----------
na_tuple : bool, default True
    If ``True``, return ``NA`` as a tuple ``(nan, nan)``. If ``False``,
    just return ``NA`` as ``nan``.

Returns
-------
tuples: ndarray (if self is IntervalArray) or Index (if self is IntervalIndex)

Examples
--------
For :class:`pandas.IntervalArray`:

>>> idx = pd.arrays.IntervalArray.from_tuples([(0, 1), (1, 2)])
>>> idx
<IntervalArray>
[(0, 1], (1, 2]]
Length: 2, dtype: interval[int64, right]
>>> idx.to_tuples()
array([(0, 1), (1, 2)], dtype=object)

For :class:`pandas.IntervalIndex`:

>>> idx = pd.interval_range(start=0, end=2)
>>> idx
IntervalIndex([(0, 1], (1, 2]], dtype='interval[int64, right]')
>>> idx.to_tuples()
Index([(0, 1), (1, 2)], dtype='object')
        """
        pass
    def repeat(self, repeats, axis: Axis | None = ...):
        """
Repeat elements of a IntervalArray.

Returns a new IntervalArray where each element of the current IntervalArray
is repeated consecutively a given number of times.

Parameters
----------
repeats : int or array of ints
    The number of repetitions for each element. This should be a
    non-negative integer. Repeating 0 times will return an empty
    IntervalArray.
axis : None
    Must be ``None``. Has no effect but is accepted for compatibility
    with numpy.

Returns
-------
IntervalArray
    Newly created IntervalArray with repeated elements.

See Also
--------
Series.repeat : Equivalent function for Series.
Index.repeat : Equivalent function for Index.
numpy.repeat : Similar method for :class:`numpy.ndarray`.
ExtensionArray.take : Take arbitrary positions.

Examples
--------
>>> cat = pd.Categorical(['a', 'b', 'c'])
>>> cat
['a', 'b', 'c']
Categories (3, object): ['a', 'b', 'c']
>>> cat.repeat(2)
['a', 'a', 'b', 'b', 'c', 'c']
Categories (3, object): ['a', 'b', 'c']
>>> cat.repeat([1, 2, 3])
['a', 'b', 'b', 'c', 'c', 'c']
Categories (3, object): ['a', 'b', 'c']
        """
        pass
    @overload
    def contains(self, other: Series) -> Series[bool]:
        """
Check elementwise if the Intervals contain the value.

Return a boolean mask whether the value is contained in the Intervals
of the IntervalArray.

Parameters
----------
other : scalar
    The value to check whether it is contained in the Intervals.

Returns
-------
boolean array

See Also
--------
Interval.contains : Check whether Interval object contains value.
IntervalArray.overlaps : Check if an Interval overlaps the values in the
    IntervalArray.

Examples
--------
>>> intervals = pd.arrays.IntervalArray.from_tuples([(0, 1), (1, 3), (2, 4)])
>>> intervals
<IntervalArray>
[(0, 1], (1, 3], (2, 4]]
Length: 3, dtype: interval[int64, right]

>>> intervals.contains(0.5)
array([ True, False, False])
        """
        pass
    @overload
    def contains(
        self, other: Scalar | ExtensionArray | Index | np.ndarray
    ) -> np_ndarray_bool: ...
    def overlaps(self, other: Interval) -> bool:
        """
Check elementwise if an Interval overlaps the values in the IntervalArray.

Two intervals overlap if they share a common point, including closed
endpoints. Intervals that only have an open endpoint in common do not
overlap.

Parameters
----------
other : IntervalArray
    Interval to check against for an overlap.

Returns
-------
ndarray
    Boolean array positionally indicating where an overlap occurs.

See Also
--------
Interval.overlaps : Check whether two Interval objects overlap.

Examples
--------
>>> data = [(0, 1), (1, 3), (2, 4)]
>>> intervals = pd.arrays.IntervalArray.from_tuples(data)
>>> intervals
<IntervalArray>
[(0, 1], (1, 3], (2, 4]]
Length: 3, dtype: interval[int64, right]

>>> intervals.overlaps(pd.Interval(0.5, 1.5))
array([ True,  True, False])

Intervals that share closed endpoints overlap:

>>> intervals.overlaps(pd.Interval(1, 3, closed='left'))
array([ True,  True, True])

Intervals that only have an open endpoint in common do not overlap:

>>> intervals.overlaps(pd.Interval(1, 2, closed='right'))
array([False,  True, False])
        """
        pass
