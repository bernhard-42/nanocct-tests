# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Line_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.GeomAbs import GeomAbs_CN
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Lin2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def line():
    return Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0))


def test_Geom2d_LineTest_ConstructFromPointAndDir(line):
    near(line.Direction().X(), 1.0)
    near(line.Direction().Y(), 0.0)
    near(line.Location().X(), 0.0)
    near(line.Location().Y(), 0.0)


def test_Geom2d_LineTest_ConstructFromLin2d():
    l = Geom2d_Line(gp_Lin2d(gp_Pnt2d(1.0, 2.0), gp_Dir2d(0.0, 1.0)))
    near(l.Direction().X(), 0.0)
    near(l.Direction().Y(), 1.0)


def test_Geom2d_LineTest_ConstructFromAxis():
    near(Geom2d_Line(gp_Ax2d(gp_Pnt2d(3.0, 4.0), gp_Dir2d(1.0, 0.0))).Location().X(), 3.0)


def test_Geom2d_LineTest_ParameterBounds(line):
    assert line.FirstParameter() < -1e90
    assert line.LastParameter() > 1e90


def test_Geom2d_LineTest_IsNotClosedNotPeriodic(line):
    assert line.IsClosed() is False
    assert line.IsPeriodic() is False


def test_Geom2d_LineTest_Continuity(line):
    assert line.Continuity() == GeomAbs_CN
    assert line.IsCN(100) is True


def test_Geom2d_LineTest_EvalD0(line):
    p = line.EvalD0(5.0)
    near(p.X(), 5.0)
    near(p.Y(), 0.0)


def test_Geom2d_LineTest_EvalD1_DirectionIsConstant(line):
    d1 = line.EvalD1(5.0).D1
    near(d1.X(), 1.0)
    near(d1.Y(), 0.0)


def test_Geom2d_LineTest_EvalD2_IsZero(line):
    near(line.EvalD2(5.0).D2.Magnitude(), 0.0)


def test_Geom2d_LineTest_EvalD3_IsZero(line):
    near(line.EvalD3(5.0).D3.Magnitude(), 0.0)


def test_Geom2d_LineTest_EvalDN_HigherOrder(line):
    near(line.EvalDN(0.0, 4).Magnitude(), 0.0)


def test_Geom2d_LineTest_Distance(line):
    near(line.Distance(gp_Pnt2d(5.0, 3.0)), 3.0)
    near(line.Distance(gp_Pnt2d(0.0, 0.0)), 0.0)


def test_Geom2d_LineTest_SetDirection(line):
    line.SetDirection(gp_Dir2d(0.0, 1.0))
    near(line.Direction().X(), 0.0)
    near(line.Direction().Y(), 1.0)


def test_Geom2d_LineTest_SetLocation(line):
    line.SetLocation(gp_Pnt2d(3.0, 4.0))
    near(line.Location().X(), 3.0)
    near(line.Location().Y(), 4.0)


def test_Geom2d_LineTest_Lin2d(line):
    l = line.Lin2d()
    near(l.Direction().X(), 1.0)
    near(l.Location().X(), 0.0)


def test_Geom2d_LineTest_Copy(line):
    c = line.Copy()
    assert isinstance(c, Geom2d_Line)
    near(c.Direction().X(), 1.0)
    c.SetDirection(gp_Dir2d(0.0, 1.0))
    near(line.Direction().X(), 1.0)


def test_Geom2d_LineTest_Transform_Translation(line):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(5.0, 10.0))
    line.Transform(t)
    near(line.Location().X(), 5.0)
    near(line.Location().Y(), 10.0)


def test_Geom2d_LineTest_Transform_Rotation(line):
    t = gp_Trsf2d()
    t.SetRotation(gp_Pnt2d(0.0, 0.0), math.pi / 2.0)
    line.Transform(t)
    near(line.Direction().X(), 0.0)
    near(abs(line.Direction().Y()), 1.0)


def test_Geom2d_LineTest_ReversedParameter(line):
    assert line.ReversedParameter(5.0) == -5.0


def test_Geom2d_LineTest_DiagonalLine_Value():
    p = Geom2d_Line(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 1.0)).EvalD0(math.sqrt(2.0))
    near(p.X(), 1.0)
    near(p.Y(), 1.0)
