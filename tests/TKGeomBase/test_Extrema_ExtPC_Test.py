# Translated from OCCT src/ModelingData/TKGeomBase/GTests/Extrema_ExtPC_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.ElSLib import ElSLib
from nanocct.Extrema import Extrema_ExtPC
from nanocct.Geom import Geom_Circle
from nanocct.GeomAdaptor import GeomAdaptor_Curve
from nanocct.gp import gp, gp_Ax2, gp_Cylinder, gp_Dir, gp_Pnt


def test_Extrema_ExtPC_Test_Bug24945_CylinderParameterNormalization():
    p3d = gp_Pnt(-1725.97, 843.257, -4.22741e-013)
    axis = gp_Ax2(gp_Pnt(0, 843.257, 0), gp_Dir(gp.DY_s()).Reversed(), gp.DX_s())
    c3d = GeomAdaptor_Curve(Geom_Circle(axis, 1725.9708621929999))
    ext = Extrema_ExtPC(p3d, c3d)
    assert ext.IsDone()
    assert ext.NbExt() > 0
    proj = ext.Point(1).Value()
    assert abs(proj.X() + 1725.97) <= 1.0e-2
    assert abs(proj.Y() - 843.257) <= 1.0e-2
    assert abs(proj.Z()) <= 1.0e-10
    cyl = gp_Cylinder(gp_Ax2(gp_Pnt(0, 2103.87, 0), gp.DY_s().Reversed(), gp.DX_s().Reversed()), 1890.0)
    u, v = ElSLib.Parameters_s(cyl, proj)
    assert abs(u) <= 1.0e-4
    assert abs(v - 1260.613) <= 1.0e-2
