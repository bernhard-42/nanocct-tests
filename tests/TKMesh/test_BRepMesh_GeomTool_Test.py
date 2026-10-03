# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_GeomTool_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from nanocct.BRepMesh import BRepMesh_GeomTool
from nanocct.Geom import Geom_Circle, Geom_TrimmedCurve
from nanocct.gp import gp, gp_Ax2, gp_Dir, gp_Pln, gp_Pnt, gp_Pnt2d, gp_XY
from nanocct.Precision import Precision


def test_BRepMesh_GeomTool_Test_OCC25547_StaticMethodsExportAndFunctionality():
    first_p, last_p = 0.0, math.pi
    circle = Geom_Circle(gp_Ax2(gp.Origin_s(), gp.DZ_s()), 10)
    half = Geom_TrimmedCurve(circle, first_p, last_p)
    edge = BRepBuilderAPI_MakeEdge(half).Edge()
    adaptor = BRepAdaptor_Curve(edge)
    geom_tool = BRepMesh_GeomTool(adaptor, first_p, last_p, 0.1, 0.5)
    assert geom_tool.NbPoints() > 0

    face = BRepBuilderAPI_MakeFace(gp_Pln(gp.Origin_s(), gp.DZ_s())).Face()
    hsurf = BRepAdaptor_Surface(face)
    pnt = gp_Pnt()
    normal = gp_Dir()
    assert BRepMesh_GeomTool.Normal_s(hsurf, 10.0, 10.0, pnt, normal) is True

    ref = [gp_XY(-10.0, -10.0), gp_XY(10.0, 10.0), gp_XY(-10.0, 10.0), gp_XY(10.0, -10.0)]
    int_pnt = gp_Pnt2d()
    flag, _params = BRepMesh_GeomTool.IntLinLin_s(ref[0], ref[1], ref[2], ref[3], int_pnt.ChangeCoord())
    assert flag == BRepMesh_GeomTool.IntFlag.Cross
    assert int_pnt.Distance(gp.Origin2d_s()) <= Precision.PConfusion_s()

    int_pnt = gp_Pnt2d(5.0, 5.0)
    flag = BRepMesh_GeomTool.IntSegSeg_s(ref[0], ref[1], ref[2], ref[3], False, False, int_pnt)
    assert flag == BRepMesh_GeomTool.IntFlag.Cross
    assert int_pnt.Distance(gp.Origin2d_s()) <= Precision.PConfusion_s()
