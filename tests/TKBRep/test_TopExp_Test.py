# Translated from OCCT src/ModelingData/TKBRep/GTests/TopExp_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.NCollection import NCollection_IndexedDataMap, NCollection_IndexedMap, NCollection_List
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
from nanocct.TopExp import TopExp, TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape, TopoDS_Vertex
from nanocct.TopTools import TopTools_ShapeMapHasher


def _box():
    maker = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _map(shape, kind):
    m = NCollection_IndexedMap[TopoDS_Shape, TopTools_ShapeMapHasher]()
    TopExp.MapShapes_s(shape, kind, m)
    return m


def test_TopExp_Test_MapShapes_Faces():
    assert _map(_box(), TopAbs_FACE).Extent() == 6


def test_TopExp_Test_MapShapes_Edges():
    assert _map(_box(), TopAbs_EDGE).Extent() == 12


def test_TopExp_Test_MapShapes_Vertices():
    assert _map(_box(), TopAbs_VERTEX).Extent() == 8


def test_TopExp_Test_FirstVertex_LastVertex():
    exp = TopExp_Explorer(_box(), TopAbs_EDGE)
    assert exp.More()
    edge = TopoDS.Edge(exp.Current())
    v1 = TopExp.FirstVertex_s(edge)
    v2 = TopExp.LastVertex_s(edge)
    assert not v1.IsNull()
    assert not v2.IsNull()
    assert not v1.IsSame(v2)


def test_TopExp_Test_Vertices():
    exp = TopExp_Explorer(_box(), TopAbs_EDGE)
    assert exp.More()
    edge = TopoDS.Edge(exp.Current())
    v1, v2 = TopoDS_Vertex(), TopoDS_Vertex()
    TopExp.Vertices_s(edge, v1, v2)
    assert not v1.IsNull()
    assert not v2.IsNull()


def test_TopExp_Test_CommonVertex():
    edges = _map(_box(), TopAbs_EDGE)
    assert edges.Extent() >= 2
    found = False
    n = edges.Extent()
    for i in range(1, n + 1):
        if found:
            break
        e1 = TopoDS.Edge(edges(i))
        for j in range(i + 1, n + 1):
            e2 = TopoDS.Edge(edges(j))
            common = TopoDS_Vertex()
            if TopExp.CommonVertex_s(e1, e2, common):
                assert not common.IsNull()
                found = True
                break
    assert found


def test_TopExp_Test_Explorer_NestedFaceEdge_Terminates():
    box = _box()
    total = 0
    faces = 0
    fexp = TopExp_Explorer(box, TopAbs_FACE)
    while fexp.More():
        faces += 1
        count = 0
        eexp = TopExp_Explorer(TopoDS.Face(fexp.Current()), TopAbs_EDGE)
        while eexp.More():
            assert not eexp.Current().IsNull()
            count += 1
            assert count < 100
            eexp.Next()
        assert count == 4
        total += count
        fexp.Next()
    assert faces == 6
    assert total == 24


def test_TopExp_Test_Explorer_ReInit_Terminates():
    box = _box()
    exp = TopExp_Explorer()
    for face_shape in TopExp_Explorer(box, TopAbs_FACE):
        exp.Init(TopoDS.Face(face_shape), TopAbs_EDGE)
        count = 0
        while exp.More():
            count += 1
            assert count < 100
            exp.Next()
        assert count == 4


def test_TopExp_Test_MapShapesAndAncestors():
    m = NCollection_IndexedDataMap[TopoDS_Shape, NCollection_List[TopoDS_Shape], TopTools_ShapeMapHasher]()
    TopExp.MapShapesAndAncestors_s(_box(), TopAbs_EDGE, TopAbs_FACE, m)
    assert m.Extent() == 12
    for i in range(1, m.Extent() + 1):
        assert m(i).Extent() == 2
