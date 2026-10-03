# Translated from OCCT src/FoundationClasses/TKMath/GTests/BSplCLib_Cache_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BSplCLib import BSplCLib, BSplCLib_Cache
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1

TOL = 1e-10


def _frange(step):
    # same accumulation as the C++ loop `for (double u = 0.0; u <= 1.0; u += step)`
    u = 0.0
    while u <= 1.0:
        yield u
        u += step


def _arr_f(values):
    a = NCollection_Array1[float](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def _arr_i(values):
    a = NCollection_Array1[int](1, len(values))
    for i, v in enumerate(values, 1):
        a[i] = v
    return a


def _poles(pts):
    a = NCollection_Array1[gp_Pnt](1, len(pts))
    for i, p in enumerate(pts, 1):
        a[i] = gp_Pnt(*p)
    return a


def _flat(knots, mults):
    out = []
    for k, m in zip(knots, mults):
        out.extend([k] * m)
    return _arr_f(out)


def _near(a, b, comps="XYZ"):
    for c in comps:
        assert abs(getattr(a, c)() - getattr(b, c)()) <= TOL


CUBIC = [(0, 0, 0), (1, 2, 1), (2, 2, 1), (3, 0, 0)]
RATIONAL = [(1, 0, 0), (1, 1, 0), (0, 1, 0)]
RAT_W = [1.0, 0.707106781186548, 1.0]


def _setup(pts, weights, mult):
    poles = _poles(pts)
    w = None if weights is None else _arr_f(weights)
    knots = _arr_f([0.0, 1.0])
    mults = _arr_i([mult, mult])
    flat = _flat([0.0, 1.0], [mult, mult])
    return poles, w, knots, mults, flat, mult - 1


def _run(pts, weights, mult, order, comps="XYZ"):
    poles, w, knots, mults, flat, deg = _setup(pts, weights, mult)
    cache = BSplCLib_Cache(deg, False, flat, poles, w)
    cache.BuildCache(0.5, flat, poles, w)
    for u in _frange(0.1):
        if not cache.IsCacheValid(u):
            cache.BuildCache(u, flat, poles, w)
        cres = [gp_Pnt()] + [gp_Vec() for _ in range(order)]
        dres = [gp_Pnt()] + [gp_Vec() for _ in range(order)]
        getattr(cache, f"D{order}")(u, *cres)
        getattr(BSplCLib, f"D{order}_s")(u, 0, deg, False, poles, w, knots, mults, *dres)
        for c, d in zip(cres, dres):
            _near(c, d, comps)


def test_BSplCLib_CacheTest_D0_NonRationalCurve3D():
    _run([(0, 0, 0), (1, 2, 0), (2, 2, 0), (3, 0, 0)], None, 4, 0)


def test_BSplCLib_CacheTest_D1_NonRationalCurve3D():
    _run(CUBIC, None, 4, 1)


def test_BSplCLib_CacheTest_D2_NonRationalCurve3D():
    _run(CUBIC, None, 4, 2)


def test_BSplCLib_CacheTest_D0_RationalCurve3D():
    _run(RATIONAL, RAT_W, 3, 0)


def test_BSplCLib_CacheTest_D1_RationalCurve3D():
    _run(RATIONAL, RAT_W, 3, 1)


def test_BSplCLib_CacheTest_D2_RationalCurve3D():
    _run(RATIONAL, RAT_W, 3, 2)


def test_BSplCLib_CacheTest_D3_NonRationalCurve3D():
    _run(CUBIC, None, 4, 3, comps="X")
