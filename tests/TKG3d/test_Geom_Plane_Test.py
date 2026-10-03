# Translated from OCCT src/ModelingData/TKG3d/GTests/Geom_Plane_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Geom import Geom_Line, Geom_Plane
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Precision import Precision

TOL = Precision.Confusion_s()


def _xy(origin=gp_Pnt(0.0, 0.0, 0.0)):
    return Geom_Plane(origin, gp_Dir(0.0, 0.0, 1.0))


def test_Geom_PlaneTest_ConstructFromAx3():
    plane = Geom_Plane(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    assert plane is not None
    assert plane.Location().IsEqual(gp_Pnt(0.0, 0.0, 0.0), TOL)


def test_Geom_PlaneTest_ConstructFromPointAndDir():
    plane = _xy(gp_Pnt(1.0, 2.0, 3.0))
    assert plane.Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), TOL)


def test_Geom_PlaneTest_D0Evaluation():
    plane = _xy()
    p = gp_Pnt()
    plane.D0(3.0, 4.0, p)
    assert abs(p.X() - 3.0) <= TOL and abs(p.Y() - 4.0) <= TOL and abs(p.Z()) <= TOL


def test_Geom_PlaneTest_Coefficients():
    plane = _xy(gp_Pnt(0.0, 0.0, 5.0))
    a, b, c, d = plane.Coefficients()
    assert abs(a) <= TOL and abs(b) <= TOL and abs(c - 1.0) <= TOL and abs(d + 5.0) <= TOL


def test_Geom_PlaneTest_UIso():
    iso = _xy().UIso(2.0)
    assert iso is not None
    assert isinstance(iso, Geom_Line)
    p = gp_Pnt()
    iso.D0(0.0, p)
    assert abs(p.X() - 2.0) <= TOL


def test_Geom_PlaneTest_VIso():
    iso = _xy().VIso(3.0)
    assert iso is not None
    assert isinstance(iso, Geom_Line)
    p = gp_Pnt()
    iso.D0(0.0, p)
    assert abs(p.Y() - 3.0) <= TOL


def test_Geom_PlaneTest_Transform():
    plane = _xy()
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(0.0, 0.0, 10.0))
    plane.Transform(t)
    assert abs(plane.Location().Z() - 10.0) <= TOL


def test_Geom_PlaneTest_Copy():
    plane = _xy(gp_Pnt(1.0, 2.0, 3.0))
    cp = plane.Copy()
    assert cp is not None
    assert isinstance(cp, Geom_Plane)
    assert cp.Location().IsEqual(gp_Pnt(1.0, 2.0, 3.0), TOL)
