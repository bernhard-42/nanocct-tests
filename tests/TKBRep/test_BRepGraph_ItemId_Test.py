# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_ItemId_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import BRepGraph_ItemId, BRepGraph_NodeId, BRepGraph_RefId


def test_BRepGraph_ItemIdTest_Default_IsInvalid():
    item = BRepGraph_ItemId()
    assert not item.IsValid()
    assert not item.IsNode()
    assert not item.IsReference()


def test_BRepGraph_ItemIdTest_NodeRoundTrip():
    node = BRepGraph_NodeId(BRepGraph_NodeId.Kind.Face, 3)
    item = BRepGraph_ItemId(node)
    assert item.IsValid()
    assert item.IsNode()
    assert not item.IsReference()
    assert item.ItemDomain() == BRepGraph_ItemId.Domain.Node
    assert item.NodeKind() == BRepGraph_NodeId.Kind.Face
    assert item.NodeId() == node
    assert not item.RefId().IsValid()


def test_BRepGraph_ItemIdTest_ReferenceRoundTrip():
    ref = BRepGraph_RefId(BRepGraph_RefId.Kind.Wire, 4)
    item = BRepGraph_ItemId(ref)
    assert item.IsValid()
    assert not item.IsNode()
    assert item.IsReference()
    assert item.ItemDomain() == BRepGraph_ItemId.Domain.Reference
    assert item.RefKind() == BRepGraph_RefId.Kind.Wire
    assert item.RefId() == ref
    assert not item.NodeId().IsValid()
