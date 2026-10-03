# Translated from OCCT src/FoundationClasses/TKMath/GTests/BSplSLib_Cache_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BSplSLib import BSplSLib, BSplSLib_Cache
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2

TOL = 1e-10
S2 = 0.707106781186548


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


def _flat(mult):
    return _arr_f([0.0] * mult + [1.0] * mult)


# poles given as {(i, j): (x, y, z)}
NONRAT = {
    (1, 1): (0, 0, 0), (2, 1): (1, 0, 1), (3, 1): (2, 0, 0),
    (1, 2): (0, 1, 1), (2, 2): (1, 1, 2), (3, 2): (2, 1, 1),
    (1, 3): (0, 2, 0), (2, 3): (1, 2, 1), (3, 3): (2, 2, 0),
}
RAT = {
    (1, 1): (1, 0, 0), (2, 1): (1, 1, 0), (3, 1): (0, 1, 0),
    (1, 2): (1, 0, 1), (2, 2): (1, 1, 1), (3, 2): (0, 1, 1),
    (1, 3): (0, 0, 1), (2, 3): (0, 0, 1), (3, 3): (0, 0, 1),
}
RAT_W = {
    (1, 1): 1.0, (2, 1): S2, (3, 1): 1.0,
    (1, 2): S2, (2, 2): 0.5, (3, 2): S2,
    (1, 3): 1.0, (2, 3): S2, (3, 3): 1.0,
}


def _grid(nu, nv):
    return {(i, j): ((i - 1) * 1.0, (j - 1) * 1.0, math.sin((i - 1) * 0.5) * math.cos((j - 1) * 0.5))
            for i in range(1, nu + 1) for j in range(1, nv + 1)}


def _run(pts, nu, nv, weights, order, step, comps="XYZ"):
    poles = NCollection_Array2[gp_Pnt](1, nu, 1, nv)
    for (i, j), p in pts.items():
        poles[i, j] = gp_Pnt(*p)
    w = None
    if weights is not None:
        w = NCollection_Array2[float](1, nu, 1, nv)
        for (i, j), v in weights.items():
            w[i, j] = v
    ku = _arr_f([0.0, 1.0])
    kv = _arr_f([0.0, 1.0])
    mu = _arr_i([nu, nu])
    mv = _arr_i([nv, nv])
    fu = _flat(nu)
    fv = _flat(nv)
    du, dv = nu - 1, nv - 1
    rat = weights is not None
    cache = BSplSLib_Cache(du, False, fu, dv, False, fv, w)
    cache.BuildCache(0.5, 0.5, fu, fv, poles, w)
    nvec = {0: 0, 1: 2, 2: 5}[order]
    for u in _frange(step):
        for v in _frange(step):
            if not cache.IsCacheValid(u, v):
                cache.BuildCache(u, v, fu, fv, poles, w)
            cres = [gp_Pnt()] + [gp_Vec() for _ in range(nvec)]
            dres = [gp_Pnt()] + [gp_Vec() for _ in range(nvec)]
            getattr(cache, f"D{order}")(u, v, *cres)
            getattr(BSplSLib, f"D{order}_s")(u, v, 0, 0, poles, w, ku, kv, mu, mv, du, dv,
                                             rat, rat, False, False, *dres)
            for c, d in zip(cres, dres):
                for comp in comps:
                    assert abs(getattr(c, comp)() - getattr(d, comp)()) <= TOL


def test_BSplSLib_CacheTest_D0_NonRationalSurface():
    _run(NONRAT, 3, 3, None, 0, 0.2)


def test_BSplSLib_CacheTest_D1_NonRationalSurface():
    _run(NONRAT, 3, 3, None, 1, 0.2)


def test_BSplSLib_CacheTest_D2_NonRationalSurface():
    _run(NONRAT, 3, 3, None, 2, 0.2)


def test_BSplSLib_CacheTest_D0_RationalSurface():
    _run(RAT, 3, 3, RAT_W, 0, 0.2)


def test_BSplSLib_CacheTest_D1_RationalSurface():
    _run(RAT, 3, 3, RAT_W, 1, 0.2)


def test_BSplSLib_CacheTest_D2_RationalSurface():
    _run(RAT, 3, 3, RAT_W, 2, 0.2)


def test_BSplSLib_CacheTest_D1_DifferentDegrees_UGreaterV():
    _run(_grid(4, 3), 4, 3, None, 1, 0.25, comps="X")


def test_BSplSLib_CacheTest_D1_DifferentDegrees_VGreaterU():
    _run(_grid(3, 4), 3, 4, None, 1, 0.25, comps="X")
