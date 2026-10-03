# Translated from OCCT src/ModelingAlgorithms/TKHelix/GTests/HelixBRep_BuilderHelix_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepGProp import BRepGProp
from nanocct.GeomAbs import GeomAbs_C1
from nanocct.gp import gp_Ax2, gp_Ax3, gp_Dir, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.HelixBRep import HelixBRep_BuilderHelix
from nanocct.HelixGeom import HelixGeom_BuilderHelix, HelixGeom_BuilderHelixCoil, HelixGeom_HelixCurve, HelixGeom_Tools
from nanocct.NCollection import NCollection_Array1
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer

TOL = 1.0e-4


def _axis():
    return gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0))


def _array(values, kind=float):
    arr = NCollection_Array1[kind](1, len(values))
    for i, v in enumerate(values, start=1):
        arr[i] = v
    return arr


def _count(shape, kind):
    n = 0
    exp = TopExp_Explorer(shape, kind)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _wire_length(shape):
    props = GProp_GProps()
    BRepGProp.LinearProperties_s(shape, props)
    return props.Mass()


def test_TKHelixTest_HelixGeomHelixCurve_Basic():
    helix = HelixGeom_HelixCurve()
    assert helix.FirstParameter() == 0.0
    assert helix.LastParameter() == 2.0 * math.pi
    p0 = helix.Value(0.0)
    assert p0.X() == 1.0
    assert p0.Y() == 0.0
    assert p0.Z() == 0.0
    p1 = helix.Value(math.pi)
    assert p1.X() == -1.0
    assert abs(p1.Y()) <= 1e-15
    assert p1.Z() == math.pi / (2.0 * math.pi)


def test_TKHelixTest_HelixGeomHelixCurve_CustomParameters():
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 4.0 * math.pi, 10.0, 5.0, 0.0, True)
    assert helix.FirstParameter() == 0.0
    assert helix.LastParameter() == 4.0 * math.pi
    p0 = helix.Value(0.0)
    assert p0.X() == 5.0
    assert p0.Y() == 0.0
    assert p0.Z() == 0.0
    p1 = helix.Value(4.0 * math.pi)
    assert p1.X() == 5.0
    assert abs(p1.Y()) <= 1e-14
    assert p1.Z() == 20.0


def test_TKHelixTest_HelixGeomHelixCurve_TaperedHelix():
    taper = 0.1
    helix = HelixGeom_HelixCurve()
    helix.Load(0.0, 2.0 * math.pi, 5.0, 2.0, taper, True)
    assert helix.Value(0.0).X() == 2.0
    expected = 2.0 + (5.0 / (2.0 * math.pi)) * math.tan(taper) * (2.0 * math.pi)
    assert helix.Value(2.0 * math.pi).X() == expected


def test_TKHelixTest_HelixGeomBuilderHelixCoil_Basic():
    b = HelixGeom_BuilderHelixCoil()
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 2.0 * math.pi, 5.0, 2.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    curves = b.Curves()
    assert curves.Length() == 1
    curve = curves[1]
    assert curve is not None
    p1 = gp_Pnt()
    p2 = gp_Pnt()
    curve.D0(curve.FirstParameter(), p1)
    curve.D0(curve.LastParameter(), p2)
    assert abs(p1.X() - 2.0) <= TOL
    assert abs(p1.Y()) <= TOL
    assert abs(p1.Z()) <= TOL
    assert abs(p2.X() - 2.0) <= TOL
    assert abs(p2.Y()) <= TOL
    assert abs(p2.Z() - 5.0) <= TOL


def test_TKHelixTest_HelixGeomBuilderHelix_SingleCoil():
    b = HelixGeom_BuilderHelix()
    b.SetPosition(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0)))
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 2.0 * math.pi, 10.0, 5.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.Curves().Length() == 1


def test_TKHelixTest_HelixGeomBuilderHelix_MultipleCoils():
    b = HelixGeom_BuilderHelix()
    b.SetPosition(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0), gp_Dir(1.0, 0.0, 0.0)))
    b.SetTolerance(TOL)
    b.SetCurveParameters(0.0, 6.0 * math.pi, 10.0, 5.0, 0.0, True)
    b.Perform()
    assert b.ErrorStatus() == 0
    assert b.Curves().Length() == 3


def test_TKHelixTest_HelixBRepBuilder_PureCylindricalHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([100.0]), _array([20.0]), _array([True], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    result = b.Shape()
    assert not result.IsNull()
    assert result.ShapeType() == TopAbs_WIRE
    assert _count(result, TopAbs_EDGE) > 0
    circ = math.pi * 100.0
    expected = (100.0 / 20.0) * math.sqrt(circ * circ + 20.0 * 20.0)
    assert abs(_wire_length(result) - expected) <= expected * 0.01


def test_TKHelixTest_HelixBRepBuilder_SpiralHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, 20.0, _array([100.0]), _array([10.0]), _array([True], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    result = b.Shape()
    assert not result.IsNull()
    assert result.ShapeType() == TopAbs_WIRE
    assert _count(result, TopAbs_EDGE) > 0


def test_TKHelixTest_HelixBRepBuilder_MultiPartHelix():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(
        _axis(),
        _array([100.0, 80.0, 60.0, 40.0]),
        _array([30.0, 40.0, 30.0]),
        _array([10.0, 15.0, 10.0]),
        _array([True, True, True], bool),
    )
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    result = b.Shape()
    assert not result.IsNull()
    assert result.ShapeType() == TopAbs_WIRE
    assert _count(result, TopAbs_EDGE) > 2


def test_TKHelixTest_HelixBRepBuilder_NumberOfTurnsInterface():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([20.0]), _array([5.0]))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() == 0
    result = b.Shape()
    assert not result.IsNull()
    circ = math.pi * 100.0
    expected = 5.0 * math.sqrt(circ * circ + 20.0 * 20.0)
    assert abs(_wire_length(result) - expected) <= expected * 0.01


def test_TKHelixTest_HelixGeomTools_ApprHelix():
    result, bspl, max_err = HelixGeom_Tools.ApprHelix_s(0.0, 2.0 * math.pi, 10.0, 5.0, 0.0, True, TOL)
    assert result == 0
    assert bspl is not None
    assert max_err <= TOL
    assert bspl.Degree() > 0
    assert bspl.NbPoles() > 0


def test_TKHelixTest_HelixBRepBuilder_ErrorConditions():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([1.0e-6]), _array([10.0]), _array([True], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() != 0


def test_TKHelixTest_HelixBRepBuilder_ZeroPitch():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([100.0]), _array([0.0]), _array([True], bool))
    b.SetApproxParameters(TOL, 8, GeomAbs_C1)
    b.Perform()
    assert b.ErrorStatus() != 0


def test_TKHelixTest_HelixBRepBuilder_ToleranceReached():
    b = HelixBRep_BuilderHelix()
    b.SetParameters(_axis(), 100.0, _array([100.0]), _array([20.0]), _array([True], bool))
    b.SetApproxParameters(1.0e-8, 8, GeomAbs_C1)
    b.Perform()
    if b.ErrorStatus() == 0:
        assert b.ToleranceReached() > 0.0
