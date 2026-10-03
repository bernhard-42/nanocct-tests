# Translated from OCCT src/ModelingData/TKG3d/GTests/GeomAdaptor_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom import Geom_Circle, Geom_Line, Geom_TrimmedCurve
from nanocct.GeomAbs import GeomAbs_Circle
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp_Ax2, gp_Circ, gp_Dir, gp_Lin, gp_Pnt
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NullObject

TOL = Precision.Confusion_s()


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def line():
    return Geom_Line(gp_Lin(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(1.0, 1.0, 0.0)))


@pytest.fixture
def circle():
    return Geom_Circle(gp_Circ(gp_Ax2(gp_Pnt(5.0, 5.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 3.0))


def test_GeomAdaptor_Curve_Test_Load_ValidParameters_Success(line):
    a = GeomAdaptor_Curve()
    a.Load(line, 0.0, 10.0)
    deq(a.FirstParameter(), 0.0)
    deq(a.LastParameter(), 10.0)


def test_GeomAdaptor_Curve_Test_Load_EqualParameters_Success(line):
    a = GeomAdaptor_Curve()
    a.Load(line, 5.0, 5.0)
    deq(a.FirstParameter(), 5.0)
    deq(a.LastParameter(), 5.0)
    assert a.Value(5.0).IsEqual(line.Value(5.0), TOL)


def test_GeomAdaptor_Curve_Test_Load_ParametersWithinConfusion_Success(line):
    p1, p2 = 5.0, 5.0 + TOL * 0.5
    a = GeomAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_GeomAdaptor_Curve_Test_Load_ParametersAtConfusionBoundary_Success(line):
    p1, p2 = 5.0, 5.0 + TOL
    a = GeomAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_GeomAdaptor_Curve_Test_Load_FirstGreaterThanLastWithinConfusion_Success(line):
    p1, p2 = 5.0 + TOL * 0.5, 5.0
    a = GeomAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_GeomAdaptor_Curve_Test_Load_FirstGreaterThanLastBeyondConfusion_ThrowsException(line):
    a = GeomAdaptor_Curve()
    with pytest.raises(Standard_ConstructionError):
        a.Load(line, 10.0, 5.0)


def test_GeomAdaptor_Curve_Test_Load_FirstSlightlyGreaterThanLast_ThrowsException(line):
    a = GeomAdaptor_Curve()
    with pytest.raises(Standard_ConstructionError):
        a.Load(line, 5.0, 5.0 - TOL * 2.0)


def test_GeomAdaptor_Curve_Test_Constructor_DegeneratedCurve_Success(circle):
    a = GeomAdaptor_Curve(circle, 0.0, 0.0)
    deq(a.FirstParameter(), 0.0)
    deq(a.LastParameter(), 0.0)


def test_GeomAdaptor_Curve_Test_Constructor_InvalidParameters_ThrowsException(circle):
    with pytest.raises(Standard_ConstructionError):
        GeomAdaptor_Curve(circle, 10.0, 0.0)


def test_GeomAdaptor_Curve_Test_Load_NullCurve_ThrowsException():
    a = GeomAdaptor_Curve()
    with pytest.raises(Standard_NullObject):
        a.Load(None, 0.0, 10.0)


def test_GeomAdaptor_Curve_Test_DegeneratedCurve_CircleAtZeroLength_Success(circle):
    param = math.pi
    a = GeomAdaptor_Curve()
    a.Load(circle, param, param)
    assert a.Value(param).IsEqual(circle.Value(param), TOL)
    assert a.IsClosed() or a.FirstParameter() == a.LastParameter()


def test_GeomAdaptor_Curve_Test_DegeneratedCurve_TrimmedCurve_Success(line):
    trimmed = Geom_TrimmedCurve(line, 0.0, 20.0)
    param = 10.0
    a = GeomAdaptor_Curve()
    a.Load(trimmed, param, param)
    deq(a.FirstParameter(), param)
    deq(a.LastParameter(), param)


def test_GeomAdaptor_Curve_Test_ToleranceBoundary_NegativeCase_ThrowsException(line):
    a = GeomAdaptor_Curve()
    with pytest.raises(Standard_ConstructionError):
        a.Load(line, 5.0, 5.0 - TOL - 1e-10)


def test_GeomAdaptor_Curve_Test_LoadWithoutParameters_Success(circle):
    a = GeomAdaptor_Curve()
    a.Load(circle)
    assert abs(a.FirstParameter() - circle.FirstParameter()) <= TOL
    assert abs(a.LastParameter() - circle.LastParameter()) <= TOL
    assert a.IsPeriodic()


def test_GeomAdaptor_Curve_Test_DegeneratedCurve_MultipleLocations_Success(line):
    for param in (0.0, 1.0, -5.0, 100.0, math.pi):
        a = GeomAdaptor_Curve()
        a.Load(line, param, param)
        assert a.Value(param).IsEqual(line.Value(param), TOL)


def test_GeomAdaptor_Curve_Test_BoundaryConditions_VerySmallInterval_Success(line):
    p1, p2 = 5.0, 5.0 + TOL + 1e-12
    a = GeomAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_GeomAdaptor_Curve_Test_Constructor_WithValidRange_Success(circle):
    first, last = 0.0, 2.0 * math.pi
    a = GeomAdaptor_Curve(circle, first, last)
    deq(a.FirstParameter(), first)
    deq(a.LastParameter(), last)
    assert a.GetType() == GeomAbs_Circle
