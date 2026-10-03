# Translated from OCCT src/ModelingAlgorithms/TKBool/GTests/BRepAlgoAPI_Fuse_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCone,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeRevol,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeTorus,
)
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt
from nanocct.GProp import GProp_GProps


def _check(result, area, tol):
    assert not result.IsNull()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(result, props)
    assert abs(props.Mass() - area) <= tol
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepAlgoAPI_FuseTest_CylinderAndCone_FuseThenCut():
    axis1 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.Z))
    cyl_in = BRepPrimAPI_MakeCylinder(axis1, 40, 110).Shape()
    cyl_out = BRepPrimAPI_MakeCylinder(axis1, 50, 100).Shape()
    axis2 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(gp_Dir.D.NZ))
    con_in = BRepPrimAPI_MakeCone(axis2, 40, 60, 110).Shape()
    con_out = BRepPrimAPI_MakeCone(axis2, 50, 70, 100).Shape()
    fuse_in = BRepAlgoAPI_Fuse(cyl_in, con_in)
    assert fuse_in.IsDone()
    fuse_out = BRepAlgoAPI_Fuse(cyl_out, con_out)
    assert fuse_out.IsDone()
    cut = BRepAlgoAPI_Cut(fuse_out.Shape(), fuse_in.Shape())
    assert cut.IsDone()
    _check(cut.Shape(), 133931.0, 133.931)


def test_BRepAlgoAPI_FuseTest_BoxAndSphere():
    box = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), gp_Pnt(100, 100, 100)).Shape()
    sphere = BRepPrimAPI_MakeSphere(gp_Pnt(100, 50, 50), 25.0).Shape()
    fuse = BRepAlgoAPI_Fuse(box, sphere)
    assert fuse.IsDone()
    _check(fuse.Shape(), 61963.5, 61.9635)


def test_BRepAlgoAPI_FuseTest_TwoCylinders():
    cyl1 = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(40, 50, 0), gp_Dir(100, 0, 0)), 20, 100).Shape()
    size = 0.001
    cyl2 = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(100, 50, size), gp_Dir(0, size, 80)), 20, 80).Shape()
    fuse = BRepAlgoAPI_Fuse(cyl2, cyl1)
    assert fuse.IsDone()
    _check(fuse.Shape(), 23189.5, 23.1895)


def test_BRepAlgoAPI_FuseTest_CylinderAndSphere():
    center = gp_Pnt(100, 0, 0)
    cyl = BRepPrimAPI_MakeCylinder(gp_Ax2(center, gp_Dir(gp_Dir.D.NX)), 20, 100).Shape()
    sphere = BRepPrimAPI_MakeSphere(center, 20.0).Shape()
    fuse = BRepAlgoAPI_Fuse(cyl, sphere)
    assert fuse.IsDone()
    _check(fuse.Shape(), 16336.3, 16.3363)


def test_BRepAlgoAPI_FuseTest_RevolvedFaceAndSphere():
    wire = BRepBuilderAPI_MakePolygon()
    x1, x2 = 181.82808, 202.39390
    y1, y2 = 31.011970, 123.06856
    wire.Add(gp_Pnt(x1, y1, 0))
    wire.Add(gp_Pnt(x2, y1, 0))
    wire.Add(gp_Pnt(x2, y2, 0))
    wire.Add(gp_Pnt(x1, y2, 0))
    wire.Add(gp_Pnt(x1, y1, 0))
    face = BRepBuilderAPI_MakeFace(wire.Wire(), False).Face()
    revol = BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 30, 0)), 2.0 * math.pi).Shape()
    sphere = BRepPrimAPI_MakeSphere(gp_Pnt(166.373, 77.0402, 96.0555), 23.218586).Shape()
    fuse = BRepAlgoAPI_Fuse(revol, sphere)
    assert fuse.IsDone()
    _check(fuse.Shape(), 272935.0, 272.935)


def test_BRepAlgoAPI_FuseTest_RevolvedSolidAndTwoTori():
    wire = BRepBuilderAPI_MakePolygon()
    for x, z in ((10, 0), (20, 0), (20, 50), (10, 50), (10, 0)):
        wire.Add(gp_Pnt(x, 0, z))
    face = BRepBuilderAPI_MakeFace(wire.Wire(), False).Face()
    revol = BRepPrimAPI_MakeRevol(face, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 30)), 2.0 * math.pi).Shape()
    tor1 = BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(0, 0, 50), gp_Dir(0, 0, 30)), 15.0, 5.0).Shape()
    tor2 = BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(0, 0, 10), gp_Dir(0, 0, 30)), 15.0, 5.0).Shape()
    fuse1 = BRepAlgoAPI_Fuse(tor1, revol)
    assert fuse1.IsDone()
    fuse2 = BRepAlgoAPI_Fuse(tor2, fuse1.Shape())
    assert fuse2.IsDone()
    _check(fuse2.Shape(), 11847.7, 11.8477)
