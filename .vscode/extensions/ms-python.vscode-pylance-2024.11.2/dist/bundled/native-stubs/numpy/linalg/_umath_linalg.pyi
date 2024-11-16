# Python: 3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]
# Library: numpy, version: 1.26.4
# Module: numpy.linalg._umath_linalg, version: 0.1.5
import typing
import builtins as _mod_builtins

__doc__: typing.Any
__file__: str
__name__: str
__package__: str
__version__: str
_ilp64: bool
def cholesky_lo(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'cholesky decomposition of hermitian positive-definite matrices. \nBroadcast to all outer dimensions. \n    "(m,m)->(m,m)" \n'
    ...

def det(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'det of the last two dimensions and broadcast on the rest. \n    "(m,m)->()" \n'
    ...

def eig(x, out1=..., out2=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eig on the last two dimension and broadcast to the rest. \nResults in a vector with the  eigenvalues and a matrix with the eigenvectors. \n    "(m,m)->(m),(m,m)" \n'
    ...

def eigh_lo(x, out1=..., out2=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eigh on the last two dimension and broadcast to the rest, using lower triangle \nResults in a vector of eigenvalues and a matrix with theeigenvectors. \n    "(m,m)->(m),(m,m)" \n'
    ...

def eigh_up(x, out1=..., out2=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eigh on the last two dimension and broadcast to the rest, using upper triangle. \nResults in a vector of eigenvalues and a matrix with the eigenvectors. \n    "(m,m)->(m),(m,m)" \n'
    ...

def eigvals(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eigvals on the last two dimension and broadcast to the rest. \nResults in a vector of eigenvalues. \n'
    ...

def eigvalsh_lo(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eigh on the last two dimension and broadcast to the rest, using lower triangle. \nResults in a vector of eigenvalues and a matrix with theeigenvectors. \n    "(m,m)->(m)" \n'
    ...

def eigvalsh_up(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'eigvalsh on the last two dimension and broadcast to the rest, using upper triangle. \nResults in a vector of eigenvalues and a matrix with theeigenvectors.\n    "(m,m)->(m)" \n'
    ...

def inv(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'compute the inverse of the last two dimensions and broadcast to the rest. \nResults in the inverse matrices. \n    "(m,m)->(m,m)" \n'
    ...

def lstsq_m(x1, x2, x3, out1=..., out2=..., out3=..., out4=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'least squares on the last two dimensions and broadcast to the rest. \nFor m <= n. \n'
    ...

def lstsq_n(x1, x2, x3, out1=..., out2=..., out3=..., out4=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'least squares on the last two dimensions and broadcast to the rest. \nFor m >= n, meaning that residuals are produced. \n'
    ...

def qr_complete(x1, x2, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'Compute Q matrix for the last two dimensions \nand broadcast to the rest. For m > n. \n'
    ...

def qr_r_raw_m(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'Compute TAU vector for the last two dimensions \nand broadcast to the rest. For m <= n. \n'
    ...

def qr_r_raw_n(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'Compute TAU vector for the last two dimensions \nand broadcast to the rest. For m > n. \n'
    ...

def qr_reduced(x1, x2, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'Compute Q matrix for the last two dimensions \nand broadcast to the rest. \n'
    ...

def slogdet(x, out1=..., out2=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'slogdet on the last two dimensions and broadcast on the rest. \nResults in two arrays, one with sign and the other with log of the determinants. \n    "(m,m)->(),()" \n'
    ...

def solve(x1, x2, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'solve the system a x = b, on the last two dimensions, broadcast to the rest. \nResults in a matrices with the solutions. \n    "(m,m),(m,n)->(m,n)" \n'
    ...

def solve1(x1, x2, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'solve the system a x = b, for b being a vector, broadcast in the outer dimensions. \nResults in vectors with the solutions. \n    "(m,m),(m)->(m)" \n'
    ...

def svd_m(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when n>=m. '
    ...

def svd_m_f(x, out1=..., out2=..., out3=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when m<=n'
    ...

def svd_m_s(x, out1=..., out2=..., out3=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when m<=n'
    ...

def svd_n(x, out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when n<=m'
    ...

def svd_n_f(x, out1=..., out2=..., out3=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when m>=n'
    ...

def svd_n_s(x, out1=..., out2=..., out3=..., out=..., *, casting=..., order=..., dtype=..., subok=..., signature=..., extobj=..., axes=..., axis=...) -> typing.Any:
    'svd when m>=n'
    ...

def __getattr__(name) -> typing.Any:
    ...

