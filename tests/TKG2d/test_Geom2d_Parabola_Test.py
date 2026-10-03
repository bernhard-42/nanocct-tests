# Translated from OCCT src/ModelingData/TKG2d/GTests/Geom2d_Parabola_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.Geom2d import Geom2d_Parabola
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Lin2d, gp_Parab2d, gp_Pnt2d, gp_Trsf2d, gp_Vec2d
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def near(a, b, t=TOL):
    assert abs(a - b) <= t, (a, b)


@pytest.fixture
def par():
    return Geom2d_Parabola(gp_Parab2d(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 4.0))


def test_Geom2d_ParabolaTest_Focal(par):
    near(par.Focal(), 4.0)


def test_Geom2d_ParabolaTest_IsNotClosedNotPeriodic(par):
    assert par.IsClosed() is False
    assert par.IsPeriodic() is False


def test_Geom2d_ParabolaTest_Eccentricity(par):
    near(par.Eccentricity(), 1.0)


def test_Geom2d_ParabolaTest_Focus(par):
    f = par.Focus()
    near(f.X(), 4.0)
    near(f.Y(), 0.0)


def test_Geom2d_ParabolaTest_Parameter(par):
    near(par.Parameter(), 8.0)


def test_Geom2d_ParabolaTest_EvalD0_AtZero(par):
    p = par.EvalD0(0.0)
    near(p.X(), 0.0)
    near(p.Y(), 0.0)


def test_Geom2d_ParabolaTest_EvalD0_Symmetric(par):
    pp, pn = par.EvalD0(3.0), par.EvalD0(-3.0)
    near(pp.X(), pn.X())
    near(pp.Y(), -pn.Y())


def test_Geom2d_ParabolaTest_EvalD1_AtZero(par):
    d1 = par.EvalD1(0.0).D1
    near(d1.X(), 0.0)
    assert d1.Magnitude() > TOL


def test_Geom2d_ParabolaTest_EvalD2_AtZero(par):
    assert par.EvalD2(0.0).D2.X() > 0.0


def test_Geom2d_ParabolaTest_PointOnParabola_FocusDirectrixProperty(par):
    focus = par.Focus()
    dline = gp_Lin2d(par.Directrix())
    u = -5.0
    while u <= 5.0:
        p = par.EvalD0(u)
        near(p.Distance(focus), dline.Distance(p), 1e-6)
        u += 1.0


def test_Geom2d_ParabolaTest_SetFocal(par):
    par.SetFocal(10.0)
    near(par.Focal(), 10.0)


def test_Geom2d_ParabolaTest_Copy(par):
    c = par.Copy()
    assert isinstance(c, Geom2d_Parabola)
    near(c.Focal(), 4.0)


def test_Geom2d_ParabolaTest_Transform_Translation(par):
    t = gp_Trsf2d()
    t.SetTranslation(gp_Vec2d(5.0, 10.0))
    par.Transform(t)
    near(par.Location().X(), 5.0)
    near(par.Location().Y(), 10.0)
