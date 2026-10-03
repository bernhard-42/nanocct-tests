# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixGeom_HelixCurve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_BSplineCurve
from nanocct.GeomAbs import GeomAbs_C0, GeomAbs_C1, GeomAbs_C2, GeomAbs_CN
from nanocct.gp import gp_Pnt, gp_Vec
from nanocct.HelixGeom import HelixGeom_BuilderHelixCoil, HelixGeom_HelixCurve, HelixGeom_Tools
from nanocct.NCollection import NCollection_Array1
from nanocct.Standard import Standard_ConstructionError, Standard_DomainError, Standard_NotImplemented

TOL = 1.0e-6


def test_HelixGeomTest_HelixCurve_Derivatives():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 2.0 * math.pi, 5.0, 2.0, 0.0, True)
    param = math.pi / 2.0
    p = gp_Pnt()
    v1 = gp_Vec()
    v2 = gp_Vec()

    helix.D1(param, p, v1)
    assert abs(p.X() - 0.0) <= 1e-15
    assert abs(p.Y() - 2.0) <= 1e-15
    assert v1.Magnitude() > 0.0

    helix.D2(param, p, v1, v2)
    assert abs(p.X() - 0.0) <= 1e-15
    assert abs(p.Y() - 2.0) <= 1e-15
    assert v2.Magnitude() > 0.0

    vn1 = helix.DN(param, 1)
    vn2 = helix.DN(param, 2)
    assert abs(vn1.X() - v1.X()) <= 1e-15
    assert abs(vn1.Y() - v1.Y()) <= 1e-15
    assert abs(vn1.Z() - v1.Z()) <= 1e-15
    assert abs(vn2.X() - v2.X()) <= 1e-15
    assert abs(vn2.Y() - v2.Y()) <= 1e-15
    assert abs(vn2.Z() - v2.Z()) <= 1e-15


def test_HelixGeomTest_HelixCurve_ErrorConditions():
    helix = HelixGeom_HelixCurve()
    with pytest.raises(Standard_ConstructionError):
        helix.Load(2.0, 1.0, 5.0, 2.0, 0.0, True)
    with pytest.raises(Standard_ConstructionError):
        helix.Load(0.0, 2.0 * math.pi, -1.0, 2.0, 0.0, True)
    with pytest.raises(Standard_ConstructionError):
        helix.Load(0.0, 2.0 * math.pi, 5.0, -1.0, 0.0, True)
    with pytest.raises(Standard_ConstructionError):
        helix.Load(0.0, 2.0 * math.pi, 5.0, 2.0, math.pi / 2.0, True)


def test_HelixGeomTest_HelixCurve_CounterClockwise():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 2.0 * math.pi, 5.0, 2.0, 0.0, False)
    p0 = helix.Value(0.0)
    p1 = helix.Value(math.pi / 2.0)
    assert abs(p0.X() - 2.0) <= 1e-15
    assert abs(p0.Y() - 0.0) <= 1e-15
    assert abs(p1.X() - 0.0) <= 1e-15
    assert abs(p1.Y() - -2.0) <= 1e-15


def test_HelixGeomTest_HelixCurve_AdaptorInterface():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 4.0 * math.pi, 10.0, 3.0, 0.0, True)
    assert helix.Continuity() == GeomAbs_CN
    assert helix.NbIntervals(GeomAbs_C0) == 1
    assert helix.NbIntervals(GeomAbs_C1) == 1
    assert helix.NbIntervals(GeomAbs_C2) == 1

    intervals = NCollection_Array1[float](1, 2)
    helix.Intervals(intervals, GeomAbs_C0)
    assert intervals[1] == pytest.approx(0.0)
    assert intervals[2] == pytest.approx(4.0 * math.pi)

    with pytest.raises(Standard_NotImplemented):
        helix.Resolution(1.0)
    with pytest.raises(Standard_NotImplemented):
        helix.IsClosed()
    with pytest.raises(Standard_NotImplemented):
        helix.IsPeriodic()
    with pytest.raises(Standard_DomainError):
        helix.Period()


def test_HelixGeomTest_BuilderHelixCoil_Approximation():
    b = HelixGeom_BuilderHelixCoil()
    b.SetTolerance(TOL)
    b.SetApproxParameters(GeomAbs_C2, 8, 100)
    b.SetCurveParameters(0.0, 2.0 * math.pi, 20.0, 5.0, 0.05, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.ToleranceReached() <= 0.1
    curves = b.Curves()
    assert curves.Length() == 1
    curve = curves[1]
    assert isinstance(curve, Geom_BSplineCurve)
    assert curve.Degree() <= 8
    assert curve.NbPoles() > 0


def test_HelixGeomTest_Tools_ApprCurve3D():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 2.0 * math.pi, 10.0, 3.0, 0.0, True)
    h_adaptor = HelixGeom_HelixCurve(helix)
    result, bspl, max_err = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C1, 50, 6)
    assert result == 0
    assert bspl is not None
    assert max_err <= TOL * 10
    n = 10
    for i in range(n + 1):
        param = helix.FirstParameter() + i * (helix.LastParameter() - helix.FirstParameter()) / n
        orig = helix.Value(param)
        bparam = bspl.FirstParameter() + i * (bspl.LastParameter() - bspl.FirstParameter()) / n
        approx = gp_Pnt()
        bspl.D0(bparam, approx)
        assert orig.Distance(approx) <= max_err * 2


def test_HelixGeomTest_Tools_DifferentContinuity():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 6.0 * math.pi, 15.0, 4.0, 0.05, True)
    h_adaptor = HelixGeom_HelixCurve(helix)
    res_c0, bspl_c0, _ = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C0, 30, 4)
    assert res_c0 == 0
    assert bspl_c0 is not None
    res_c2, bspl_c2, _ = HelixGeom_Tools.ApprCurve3D_s(h_adaptor, TOL, GeomAbs_C2, 30, 6)
    assert res_c2 == 0
    assert bspl_c2 is not None
    assert bspl_c2.Degree() >= bspl_c0.Degree()


def test_HelixGeomTest_BuilderHelixCoil_DefaultParameters():
    b = HelixGeom_BuilderHelixCoil()
    b.Perform()
    assert b.ErrorStatus() == 0
    cont, max_degree, max_seg = b.ApproxParameters()
    assert cont == GeomAbs_C2
    assert max_degree == 8
    assert max_seg == 150
    assert b.Tolerance() == 0.0001


def test_HelixGeomTest_BuilderHelixCoil_ParameterSymmetry():
    b = HelixGeom_BuilderHelixCoil()
    params = (0.5, 5.5, 12.5, 3.5, 0.15, False)
    b.SetCurveParameters(*params)
    assert b.CurveParameters() == params
