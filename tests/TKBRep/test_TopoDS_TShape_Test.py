# Translated from OCCT src/ModelingData/TKBRep/GTests/TopoDS_TShape_Test.cxx (LGPL-2.1 with the OCCT exception)
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


def _edge():
    return BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0)).Edge()


def _compound(b):
    c = TopoDS_Compound()
    b.MakeCompound(c)
    return c


def test_TopoDS_TShape_Test_ShapeType_AllTypes():
    b = TopoDS_Builder()
    assert _vertex(0, 0, 0).TShape().ShapeType() == TopAbs_VERTEX
    assert _edge().TShape().ShapeType() == TopAbs_EDGE
    w = TopoDS_Wire()
    b.MakeWire(w)
    assert w.TShape().ShapeType() == TopAbs_WIRE
    sh = TopoDS_Shell()
    b.MakeShell(sh)
    assert sh.TShape().ShapeType() == TopAbs_SHELL
    so = TopoDS_Solid()
    b.MakeSolid(so)
    assert so.TShape().ShapeType() == TopAbs_SOLID
    cs = TopoDS_CompSolid()
    b.MakeCompSolid(cs)
    assert cs.TShape().ShapeType() == TopAbs_COMPSOLID
    assert _compound(b).TShape().ShapeType() == TopAbs_COMPOUND


def test_TopoDS_TShape_Test_FlagSettersGetters():
    t = _compound(TopoDS_Builder()).TShape()
    assert t.Free()
    t.Free(False)
    assert not t.Free()
    t.Free(True)
    assert t.Free()
    assert t.Modified()
    t.Modified(False)
    assert not t.Modified()
    assert not t.Checked()
    t.Checked(True)
    assert t.Checked()
    t.Modified(True)
    assert not t.Checked()
    assert not t.Orientable()
    assert not t.Closed()
    t.Closed(True)
    assert t.Closed()
    assert not t.Infinite()
    t.Infinite(True)
    assert t.Infinite()
    assert not t.Convex()
    t.Convex(True)
    assert t.Convex()
    assert not t.Locked()
    t.Locked(True)
    assert t.Locked()


def test_TopoDS_TShape_Test_NbChildren():
    b = TopoDS_Builder()
    assert _vertex(0, 0, 0).TShape().NbChildren() == 0
    e = _edge()
    assert e.TShape().NbChildren() == 2
    w = TopoDS_Wire()
    b.MakeWire(w)
    assert w.TShape().NbChildren() == 0
    b.Add(w, e)
    assert w.TShape().NbChildren() == 1
    c = _compound(b)
    for i in range(10):
        b.Add(c, _vertex(i, 0, 0))
    assert c.TShape().NbChildren() == 10


def test_TopoDS_TShape_Test_EmptyCopy():
    b = TopoDS_Builder()
    c = _compound(b)
    b.Add(c, _vertex(0, 0, 0))
    b.Add(c, _vertex(1, 0, 0))
    assert c.TShape().NbChildren() == 2
    copy = c.TShape().EmptyCopy()
    assert copy.ShapeType() == TopAbs_COMPOUND
    assert copy.NbChildren() == 0


def test_TopoDS_TShape_Test_EmptyCopy_AllTypes():
    b = TopoDS_Builder()
    copy = _edge().TShape().EmptyCopy()
    assert copy.ShapeType() == TopAbs_EDGE
    assert copy.NbChildren() == 0
    w = TopoDS_Wire()
    b.MakeWire(w)
    assert w.TShape().EmptyCopy().ShapeType() == TopAbs_WIRE
    sh = TopoDS_Shell()
    b.MakeShell(sh)
    assert sh.TShape().EmptyCopy().ShapeType() == TopAbs_SHELL
    so = TopoDS_Solid()
    b.MakeSolid(so)
    assert so.TShape().EmptyCopy().ShapeType() == TopAbs_SOLID
    cs = TopoDS_CompSolid()
    b.MakeCompSolid(cs)
    assert cs.TShape().EmptyCopy().ShapeType() == TopAbs_COMPSOLID


def test_TopoDS_TShape_Test_Orientable_DifferentTypes():
    b = TopoDS_Builder()
    assert _edge().TShape().Orientable()
    assert not _compound(b).TShape().Orientable()
    w = TopoDS_Wire()
    b.MakeWire(w)
    assert w.TShape().Orientable()


def test_TopoDS_TShape_Test_FlagsIndependent():
    t = _compound(TopoDS_Builder()).TShape()
    t.Closed(True)
    t.Infinite(True)
    t.Convex(True)
    t.Locked(True)
    assert t.Closed() and t.Infinite() and t.Convex() and t.Locked()
    t.Closed(False)
    assert not t.Closed()
    assert t.Infinite()
    assert t.Convex()
    assert t.Locked()


def test_TopoDS_TShape_Test_NbChildren_ConsistencyWithIterator():
    b = TopoDS_Builder()
    w = TopoDS_Wire()
    b.MakeWire(w)
    b.Add(w, _edge())
    n = w.TShape().NbChildren()
    assert n == len(list(TopoDS_Iterator(w)))
    assert n == 1
