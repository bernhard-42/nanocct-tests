# Translated from OCCT src/FoundationClasses/TKMath/GTests/PLib_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

import nanocct.GeomAbs as GeomAbs
from nanocct.gp import gp_Pnt, gp_Pnt2d
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.PLib import PLib
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def arr_f(lower, values):
    a = NCollection_Array1[float](lower, lower + len(values) - 1)
    for i, v in enumerate(values, start=lower):
        a[i] = v
    return a


def test_PLibTest_NoWeightsPointers():
    assert PLib.NoWeights_s() is None
    assert PLib.NoWeights2_s() is None


def test_PLibTest_SetGetPoles3D():
    poles = NCollection_Array1[gp_Pnt](1, 3)
    poles[1] = gp_Pnt(1.0, 2.0, 3.0)
    poles[2] = gp_Pnt(4.0, 5.0, 6.0)
    poles[3] = gp_Pnt(7.0, 8.0, 9.0)
    fp = NCollection_Array1[float](1, 9)
    PLib.SetPoles_s(poles, fp)
    res = NCollection_Array1[gp_Pnt](1, 3)
    PLib.GetPoles_s(fp, res)
    for i in range(1, 4):
        assert poles[i].Distance(res[i]) <= CONF


def test_PLibTest_SetGetPoles3DWithWeights():
    poles = NCollection_Array1[gp_Pnt](1, 2)
    poles[1] = gp_Pnt(1.0, 2.0, 3.0)
    poles[2] = gp_Pnt(4.0, 5.0, 6.0)
    w = arr_f(1, [0.5, 2.0])
    fp = NCollection_Array1[float](1, 8)
    PLib.SetPoles_s(poles, w, fp)
    res = NCollection_Array1[gp_Pnt](1, 2)
    rw = NCollection_Array1[float](1, 2)
    PLib.GetPoles_s(fp, res, rw)
    for i in range(1, 3):
        for c in ("X", "Y", "Z"):
            assert abs(getattr(poles[i], c)() - getattr(res[i], c)()) <= CONF
        assert abs(w[i] - rw[i]) <= CONF


def test_PLibTest_SetGetPoles2D():
    poles = NCollection_Array1[gp_Pnt2d](1, 3)
    poles[1] = gp_Pnt2d(1.0, 2.0)
    poles[2] = gp_Pnt2d(3.0, 4.0)
    poles[3] = gp_Pnt2d(5.0, 6.0)
    fp = NCollection_Array1[float](1, 6)
    PLib.SetPoles_s(poles, fp)
    res = NCollection_Array1[gp_Pnt2d](1, 3)
    PLib.GetPoles_s(fp, res)
    for i in range(1, 4):
        assert abs(poles[i].X() - res[i].X()) <= CONF
        assert abs(poles[i].Y() - res[i].Y()) <= CONF


def test_PLibTest_SetGetPoles2DWithWeights():
    poles = NCollection_Array1[gp_Pnt2d](1, 2)
    poles[1] = gp_Pnt2d(1.0, 2.0)
    poles[2] = gp_Pnt2d(3.0, 4.0)
    w = arr_f(1, [0.8, 1.5])
    fp = NCollection_Array1[float](1, 6)
    PLib.SetPoles_s(poles, w, fp)
    res = NCollection_Array1[gp_Pnt2d](1, 2)
    rw = NCollection_Array1[float](1, 2)
    PLib.GetPoles_s(fp, res, rw)
    for i in range(1, 3):
        assert abs(poles[i].X() - res[i].X()) <= CONF
        assert abs(poles[i].Y() - res[i].Y()) <= CONF
        assert abs(w[i] - rw[i]) <= CONF


def test_PLibTest_ZeroWeightsHandling():
    poles = NCollection_Array1[gp_Pnt2d](1, 2)
    poles[1] = gp_Pnt2d(1.0, 2.0)
    poles[2] = gp_Pnt2d(3.0, 4.0)
    w = arr_f(1, [1.0, 0.0])
    fp = NCollection_Array1[float](1, 6)
    PLib.SetPoles_s(poles, w, fp)


def test_PLibTest_BinomialCoefficient_BasicValues():
    assert abs(PLib.Bin_s(0, 0) - 1.0) <= CONF
    assert abs(PLib.Bin_s(1, 0) - 1.0) <= CONF
    assert abs(PLib.Bin_s(1, 1) - 1.0) <= CONF
    for k, e in enumerate([1.0, 5.0, 10.0, 10.0, 5.0, 1.0]):
        assert abs(PLib.Bin_s(5, k) - e) <= CONF
    for k, e in enumerate([1.0, 10.0, 45.0, 120.0, 210.0, 252.0]):
        assert abs(PLib.Bin_s(10, k) - e) <= CONF


def test_PLibTest_BinomialCoefficient_Symmetry():
    for n in range(21):
        for k in range(n + 1):
            assert abs(PLib.Bin_s(n, k) - PLib.Bin_s(n, n - k)) <= CONF


def test_PLibTest_BinomialCoefficient_Recurrence():
    for n in range(2, 21):
        for k in range(1, n):
            assert abs(PLib.Bin_s(n, k) - (PLib.Bin_s(n - 1, k - 1) + PLib.Bin_s(n - 1, k))) <= CONF


def test_PLibTest_BinomialCoefficient_LargeValues():
    assert abs(PLib.Bin_s(20, 10) - 184756.0) <= CONF
    assert abs(PLib.Bin_s(15, 7) - 6435.0) <= CONF
    assert abs(PLib.Bin_s(25, 5) - 53130.0) <= CONF
    assert abs(PLib.Bin_s(25, 12) - 5200300.0) <= CONF
    assert abs(PLib.Bin_s(25, 0) - 1.0) <= CONF
    assert abs(PLib.Bin_s(25, 1) - 25.0) <= CONF
    assert abs(PLib.Bin_s(25, 25) - 1.0) <= CONF


def test_PLibTest_BinomialCoefficient_EdgeColumns():
    for n in range(26):
        assert abs(PLib.Bin_s(n, 0) - 1.0) <= CONF
        assert abs(PLib.Bin_s(n, n) - 1.0) <= CONF
    for n in range(1, 26):
        assert abs(PLib.Bin_s(n, 1) - float(n)) <= CONF


def test_PLibTest_BinomialCoefficient_CompleteRows():
    for k, e in enumerate([1.0, 6.0, 15.0, 20.0, 15.0, 6.0, 1.0]):
        assert abs(PLib.Bin_s(6, k) - e) <= CONF
    for k, e in enumerate([1.0, 8.0, 28.0, 56.0, 70.0, 56.0, 28.0, 8.0, 1.0]):
        assert abs(PLib.Bin_s(8, k) - e) <= CONF


def test_PLibTest_BinomialCoefficient_SumProperty():
    for n in range(21):
        s = sum(PLib.Bin_s(n, k) for k in range(n + 1))
        assert abs(s - 2.0**n) <= CONF


# test_PLibTest_EvalPolynomial: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


# test_PLibTest_EvalPolynomialWithDerivatives: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


def test_PLibTest_ConstraintOrderConversion():
    assert PLib.NivConstr_s(GeomAbs.GeomAbs_C0) == 0
    assert PLib.NivConstr_s(GeomAbs.GeomAbs_C1) == 1
    assert PLib.NivConstr_s(GeomAbs.GeomAbs_C2) == 2
    assert PLib.ConstraintOrder_s(0) == GeomAbs.GeomAbs_C0
    assert PLib.ConstraintOrder_s(1) == GeomAbs.GeomAbs_C1
    assert PLib.ConstraintOrder_s(2) == GeomAbs.GeomAbs_C2
    for i in range(3):
        assert PLib.NivConstr_s(PLib.ConstraintOrder_s(i)) == i


def test_PLibTest_HermiteInterpolate():
    dim, first, last, fo, lo = 1, 0.0, 1.0, 1, 1
    fc = NCollection_Array2[float](1, dim, 0, fo)
    fc[1, 0] = 0.0
    fc[1, 1] = 1.0
    lc = NCollection_Array2[float](1, dim, 0, lo)
    lc[1, 0] = 1.0
    lc[1, 1] = 0.0
    n = fo + lo + 2
    coeffs = NCollection_Array1[float](0, n - 1)
    assert PLib.HermiteInterpolate_s(dim, first, last, fo, lo, fc, lc, coeffs) is True

    # The C++ test checks the result with PLib::EvalPolynomial (not usable from Python,
    # see test_PLibTest_EvalPolynomial); evaluate the canonical polynomial here instead.
    c = [coeffs[i] for i in range(n)]

    def f(x):
        return sum(c[i] * x**i for i in range(n))

    def df(x):
        return sum(i * c[i] * x ** (i - 1) for i in range(1, n))

    assert abs(f(first) - 0.0) <= CONF
    assert abs(df(first) - 1.0) <= CONF
    assert abs(f(last) - 1.0) <= CONF
    assert abs(df(last) - 0.0) <= CONF


def test_PLibTest_JacobiParameters():
    for shape, maxdeg, code in (
        (GeomAbs.GeomAbs_C0, 10, 1),
        (GeomAbs.GeomAbs_C1, 15, 2),
        (GeomAbs.GeomAbs_C2, 20, 3),
    ):
        nb_gauss, work_degree = PLib.JacobiParameters_s(shape, maxdeg, code)
        assert nb_gauss > 0
        assert work_degree > 0
