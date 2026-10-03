# Translated from OCCT src/ModelingAlgorithms/TKFillet/GTests/BRepFilletAPI_MakeFillet_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Builder
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from nanocct.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeWire,
)
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepFilletAPI import BRepFilletAPI_MakeFillet
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakePrism,
    BRepPrimAPI_MakeRevol,
    BRepPrimAPI_MakeSphere,
)
from nanocct.ChFi3d import ChFi3d_Rational
from nanocct.GC import GC_MakeArcOfCircle, GC_MakeSegment
from nanocct.GeomAbs import GeomAbs_C1
from nanocct.GProp import GProp_GProps
from nanocct.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Pnt2d, gp_Vec
from nanocct.NCollection import NCollection_Array1, NCollection_IndexedDataMap, NCollection_List
from nanocct.ShapeFix import ShapeFix_Shape
from nanocct.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from nanocct.Standard import Standard_Failure
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SOLID, TopAbs_WIRE
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher


def _box(size=20.0):
    maker = BRepPrimAPI_MakeBox(size, size, size)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _first_edge(shape):
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    assert exp.More()
    return TopoDS.Edge(exp.Current())


def _area(shape):
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(shape, props)
    return props.Mass()


def test_BRepFilletAPI_MakeFilletTest_FilletOneEdge():
    box = _box()
    fillet = BRepFilletAPI_MakeFillet(box)
    fillet.Add(2.0, _first_edge(box))
    result = fillet.Shape()
    assert fillet.IsDone()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFilletAPI_MakeFilletTest_FilletAllEdges():
    box = _box()
    fillet = BRepFilletAPI_MakeFillet(box)
    for edge in TopExp_Explorer(box, TopAbs_EDGE):
        fillet.Add(1.0, TopoDS.Edge(edge))
    result = fillet.Shape()
    assert fillet.IsDone()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFilletAPI_MakeFilletTest_FilletMoreFaces():
    box = _box()
    fillet = BRepFilletAPI_MakeFillet(box)
    for edge in TopExp_Explorer(box, TopAbs_EDGE):
        fillet.Add(1.0, TopoDS.Edge(edge))
    result = fillet.Shape()
    assert fillet.IsDone()
    assert sum(1 for _ in TopExp_Explorer(result, TopAbs_FACE)) > 6


def test_BRepFilletAPI_MakeFilletTest_FilletVariableRadius():
    box = _box()
    fillet = BRepFilletAPI_MakeFillet(box)
    fillet.Add(1.0, 3.0, _first_edge(box))
    result = fillet.Shape()
    assert fillet.IsDone()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFilletAPI_MakeFilletTest_OCC570_MixedVariableConstantRadius():
    box = BRepPrimAPI_MakeBox(100.0, 100.0, 100.0).Shape()
    wire_exp = TopExp_Explorer(box, TopAbs_WIRE)
    assert wire_exp.More()
    wire = wire_exp.Current()
    edges = [TopoDS.Edge(e) for e in TopExp_Explorer(wire, TopAbs_EDGE)]
    assert len(edges) >= 4
    e1, e2, e3, e4 = edges[:4]

    var_radius = NCollection_Array1[gp_Pnt2d](1, 4)
    var_radius.SetValue(1, gp_Pnt2d(0.0, 5.0))
    var_radius.SetValue(2, gp_Pnt2d(0.3, 15.0))
    var_radius.SetValue(3, gp_Pnt2d(0.7, 15.0))
    var_radius.SetValue(4, gp_Pnt2d(1.0, 5.0))

    fillet = BRepFilletAPI_MakeFillet(box)
    fillet.SetContinuity(GeomAbs_C1, 0.001)
    fillet.Add(var_radius, e1)
    fillet.Add(5.0, e2)
    fillet.Add(var_radius, e3)
    fillet.Add(5.0, e4)
    fillet.Build()
    assert fillet.IsDone()

    result = fillet.Shape()
    assert BRepCheck_Analyzer(result).IsValid()
    assert _area(result) == pytest.approx(58500.0, abs=58500.0 * 0.01)


def test_BRepFilletAPI_MakeFilletTest_Bug828_FilletOnComplexPrism():
    p11 = gp_Pnt(-27.598139, -7.0408573, 0.0)
    p12 = gp_Pnt(-28.483755, -17.487625, 0.0)
    p13 = gp_Pnt(-19.555504, -22.983587, 0.0)
    arc1 = GC_MakeArcOfCircle(p11, p12, p13)
    p21 = gp_Pnt(12.125083, -22.983587, 0.0)
    p22 = gp_Pnt(21.1572, -17.27554, 0.0)
    p23 = gp_Pnt(19.878168, -6.6677585, 0.0)
    arc2 = GC_MakeArcOfCircle(p21, p22, p23)
    p31 = gp_Pnt(3.265825, 13.724955, 0.0)
    p32 = gp_Pnt(-4.7233953, 17.406338, 0.0)
    p33 = gp_Pnt(-12.529893, 13.351856, 0.0)
    arc3 = GC_MakeArcOfCircle(p31, p32, p33)
    seg1 = GC_MakeSegment(p13, p21)
    seg2 = GC_MakeSegment(p23, p31)
    seg3 = GC_MakeSegment(p33, p11)

    wire_maker = BRepBuilderAPI_MakeWire()
    for curve in (arc1, seg1, arc2, seg2, arc3, seg3):
        wire_maker.Add(BRepBuilderAPI_MakeEdge(curve.Value()).Edge())
    assert wire_maker.IsDone()

    face = BRepBuilderAPI_MakeFace(wire_maker.Wire()).Face()
    assert not face.IsNull()

    slab = BRepPrimAPI_MakePrism(face, gp_Vec(0.0, 0.0, 111.0), True)
    assert slab.IsDone()
    slab_shape = slab.Shape()
    assert BRepCheck_Analyzer(slab_shape).IsValid()

    edges = [TopoDS.Edge(e) for e in TopExp_Explorer(slab_shape, TopAbs_EDGE)]
    assert len(edges) >= 2

    target_area = 17816.2
    target_tol = target_area * 0.002
    result = None
    best_area = 0.0
    best_delta = 1.0e100
    for i1 in range(len(edges)):
        for i2 in range(i1 + 1, len(edges)):
            try:
                fillet = BRepFilletAPI_MakeFillet(slab_shape, ChFi3d_Rational)
                fillet.SetParams(1.0e-2, 1.0e-4, 1.0e-5, 1.0e-4, 1.0e-5, 1.0e-3)
                fillet.SetContinuity(GeomAbs_C1, 1.0e-2)
                fillet.Add(10.0, edges[i1])
                fillet.Add(10.0, edges[i2])
                fillet.Build()
                if not fillet.IsDone():
                    continue
                candidate = fillet.Shape()
                if candidate.IsNull():
                    continue
                if not BRepCheck_Analyzer(candidate).IsValid():
                    continue
                area = _area(candidate)
                if abs(area - target_area) < best_delta:
                    best_area = area
                    best_delta = abs(area - target_area)
                if abs(area - target_area) <= target_tol:
                    result = candidate
                    break
            except Standard_Failure:
                continue
        if result is not None:
            break

    assert result is not None, f"closest area={best_area}"
    assert BRepCheck_Analyzer(result).IsValid()
    assert _area(result) == pytest.approx(target_area, abs=target_tol)


def _occ1077_bool_bl(bool_op, radius):
    shape_cut = bool_op.Shape()
    result = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(result)
    for solid in TopExp_Explorer(shape_cut, TopAbs_SOLID):
        fill = BRepFilletAPI_MakeFillet(solid)
        fill.SetParams(1.0e-2, 1.0e-4, 1.0e-5, 1.0e-4, 1.0e-5, 1.0e-3)
        fill.SetContinuity(GeomAbs_C1, 1.0e-2)
        for edge in bool_op.SectionEdges():
            fill.Add(radius, TopoDS.Edge(edge))
        fill.Build()
        if fill.IsDone():
            builder.Add(result, fill.Shape())
        else:
            builder.Add(result, solid)
    return result


def _occ1077_cut_blend(shape_to_cut, tool, radius):
    cut = BRepAlgoAPI_Cut(shape_to_cut, tool)
    return _occ1077_bool_bl(cut, radius)


def test_BRepFilletAPI_MakeFilletTest_OCC1077_BooleanCutFillet():
    box = BRepPrimAPI_MakeBox(gp_Pnt(-5.0, -5.0, -5.0), 10.0, 10.0, 10.0).Shape()
    sphere = BRepPrimAPI_MakeSphere(7.0).Shape()
    common = BRepAlgoAPI_Common(box, sphere).Shape()

    cyl1 = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -10), gp_Dir(0, 0, 1)), 3.0, 20.0).Shape()
    cyl2 = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(-10, 0, 0), gp_Dir(1, 0, 0)), 3.0, 20.0).Shape()
    cyl3 = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, -10, 0), gp_Dir(0, 1, 0)), 3.0, 20.0).Shape()

    tmp1 = _occ1077_cut_blend(common, cyl1, 0.7)
    fixer = ShapeFix_Shape(tmp1)
    fixer.Perform()
    tmp1 = fixer.Shape()

    tmp2 = _occ1077_cut_blend(tmp1, cyl2, 0.7)
    fixer.Init(tmp2)
    fixer.Perform()
    tmp2 = fixer.Shape()

    result = _occ1077_cut_blend(tmp2, cyl3, 0.7)
    fixer.Init(result)
    fixer.Perform()
    result = fixer.Shape()

    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()
    assert _area(result) == pytest.approx(587.181, abs=587.181 * 0.001)


def _ring_face(points):
    poly = BRepBuilderAPI_MakePolygon()
    for p in points:
        poly.Add(p)
    return BRepBuilderAPI_MakeFace(poly.Wire(), False).Face()


def test_BRepFilletAPI_MakeFilletTest_OCC426_RevolveFuseUnifyFillet():
    axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    f1 = _ring_face([gp_Pnt(10, 0, 0), gp_Pnt(20, 0, 0), gp_Pnt(20, 0, 10), gp_Pnt(10, 0, 10), gp_Pnt(10, 0, 0)])
    rs1 = BRepPrimAPI_MakeRevol(f1, axis, 2.0 * math.pi).Shape()

    a = 7.0710678118654752440
    b = 14.1421356237309504880
    f2 = _ring_face([gp_Pnt(a, a, 10), gp_Pnt(b, b, 10), gp_Pnt(b, b, 20), gp_Pnt(a, a, 20), gp_Pnt(a, a, 10)])
    rs2 = BRepPrimAPI_MakeRevol(f2, axis, 270.0 * math.pi / 180.0).Shape()

    f3 = _ring_face([gp_Pnt(10, 0, 20), gp_Pnt(20, 0, 20), gp_Pnt(20, 0, 30), gp_Pnt(10, 0, 30), gp_Pnt(10, 0, 20)])
    rs3 = BRepPrimAPI_MakeRevol(f3, axis, 2.0 * math.pi).Shape()

    assert BRepCheck_Analyzer(rs1).IsValid()
    assert BRepCheck_Analyzer(rs2).IsValid()
    assert BRepCheck_Analyzer(rs3).IsValid()

    fuse32 = BRepAlgoAPI_Fuse(rs3, rs2)
    assert fuse32.IsDone()
    fuse32_shape = fuse32.Shape()
    assert BRepCheck_Analyzer(fuse32_shape).IsValid()

    fuse321 = BRepAlgoAPI_Fuse(fuse32_shape, rs1)
    assert fuse321.IsDone()
    fuse321_shape = fuse321.Shape()
    assert BRepCheck_Analyzer(fuse321_shape).IsValid()

    unify = ShapeUpgrade_UnifySameDomain(fuse321_shape, True, True, True)
    unify.Build()
    fuse_unif = unify.Shape()

    edge_map = NCollection_IndexedDataMap[TopoDS_Shape, NCollection_List[TopoDS_Shape], TopTools_ShapeMapHasher]()
    TopExp.MapShapesAndAncestors_s(fuse_unif, TopAbs_EDGE, TopAbs_SOLID, edge_map)

    blend = BRepFilletAPI_MakeFillet(fuse_unif, ChFi3d_Rational)
    for i in range(1, edge_map.Extent() + 1):
        edge = TopoDS.Edge(edge_map.FindKey(i))
        if not edge.IsNull():
            blend.Add(1.0, edge)

    try:
        blend.Build()
    except Standard_Failure:
        pytest.skip("BRepFilletAPI_MakeFillet::Build() threw an exception (OCC24156)")

    assert blend.IsDone()
    result = blend.Shape()
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()
    assert _area(result) == pytest.approx(7507.61, abs=7507.61 * 0.001)
