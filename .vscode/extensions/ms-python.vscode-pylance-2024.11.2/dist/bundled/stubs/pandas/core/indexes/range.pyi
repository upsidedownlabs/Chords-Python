from collections.abc import Sequence
from typing import overload

import numpy as np
from pandas import Series
from pandas.core.indexes.base import Index

from pandas._typing import (
    HashableT,
    np_ndarray_anyint,
    np_ndarray_bool,
    npt,
)

class RangeIndex(Index[int]):
    def __new__(
        cls,
        start: int | RangeIndex | range = ...,
        stop: int = ...,
        step: int = ...,
        dtype=...,
        copy: bool = ...,
        name=...,
    ): ...
    @classmethod
    def from_range(cls, data, name=..., dtype=...): ...
    def __reduce__(self): ...
    def start(self): ...
    def stop(self): ...
    def step(self): ...
    @property
    def nbytes(self) -> int: ...
    def memory_usage(self, deep: bool = ...) -> int: ...
    @property
    def dtype(self) -> np.dtype: ...
    @property
    def is_unique(self) -> bool: ...
    @property
    def is_monotonic_increasing(self) -> bool: ...
    @property
    def is_monotonic_decreasing(self) -> bool: ...
    @property
    def has_duplicates(self) -> bool: ...
    def __contains__(self, key: int | np.integer) -> bool: ...
    def get_indexer(self, target, method=..., limit=..., tolerance=...): ...
    def tolist(self): ...
    def copy(self, name=..., deep: bool = ..., dtype=..., **kwargs):
        """
Make a copy of this object.

Name is set on the new object.

Parameters
----------
name : Label, optional
    Set name for new object.
deep : bool, default False

Returns
-------
Index
    Index refer to new object which is a copy of this object.

Notes
-----
In most cases, there should be no functional difference from using
``deep``, but if ``deep`` is passed it will attempt to deepcopy.

Examples
--------
>>> idx = pd.Index(['a', 'b', 'c'])
>>> new_idx = idx.copy()
>>> idx is new_idx
False
        """
        pass
    def min(self, axis=..., skipna: bool = ..., *args, **kwargs): ...
    def max(self, axis=..., skipna: bool = ..., *args, **kwargs): ...
    def argsort(self, *args, **kwargs): ...
    def factorize(
        self, sort: bool = ..., use_na_sentinel: bool = ...
    ) -> tuple[npt.NDArray[np.intp], RangeIndex]: ...
    def equals(self, other): ...
    def join(
        self,
        other,
        *,
        how: str = ...,
        level=...,
        return_indexers: bool = ...,
        sort: bool = ...,
    ): ...
    def __len__(self) -> int: ...
    @property
    def size(self) -> int: ...
    def __floordiv__(self, other): ...
    def all(self) -> bool: ...
    def any(self) -> bool: ...
    def union(
        self, other: list[HashableT] | Index, sort=...
    ) -> Index | Index[int] | RangeIndex: ...
    @overload  # type: ignore[override]
    def __getitem__(
        self,
        idx: (
            slice
            | np_ndarray_anyint
            | Sequence[int]
            | Index
            | Series[bool]
            | Sequence[bool]
            | np_ndarray_bool
        ),
    ) -> Index: ...
    @overload
    def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, idx: int
    ) -> int: ...
