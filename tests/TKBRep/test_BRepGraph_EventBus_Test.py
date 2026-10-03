# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_EventBus_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Most OCCT tests here use C++ subclasses of BRepGraph_Layer that record events; BRepGraph_Layer has no Python
# constructor, so those are not translated. Tests that only need "some registered layer" use the concrete
# BRepGraph_LayerLock / BRepGraph_LayerDeferred instead of the recording test layer.

import pytest

from nanocct.BRepGraph import (
    BRepGraph,
    BRepGraph_EdgeId,
    BRepGraph_Layer,
    BRepGraph_LayerDeferred,
    BRepGraph_LayerIterator,
    BRepGraph_LayerLock,
    BRepGraph_NodeId,
    BRepGraph_RefId,
)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox


@pytest.fixture
def graph():
    g = BRepGraph()
    g.Clear()
    g.Shapes().Add(BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape())
    assert not g.IsEmpty()
    return g


def _bit_count(v):
    return bin(v).count("1")


def test_BRepGraph_EventBusTest_ZeroCost_NoSubscribers(graph):
    e0 = BRepGraph_EdgeId.Start_s()
    mut = graph.Editor().Edges().Mut(e0)
    graph.Editor().Edges().SetTolerance(mut, 0.5)
    del mut  # end of the C++ guard scope: the destructor fires markModified
    assert graph.Topo().Edges().Definition(e0).OwnGen > 0


def test_BRepGraph_EventBusTest_FindLayer_ByGuid_ReturnsRegisteredLayer(graph):
    layer = BRepGraph_LayerLock()
    graph.LayerRegistry().RegisterLayer(layer)
    assert graph.LayerRegistry().FindLayer(layer.ID()) is layer
    found, _slot = graph.LayerRegistry().FindSlot(layer.ID())
    assert found


def test_BRepGraph_EventBusTest_KindBit_Helpers():
    Kind = BRepGraph_NodeId.Kind
    kinds = [
        Kind.Solid,
        Kind.Shell,
        Kind.Face,
        Kind.Wire,
        Kind.Edge,
        Kind.Vertex,
        Kind.Compound,
        Kind.CompSolid,
    ]
    all_bits = 0
    for k in kinds:
        assert BRepGraph_Layer.KindBit_s(k) == 1 << k.value
        all_bits |= BRepGraph_Layer.KindBit_s(k)
    assert _bit_count(all_bits) == 8


def test_BRepGraph_EventBusTest_RefKindBit_Helpers():
    Kind = BRepGraph_RefId.Kind
    kinds = [Kind.Shell, Kind.Face, Kind.Wire, Kind.Vertex, Kind.Solid, Kind.Child, Kind.Occurrence]
    all_bits = 0
    for k in kinds:
        assert BRepGraph_Layer.RefKindBit_s(k) == 1 << k.value
        all_bits |= BRepGraph_Layer.RefKindBit_s(k)
    assert _bit_count(all_bits) == 7


def test_BRepGraph_EventBusTest_LayerIterator_TraditionalLoop(graph):
    reg = graph.LayerRegistry()
    base = reg.NbLayers()
    reg.RegisterLayer(BRepGraph_LayerLock())
    reg.RegisterLayer(BRepGraph_LayerDeferred())

    count = 0
    it = BRepGraph_LayerIterator(reg)
    while it.More():
        assert it.Value() is not None
        assert reg.Layer(it.Slot()) is it.Value()
        count += 1
        it.Next()
    assert count == base + 2


def test_BRepGraph_EventBusTest_LayerIterator_RangeFor(graph):
    reg = graph.LayerRegistry()
    base = reg.NbLayers()
    layer1 = BRepGraph_LayerLock()
    layer2 = BRepGraph_LayerDeferred()
    reg.RegisterLayer(layer1)
    reg.RegisterLayer(layer2)

    count = 0
    has1 = False
    has2 = False
    for layer in BRepGraph_LayerIterator(reg):
        if layer is layer1:
            has1 = True
        if layer is layer2:
            has2 = True
        count += 1
    assert count == base + 2
    assert has1
    assert has2


def test_BRepGraph_EventBusTest_LayerIterator_RangeFor_DefaultLayers(graph):
    reg = graph.LayerRegistry()
    assert reg.NbLayers() >= 1
    count = sum(1 for _ in BRepGraph_LayerIterator(reg))
    assert count == reg.NbLayers()
