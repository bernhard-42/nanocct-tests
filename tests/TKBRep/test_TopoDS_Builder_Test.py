# Translated from OCCT src/ModelingData/TKBRep/GTests/TopoDS_Builder_Test.cxx (LGPL-2.1 with the OCCT exception)
from collections import Counter

from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from nanocct.gp import gp_Pnt
from nanocct.TopAbs import (
    TopAbs_COMPOUND,
    TopAbs_COMPSOLID,
    TopAbs_EDGE,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_VERTEX,
    TopAbs_WIRE,
)
from nanocct.TopoDS import (
    TopoDS_Builder,
    TopoDS_Compound,
    TopoDS_CompSolid,
    TopoDS_Iterator,
    TopoDS_Shell,
    TopoDS_Solid,
    TopoDS_Wire,
)


def _vertex(x, y, z):
    return BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Vertex()


def _edge(p1, p2):
    return BRepBuilderAPI_MakeEdge(gp_Pnt(*p1), gp_Pnt(*p2)).Edge()


def _compound(b):
    c = TopoDS_Compound()
    b.MakeCompound(c)
    return c


def _wire(b):
    w = TopoDS_Wire()
    b.MakeWire(w)
    return w


def _n(shape):
    return len(list(TopoDS_Iterator(shape)))


def _three(b, c):
    vs = [_vertex(1, 0, 0), _vertex(2, 0, 0), _vertex(3, 0, 0)]
    for v in vs:
        b.Add(c, v)
    return vs


def test_TopoDS_Builder_Test_MakeWire():
    w = _wire(TopoDS_Builder())
    assert not w.IsNull()
    assert w.ShapeType() == TopAbs_WIRE
    assert w.Free()


def test_TopoDS_Builder_Test_MakeShell():
    s = TopoDS_Shell()
    TopoDS_Builder().MakeShell(s)
    assert not s.IsNull()
    assert s.ShapeType() == TopAbs_SHELL


def test_TopoDS_Builder_Test_MakeSolid():
    s = TopoDS_Solid()
    TopoDS_Builder().MakeSolid(s)
    assert not s.IsNull()
    assert s.ShapeType() == TopAbs_SOLID


def test_TopoDS_Builder_Test_MakeCompSolid():
    s = TopoDS_CompSolid()
    TopoDS_Builder().MakeCompSolid(s)
    assert not s.IsNull()
    assert s.ShapeType() == TopAbs_COMPSOLID


def test_TopoDS_Builder_Test_MakeCompound():
    c = _compound(TopoDS_Builder())
    assert not c.IsNull()
    assert c.ShapeType() == TopAbs_COMPOUND


def test_TopoDS_Builder_Test_Add_VerticesToCompound():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    b.Add(c, _vertex(1, 0, 0))
    b.Add(c, _vertex(0, 1, 0))
    assert _n(c) == 3


def test_TopoDS_Builder_Test_Add_EdgesToWire():
    b = TopoDS_Builder()
    w = _wire(b)
    b.Add(w, _edge((0, 0, 0), (1, 0, 0)))
    b.Add(w, _edge((1, 0, 0), (0.5, 1, 0)))
    b.Add(w, _edge((0.5, 1, 0), (0, 0, 0)))
    kids = list(TopoDS_Iterator(w))
    assert all(k.ShapeType() == TopAbs_EDGE for k in kids)
    assert len(kids) == 3


def test_TopoDS_Builder_Test_Remove_FromCompound():
    b = TopoDS_Builder()
    c = _compound(b)
    v1, v2, v3 = _vertex(0, 0, 0), _vertex(1, 0, 0), _vertex(0, 1, 0)
    for v in (v1, v2, v3):
        b.Add(c, v)
    b.Remove(c, v2)
    assert _n(c) == 2


def test_TopoDS_Builder_Test_Add_ManyShapes():
    b = TopoDS_Builder()
    c = _compound(b)
    for i in range(500):
        b.Add(c, _vertex(i, 0, 0))
    assert _n(c) == 500


def test_TopoDS_Builder_Test_TShapeFlags():
    c = _compound(TopoDS_Builder())
    assert c.Free()
    assert c.Modified()
    c.Checked(True)
    assert c.Checked()
    c.Closed(True)
    assert c.Closed()
    c.Infinite(True)
    assert c.Infinite()
    c.Convex(True)
    assert c.Convex()


def test_TopoDS_Builder_Test_Remove_FirstChild():
    b = TopoDS_Builder()
    c = _compound(b)
    vs = _three(b, c)
    b.Remove(c, vs[0])
    assert _n(c) == 2


def test_TopoDS_Builder_Test_Remove_LastChild():
    b = TopoDS_Builder()
    c = _compound(b)
    vs = _three(b, c)
    b.Remove(c, vs[2])
    assert _n(c) == 2


def test_TopoDS_Builder_Test_Remove_AllChildren():
    b = TopoDS_Builder()
    c = _compound(b)
    for v in _three(b, c):
        b.Remove(c, v)
    assert not TopoDS_Iterator(c).More()


def test_TopoDS_Builder_Test_Remove_FromWire():
    b = TopoDS_Builder()
    w = _wire(b)
    e1 = _edge((0, 0, 0), (1, 0, 0))
    e2 = _edge((1, 0, 0), (1, 1, 0))
    e3 = _edge((1, 1, 0), (0, 0, 0))
    for e in (e1, e2, e3):
        b.Add(w, e)
    b.Remove(w, e2)
    assert _n(w) == 2


def test_TopoDS_Builder_Test_NestedCompounds():
    b = TopoDS_Builder()
    outer = _compound(b)
    inner = _compound(b)
    b.Add(inner, _vertex(0, 0, 0))
    b.Add(inner, _vertex(1, 0, 0))
    b.Add(outer, inner)
    kids = list(TopoDS_Iterator(outer))
    assert all(k.ShapeType() == TopAbs_COMPOUND for k in kids)
    assert len(kids) == 1
    assert inner.TShape().NbChildren() == 2


def test_TopoDS_Builder_Test_Add_SetsModifiedFlag():
    b = TopoDS_Builder()
    c = _compound(b)
    c.TShape().Modified(False)
    assert not c.Modified()
    b.Add(c, _vertex(0, 0, 0))
    assert c.Modified()


def test_TopoDS_Builder_Test_Remove_SetsModifiedFlag():
    b = TopoDS_Builder()
    c = _compound(b)
    v = _vertex(0, 0, 0)
    b.Add(c, v)
    c.TShape().Modified(False)
    assert not c.Modified()
    b.Remove(c, v)
    assert c.Modified()


def test_TopoDS_Builder_Test_AllTypes():
    b = TopoDS_Builder()
    for cls, make, kind in (
        (TopoDS_Wire, b.MakeWire, TopAbs_WIRE),
        (TopoDS_Shell, b.MakeShell, TopAbs_SHELL),
        (TopoDS_Solid, b.MakeSolid, TopAbs_SOLID),
        (TopoDS_CompSolid, b.MakeCompSolid, TopAbs_COMPSOLID),
        (TopoDS_Compound, b.MakeCompound, TopAbs_COMPOUND),
    ):
        s = cls()
        make(s)
        assert not s.IsNull()
        assert s.ShapeType() == kind
        assert s.Free()


def test_TopoDS_Builder_Test_MixedShapesInCompound():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    b.Add(c, _edge((0, 0, 0), (1, 0, 0)))
    b.Add(c, _wire(b))
    sh = TopoDS_Shell()
    b.MakeShell(sh)
    b.Add(c, sh)
    b.Add(c, _compound(b))
    assert c.TShape().NbChildren() == 5
    counts = Counter(k.ShapeType() for k in TopoDS_Iterator(c))
    assert counts[TopAbs_VERTEX] == 1
    assert counts[TopAbs_EDGE] == 1
    assert counts[TopAbs_WIRE] == 1
    assert counts[TopAbs_SHELL] == 1
    assert counts[TopAbs_COMPOUND] == 1
