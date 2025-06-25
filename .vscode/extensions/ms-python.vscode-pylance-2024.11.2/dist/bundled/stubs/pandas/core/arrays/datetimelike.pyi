from collections.abc import Sequence

import numpy as np
from pandas.core.arrays.base import (
    ExtensionArray,
    ExtensionOpsMixin,
)
from typing_extensions import Self

from pandas._libs import (
    NaT as NaT,
    NaTType as NaTType,
)
from pandas._typing import TimeUnit

class DatelikeOps:
    def strftime(self, date_format): ...

class TimelikeOps:
    @property
    def unit(self) -> TimeUnit: ...
    def as_unit(self, unit: TimeUnit) -> Self: ...
    def round(self, freq, ambiguous: str = ..., nonexistent: str = ...):
        """
Perform round operation on the data to the specified `freq`.

Parameters
----------
freq : str or Offset
    The frequency level to round the index to. Must be a fixed
    frequency like 'S' (second) not 'ME' (month end). See
    :ref:`frequency aliases <timeseries.offset_aliases>` for
    a list of possible `freq` values.
ambiguous : 'infer', bool-ndarray, 'NaT', default 'raise'
    Only relevant for DatetimeIndex:

    - 'infer' will attempt to infer fall dst-transition hours based on
      order
    - bool-ndarray where True signifies a DST time, False designates
      a non-DST time (note that this flag is only applicable for
      ambiguous times)
    - 'NaT' will return NaT where there are ambiguous times
    - 'raise' will raise an AmbiguousTimeError if there are ambiguous
      times.

nonexistent : 'shift_forward', 'shift_backward', 'NaT', timedelta, default 'raise'
    A nonexistent time does not exist in a particular timezone
    where clocks moved forward due to DST.

    - 'shift_forward' will shift the nonexistent time forward to the
      closest existing time
    - 'shift_backward' will shift the nonexistent time backward to the
      closest existing time
    - 'NaT' will return NaT where there are nonexistent times
    - timedelta objects will shift nonexistent times by the timedelta
    - 'raise' will raise an NonExistentTimeError if there are
      nonexistent times.

Returns
-------
DatetimeIndex, TimedeltaIndex, or Series
    Index of the same type for a DatetimeIndex or TimedeltaIndex,
    or a Series with the same index for a Series.

Raises
------
ValueError if the `freq` cannot be converted.

Notes
-----
If the timestamps have a timezone, rounding will take place relative to the
local ("wall") time and re-localized to the same timezone. When rounding
near daylight savings time, use ``nonexistent`` and ``ambiguous`` to
control the re-localization behavior.

Examples
--------
**DatetimeIndex**

>>> rng = pd.date_range('1/1/2018 11:59:00', periods=3, freq='min')
>>> rng
DatetimeIndex(['2018-01-01 11:59:00', '2018-01-01 12:00:00',
               '2018-01-01 12:01:00'],
              dtype='datetime64[ns]', freq='min')
>>> rng.round('h')
DatetimeIndex(['2018-01-01 12:00:00', '2018-01-01 12:00:00',
               '2018-01-01 12:00:00'],
              dtype='datetime64[ns]', freq=None)

**Series**

>>> pd.Series(rng).dt.round("h")
0   2018-01-01 12:00:00
1   2018-01-01 12:00:00
2   2018-01-01 12:00:00
dtype: datetime64[ns]

When rounding near a daylight savings time transition, use ``ambiguous`` or
``nonexistent`` to control how the timestamp should be re-localized.

>>> rng_tz = pd.DatetimeIndex(["2021-10-31 03:30:00"], tz="Europe/Amsterdam")

>>> rng_tz.floor("2h", ambiguous=False)
DatetimeIndex(['2021-10-31 02:00:00+01:00'],
              dtype='datetime64[ns, Europe/Amsterdam]', freq=None)

>>> rng_tz.floor("2h", ambiguous=True)
DatetimeIndex(['2021-10-31 02:00:00+02:00'],
              dtype='datetime64[ns, Europe/Amsterdam]', freq=None)
        """
        pass
    def floor(self, freq, ambiguous: str = ..., nonexistent: str = ...):
        """
Perform floor operation on the data to the specified `freq`.

Parameters
----------
freq : str or Offset
    The frequency level to floor the index to. Must be a fixed
    frequency like 'S' (second) not 'ME' (month end). See
    :ref:`frequency aliases <timeseries.offset_aliases>` for
    a list of possible `freq` values.
ambiguous : 'infer', bool-ndarray, 'NaT', default 'raise'
    Only relevant for DatetimeIndex:

    - 'infer' will attempt to infer fall dst-transition hours based on
      order
    - bool-ndarray where True signifies a DST time, False designates
      a non-DST time (note that this flag is only applicable for
      ambiguous times)
    - 'NaT' will return NaT where there are ambiguous times
    - 'raise' will raise an AmbiguousTimeError if there are ambiguous
      times.

nonexistent : 'shift_forward', 'shift_backward', 'NaT', timedelta, default 'raise'
    A nonexistent time does not exist in a particular timezone
    where clocks moved forward due to DST.

    - 'shift_forward' will shift the nonexistent time forward to the
      closest existing time
    - 'shift_backward' will shift the nonexistent time backward to the
      closest existing time
    - 'NaT' will return NaT where there are nonexistent times
    - timedelta objects will shift nonexistent times by the timedelta
    - 'raise' will raise an NonExistentTimeError if there are
      nonexistent times.

Returns
-------
DatetimeIndex, TimedeltaIndex, or Series
    Index of the same type for a DatetimeIndex or TimedeltaIndex,
    or a Series with the same index for a Series.

Raises
------
ValueError if the `freq` cannot be converted.

Notes
-----
If the timestamps have a timezone, flooring will take place relative to the
local ("wall") time and re-localized to the same timezone. When flooring
near daylight savings time, use ``nonexistent`` and ``ambiguous`` to
control the re-localization behavior.

Examples
--------
**DatetimeIndex**

>>> rng = pd.date_range('1/1/2018 11:59:00', periods=3, freq='min')
>>> rng
DatetimeIndex(['2018-01-01 11:59:00', '2018-01-01 12:00:00',
               '2018-01-01 12:01:00'],
              dtype='datetime64[ns]', freq='min')
>>> rng.floor('h')
DatetimeIndex(['2018-01-01 11:00:00', '2018-01-01 12:00:00',
               '2018-01-01 12:00:00'],
              dtype='datetime64[ns]', freq=None)

**Series**

>>> pd.Series(rng).dt.floor("h")
0   2018-01-01 11:00:00
1   2018-01-01 12:00:00
2   2018-01-01 12:00:00
dtype: datetime64[ns]

When rounding near a daylight savings time transition, use ``ambiguous`` or
``nonexistent`` to control how the timestamp should be re-localized.

>>> rng_tz = pd.DatetimeIndex(["2021-10-31 03:30:00"], tz="Europe/Amsterdam")

>>> rng_tz.floor("2h", ambiguous=False)
DatetimeIndex(['2021-10-31 02:00:00+01:00'],
             dtype='datetime64[ns, Europe/Amsterdam]', freq=None)

>>> rng_tz.floor("2h", ambiguous=True)
DatetimeIndex(['2021-10-31 02:00:00+02:00'],
              dtype='datetime64[ns, Europe/Amsterdam]', freq=None)
        """
        pass
    def ceil(self, freq, ambiguous: str = ..., nonexistent: str = ...):
        """
Perform ceil operation on the data to the specified `freq`.

Parameters
----------
freq : str or Offset
    The frequency level to ceil the index to. Must be a fixed
    frequency like 'S' (second) not 'ME' (month end). See
    :ref:`frequency aliases <timeseries.offset_aliases>` for
    a list of possible `freq` values.
ambiguous : 'infer', bool-ndarray, 'NaT', default 'raise'
    Only relevant for DatetimeIndex:

    - 'infer' will attempt to infer fall dst-transition hours based on
      order
    - bool-ndarray where True signifies a DST time, False designates
      a non-DST time (note that this flag is only applicable for
      ambiguous times)
    - 'NaT' will return NaT where there are ambiguous times
    - 'raise' will raise an AmbiguousTimeError if there are ambiguous
      times.

nonexistent : 'shift_forward', 'shift_backward', 'NaT', timedelta, default 'raise'
    A nonexistent time does not exist in a particular timezone
    where clocks moved forward due to DST.

    - 'shift_forward' will shift the nonexistent time forward to the
      closest existing time
    - 'shift_backward' will shift the nonexistent time backward to the
      closest existing time
    - 'NaT' will return NaT where there are nonexistent times
    - timedelta objects will shift nonexistent times by the timedelta
    - 'raise' will raise an NonExistentTimeError if there are
      nonexistent times.

Returns
-------
DatetimeIndex, TimedeltaIndex, or Series
    Index of the same type for a DatetimeIndex or TimedeltaIndex,
    or a Series with the same index for a Series.

Raises
------
ValueError if the `freq` cannot be converted.

Notes
-----
If the timestamps have a timezone, ceiling will take place relative to the
local ("wall") time and re-localized to the same timezone. When ceiling
near daylight savings time, use ``nonexistent`` and ``ambiguous`` to
control the re-localization behavior.

Examples
--------
**DatetimeIndex**

>>> rng = pd.date_range('1/1/2018 11:59:00', periods=3, freq='min')
>>> rng
DatetimeIndex(['2018-01-01 11:59:00', '2018-01-01 12:00:00',
               '2018-01-01 12:01:00'],
              dtype='datetime64[ns]', freq='min')
>>> rng.ceil('h')
DatetimeIndex(['2018-01-01 12:00:00', '2018-01-01 12:00:00',
               '2018-01-01 13:00:00'],
              dtype='datetime64[ns]', freq=None)

**Series**

>>> pd.Series(rng).dt.ceil("h")
0   2018-01-01 12:00:00
1   2018-01-01 12:00:00
2   2018-01-01 13:00:00
dtype: datetime64[ns]

When rounding near a daylight savings time transition, use ``ambiguous`` or
``nonexistent`` to control how the timestamp should be re-localized.

>>> rng_tz = pd.DatetimeIndex(["2021-10-31 01:30:00"], tz="Europe/Amsterdam")

>>> rng_tz.ceil("h", ambiguous=False)
DatetimeIndex(['2021-10-31 02:00:00+01:00'],
              dtype='datetime64[ns, Europe/Amsterdam]', freq=None)

>>> rng_tz.ceil("h", ambiguous=True)
DatetimeIndex(['2021-10-31 02:00:00+02:00'],
              dtype='datetime64[ns, Europe/Amsterdam]', freq=None)
        """
        pass

class DatetimeLikeArrayMixin(ExtensionOpsMixin, ExtensionArray):
    @property
    def ndim(self) -> int: ...
    @property
    def shape(self): ...
    def reshape(self, *args, **kwargs): ...
    def ravel(self, *args, **kwargs): ...
    def __iter__(self): ...
    @property
    def asi8(self) -> np.ndarray: ...
    @property
    def nbytes(self): ...
    def __array__(self, dtype=...) -> np.ndarray: ...
    @property
    def size(self) -> int: ...
    def __len__(self) -> int: ...
    def __getitem__(self, key): ...
    def __setitem__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, key: int | Sequence[int] | Sequence[bool] | slice, value
    ) -> None: ...
    def astype(self, dtype, copy: bool = ...): ...
    def view(self, dtype=...): ...
    def unique(self): ...
    def copy(self): ...
    def shift(self, periods: int = ..., fill_value=..., axis: int = ...): ...
    def searchsorted(self, value, side: str = ..., sorter=...): ...
    def repeat(self, repeats, *args, **kwargs): ...
    def value_counts(self, dropna: bool = ...): ...
    def map(self, mapper): ...
    def isna(self): ...
    def fillna(self, value=..., method=..., limit=...): ...
    @property
    def freq(self): ...
    @freq.setter
    def freq(self, value) -> None: ...
    @property
    def freqstr(self): ...
    @property
    def inferred_freq(self): ...
    @property
    def resolution(self): ...
    __pow__ = ...
    __rpow__ = ...
    __mul__ = ...
    __rmul__ = ...
    __truediv__ = ...
    __rtruediv__ = ...
    __floordiv__ = ...
    __rfloordiv__ = ...
    __mod__ = ...
    __rmod__ = ...
    __divmod__ = ...
    __rdivmod__ = ...
    def __add__(self, other): ...
    def __radd__(self, other): ...
    def __sub__(self, other): ...
    def __rsub__(self, other): ...
    def __iadd__(self, other): ...
    def __isub__(self, other): ...
    def min(self, *, axis=..., skipna: bool = ..., **kwargs): ...
    def max(self, *, axis=..., skipna: bool = ..., **kwargs): ...
    def mean(self, *, skipna: bool = ...): ...

def maybe_infer_freq(freq): ...
