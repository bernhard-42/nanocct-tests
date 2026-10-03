# Translated from OCCT src/FoundationClasses/TKMath/GTests/PLib_HermitJacobi_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

import nanocct.GeomAbs as GeomAbs
from nanocct.NCollection import NCollection_Array1
from nanocct.PLib import PLib_HermitJacobi
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def finite(arr):
    for i in range(arr.Lower(), arr.Upper() + 1):
        assert Precision.IsInfinite_s(arr[i]) is False


def basis(herm):
    return NCollection_Array1[float](0, herm.WorkDegree())


def test_PLibHermitJacobiTest_ConstructorAndBasicProperties():
    c0 = PLib_HermitJacobi(10, GeomAbs.GeomAbs_C0)
    c1 = PLib_HermitJacobi(15, GeomAbs.GeomAbs_C1)
    c2 = PLib_HermitJacobi(20, GeomAbs.GeomAbs_C2)
    assert (c0.WorkDegree(), c1.WorkDegree(), c2.WorkDegree()) == (10, 15, 20)
    assert (c0.NivConstr(), c1.NivConstr(), c2.NivConstr()) == (0, 1, 2)


def test_PLibHermitJacobiTest_BasisFunctionD0():
    herm = PLib_HermitJacobi(6, GeomAbs.GeomAbs_C0)
    bv = basis(herm)
    for u in (-1.0, -0.5, 0.0, 0.5, 1.0):
        herm.D0(u, bv)
        finite(bv)


def test_PLibHermitJacobiTest_BasisFunctionDerivatives():
    herm = PLib_HermitJacobi(8, GeomAbs.GeomAbs_C1)
    bv, b1, b2, b3 = (basis(herm) for _ in range(4))
    u = 0.5
    herm.D1(u, bv, b1)
    herm.D2(u, bv, b1, b2)
    herm.D3(u, bv, b1, b2, b3)
    for a in (bv, b1, b2, b3):
        finite(a)


def test_PLibHermitJacobiTest_CoefficientConversion():
    herm = PLib_HermitJacobi(6, GeomAbs.GeomAbs_C0)
    dim = 1
    deg = herm.WorkDegree() - 2 * (herm.NivConstr() + 1)
    size = (deg + 1) * dim
    hj = NCollection_Array1[float](0, size - 1)
    for i in range(hj.Lower(), hj.Upper() + 1):
        hj[i] = math.sin(i * 0.3)
    co = NCollection_Array1[float](0, size - 1)
    herm.ToCoefficients(dim, deg, hj, co)
    finite(co)


# test_PLibHermitJacobiTest_DegreeReduction: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


# test_PLibHermitJacobiTest_ErrorEstimation: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


def test_PLibHermitJacobiTest_ExtremeParameterValues():
    herm = PLib_HermitJacobi(10, GeomAbs.GeomAbs_C2)
    bv = basis(herm)
    for u in (-0.99999, -1e-12, 1e-12, 0.99999):
        herm.D0(u, bv)
        finite(bv)


def test_PLibHermitJacobiTest_DerivativeConsistency():
    herm = PLib_HermitJacobi(6, GeomAbs.GeomAbs_C2)
    v1, d1_1 = basis(herm), basis(herm)
    v2, d1_2, d2_2 = basis(herm), basis(herm), basis(herm)
    u = 0.3
    herm.D1(u, v1, d1_1)
    herm.D2(u, v2, d1_2, d2_2)
    for i in range(v1.Lower(), v1.Upper() + 1):
        assert abs(v1[i] - v2[i]) <= CONF
        assert abs(d1_1[i] - d1_2[i]) <= CONF


def test_PLibHermitJacobiTest_PerformanceTest():
    herm = PLib_HermitJacobi(30, GeomAbs.GeomAbs_C2)
    bv, b1, b2, b3 = (basis(herm) for _ in range(4))
    for u in (-0.8, -0.5, 0.0, 0.5, 0.8):
        herm.D0(u, bv)
        herm.D1(u, bv, b1)
        herm.D2(u, bv, b1, b2)
        herm.D3(u, bv, b1, b2, b3)
