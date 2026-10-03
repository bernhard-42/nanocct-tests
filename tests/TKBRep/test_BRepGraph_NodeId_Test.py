# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_NodeId_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_EdgeId,
    BRepGraph_FaceId,
    BRepGraph_NodeId,
    BRepGraph_RelatedIterator,
    BRepGraph_VertexId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox

Kind = BRepGraph_NodeId.Kind


def _box_graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def test_BRepGraph_NodeIdTest_Construction_DefaultInvalid():
    face = BRepGraph_FaceId()
    assert not face.IsValid()
    assert face.Index == BRepGraph_FaceId.THE_INVALID_INDEX


def test_BRepGraph_NodeIdTest_Construction_FromIndex():
    face = BRepGraph_FaceId(5)
    assert face.IsValid()
    assert face.Index == 5


def test_BRepGraph_NodeIdTest_TypedAliases_ConstructFromIndex():
    face = BRepGraph_FaceId(3)
    assert face.IsValid()
    assert face.Index == 3
    assert BRepGraph_EdgeId(7).Index == 7


def test_BRepGraph_NodeIdTest_ImplicitConversion_ToNodeId():
    node = BRepGraph_NodeId(BRepGraph_FaceId(5))
    assert node.NodeKind == Kind.Face
    assert node.Index == 5


def test_BRepGraph_NodeIdTest_ImplicitConversion_PassToFunction():
    g = _box_graph()
    nb_adjacent = 0
    it = BRepGraph_RelatedIterator(g, BRepGraph_NodeId(BRepGraph_FaceId(0)))
    while it.More():
        if it.CurrentRelation() == BRepGraph_RelatedIterator.RelationKind.AdjacentFace:
            nb_adjacent += 1
        it.Next()
    assert nb_adjacent > 0


def test_BRepGraph_NodeIdTest_FromNodeId_CorrectKind():
    edge = BRepGraph_EdgeId.FromNodeId_s(BRepGraph_NodeId(Kind.Edge, 3))
    assert edge.Index == 3


def test_BRepGraph_NodeIdTest_Comparison_TypedVsTyped():
    f1, f2, f3 = BRepGraph_FaceId(3), BRepGraph_FaceId(3), BRepGraph_FaceId(5)
    assert f1 == f2
    assert f1 != f3


def test_BRepGraph_NodeIdTest_Comparison_TypedVsNodeId():
    face = BRepGraph_FaceId(3)
    match = BRepGraph_NodeId(Kind.Face, 3)
    diff_kind = BRepGraph_NodeId(Kind.Edge, 3)
    diff_idx = BRepGraph_NodeId(Kind.Face, 5)
    assert face == match
    assert match == face
    assert face != diff_kind
    assert face != diff_idx


def test_BRepGraph_NodeIdTest_Hash_ConsistentWithNodeId():
    face = BRepGraph_FaceId(5)
    assert hash(face) == hash(BRepGraph_NodeId(face))


def test_BRepGraph_NodeIdTest_UntypedArithmetic_PreservesKindAndIndex():
    # ++/-- are not bound; the +/- offset operators are.
    node = BRepGraph_NodeId(Kind.Face, 4)
    advanced = node + 3
    assert advanced.NodeKind == Kind.Face
    assert advanced.Index == 7
    retreated = advanced - 5
    assert retreated.NodeKind == Kind.Face
    assert retreated.Index == 2


def test_BRepGraph_NodeIdTest_TypedArithmetic_PreservesKindAndIndex():
    face = BRepGraph_FaceId(4)
    advanced = face + 3
    assert advanced.Index == 7
    retreated = advanced - 5
    assert retreated.Index == 2
    node = BRepGraph_NodeId(advanced)
    assert node.NodeKind == Kind.Face
    assert node.Index == 7


def test_BRepGraph_NodeIdTest_TypedArithmetic_IndexZeroBoundary():
    edge = BRepGraph_EdgeId(0)
    assert edge.IsValid()
    edge = edge + 1
    assert edge.Index == 1
    zero = edge - 1
    assert zero.Index == 0
    assert zero.IsValid()
    invalid = zero - 1
    assert invalid.Index == BRepGraph_EdgeId.THE_INVALID_INDEX
    assert not invalid.IsValid()


def test_BRepGraph_NodeIdTest_FromNodeId_WrongKindReturnsInvalid():
    edge = BRepGraph_EdgeId.FromNodeId_s(BRepGraph_NodeId(Kind.Face, 3))
    assert not edge.IsValid()
    assert edge.Index == BRepGraph_EdgeId.THE_INVALID_INDEX


def test_BRepGraph_NodeIdTest_OutOfRangeMetadataQueriesReturnFalse():
    g = _box_graph()
    vertex = BRepGraph_VertexId(g.Topo().Vertices().Nb())
    assert not vertex.IsRemoved(g)
    assert not vertex.IsOwned(g)
    face = BRepGraph_NodeId(Kind.Face, g.Topo().Faces().Nb())
    assert not face.IsRemoved(g)
    assert not face.IsOwned(g)
