# Translated from OCCT src/FoundationClasses/TKMath/GTests/CSLib_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.CSLib import (
    CSLib,
    CSLib_Class2d,
    CSLib_DerivativeStatus,
    CSLib_NormalPolyDef,
    CSLib_NormalStatus,
)
from nanocct.gp import gp_Dir, gp_Pnt2d, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_Array2, NCollection_Sequence

DS = CSLib_DerivativeStatus
NS = CSLib_NormalStatus


def check3(a, b, tol=1e-10):
    assert abs(a.X() - b.X()) <= tol
    assert abs(a.Y() - b.Y()) <= tol
    assert abs(a.Z() - b.Z()) <= tol


def normal_ds(d1u, d1v, tol):
    n = gp_Dir()
    status = CSLib.Normal_s__CSLib_DerivativeStatus(d1u, d1v, tol, n)
    return status, n


def square(pts):
    arr = NCollection_Array1[gp_Pnt2d](1, len(pts))
    for i, (x, y) in enumerate(pts, start=1):
        arr[i] = gp_Pnt2d(x, y)
    return arr


UNIT_SQUARE = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


def lam(values):
    arr = NCollection_Array1[float](0, len(values) - 1)
    for i, v in enumerate(values):
        arr[i] = v
    return arr


# ---- CSLib Normal ----


def test_CSLibNormalTest_Normal_FromD1U_D1V_OrthogonalVectors():
    s, n = normal_ds(gp_Vec(1.0, 0.0, 0.0), gp_Vec(0.0, 1.0, 0.0), 1e-10)
    assert s == DS.CSLib_Done
    check3(n, gp_Dir(0.0, 0.0, 1.0))


def test_CSLibNormalTest_Normal_FromD1U_D1V_ScaledVectors():
    s, n = normal_ds(gp_Vec(3.0, 0.0, 0.0), gp_Vec(0.0, 5.0, 0.0), 1e-10)
    assert s == DS.CSLib_Done
    check3(n, gp_Dir(0.0, 0.0, 1.0))


def test_CSLibNormalTest_Normal_FromD1U_D1V_ParallelVectors():
    s, _ = normal_ds(gp_Vec(1.0, 0.0, 0.0), gp_Vec(2.0, 0.0, 0.0), 1e-6)
    assert s == DS.CSLib_D1uIsParallelD1v


def test_CSLibNormalTest_Normal_FromD1U_D1V_D1UIsNull():
    s, _ = normal_ds(gp_Vec(0.0, 0.0, 0.0), gp_Vec(0.0, 1.0, 0.0), 1e-10)
    assert s == DS.CSLib_D1uIsNull


def test_CSLibNormalTest_Normal_FromD1U_D1V_D1VIsNull():
    s, _ = normal_ds(gp_Vec(1.0, 0.0, 0.0), gp_Vec(0.0, 0.0, 0.0), 1e-10)
    assert s == DS.CSLib_D1vIsNull


def test_CSLibNormalTest_Normal_FromD1U_D1V_BothNull():
    s, _ = normal_ds(gp_Vec(0.0, 0.0, 0.0), gp_Vec(0.0, 0.0, 0.0), 1e-10)
    assert s == DS.CSLib_D1IsNull


def test_CSLibNormalTest_Normal_WithMagTol_Defined():
    n = gp_Dir()
    s = CSLib.Normal_s__CSLib_NormalStatus(gp_Vec(1.0, 0.0, 0.0), gp_Vec(0.0, 1.0, 0.0), 1e-10, n)
    assert s == NS.CSLib_Defined
    check3(n, gp_Dir(0.0, 0.0, 1.0))


def test_CSLibNormalTest_Normal_WithMagTol_Singular():
    n = gp_Dir()
    s = CSLib.Normal_s__CSLib_NormalStatus(gp_Vec(1e-12, 0.0, 0.0), gp_Vec(0.0, 1e-12, 0.0), 1e-10, n)
    assert s == NS.CSLib_Singular


def test_CSLibNormalTest_DNNUV_ZeroDerivative():
    der = NCollection_Array2[gp_Vec](0, 2, 0, 2)
    der.SetValue(1, 0, gp_Vec(1.0, 0.0, 0.0))
    der.SetValue(0, 1, gp_Vec(0.0, 1.0, 0.0))
    der.SetValue(0, 0, gp_Vec(0.0, 0.0, 0.0))
    der.SetValue(1, 1, gp_Vec(0.0, 0.0, 0.0))
    der.SetValue(2, 0, gp_Vec(0.0, 0.0, 0.0))
    der.SetValue(0, 2, gp_Vec(0.0, 0.0, 0.0))
    check3(CSLib.DNNUV_s(0, 0, der), gp_Vec(0.0, 0.0, 1.0))


# ---- CSLib_Class2d ----


def test_CSLibClass2dTest_SiDans_PointInsideSquare():
    c = CSLib_Class2d(square(UNIT_SQUARE), 1e-10, 1e-10, 0.0, 0.0, 1.0, 1.0)
    assert c.SiDans(gp_Pnt2d(0.5, 0.5)) == 1


def test_CSLibClass2dTest_SiDans_PointOutsideSquare():
    c = CSLib_Class2d(square(UNIT_SQUARE), 1e-10, 1e-10, 0.0, 0.0, 1.0, 1.0)
    assert c.SiDans(gp_Pnt2d(2.0, 2.0)) == -1


def test_CSLibClass2dTest_SiDans_PointOnBoundary():
    c = CSLib_Class2d(square(UNIT_SQUARE), 0.01, 0.01, 0.0, 0.0, 1.0, 1.0)
    assert c.SiDans(gp_Pnt2d(0.5, 0.0)) == 0


def test_CSLibClass2dTest_SiDans_TriangularPolygon():
    c = CSLib_Class2d(square([(0.0, 0.0), (2.0, 0.0), (1.0, 2.0)]), 1e-10, 1e-10, 0.0, 0.0, 2.0, 2.0)
    assert c.SiDans(gp_Pnt2d(1.0, 0.5)) == 1
    assert c.SiDans(gp_Pnt2d(0.0, 1.0)) == -1


def test_CSLibClass2dTest_SequenceConstructor_PointInsideSquare():
    seq = NCollection_Sequence[gp_Pnt2d]()
    for x, y in UNIT_SQUARE:
        seq.Append(gp_Pnt2d(x, y))
    c = CSLib_Class2d(seq, 1e-10, 1e-10, 0.0, 0.0, 1.0, 1.0)
    assert c.SiDans(gp_Pnt2d(0.5, 0.5)) == 1


def test_CSLibClass2dTest_InternalSiDans_NormalizedCoordinates():
    c = CSLib_Class2d(
        square([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]), 0.1, 0.1, 0.0, 0.0, 10.0, 10.0
    )
    assert c.SiDans(gp_Pnt2d(5.0, 5.0)) == CSLib_Class2d.Result.Result_Inside
    assert c.SiDans(gp_Pnt2d(15.0, 15.0)) == CSLib_Class2d.Result.Result_Outside


def test_CSLibClass2dTest_SiDans_OnMode_PointInside():
    c = CSLib_Class2d(square(UNIT_SQUARE), 1e-10, 1e-10, 0.0, 0.0, 1.0, 1.0)
    assert c.SiDans_OnMode(gp_Pnt2d(0.5, 0.5), 0.01) == 1


def test_CSLibClass2dTest_DegeneratePolygon_InvalidBounds():
    c = CSLib_Class2d(square(UNIT_SQUARE), 1e-10, 1e-10, 1.0, 0.0, 0.0, 1.0)
    assert c.SiDans(gp_Pnt2d(0.5, 0.5)) == 0


# ---- CSLib_NormalPolyDef ----


def test_CSLibNormalPolyDefTest_Value_ConstantPolynomial():
    poly = CSLib_NormalPolyDef(0, lam([1.0]))
    ok, v = poly.Value(0.5)
    assert ok is True
    assert abs(v - 1.0) <= 1e-10
    ok, v = poly.Value(1.0)
    assert ok is True
    assert abs(v - 1.0) <= 1e-10


def test_CSLibNormalPolyDefTest_Value_LinearPolynomial():
    poly = CSLib_NormalPolyDef(1, lam([1.0, 1.0]))
    ok, v = poly.Value(math.pi / 4.0)
    assert ok is True
    assert abs(v - math.sqrt(2.0)) <= 1e-10


def test_CSLibNormalPolyDefTest_Value_AtSingularPoints():
    poly = CSLib_NormalPolyDef(2, lam([1.0, 1.0, 1.0]))
    ok, v = poly.Value(0.0)
    assert ok is True
    assert math.isfinite(v)
    ok, v = poly.Value(math.pi / 2.0)
    assert ok is True
    assert math.isfinite(v)


def test_CSLibNormalPolyDefTest_Derivative_AtRegularPoint():
    poly = CSLib_NormalPolyDef(2, lam([1.0, 0.0, 1.0]))
    ok, d = poly.Derivative(math.pi / 4.0)
    assert ok is True
    assert math.isfinite(d)


def test_CSLibNormalPolyDefTest_Derivative_AtSingularPoint():
    poly = CSLib_NormalPolyDef(2, lam([1.0, 1.0, 1.0]))
    ok, d = poly.Derivative(0.0)
    assert ok is True
    assert abs(d) <= 1e-10


def test_CSLibNormalPolyDefTest_Values_Consistency():
    poly = CSLib_NormalPolyDef(2, lam([1.0, 2.0, 1.0]))
    ok1, f1 = poly.Value(0.7)
    ok2, d1 = poly.Derivative(0.7)
    ok3, f2, d2 = poly.Values(0.7)
    assert ok1 is True and ok2 is True and ok3 is True
    assert abs(f1 - f2) <= 1e-10
    assert abs(d1 - d2) <= 1e-10


def test_CSLibNormalPolyDefTest_Derivative_NumericalApproximation():
    poly = CSLib_NormalPolyDef(2, lam([1.0, 2.0, 3.0]))
    x, h = 0.8, 1e-6
    ok1, fm = poly.Value(x - h)
    ok2, fp = poly.Value(x + h)
    ok3, d = poly.Derivative(x)
    assert ok1 is True and ok2 is True and ok3 is True
    assert abs(d - (fp - fm) / (2.0 * h)) <= 1e-4


# ---- Enumerations ----


def test_CSLibEnumTest_DerivativeStatus_AllValues():
    for other in (
        DS.CSLib_D1uIsNull,
        DS.CSLib_D1vIsNull,
        DS.CSLib_D1IsNull,
        DS.CSLib_D1uD1vRatioIsNull,
        DS.CSLib_D1vD1uRatioIsNull,
        DS.CSLib_D1uIsParallelD1v,
    ):
        assert DS.CSLib_Done != other


def test_CSLibEnumTest_NormalStatus_AllValues():
    for other in (
        NS.CSLib_Defined,
        NS.CSLib_InfinityOfSolutions,
        NS.CSLib_D1NuIsNull,
        NS.CSLib_D1NvIsNull,
        NS.CSLib_D1NIsNull,
        NS.CSLib_D1NuNvRatioIsNull,
        NS.CSLib_D1NvNuRatioIsNull,
        NS.CSLib_D1NuIsParallelD1Nv,
    ):
        assert NS.CSLib_Singular != other


# ---- Integration ----


def test_CSLibIntegrationTest_PlanarSurface_ConstantNormal():
    s, n = normal_ds(gp_Vec(1.0, 0.0, 0.0), gp_Vec(0.0, 1.0, 0.0), 1e-10)
    assert s == DS.CSLib_Done
    check3(n, gp_Dir(0.0, 0.0, 1.0))


def test_CSLibIntegrationTest_CylindricalSurface_VaryingNormal():
    s, n = normal_ds(gp_Vec(0.0, 1.0, 0.0), gp_Vec(0.0, 0.0, 1.0), 1e-10)
    assert s == DS.CSLib_Done
    check3(n, gp_Dir(1.0, 0.0, 0.0))
    s, n = normal_ds(gp_Vec(-1.0, 0.0, 0.0), gp_Vec(0.0, 0.0, 1.0), 1e-10)
    assert s == DS.CSLib_Done
    check3(n, gp_Dir(0.0, 1.0, 0.0))


def test_CSLibIntegrationTest_Class2d_ComplexPolygon():
    pts = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0), (1.0, 2.0), (0.0, 2.0)]
    c = CSLib_Class2d(square(pts), 1e-10, 1e-10, 0.0, 0.0, 2.0, 2.0)
    assert c.SiDans(gp_Pnt2d(0.5, 0.5)) == 1
    assert c.SiDans(gp_Pnt2d(1.5, 1.5)) == -1
    assert c.SiDans(gp_Pnt2d(3.0, 3.0)) == -1
