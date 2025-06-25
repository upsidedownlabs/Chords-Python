from pandas import (
    DataFrame,
    Series,
)
from pandas.core.window.rolling import (
    BaseWindow,
    BaseWindowGroupby,
)

from pandas._typing import (
    NDFrameT,
    WindowingEngine,
    WindowingEngineKwargs,
)

class ExponentialMovingWindow(BaseWindow[NDFrameT]):
    def online(
        self,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
    ) -> OnlineExponentialMovingWindow[NDFrameT]: ...
    def mean(
        self,
        numeric_only: bool = ...,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
    ) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) mean.

Parameters
----------
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

engine : str, default None
    * ``'cython'`` : Runs the operation through C-extensions from cython.
    * ``'numba'`` : Runs the operation through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or globally setting ``compute.use_numba``

      .. versionadded:: 1.3.0

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}``

      .. versionadded:: 1.3.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.mean : Aggregating mean for Series.
pandas.DataFrame.mean : Aggregating mean for DataFrame.

Notes
-----
See :ref:`window.numba_engine` and :ref:`enhancingperf.numba` for extended documentation and performance considerations for the Numba engine.

Examples
--------
>>> ser = pd.Series([1, 2, 3, 4])
>>> ser.ewm(alpha=.2).mean()
0    1.000000
1    1.555556
2    2.147541
3    2.775068
dtype: float64
        """
        pass
    def sum(
        self,
        numeric_only: bool = ...,
        engine: WindowingEngine = ...,
        engine_kwargs: WindowingEngineKwargs = ...,
    ) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) sum.

Parameters
----------
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

engine : str, default None
    * ``'cython'`` : Runs the operation through C-extensions from cython.
    * ``'numba'`` : Runs the operation through JIT compiled code from numba.
    * ``None`` : Defaults to ``'cython'`` or globally setting ``compute.use_numba``

      .. versionadded:: 1.3.0

engine_kwargs : dict, default None
    * For ``'cython'`` engine, there are no accepted ``engine_kwargs``
    * For ``'numba'`` engine, the engine can accept ``nopython``, ``nogil``
      and ``parallel`` dictionary keys. The values must either be ``True`` or
      ``False``. The default ``engine_kwargs`` for the ``'numba'`` engine is
      ``{'nopython': True, 'nogil': False, 'parallel': False}``

      .. versionadded:: 1.3.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.sum : Aggregating sum for Series.
pandas.DataFrame.sum : Aggregating sum for DataFrame.

Notes
-----
See :ref:`window.numba_engine` and :ref:`enhancingperf.numba` for extended documentation and performance considerations for the Numba engine.

Examples
--------
>>> ser = pd.Series([1, 2, 3, 4])
>>> ser.ewm(alpha=.2).sum()
0    1.000
1    2.800
2    5.240
3    8.192
dtype: float64
        """
        pass
    def std(self, bias: bool = ..., numeric_only: bool = ...) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) standard deviation.

Parameters
----------
bias : bool, default False
    Use a standard estimation bias correction.
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.std : Aggregating std for Series.
pandas.DataFrame.std : Aggregating std for DataFrame.

Examples
--------
>>> ser = pd.Series([1, 2, 3, 4])
>>> ser.ewm(alpha=.2).std()
0         NaN
1    0.707107
2    0.995893
3    1.277320
dtype: float64
        """
        pass
    def var(self, bias: bool = ..., numeric_only: bool = ...) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) variance.

Parameters
----------
bias : bool, default False
    Use a standard estimation bias correction.
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.var : Aggregating var for Series.
pandas.DataFrame.var : Aggregating var for DataFrame.

Examples
--------
>>> ser = pd.Series([1, 2, 3, 4])
>>> ser.ewm(alpha=.2).var()
0         NaN
1    0.500000
2    0.991803
3    1.631547
dtype: float64
        """
        pass
    def cov(
        self,
        other: DataFrame | Series | None = ...,
        pairwise: bool | None = ...,
        bias: bool = ...,
        numeric_only: bool = ...,
    ) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) sample covariance.

Parameters
----------
other : Series or DataFrame , optional
    If not supplied then will default to self and produce pairwise
    output.
pairwise : bool, default None
    If False then only matching columns between self and other will be
    used and the output will be a DataFrame.
    If True then all pairwise combinations will be calculated and the
    output will be a MultiIndex DataFrame in the case of DataFrame
    inputs. In the case of missing elements, only complete pairwise
    observations will be used.
bias : bool, default False
    Use a standard estimation bias correction.
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.cov : Aggregating cov for Series.
pandas.DataFrame.cov : Aggregating cov for DataFrame.

Examples
--------
>>> ser1 = pd.Series([1, 2, 3, 4])
>>> ser2 = pd.Series([10, 11, 13, 16])
>>> ser1.ewm(alpha=.2).cov(ser2)
0         NaN
1    0.500000
2    1.524590
3    3.408836
dtype: float64
        """
        pass
    def corr(
        self,
        other: DataFrame | Series | None = ...,
        pairwise: bool | None = ...,
        numeric_only: bool = ...,
    ) -> NDFrameT:
        """
Calculate the ewm (exponential weighted moment) sample correlation.

Parameters
----------
other : Series or DataFrame, optional
    If not supplied then will default to self and produce pairwise
    output.
pairwise : bool, default None
    If False then only matching columns between self and other will be
    used and the output will be a DataFrame.
    If True then all pairwise combinations will be calculated and the
    output will be a MultiIndex DataFrame in the case of DataFrame
    inputs. In the case of missing elements, only complete pairwise
    observations will be used.
numeric_only : bool, default False
    Include only float, int, boolean columns.

    .. versionadded:: 1.5.0

Returns
-------
Series or DataFrame
    Return type is the same as the original object with ``np.float64`` dtype.

See Also
--------
pandas.Series.ewm : Calling ewm with Series data.
pandas.DataFrame.ewm : Calling ewm with DataFrames.
pandas.Series.corr : Aggregating corr for Series.
pandas.DataFrame.corr : Aggregating corr for DataFrame.

Examples
--------
>>> ser1 = pd.Series([1, 2, 3, 4])
>>> ser2 = pd.Series([10, 11, 13, 16])
>>> ser1.ewm(alpha=.2).corr(ser2)
0         NaN
1    1.000000
2    0.982821
3    0.977802
dtype: float64
        """
        pass

class ExponentialMovingWindowGroupby(
    BaseWindowGroupby[NDFrameT], ExponentialMovingWindow[NDFrameT]
): ...

class OnlineExponentialMovingWindow(ExponentialMovingWindow[NDFrameT]):
    def reset(self) -> None: ...
    def aggregate(self, func, *args, **kwargs): ...
    def std(self, bias: bool = ..., *args, **kwargs): ...
    def corr(
        self,
        other: DataFrame | Series | None = ...,
        pairwise: bool | None = ...,
        numeric_only: bool = ...,
    ): ...
    def cov(
        self,
        other: DataFrame | Series | None = ...,
        pairwise: bool | None = ...,
        bias: bool = ...,
        numeric_only: bool = ...,
    ): ...
    def var(self, bias: bool = ..., numeric_only: bool = ...): ...
    def mean(
        self, *args, update: NDFrameT | None = ..., update_times: None = ..., **kwargs
    ) -> NDFrameT: ...
