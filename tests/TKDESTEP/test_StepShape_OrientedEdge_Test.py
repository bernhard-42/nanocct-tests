# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepShape_OrientedEdge_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.StepShape import StepShape_Edge, StepShape_OrientedEdge, StepShape_Vertex
from nanocct.TCollection import TCollection_HAsciiString


def test_StepShape_OrientedEdgeTest_ResolvesNestedOrientation():
    name = TCollection_HAsciiString("edge")
    start, end = StepShape_Vertex(), StepShape_Vertex()
    edge = StepShape_Edge()
    edge.Init(name, start, end)
    reversed_edge = StepShape_OrientedEdge()
    reversed_edge.Init(name, edge, False)
    nested = StepShape_OrientedEdge()
    nested.Init(name, reversed_edge, True)
    assert nested.EdgeStart() is end
    assert nested.EdgeEnd() is start


def test_StepShape_OrientedEdgeTest_RejectsCycles():
    name = TCollection_HAsciiString("edge")
    edge = StepShape_OrientedEdge()
    edge.Init(name, edge, True)
    assert edge.EdgeStart() is None
    assert edge.EdgeEnd() is None
    other = StepShape_OrientedEdge()
    other.Init(name, edge, True)
    edge.SetEdgeElement(other)
    assert edge.EdgeStart() is None
    assert edge.EdgeEnd() is None
    edge.SetEdgeElement(None)


def test_StepShape_OrientedEdgeTest_ResolvesDeepAcyclicNesting():
    name = TCollection_HAsciiString("edge")
    start, end = StepShape_Vertex(), StepShape_Vertex()
    edge = StepShape_Edge()
    edge.Init(name, start, end)
    is_reversed = False
    for i in range(256):
        is_forward = i % 3 != 0
        oriented = StepShape_OrientedEdge()
        oriented.Init(name, edge, is_forward)
        edge = oriented
        if is_forward is False:
            is_reversed = not is_reversed
    assert edge.EdgeStart() is (end if is_reversed else start)
    assert edge.EdgeEnd() is (start if is_reversed else end)
