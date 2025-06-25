from collections.abc import Iterable
from typing import Literal

import numpy as np
from pandas.core import accessor
from pandas.core.indexes.base import Index
from pandas.core.indexes.extension import ExtensionIndex
from typing_extensions import Self

from pandas._typing import (
    S1,
    DtypeArg,
)

class CategoricalIndex(ExtensionIndex[S1], accessor.PandasDelegate):
    codes: np.ndarray = ...
    categories: Index = ...
    def __new__(
        cls,
        data: Iterable[S1] = ...,
        categories=...,
        ordered=...,
        dtype=...,
        copy: bool = ...,
        name=...,
    ) -> Self: ...
    def equals(self, other): ...
    @property
    def inferred_type(self) -> str: ...
    @property
    def values(self): ...
    def __contains__(self, key) -> bool:
        """
Return a boolean indicating whether the provided key is in the index.

Parameters
----------
key : label
    The key to check if it is present in the index.

Returns
-------
bool
    Whether the key search is in the index.

Raises
------
TypeError
    If the key is not hashable.

See Also
--------
Index.isin : Returns an ndarray of boolean dtype indicating whether the
    list-like key is in the index.

Examples
--------
>>> idx = pd.Index([1, 2, 3, 4])
>>> idx
Index([1, 2, 3, 4], dtype='int64')

>>> 2 in idx
True
>>> 6 in idx
False
        """
        pass
    def __array__(self, dtype=...) -> np.ndarray: ...
    def astype(self, dtype: DtypeArg, copy: bool = ...) -> Index: ...
    def fillna(self, value=..., downcast=...): ...
    @property
    def is_unique(self) -> bool: ...
    @property
    def is_monotonic_increasing(self) -> bool: ...
    @property
    def is_monotonic_decreasing(self) -> bool: ...
    def unique(self, level=...): ...
    def duplicated(self, keep: Literal["first", "last", False] = ...): ...
    def where(self, cond, other=...): ...
    def reindex(self, target, method=..., level=..., limit=..., tolerance=...): ...
    def get_indexer(self, target, method=..., limit=..., tolerance=...): ...
    def get_indexer_non_unique(self, target): ...
    def delete(self, loc): ...
    def insert(self, loc, item): ...
