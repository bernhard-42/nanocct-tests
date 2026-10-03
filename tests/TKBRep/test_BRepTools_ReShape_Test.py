# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepTools_ReShape_Test.cxx (LGPL-2.1 with the OCCT exception)
# TShape pointer comparisons (a.TShape() == b.TShape()) are written as a.IsPartner(b): the same TShape.
from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex
from nanocct.BRepTools import BRepTools_ReShape
from nanocct.gp import gp_Pnt
from nanocct.TopAbs import TopAbs_EDGE, TopAbs_VERTEX
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Compound, TopoDS_Iterator


def _v(x, y, z):
    return BRepBuilderAPI_MakeVertex(gp_Pnt(x, y, z)).Vertex()


def _e(v1, v2):
    return BRepBuilderAPI_MakeEdge(v1, v2).Edge()


def _compound(b, *children):
    c = TopoDS_Compound()
    b.MakeCompound(c)
    for s in children:
        b.Add(c, s)
    return c


def test_BRepTools_ReShapeTest_ValueLeaf_FollowsChainToLeaf():
    a, b, c = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    rs.Replace(b, c)
    assert rs.Value(a).IsSame(b)
    assert rs.ValueLeaf(a).IsSame(c)
    assert rs.ValueLeaf(b).IsSame(c)
    assert rs.ValueLeaf(c).IsSame(c)


def test_BRepTools_ReShapeTest_ValueLeaf_UnrecordedShapeIsIdentity():
    a = _v(0, 0, 0)
    assert BRepTools_ReShape().ValueLeaf(a).IsSame(a)


def test_BRepTools_ReShapeTest_ValueLeaf_ChainEndingInRemoveReturnsNull():
    a, b = _v(0, 0, 0), _v(1, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    rs.Remove(b)
    assert rs.ValueLeaf(a).IsNull()


def test_BRepTools_ReShapeTest_Replace_DirectCycleHandledByApply():
    a, b = _v(0, 0, 0), _v(1, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    rs.Replace(b, a)
    assert rs.Value(a).IsSame(b)
    assert rs.Value(b).IsSame(a)
    assert not rs.Apply(a).IsNull()


def test_BRepTools_ReShapeTest_Replace_LongerCycleHandledByApply():
    a, b, c = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    rs.Replace(b, c)
    rs.Replace(c, a)
    assert rs.Value(a).IsSame(b)
    assert rs.Value(b).IsSame(c)
    assert rs.Value(c).IsSame(a)
    assert not rs.Apply(a).IsNull()


def test_BRepTools_ReShapeTest_Apply_HandlesStructuralContainmentWithoutCrash():
    v1, v2, v3 = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    e = _e(v1, v2)
    container = _compound(BRep_Builder(), e, v3)
    rs = BRepTools_ReShape()
    rs.Replace(e, container)
    assert not rs.Apply(e).IsNull()


def test_BRepTools_ReShapeTest_Apply_DiamondSharingIsProcessedCorrectly():
    v1, v2, v3, v2r = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0), _v(1.5, 0, 0)
    e1 = _e(v1, v2)
    e2 = _e(v2, v3)
    pair = _compound(BRep_Builder(), e1, e2)
    rs = BRepTools_ReShape()
    rs.Replace(v2, v2r)
    result = rs.Apply(pair)
    assert not result.IsNull()
    n = 0
    for v in TopExp_Explorer(result, TopAbs_VERTEX):
        assert not v.IsPartner(v2)
        if v.IsPartner(v2r):
            n += 1
    assert n >= 2


def test_BRepTools_ReShapeTest_Clear_DropsAllBindings():
    a, b = _v(0, 0, 0), _v(1, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    assert rs.Value(a).IsSame(b)
    rs.Clear()
    assert rs.Value(a).IsSame(a)
    assert rs.ValueLeaf(a).IsSame(a)


def test_BRepTools_ReShapeTest_Replace_LastWins():
    a, b, c = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, b)
    rs.Replace(a, c)
    assert rs.Value(a).IsSame(c)
    assert rs.ValueLeaf(a).IsSame(c)


def test_BRepTools_ReShapeTest_Replace_SelfIsNoOp():
    a = _v(0, 0, 0)
    rs = BRepTools_ReShape()
    rs.Replace(a, a)
    assert not rs.IsRecorded(a)
    assert rs.Value(a).IsSame(a)


def test_BRepTools_ReShapeTest_Apply_RemoveDropsSubShapeFromParent():
    v1, v2, v3 = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    parent = _compound(BRep_Builder(), v1, v2, v3)
    rs = BRepTools_ReShape()
    rs.Remove(v2)
    result = rs.Apply(parent)
    assert not result.IsNull()
    kids = list(TopoDS_Iterator(result))
    assert not any(k.IsPartner(v2) for k in kids)
    assert len(kids) == 2


def test_BRepTools_ReShapeTest_Apply_SharedEdgeAcrossTwoParents():
    v1, v2, v3 = _v(0, 0, 0), _v(1, 0, 0), _v(2, 0, 0)
    e1 = _e(v1, v2)
    e2 = _e(v2, v3)
    e1new = _e(_v(0.5, 0, 0), v2)
    b = BRep_Builder()
    pa = _compound(b, e1, v3)
    pb = _compound(b, e1, e2)
    rs = BRepTools_ReShape()
    rs.Replace(e1, e1new)
    ra = rs.Apply(pa)
    rb = rs.Apply(pb)
    assert not ra.IsNull()
    assert not rb.IsNull()
    for r in (ra, rb):
        edges = list(TopExp_Explorer(r, TopAbs_EDGE))
        assert not any(x.IsPartner(e1) for x in edges)
        assert any(x.IsPartner(e1new) for x in edges)


def test_BRepTools_ReShapeTest_Apply_NoBindingsIsIdentity():
    e = _e(_v(0, 0, 0), _v(1, 0, 0))
    assert BRepTools_ReShape().Apply(e).IsSame(e)


def test_BRepTools_ReShapeTest_Apply_DeepStructuralContainmentWithoutCrash():
    e = _e(_v(0, 0, 0), _v(1, 0, 0))
    b = BRep_Builder()
    inner = _compound(b, e)
    outer = _compound(b, inner, _v(3, 0, 0))
    rs = BRepTools_ReShape()
    rs.Replace(e, outer)
    assert not rs.Apply(e).IsNull()


def test_BRepTools_ReShapeTest_ValueLeaf_ConsidersLocationMode():
    a, b = _v(0, 0, 0), _v(1, 0, 0)
    rs = BRepTools_ReShape()
    rs.SetModeConsiderLocation(True)
    assert rs.ModeConsiderLocation()
    rs.Replace(a, b)
    assert rs.ValueLeaf(a).IsSame(b)
