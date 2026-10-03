# Translated from OCCT src/ModelingData/TKBRep/GTests/TopoDS_Iterator_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct import TopoDS
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt, gp_Trsf, gp_Vec
from nanocct.Standard import Standard_NoSuchObject
from nanocct.TopAbs import TopAbs_COMPOUND, TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_VERTEX, TopAbs_WIRE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopLoc import TopLoc_Location
from nanocct.TopoDS import TopoDS_Builder, TopoDS_Compound, TopoDS_Iterator, TopoDS_Shape, TopoDS_Wire


def _vertex(x, y, z):
    return BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Vertex()


def _compound(b):
    c = TopoDS_Compound()
    b.MakeCompound(c)
    return c


def _count(it):
    n = 0
    while it.More():
        n += 1
        it.Next()
    return n


def test_TopoDS_Iterator_Test_OCC30708_1_InitializeWithNullShape():
    it = TopoDS_Iterator()
    it.Initialize(TopoDS_Shape())
    assert not it.More()


def test_TopoDS_Iterator_Test_EmptyCompound():
    assert not TopoDS_Iterator(_compound(TopoDS_Builder())).More()


def test_TopoDS_Iterator_Test_CompoundWithVertices():
    b = TopoDS_Builder()
    c = _compound(b)
    for i in range(5):
        b.Add(c, _vertex(i, 0, 0))
    kids = list(TopoDS_Iterator(c))
    assert all(k.ShapeType() == TopAbs_VERTEX for k in kids)
    assert len(kids) == 5


def test_TopoDS_Iterator_Test_WireWithEdges():
    b = TopoDS_Builder()
    w = TopoDS_Wire()
    b.MakeWire(w)
    pts = [gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0), gp_Pnt(1, 1, 0), gp_Pnt(0, 1, 0)]
    for i in range(4):
        b.Add(w, BRepBuilderAPI_MakeEdge(pts[i], pts[(i + 1) % 4]).Edge())
    kids = list(TopoDS_Iterator(w))
    assert all(k.ShapeType() == TopAbs_EDGE for k in kids)
    assert len(kids) == 4


def test_TopoDS_Iterator_Test_EdgeWithVertices():
    e = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 1, 1)).Edge()
    kids = list(TopoDS_Iterator(e))
    assert all(k.ShapeType() == TopAbs_VERTEX for k in kids)
    assert len(kids) == 2


def test_TopoDS_Iterator_Test_VertexNoChildren():
    assert not TopoDS_Iterator(_vertex(0, 0, 0)).More()


def test_TopoDS_Iterator_Test_CumulativeOrientation():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    c.Reverse()
    it1 = TopoDS_Iterator(c, True, True)
    assert it1.More()
    it2 = TopoDS_Iterator(c, False, True)
    assert it2.More()
    assert it1.Value().Orientation() != it2.Value().Orientation()


def test_TopoDS_Iterator_Test_ReInitialization():
    b = TopoDS_Builder()
    c1 = _compound(b)
    c2 = _compound(b)
    for i in range(3):
        b.Add(c1, _vertex(i, 0, 0))
    for i in range(5):
        b.Add(c2, _vertex(i, 1, 0))
    it = TopoDS_Iterator(c1)
    assert _count(it) == 3
    it.Initialize(c2)
    assert _count(it) == 5


def test_TopoDS_Iterator_Test_BoxSolidIteration():
    box = BRepPrimAPI_MakeBox(1.0, 2.0, 3.0).Shape()
    shells = 0
    it = TopoDS_Iterator(box)
    while it.More():
        assert it.Value().ShapeType() == TopAbs_SHELL
        shells += 1
        faces = list(TopoDS_Iterator(it.Value()))
        assert all(f.ShapeType() == TopAbs_FACE for f in faces)
        assert len(faces) == 6
        it.Next()
    assert shells == 1


def test_TopoDS_Iterator_Test_ManyChildren():
    b = TopoDS_Builder()
    c = _compound(b)
    for i in range(1000):
        b.Add(c, _vertex(i, 0, 0))
    assert _count(TopoDS_Iterator(c)) == 1000


def test_TopoDS_Iterator_Test_DefaultConstructorThenInitialize():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    it = TopoDS_Iterator()
    assert not it.More()
    it.Initialize(c)
    assert it.More()
    assert it.Value().ShapeType() == TopAbs_VERTEX


def test_TopoDS_Iterator_Test_ValueThrowsWhenNotMore():
    it = TopoDS_Iterator(_compound(TopoDS_Builder()))
    assert not it.More()
    with pytest.raises(Standard_NoSuchObject):
        it.Value()


def test_TopoDS_Iterator_Test_CumulativeLocation():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(10, 20, 30))
    c.Location(TopLoc_Location(trsf))
    it1 = TopoDS_Iterator(c, True, True)
    assert it1.More()
    it2 = TopoDS_Iterator(c, True, False)
    assert it2.More()
    assert it1.Value().Location().IsIdentity() != it2.Value().Location().IsIdentity()


def test_TopoDS_Iterator_Test_NestedCompounds():
    b = TopoDS_Builder()
    outer = _compound(b)
    in1 = _compound(b)
    in2 = _compound(b)
    b.Add(in1, _vertex(0, 0, 0))
    b.Add(in1, _vertex(1, 0, 0))
    b.Add(in2, _vertex(2, 0, 0))
    b.Add(outer, in1)
    b.Add(outer, in2)
    kids = list(TopoDS_Iterator(outer))
    assert all(k.ShapeType() == TopAbs_COMPOUND for k in kids)
    assert len(kids) == 2
    it = TopoDS_Iterator(outer)
    assert _count(TopoDS_Iterator(it.Value())) == 2


def test_TopoDS_Iterator_Test_FaceWithWires():
    box = BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()
    exp = TopExp_Explorer(box, TopAbs_FACE)
    assert exp.More()
    kids = list(TopoDS_Iterator(TopoDS.Face(exp.Current())))
    assert all(k.ShapeType() == TopAbs_WIRE for k in kids)
    assert len(kids) >= 1


def test_TopoDS_Iterator_Test_ShapeIdentity():
    b = TopoDS_Builder()
    c = _compound(b)
    v1 = _vertex(1, 0, 0)
    v2 = _vertex(2, 0, 0)
    b.Add(c, v1)
    b.Add(c, v2)
    it = TopoDS_Iterator(c)
    t = it.Value().TShape()
    assert t == v1.TShape() or t == v2.TShape()
    it.Next()
    t = it.Value().TShape()
    assert t == v1.TShape() or t == v2.TShape()


def test_TopoDS_Iterator_Test_ShellWithFaces():
    box = BRepPrimAPI_MakeBox(1.0, 1.0, 1.0).Shape()
    exp = TopExp_Explorer(box, TopAbs_SHELL)
    assert exp.More()
    kids = list(TopoDS_Iterator(TopoDS.Shell(exp.Current())))
    assert all(k.ShapeType() == TopAbs_FACE for k in kids)
    assert len(kids) == 6
