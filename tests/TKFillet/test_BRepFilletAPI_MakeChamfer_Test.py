# Translated from OCCT src/ModelingAlgorithms/TKFillet/GTests/BRepFilletAPI_MakeChamfer_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Fuse
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepFilletAPI import BRepFilletAPI_MakeChamfer
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from nanocct.gp import gp_Ax2, gp_Dir, gp_Pnt
from nanocct.NCollection import NCollection_IndexedDataMap, NCollection_IndexedMap, NCollection_List
from nanocct.Standard import Standard_ConstructionError, Standard_Failure
from nanocct.StdFail import StdFail_NotDone
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape
from nanocct.TopTools import TopTools_ShapeMapHasher


def _ancestor_map():
    return NCollection_IndexedDataMap[TopoDS_Shape, NCollection_List[TopoDS_Shape], TopTools_ShapeMapHasher]()


def _box(size=20.0):
    maker = BRepPrimAPI_MakeBox(size, size, size)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _first_edge(shape):
    exp = TopExp_Explorer(shape, TopAbs_EDGE)
    assert exp.More()
    return TopoDS.Edge(exp.Current())


def test_BRepFilletAPI_MakeChamferTest_SymmetricChamfer():
    box = _box()
    edge = _first_edge(box)
    chamfer = BRepFilletAPI_MakeChamfer(box)
    chamfer.Add(2.0, edge)
    result = chamfer.Shape()
    assert chamfer.IsDone()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFilletAPI_MakeChamferTest_AsymmetricChamfer():
    box = _box()
    edge_face_map = _ancestor_map()
    TopExp.MapShapesAndAncestors_s(box, TopAbs_EDGE, TopAbs_FACE, edge_face_map)
    edge = _first_edge(box)
    face = TopoDS.Face(edge_face_map.FindFromKey(edge).First())
    chamfer = BRepFilletAPI_MakeChamfer(box)
    chamfer.Add(1.0, 3.0, edge, face)
    result = chamfer.Shape()
    assert chamfer.IsDone()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepFilletAPI_MakeChamferTest_ChamferMoreFaces():
    box = _box()
    edge = _first_edge(box)
    chamfer = BRepFilletAPI_MakeChamfer(box)
    chamfer.Add(2.0, edge)
    result = chamfer.Shape()
    assert chamfer.IsDone()
    face_count = sum(1 for _ in TopExp_Explorer(result, TopAbs_FACE))
    assert face_count > 6


def test_BRepFilletAPI_MakeChamferTest_ChamferAfterBooleanFusion():
    box = _box(10.0)
    cyl_maker = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(5.0, 0.0, 5.0), gp_Dir(0.0, 1.0, 0.0)), 3.0, 10.0)
    cyl = cyl_maker.Shape()
    assert cyl_maker.IsDone()
    fuse = BRepAlgoAPI_Fuse(box, cyl)
    assert fuse.IsDone()
    fused = fuse.Shape()

    vtx_face_map = _ancestor_map()
    TopExp.MapShapesAndAncestors_s(fused, TopAbs_VERTEX, TopAbs_FACE, vtx_face_map)
    edge_face_map = _ancestor_map()
    TopExp.MapShapesAndAncestors_s(fused, TopAbs_EDGE, TopAbs_FACE, edge_face_map)

    chamfer = BRepFilletAPI_MakeChamfer(fused)
    edge_count = 0
    edge_exp = TopExp_Explorer(fused, TopAbs_EDGE)
    while edge_exp.More() and edge_count < 4:
        edge = TopoDS.Edge(edge_exp.Current())
        edge_exp.Next()
        if not edge_face_map.Contains(edge) or edge_face_map.FindFromKey(edge).IsEmpty():
            continue
        has_complex_vertex = False
        for vtx in TopExp_Explorer(edge, TopAbs_VERTEX):
            if vtx_face_map.Contains(vtx) and vtx_face_map.FindFromKey(vtx).Size() >= 3:
                has_complex_vertex = True
                break
        if has_complex_vertex is False:
            continue
        face = TopoDS.Face(edge_face_map.FindFromKey(edge).First())
        chamfer.Add(0.5, 0.5, edge, face)
        edge_count += 1
    assert edge_count > 0

    try:
        chamfer.Build()
        if chamfer.IsDone():
            assert BRepCheck_Analyzer(chamfer.Shape()).IsValid()
    except Standard_Failure:
        pass


def test_BRepFilletAPI_MakeChamferTest_SequentialChamferNoCrash():
    shape = _box()
    prev_edges = 0
    success_count = 0
    for i in range(3):
        edge_map = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
        TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)
        if edge_map.IsEmpty():
            break
        if i > 0 and prev_edges > 0:
            assert edge_map.Extent() != prev_edges
        prev_edges = edge_map.Extent()
        idx = (i * 3 + 1) % edge_map.Extent() + 1
        edge = TopoDS.Edge(edge_map.FindKey(idx))
        chamfer = BRepFilletAPI_MakeChamfer(shape)
        chamfer.Add(1.0, edge)
        try:
            chamfer.Build()
            if chamfer.IsDone():
                shape = chamfer.Shape()
                success_count += 1
            else:
                break
        except (Standard_ConstructionError, StdFail_NotDone):
            break
    assert success_count >= 1
