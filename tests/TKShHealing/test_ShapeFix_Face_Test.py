# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeFix_Face_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepLib import BRepLib_MakeWire
from nanocct.Geom import Geom_ConicalSurface
from nanocct.GeomAPI import GeomAPI_Interpolate
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pln, gp_Pnt
from nanocct.NCollection import NCollection_HArray1
from nanocct.ShapeBuild import ShapeBuild_ReShape
from nanocct.ShapeExtend import ShapeExtend_OK
from nanocct.ShapeFix import ShapeFix_Face
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Face


def _make_planar_face():
    maker = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0)), 0.0, 1.0, 0.0, 1.0)
    if not maker.IsDone():
        return TopoDS_Face()
    return maker.Face()


def _make_face_on_periodic_conical_single_wire():
    axis = gp_Ax3(gp_Pnt(0.0, 4.0, -9.1), gp_Dir(0.0, 0.09, -1.0))
    cone = Geom_ConicalSurface(axis, 0.35, 0.0)

    n = 8
    v = 0.5
    pts = NCollection_HArray1[gp_Pnt](1, n)
    for i in range(1, n + 1):
        u = 2.0 * math.pi * (i - 1) / n
        pts.SetValue(i, cone.Value(u, v))

    interp = GeomAPI_Interpolate(pts, True, 1e-6)
    interp.Perform()
    if not interp.IsDone():
        return TopoDS_Face()

    make_edge = BRepBuilderAPI_MakeEdge(interp.Curve())
    if not make_edge.IsDone():
        return TopoDS_Face()

    make_wire = BRepLib_MakeWire()
    make_wire.Add(make_edge.Edge())
    if not make_wire.IsDone() or not make_wire.Wire().Closed():
        return TopoDS_Face()

    make_face = BRepBuilderAPI_MakeFace(cone, make_wire.Wire(), True)
    if make_face.IsDone():
        return make_face.Face()
    return TopoDS_Face()


def test_ShapeFix_FaceTest_Perform_FaceReplacedByCompound_PreservesReplacement():
    face = _make_planar_face()
    assert not face.IsNull()

    builder = BRep_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)

    context = ShapeBuild_ReShape()
    context.Replace(face, compound)

    fixer = ShapeFix_Face(face)
    fixer.SetContext(context)

    assert not fixer.Perform()
    assert fixer.Status(ShapeExtend_OK)
    assert fixer.Result().IsSame(compound)


def test_ShapeFix_FaceTest_Perform_RemovedFace_PreservesNullReplacement():
    face = _make_planar_face()
    assert not face.IsNull()

    context = ShapeBuild_ReShape()
    context.Remove(face)

    fixer = ShapeFix_Face(face)
    fixer.SetContext(context)

    assert not fixer.Perform()
    assert fixer.Status(ShapeExtend_OK)
    assert fixer.Result().IsNull()


def test_ShapeFix_FaceTest_NoCrashOnPeriodicConicalSingleWire():
    face = _make_face_on_periodic_conical_single_wire()
    assert not face.IsNull()

    fixer = ShapeFix_Face(face)
    fixer.Perform()
    assert not fixer.Face().IsNull()


def test_ShapeFix_FaceTest_ValidFaceOnPeriodicConicalSingleWireWithContext():
    face = _make_face_on_periodic_conical_single_wire()
    assert not face.IsNull()

    fixer = ShapeFix_Face(face)
    fixer.SetContext(ShapeBuild_ReShape())
    fixer.Perform()

    fixed = fixer.Face()
    assert not fixed.IsNull()
    assert BRepCheck_Analyzer(fixed).IsValid()
