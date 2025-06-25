from collections.abc import Sequence

import numpy as np
from pandas import PeriodDtype
from pandas.core.arrays.datetimelike import (
    DatelikeOps,
    DatetimeLikeArrayMixin,
)

from pandas._libs.tslibs import Timestamp
from pandas._libs.tslibs.period import Period

from pandas.tseries.offsets import Tick

class PeriodArray(DatetimeLikeArrayMixin, DatelikeOps):
    __array_priority__: int = ...
    def __init__(self, values, freq=..., dtype=..., copy: bool = ...) -> None: ...
    @property
    def dtype(self) -> PeriodDtype: ...
    def __array__(self, dtype=...) -> np.ndarray: ...
    def __arrow_array__(self, type=...): ...
    year: int = ...
    month: int = ...
    day: int = ...
    hour: int = ...
    minute: int = ...
    second: int = ...
    weekofyear: int = ...
    week: int = ...
    dayofweek: int = ...
    weekday: int = ...
    dayofyear: int = ...
    day_of_year = ...
    quarter: int = ...
    qyear: int = ...
    days_in_month: int = ...
    daysinmonth: int = ...
    @property
    def is_leap_year(self) -> bool: ...
    @property
    def start_time(self) -> Timestamp: ...
    @property
    def end_time(self) -> Timestamp: ...
    def to_timestamp(self, freq: str | None = ..., how: str = ...) -> Timestamp: ...
    def asfreq(self, freq: str | None = ..., how: str = ...) -> Period:
        """
Convert the PeriodArray to the specified frequency `freq`.

Equivalent to applying :meth:`pandas.Period.asfreq` with the given arguments
to each :class:`~pandas.Period` in this PeriodArray.

Parameters
----------
freq : str
    A frequency.
how : str {'E', 'S'}, default 'E'
    Whether the elements should be aligned to the end
    or start within pa period.

    * 'E', 'END', or 'FINISH' for end,
    * 'S', 'START', or 'BEGIN' for start.

    January 31st ('END') vs. January 1st ('START') for example.

Returns
-------
PeriodArray
    The transformed PeriodArray with the new frequency.

See Also
--------
PeriodIndex.asfreq: Convert each Period in a PeriodIndex to the given frequency.
Period.asfreq : Convert a :class:`~pandas.Period` object to the given frequency.

Examples
--------
>>> pidx = pd.period_range('2010-01-01', '2015-01-01', freq='Y')
>>> pidx
PeriodIndex(['2010', '2011', '2012', '2013', '2014', '2015'],
dtype='period[Y-DEC]')

>>> pidx.asfreq('M')
PeriodIndex(['2010-12', '2011-12', '2012-12', '2013-12', '2014-12',
'2015-12'], dtype='period[M]')

>>> pidx.asfreq('M', how='S')
PeriodIndex(['2010-01', '2011-01', '2012-01', '2013-01', '2014-01',
'2015-01'], dtype='period[M]')
        """
        pass
    def astype(self, dtype, copy: bool = ...): ...

def raise_on_incompatible(left, right): ...
def period_array(
    data: Sequence[Period | None],
    freq: str | Tick | None = ...,
    copy: bool = ...,
) -> PeriodArray: ...
def validate_dtype_freq(dtype, freq): ...
def dt64arr_to_periodarr(data, freq, tz=...): ...
