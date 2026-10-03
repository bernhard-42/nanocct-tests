# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepBuilderAPI_MakeFace_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.Geom import Geom_CylindricalSurface, Geom_Plane
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision


def _area(face):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face, props)
    return props.Mass()


def test_BRepBuilderAPI_MakeFaceTest_FaceFromPlane():
    mk = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)))
    assert mk.IsDone()
    assert not mk.Face().IsNull()


def test_BRepBuilderAPI_MakeFaceTest_FaceFromWire():
    p1, p2, p3, p4 = gp_Pnt(0.0, 0.0, 0.0), gp_Pnt(10.0, 0.0, 0.0), gp_Pnt(10.0, 5.0, 0.0), gp_Pnt(0.0, 5.0, 0.0)
    mk_wire = BRepBuilderAPI_MakeWire()
    for a, b in ((p1, p2), (p2, p3), (p3, p4), (p4, p1)):
        mk_wire.Add(BRepBuilderAPI_MakeEdge(a, b).Edge())
    assert mk_wire.IsDone()
    mk = BRepBuilderAPI_MakeFace(mk_wire.Wire())
    assert mk.IsDone()
    face = mk.Face()
    assert not face.IsNull()
    assert BRepCheck_Analyzer(face).IsValid()
    assert abs(_area(face) - 50.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeFaceTest_FaceFromGeomPlane_WithBounds():
    plane = Geom_Plane(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0))
    mk = BRepBuilderAPI_MakeFace(plane, 0.0, 10.0, 0.0, 5.0, Precision.Confusion_s())
    assert mk.IsDone()
    face = mk.Face()
    assert not face.IsNull()
    assert BRepCheck_Analyzer(face).IsValid()
    assert abs(_area(face) - 50.0) <= Precision.Confusion_s()


def test_BRepBuilderAPI_MakeFaceTest_FaceFromCylindricalSurface():
    surf = Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 5.0)
    mk = BRepBuilderAPI_MakeFace(surf, 0.0, 2.0 * math.pi, 0.0, 10.0, Precision.Confusion_s())
    assert mk.IsDone()
    face = mk.Face()
    assert not face.IsNull()
    assert BRepCheck_Analyzer(face).IsValid()
    assert abs(_area(face) - 2.0 * math.pi * 5.0 * 10.0) <= 0.01
