# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_LayerIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
# The C++ test derives its own TestLayer from BRepGraph_Layer; Python cannot subclass it (no trampoline),
# so the concrete built-in layers History, Deferred and Lock stand in for LayerA/B/C.
from nanocct.BRepGraph import (
    BRepGraph_LayerDeferred,
    BRepGraph_LayerHistory,
    BRepGraph_LayerIterator,
    BRepGraph_LayerLock,
    BRepGraph_LayerRegistry,
)


def test_BRepGraph_LayerIteratorTest_EmptyRegistry_IsEmpty():
    registry = BRepGraph_LayerRegistry()
    it = BRepGraph_LayerIterator(registry)
    assert not it.More()
    assert it.NbLayers() == 0
    assert registry.Layer(0) is None


def test_BRepGraph_LayerIteratorTest_SingleLayer_IteratesOnce():
    registry = BRepGraph_LayerRegistry()
    layer = BRepGraph_LayerHistory()
    registry.RegisterLayer(layer)

    it = BRepGraph_LayerIterator(registry)
    assert it.More()
    assert it.NbLayers() == 1
    assert it.Slot() == 0
    assert it.Value() is not None
    assert it.Value().Name().ToCString() == layer.Name().ToCString()
    it.Next()
    assert not it.More()


def test_BRepGraph_LayerIteratorTest_MultipleLayers_IteratesAll():
    registry = BRepGraph_LayerRegistry()
    layers = [BRepGraph_LayerHistory(), BRepGraph_LayerDeferred(), BRepGraph_LayerLock()]
    for layer in layers:
        registry.RegisterLayer(layer)

    n = 0
    it = BRepGraph_LayerIterator(registry)
    while it.More():
        assert it.Value() is not None
        assert it.Slot() == n
        n += 1
        it.Next()
    assert n == 3


def test_BRepGraph_LayerIteratorTest_RangeFor_WorksCorrectly():
    registry = BRepGraph_LayerRegistry()
    registry.RegisterLayer(BRepGraph_LayerHistory())
    registry.RegisterLayer(BRepGraph_LayerDeferred())

    n = 0
    for layer in BRepGraph_LayerIterator(registry):
        assert layer is not None
        n += 1
    assert n == 2
