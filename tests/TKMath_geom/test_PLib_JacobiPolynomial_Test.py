# Translated from OCCT src/FoundationClasses/TKMath/GTests/PLib_JacobiPolynomial_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

import nanocct.GeomAbs as GeomAbs
from nanocct.NCollection import NCollection_Array1, NCollection_Array2
from nanocct.PLib import PLib_JacobiPolynomial
from nanocct.Precision import Precision

CONF = Precision.Confusion_s()


def finite(arr):
    for i in range(arr.Lower(), arr.Upper() + 1):
        assert Precision.IsInfinite_s(arr[i]) is False


def nb_basis(jac):
    return jac.WorkDegree() - 2 * (jac.NivConstr() + 1)


def test_PLibJacobiPolynomialTest_ConstructorAndBasicProperties():
    c0 = PLib_JacobiPolynomial(10, GeomAbs.GeomAbs_C0)
    c1 = PLib_JacobiPolynomial(15, GeomAbs.GeomAbs_C1)
    c2 = PLib_JacobiPolynomial(20, GeomAbs.GeomAbs_C2)
    assert (c0.WorkDegree(), c1.WorkDegree(), c2.WorkDegree()) == (10, 15, 20)
    assert (c0.NivConstr(), c1.NivConstr(), c2.NivConstr()) == (0, 1, 2)


def test_PLibJacobiPolynomialTest_ConstructorEdgeCases():
    assert PLib_JacobiPolynomial(2, GeomAbs.GeomAbs_C0).WorkDegree() == 2
    assert PLib_JacobiPolynomial(4, GeomAbs.GeomAbs_C1).WorkDegree() == 4
    assert PLib_JacobiPolynomial(6, GeomAbs.GeomAbs_C2).WorkDegree() == 6
    assert PLib_JacobiPolynomial(30, GeomAbs.GeomAbs_C0).WorkDegree() == 30
    assert PLib_JacobiPolynomial(25, GeomAbs.GeomAbs_C0).WorkDegree() > 20


def test_PLibJacobiPolynomialTest_GaussIntegrationPoints():
    jac = PLib_JacobiPolynomial(10, GeomAbs.GeomAbs_C0)
    for nb in (8, 10, 15, 20, 25, 30, 40, 50, 61):
        if nb <= jac.WorkDegree():
            continue
        pts = NCollection_Array1[float](0, nb // 2)
        jac.Points(nb, pts)
        for i in range(pts.Lower(), pts.Upper() + 1):
            if i == 0 and nb % 2 == 0:
                assert pts[i] == -999
            elif i == 0 and nb % 2 == 1:
                assert pts[i] == 0.0
            else:
                assert pts[i] > 0.0
                assert pts[i] <= 1.0
                if i > pts.Lower() and i > 0:
                    assert pts[i] >= pts[i - 1]


def test_PLibJacobiPolynomialTest_GaussIntegrationWeights():
    jac = PLib_JacobiPolynomial(8, GeomAbs.GeomAbs_C1)
    nb = 15
    w = NCollection_Array2[float](0, nb // 2, 0, jac.WorkDegree())
    jac.Weights(nb, w)
    assert w.LowerRow() == 0
    assert w.UpperRow() == nb // 2
    assert w.LowerCol() == 0
    assert w.UpperCol() == jac.WorkDegree()
    for i in range(w.LowerRow(), w.UpperRow() + 1):
        for j in range(w.LowerCol(), w.UpperCol() + 1):
            assert Precision.IsInfinite_s(w[i, j]) is False


def test_PLibJacobiPolynomialTest_MaxValue():
    jac = PLib_JacobiPolynomial(10, GeomAbs.GeomAbs_C0)
    n = nb_basis(jac)
    assert n > 0
    tab = NCollection_Array1[float](0, n)
    jac.MaxValue(tab)
    for i in range(tab.Lower(), tab.Upper() + 1):
        assert tab[i] > 0.0
        assert Precision.IsInfinite_s(tab[i]) is False


def test_PLibJacobiPolynomialTest_BasisFunctionD0():
    jac = PLib_JacobiPolynomial(6, GeomAbs.GeomAbs_C0)
    bv = NCollection_Array1[float](0, nb_basis(jac))
    for u in (-1.0, -0.5, 0.0, 0.5, 1.0):
        jac.D0(u, bv)
        finite(bv)


def test_PLibJacobiPolynomialTest_BasisFunctionDerivatives():
    jac = PLib_JacobiPolynomial(8, GeomAbs.GeomAbs_C1)
    n = nb_basis(jac)
    bv, b1, b2, b3 = (NCollection_Array1[float](0, n) for _ in range(4))
    u = 0.5
    jac.D1(u, bv, b1)
    jac.D2(u, bv, b1, b2)
    jac.D3(u, bv, b1, b2, b3)
    for a in (bv, b1, b2, b3):
        finite(a)


def test_PLibJacobiPolynomialTest_CoefficientConversion():
    jac = PLib_JacobiPolynomial(6, GeomAbs.GeomAbs_C0)
    dim = 1
    deg = nb_basis(jac)
    size = (deg + 1) * dim
    jc = NCollection_Array1[float](0, size - 1)
    for i in range(jc.Lower(), jc.Upper() + 1):
        jc[i] = math.sin(i * 0.1)
    co = NCollection_Array1[float](0, size - 1)
    jac.ToCoefficients(dim, deg, jc, co)
    finite(co)


# test_PLibJacobiPolynomialTest_DegreeReduction: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


# test_PLibJacobiPolynomialTest_ErrorEstimation: not translatable -- nanocct omits the array-by-first-element overloads (Design.md 2d)


def test_PLibJacobiPolynomialTest_StressTests():
    jac = PLib_JacobiPolynomial(30, GeomAbs.GeomAbs_C2)
    bv = NCollection_Array1[float](0, nb_basis(jac))
    jac.D0(0.0, bv)
    jac.D0(0.5, bv)
    jac.D0(1.0, bv)
    for u in (-0.99999, -1e-10, 1e-10, 0.99999):
        jac.D0(u, bv)
        finite(bv)
