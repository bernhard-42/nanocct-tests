# Translated from OCCT src/ModelingData/TKG2d/GTests/Adaptor2d_Line2d_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Adaptor2d import Adaptor2d_Line2d
from nanocct.GeomAbs import GeomAbs_CN, GeomAbs_C0, GeomAbs_Line
from nanocct.gp import gp_Dir2d, gp_Lin2d, gp_Pnt2d, gp_Vec2d
from nanocct.NCollection import NCollection_Array1
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def deq(a, b):
    assert a == pytest.approx(b, rel=1e-14, abs=1e-300)


@pytest.fixture
def line():
    return Adaptor2d_Line2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0), 0.0, 10.0)


@pytest.fixture
def diag():
    return Adaptor2d_Line2d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(3.0 / 5.0, 4.0 / 5.0), -5.0, 5.0)


def test_Adaptor2d_Line2dTest_DefaultConstructor():
    assert Adaptor2d_Line2d().GetType() == GeomAbs_Line


def test_Adaptor2d_Line2dTest_ParameterBounds(line, diag):
    deq(line.FirstParameter(), 0.0)
    deq(line.LastParameter(), 10.0)
    deq(diag.FirstParameter(), -5.0)
    deq(diag.LastParameter(), 5.0)


def test_Adaptor2d_Line2dTest_Continuity(line):
    assert line.Continuity() == GeomAbs_CN


def test_Adaptor2d_Line2dTest_NbIntervals(line):
    assert line.NbIntervals(GeomAbs_C0) == 1
    assert line.NbIntervals(GeomAbs_CN) == 1


def test_Adaptor2d_Line2dTest_Intervals(line):
    arr = NCollection_Array1[float](1, 2)
    line.Intervals(arr, GeomAbs_CN)
    deq(arr[1], 0.0)
    deq(arr[2], 10.0)


def test_Adaptor2d_Line2dTest_IsNotClosed(line):
    assert line.IsClosed() is False


def test_Adaptor2d_Line2dTest_IsNotPeriodic(line):
    assert line.IsPeriodic() is False


def test_Adaptor2d_Line2dTest_GetType(line):
    assert line.GetType() == GeomAbs_Line


def test_Adaptor2d_Line2dTest_Value_AtOrigin(line):
    p = line.Value(0.0)
    assert abs(p.X()) <= TOL
    assert abs(p.Y()) <= TOL


def test_Adaptor2d_Line2dTest_Value_AtParameter(line):
    p = line.Value(5.0)
    assert abs(p.X() - 5.0) <= TOL
    assert abs(p.Y()) <= TOL


def test_Adaptor2d_Line2dTest_Value_DiagonalLine(diag):
    p0 = diag.Value(0.0)
    assert abs(p0.X() - 1.0) <= TOL
    assert abs(p0.Y() - 2.0) <= TOL
    p5 = diag.Value(5.0)
    assert abs(p5.X() - 4.0) <= TOL
    assert abs(p5.Y() - 6.0) <= TOL


def test_Adaptor2d_Line2dTest_D0(line):
    p = gp_Pnt2d()
    line.D0(3.0, p)
    assert abs(p.X() - 3.0) <= TOL
    assert abs(p.Y()) <= TOL


def test_Adaptor2d_Line2dTest_D1_FirstDerivativeIsDirection(line):
    p, v = gp_Pnt2d(), gp_Vec2d()
    line.D1(5.0, p, v)
    assert abs(p.X() - 5.0) <= TOL
    assert abs(v.X() - 1.0) <= TOL
    assert abs(v.Y()) <= TOL


def test_Adaptor2d_Line2dTest_D2_SecondDerivativeIsZero(line):
    p, v1, v2 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
    line.D2(5.0, p, v1, v2)
    assert abs(v2.Magnitude()) <= TOL


def test_Adaptor2d_Line2dTest_D3_ThirdDerivativeIsZero(line):
    p, v1, v2, v3 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d(), gp_Vec2d()
    line.D3(5.0, p, v1, v2, v3)
    assert abs(v3.Magnitude()) <= TOL


def test_Adaptor2d_Line2dTest_DN_FirstOrderMatchesD1(line):
    d = line.DN(5.0, 1)
    assert abs(d.X() - 1.0) <= TOL
    assert abs(d.Y()) <= TOL


def test_Adaptor2d_Line2dTest_DN_HigherOrderIsZero(line):
    assert abs(line.DN(5.0, 2).Magnitude()) <= TOL
    assert abs(line.DN(5.0, 3).Magnitude()) <= TOL


def test_Adaptor2d_Line2dTest_Resolution(line):
    assert abs(line.Resolution(0.001) - 0.001) <= TOL


def test_Adaptor2d_Line2dTest_LineGeometry(line):
    lin = line.Line()
    assert abs(lin.Direction().X() - 1.0) <= TOL
    assert abs(lin.Direction().Y()) <= TOL
    assert abs(lin.Location().X()) <= TOL
    assert abs(lin.Location().Y()) <= TOL


def test_Adaptor2d_Line2dTest_Load_WithLine():
    a = Adaptor2d_Line2d()
    a.Load(gp_Lin2d(gp_Pnt2d(1.0, 1.0), gp_Dir2d(0.0, 1.0)))
    p = a.Value(3.0)
    assert abs(p.X() - 1.0) <= TOL
    assert abs(p.Y() - 4.0) <= TOL


def test_Adaptor2d_Line2dTest_Load_WithBounds():
    a = Adaptor2d_Line2d()
    a.Load(gp_Lin2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 2.0, 8.0)
    deq(a.FirstParameter(), 2.0)
    deq(a.LastParameter(), 8.0)


def test_Adaptor2d_Line2dTest_Trim(line):
    t = line.Trim(2.0, 7.0, TOL)
    deq(t.FirstParameter(), 2.0)
    deq(t.LastParameter(), 7.0)
    assert abs(t.Value(2.0).X() - 2.0) <= TOL


def test_Adaptor2d_Line2dTest_ShallowCopy(line):
    c = line.ShallowCopy()
    deq(c.FirstParameter(), 0.0)
    deq(c.LastParameter(), 10.0)
    assert c.GetType() == GeomAbs_Line
    assert abs(c.Value(5.0).X() - 5.0) <= TOL
