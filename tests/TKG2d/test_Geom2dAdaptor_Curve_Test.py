# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2dAdaptor_Curve_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Geom2d import Geom2d_Circle, Geom2d_Line, Geom2d_TrimmedCurve
from nanocct.Geom2dAdaptor import Geom2dAdaptor_Curve
from nanocct.gp import gp_Ax2d, gp_Circ2d, gp_Dir2d, gp_Lin2d, gp_Pnt2d
from nanocct.Precision import Precision
from nanocct.Standard import Standard_ConstructionError, Standard_NullObject

TOL = Precision.Confusion_s()


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def line():
    return Geom2d_Line(gp_Lin2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 1.0)))


@pytest.fixture
def circle():
    return Geom2d_Circle(gp_Circ2d(gp_Ax2d(gp_Pnt2d(5.0, 5.0), gp_Dir2d(1.0, 0.0)), 3.0))


def test_Geom2dAdaptor_Curve_Test_Load_ValidParameters_Success(line):
    a = Geom2dAdaptor_Curve()
    a.Load(line, 0.0, 10.0)
    deq(a.FirstParameter(), 0.0)
    deq(a.LastParameter(), 10.0)


def test_Geom2dAdaptor_Curve_Test_Load_EqualParameters_Success(line):
    a = Geom2dAdaptor_Curve()
    a.Load(line, 5.0, 5.0)
    deq(a.FirstParameter(), 5.0)
    deq(a.LastParameter(), 5.0)
    assert a.Value(5.0).IsEqual(line.Value(5.0), TOL)


def test_Geom2dAdaptor_Curve_Test_Load_ParametersWithinConfusion_Success(line):
    p1, p2 = 5.0, 5.0 + TOL * 0.5
    a = Geom2dAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_Geom2dAdaptor_Curve_Test_Load_ParametersAtConfusionBoundary_Success(line):
    p1, p2 = 5.0, 5.0 + TOL
    a = Geom2dAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_Geom2dAdaptor_Curve_Test_Load_FirstGreaterThanLastWithinConfusion_Success(line):
    p1, p2 = 5.0 + TOL * 0.5, 5.0
    a = Geom2dAdaptor_Curve()
    a.Load(line, p1, p2)
    deq(a.FirstParameter(), p1)
    deq(a.LastParameter(), p2)


def test_Geom2dAdaptor_Curve_Test_Load_FirstGreaterThanLastBeyondConfusion_ThrowsException(line):
    with pytest.raises(Standard_ConstructionError):
        Geom2dAdaptor_Curve().Load(line, 10.0, 5.0)


def test_Geom2dAdaptor_Curve_Test_Load_FirstSlightlyGreaterThanLast_ThrowsException(line):
    with pytest.raises(Standard_ConstructionError):
        Geom2dAdaptor_Curve().Load(line, 5.0, 5.0 - TOL * 2.0)


def test_Geom2dAdaptor_Curve_Test_Constructor_DegeneratedCurve_Success(circle):
    a = Geom2dAdaptor_Curve(circle, 0.0, 0.0)
    deq(a.FirstParameter(), 0.0)
    deq(a.LastParameter(), 0.0)


def test_Geom2dAdaptor_Curve_Test_Constructor_InvalidParameters_ThrowsException(circle):
    with pytest.raises(Standard_ConstructionError):
        Geom2dAdaptor_Curve(circle, 10.0, 0.0)


def test_Geom2dAdaptor_Curve_Test_Load_NullCurve_ThrowsException():
    with pytest.raises(Standard_NullObject):
        Geom2dAdaptor_Curve().Load(None, 0.0, 10.0)


def test_Geom2dAdaptor_Curve_Test_DegeneratedCurve_CircleAtZeroLength_Success(circle):
    a = Geom2dAdaptor_Curve()
    a.Load(circle, math.pi, math.pi)
    assert a.Value(math.pi).IsEqual(circle.Value(math.pi), TOL)
    assert a.IsClosed() or a.FirstParameter() == a.LastParameter()


def test_Geom2dAdaptor_Curve_Test_DegeneratedCurve_TrimmedCurve_Success(line):
    t = Geom2d_TrimmedCurve(line, 0.0, 20.0)
    a = Geom2dAdaptor_Curve()
    a.Load(t, 10.0, 10.0)
    deq(a.FirstParameter(), 10.0)
    deq(a.LastParameter(), 10.0)


def test_Geom2dAdaptor_Curve_Test_ToleranceBoundary_NegativeCase_ThrowsException(line):
    with pytest.raises(Standard_ConstructionError):
        Geom2dAdaptor_Curve().Load(line, 5.0, 5.0 - TOL - 1e-10)


def test_Geom2dAdaptor_Curve_Test_LoadWithoutParameters_Success(circle):
    a = Geom2dAdaptor_Curve()
    a.Load(circle)
    assert abs(a.FirstParameter() - circle.FirstParameter()) <= TOL
    assert abs(a.LastParameter() - circle.LastParameter()) <= TOL
    assert a.IsPeriodic() is True
