# Python: 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]
# Library: numpy, version: 1.26.4
# Module: numpy.random._common, version: unspecified
import typing
import builtins as _mod_builtins
import importlib._bootstrap as _mod_importlib__bootstrap

__all__: list
__doc__: typing.Any
__file__: str
__name__: str
__package__: str
__pyx_capi__: dict
__test__: dict
interface = _mod_importlib__bootstrap.interface
def namedtuple(typename, field_names) -> typing.Any:
    "Returns a new subclass of tuple with named fields.\n\n    >>> Point = namedtuple('Point', ['x', 'y'])\n    >>> Point.__doc__                   # docstring for the new class\n    'Point(x, y)'\n    >>> p = Point(11, y=22)             # instantiate with positional args or keywords\n    >>> p[0] + p[1]                     # indexable like a plain tuple\n    33\n    >>> x, y = p                        # unpack like a regular tuple\n    >>> x, y\n    (11, 22)\n    >>> p.x + p.y                       # fields also accessible by name\n    33\n    >>> d = p._asdict()                 # convert to a dictionary\n    >>> d['x']\n    11\n    >>> Point(**d)                      # convert from a dictionary\n    Point(x=11, y=22)\n    >>> p._replace(x=100)               # _replace() is like str.replace() but targets named fields\n    Point(x=100, y=22)\n\n    "
    ...

def __getattr__(name) -> typing.Any:
    ...

