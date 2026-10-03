# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeUpgrade_UnifySameDomain_Test.cxx (LGPL-2.1 with the OCCT exception)
import math
from types import SimpleNamespace

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder, BRep_Tool
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.Geom import Geom_CylindricalSurface
from nanocct.Geom2d import Geom2d_Line
from nanocct.gp import gp, gp_Dir, gp_Dir2d, gp_Pln, gp_Pnt, gp_Pnt2d, gp_Vec2d
from nanocct.Precision import Precision
from nanocct.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from nanocct.TopAbs import TopAbs_FACE, TopAbs_INTERNAL
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Edge, TopoDS_Face, TopoDS_Shell, TopoDS_Vertex, TopoDS_Wire


def _make_vertex(builder, point):
    v = TopoDS_Vertex()
    builder.MakeVertex(v, point, Precision.Confusion_s())
    return v


def _make_edge(builder, surface, location, first, last, add_pcurve):
    maker = BRepBuilderAPI_MakeEdge(first, last)
    if not maker.IsDone():
        return TopoDS_Edge()
    edge = maker.Edge()
    if add_pcurve:
        p1 = BRep_Tool.Pnt_s(first)
        p2 = BRep_Tool.Pnt_s(last)
        p1_2d = gp_Pnt2d(math.atan2(p1.Y(), p1.X()), p1.Z())
        p2_2d = gp_Pnt2d(math.atan2(p2.Y(), p2.X()), p2.Z())
        direction = gp_Vec2d(p1_2d, p2_2d)
        pcurve = Geom2d_Line(p1_2d, gp_Dir2d(direction))
        builder.UpdateEdge(edge, pcurve, surface, location, Precision.Confusion_s())
        builder.Range(edge, 0.0, direction.Magnitude())
    return edge


def _make_missing_pcurve_shape(builder):
    surface = Geom_CylindricalSurface(gp.XOY_s(), 1.0)
    loc = TopLoc_Location()
    va = _make_vertex(builder, surface.Value(0.0, 0.0))
    vb = _make_vertex(builder, surface.Value(1.0, 0.0))
    vc = _make_vertex(builder, surface.Value(1.0, 1.0))
    vd = _make_vertex(builder, surface.Value(0.5, -1.0))
    ve = _make_vertex(builder, surface.Value(0.5, 1.0))

    common = _make_edge(builder, surface, loc, va, vb, True)
    e_bc = _make_edge(builder, surface, loc, vb, vc, False)
    e_cb = _make_edge(builder, surface, loc, vc, vb, True)
    e_bd = _make_edge(builder, surface, loc, vb, vd, True)
    e_da = _make_edge(builder, surface, loc, vd, va, True)
    e_ae = _make_edge(builder, surface, loc, va, ve, True)
    e_eb = _make_edge(builder, surface, loc, ve, vb, True)

    self_touching_wire = TopoDS_Wire()
    builder.MakeWire(self_touching_wire)
    for e in (common, e_bc, e_cb, e_bd, e_da):
        builder.Add(self_touching_wire, e)
    self_touching_wire.Closed(True)

    self_touching_face = TopoDS_Face()
    builder.MakeFace(self_touching_face, surface, loc, Precision.Confusion_s())
    builder.Add(self_touching_face, self_touching_wire)

    reversed_common = common.Reversed()
    second_wire = TopoDS_Wire()
    builder.MakeWire(second_wire)
    for e in (reversed_common, e_ae, e_eb):
        builder.Add(second_wire, e)
    second_wire.Closed(True)

    second_face = TopoDS_Face()
    builder.MakeFace(second_face, surface, loc, Precision.Confusion_s())
    builder.Add(second_face, second_wire)

    r = SimpleNamespace(Shell=TopoDS_Shell())
    builder.MakeShell(r.Shell)
    builder.Add(r.Shell, self_touching_face)
    builder.Add(r.Shell, second_face)
    r.ReferenceFace = self_touching_face
    r.MissingPCurveEdge = e_bc
    r.ValidPCurveEdge = e_bd
    return r


def _make_missing_pcurve_transformation_shape(builder):
    surface = Geom_CylindricalSurface(gp.XOY_s(), 1.0)
    loc = TopLoc_Location()
    va = _make_vertex(builder, surface.Value(0.0, 0.0))
    vb = _make_vertex(builder, surface.Value(0.5, 0.0))
    vc = _make_vertex(builder, surface.Value(0.5, 1.0))
    vd = _make_vertex(builder, surface.Value(0.0, 1.0))
    ve = _make_vertex(builder, surface.Value(1.0, 0.0))
    vf = _make_vertex(builder, surface.Value(1.0, 1.0))

    e_ab = _make_edge(builder, surface, loc, va, vb, True)
    e_bc = _make_edge(builder, surface, loc, vb, vc, True)
    e_cd = _make_edge(builder, surface, loc, vc, vd, True)
    e_da = _make_edge(builder, surface, loc, vd, va, True)
    e_be = _make_edge(builder, surface, loc, vb, ve, False)
    e_ef = _make_edge(builder, surface, loc, ve, vf, True)
    e_fc = _make_edge(builder, surface, loc, vf, vc, True)

    left_wire = TopoDS_Wire()
    builder.MakeWire(left_wire)
    for e in (e_ab, e_bc, e_cd, e_da):
        builder.Add(left_wire, e)
    left_wire.Closed(True)

    right_wire = TopoDS_Wire()
    builder.MakeWire(right_wire)
    for e in (e_be, e_ef, e_fc, e_bc.Reversed()):
        builder.Add(right_wire, e)
    right_wire.Closed(True)

    r = SimpleNamespace(ReferenceFace=TopoDS_Face(), Shell=TopoDS_Shell())
    builder.MakeFace(r.ReferenceFace, surface, loc, Precision.Confusion_s())
    builder.Add(r.ReferenceFace, left_wire)
    right_face = TopoDS_Face()
    builder.MakeFace(right_face, surface, loc, Precision.Confusion_s())
    builder.Add(right_face, right_wire)
    builder.MakeShell(r.Shell)
    builder.Add(r.Shell, r.ReferenceFace)
    builder.Add(r.Shell, right_face)
    r.MissingPCurveEdge = e_be
    r.ValidPCurveEdge = e_bc
    return r


def _add_planar_face_pair(builder, shell):
    loc = TopLoc_Location()
    v1 = _make_vertex(builder, gp_Pnt(3.0, 0.0, 0.0))
    v2 = _make_vertex(builder, gp_Pnt(4.0, 0.0, 0.0))
    v3 = _make_vertex(builder, gp_Pnt(4.0, 1.0, 0.0))
    v4 = _make_vertex(builder, gp_Pnt(3.0, 1.0, 0.0))
    v5 = _make_vertex(builder, gp_Pnt(5.0, 0.0, 0.0))
    v6 = _make_vertex(builder, gp_Pnt(5.0, 1.0, 0.0))

    e12 = _make_edge(builder, None, loc, v1, v2, False)
    e23 = _make_edge(builder, None, loc, v2, v3, False)
    e34 = _make_edge(builder, None, loc, v3, v4, False)
    e41 = _make_edge(builder, None, loc, v4, v1, False)
    e25 = _make_edge(builder, None, loc, v2, v5, False)
    e56 = _make_edge(builder, None, loc, v5, v6, False)
    e63 = _make_edge(builder, None, loc, v6, v3, False)
    if any(e.IsNull() for e in (e12, e23, e34, e41, e25, e56, e63)):
        return False

    left = BRepBuilderAPI_MakeWire()
    for e in (e12, e23, e34, e41):
        left.Add(e)
    if not left.IsDone():
        return False

    right = BRepBuilderAPI_MakeWire()
    for e in (TopoDS.Edge(e23.Reversed()), e25, e56, e63):
        right.Add(e)
    if not right.IsDone():
        return False

    plane = gp_Pln(gp.XOY_s())
    left_face = BRepBuilderAPI_MakeFace(plane, left.Wire())
    right_face = BRepBuilderAPI_MakeFace(plane, right.Wire())
    if not left_face.IsDone() or not right_face.IsDone():
        return False
    builder.Add(shell, left_face.Face())
    builder.Add(shell, right_face.Face())
    return True


def _count_faces(shape):
    n = 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        n += 1
        exp.Next()
    return n


def _rect_wire(pts):
    mw = BRepBuilderAPI_MakeWire()
    for a, b in zip(pts, pts[1:] + pts[:1]):
        mw.Add(BRepBuilderAPI_MakeEdge(a, b).Edge())
    return mw


def test_ShapeUpgrade_UnifySameDomainTest_InternalEdgesTermination_Issue925():
    builder = BRep_Builder()
    mw = _rect_wire([gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0), gp_Pnt(10, 10, 0), gp_Pnt(0, 10, 0)])
    assert mw.IsDone(), "Failed to create outer wire"

    mf = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), mw.Wire())
    assert mf.IsDone(), "Failed to create face"
    face = mf.Face()

    mie1 = BRepBuilderAPI_MakeEdge(gp_Pnt(2, 2, 0), gp_Pnt(5, 5, 0))
    mie2 = BRepBuilderAPI_MakeEdge(gp_Pnt(5, 5, 0), gp_Pnt(8, 2, 0))
    assert mie1.IsDone()
    assert mie2.IsDone()

    miw = BRepBuilderAPI_MakeWire()
    miw.Add(mie1.Edge())
    miw.Add(mie2.Edge())
    assert miw.IsDone()
    internal_wire = miw.Wire()
    internal_wire.Orientation(TopAbs_INTERNAL)
    builder.Add(face, internal_wire)

    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    builder.Add(shell, face)

    unifier = ShapeUpgrade_UnifySameDomain(shell)
    unifier.SetAngularTolerance(1e-6)
    unifier.SetLinearTolerance(1e-5)
    unifier.AllowInternalEdges(True)
    unifier.Build()

    result = unifier.Shape()
    assert not result.IsNull()
    assert _count_faces(result) >= 1


def test_ShapeUpgrade_UnifySameDomainTest_MultipleCoplanarFacesWithInternalWires():
    builder = BRep_Builder()
    plane = gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))

    mw1 = _rect_wire([gp_Pnt(0, 0, 0), gp_Pnt(5, 0, 0), gp_Pnt(5, 10, 0), gp_Pnt(0, 10, 0)])
    assert mw1.IsDone()
    mf1 = BRepBuilderAPI_MakeFace(plane, mw1.Wire())
    assert mf1.IsDone()
    face1 = mf1.Face()

    mw2 = _rect_wire([gp_Pnt(5, 0, 0), gp_Pnt(10, 0, 0), gp_Pnt(10, 10, 0), gp_Pnt(5, 10, 0)])
    assert mw2.IsDone()
    mf2 = BRepBuilderAPI_MakeFace(plane, mw2.Wire())
    assert mf2.IsDone()
    face2 = mf2.Face()

    miw1 = BRepBuilderAPI_MakeWire()
    miw1.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(1, 5, 0), gp_Pnt(4, 5, 0)).Edge())
    assert miw1.IsDone()
    iw1 = miw1.Wire()
    iw1.Orientation(TopAbs_INTERNAL)
    builder.Add(face1, iw1)

    miw2 = BRepBuilderAPI_MakeWire()
    miw2.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(6, 5, 0), gp_Pnt(9, 5, 0)).Edge())
    assert miw2.IsDone()
    iw2 = miw2.Wire()
    iw2.Orientation(TopAbs_INTERNAL)
    builder.Add(face2, iw2)

    sewer = BRepBuilderAPI_Sewing(1e-6)
    sewer.Add(face1)
    sewer.Add(face2)
    sewer.Perform()
    sewed = sewer.SewedShape()
    assert not sewed.IsNull(), "Sewing failed"

    unifier = ShapeUpgrade_UnifySameDomain(sewed)
    unifier.SetAngularTolerance(1e-6)
    unifier.SetLinearTolerance(1e-5)
    unifier.AllowInternalEdges(True)
    unifier.Build()

    result = unifier.Shape()
    assert not result.IsNull()
    assert _count_faces(result) == 1, "Coplanar faces should be merged into one"


def test_ShapeUpgrade_UnifySameDomainTest_ClosedInternalWire():
    builder = BRep_Builder()
    mw = _rect_wire([gp_Pnt(0, 0, 0), gp_Pnt(20, 0, 0), gp_Pnt(20, 20, 0), gp_Pnt(0, 20, 0)])
    assert mw.IsDone()
    mf = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), mw.Wire())
    assert mf.IsDone()
    face = mf.Face()

    miw = _rect_wire([gp_Pnt(5, 5, 0), gp_Pnt(15, 5, 0), gp_Pnt(10, 15, 0)])
    assert miw.IsDone()
    internal_wire = miw.Wire()
    internal_wire.Orientation(TopAbs_INTERNAL)
    builder.Add(face, internal_wire)

    shell = TopoDS_Shell()
    builder.MakeShell(shell)
    builder.Add(shell, face)

    unifier = ShapeUpgrade_UnifySameDomain(shell)
    unifier.SetAngularTolerance(1e-6)
    unifier.SetLinearTolerance(1e-5)
    unifier.AllowInternalEdges(True)
    unifier.Build()

    assert not unifier.Shape().IsNull()


def test_ShapeUpgrade_UnifySameDomainTest_BasicBoxUnification():
    box_maker = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), gp_Pnt(10, 10, 10))
    box_maker.Build()
    assert box_maker.IsDone()
    box = box_maker.Shape()

    unifier = ShapeUpgrade_UnifySameDomain(box)
    unifier.Build()

    result = unifier.Shape()
    assert not result.IsNull()
    assert _count_faces(result) == 6, "Box should have 6 faces"


def test_ShapeUpgrade_UnifySameDomainTest_MissingPCurveDoesNotAbortShellProcessing():
    builder = BRep_Builder()
    shape = _make_missing_pcurve_shape(builder)
    assert not shape.Shell.IsNull()
    assert _add_planar_face_pair(builder, shape.Shell)

    assert BRep_Tool.CurveOnSurface_s(shape.MissingPCurveEdge, shape.ReferenceFace)[0] is None
    assert BRep_Tool.CurveOnSurface_s(shape.ValidPCurveEdge, shape.ReferenceFace)[0] is not None

    unifier = ShapeUpgrade_UnifySameDomain(shape.Shell, False, True, False)
    unifier.AllowInternalEdges(True)
    unifier.Build()

    result = unifier.Shape()
    assert not result.IsNull()
    assert _count_faces(result) == 3


def test_ShapeUpgrade_UnifySameDomainTest_MissingSourcePCurveDuringTransformation():
    builder = BRep_Builder()
    shape = _make_missing_pcurve_transformation_shape(builder)
    assert not shape.Shell.IsNull()

    assert BRep_Tool.CurveOnSurface_s(shape.MissingPCurveEdge, shape.ReferenceFace)[0] is None

    unifier = ShapeUpgrade_UnifySameDomain(shape.Shell, False, True, False)
    unifier.AllowInternalEdges(True)
    unifier.Build()

    result = unifier.Shape()
    assert not result.IsNull()
    assert _count_faces(result) == 2
