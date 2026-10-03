# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepGraph_CacheRegistry_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# The OCCT tests use C++ subclasses of BRepGraph_Cache (TestCache with a free GUID, EntryTestCache using
# protected entry helpers). BRepGraph_Cache has no Python constructor, so only the registry tests that work
# with one concrete cache (BRepGraph_CacheDerivedState, fixed GUID) are translated.

from nanocct.BRepGraph import BRepGraph_CacheDerivedState, BRepGraph_CacheRegistry


def test_BRepGraph_CacheRegistryTest_Register_SameGUID_SameSlot():
    kind1 = BRepGraph_CacheDerivedState()
    kind2 = BRepGraph_CacheDerivedState()
    registry = BRepGraph_CacheRegistry()
    slot1 = registry.RegisterCache(kind1)
    slot2 = registry.RegisterCache(kind2)
    assert slot1 == slot2


def test_BRepGraph_CacheRegistryTest_FindSlot_ByGUID_ReturnsCorrectSlot():
    kind = BRepGraph_CacheDerivedState()
    registry = BRepGraph_CacheRegistry()
    expected = registry.RegisterCache(kind)
    found, slot = registry.FindSlot(kind.ID())
    assert found
    assert slot == expected


def test_BRepGraph_CacheRegistryTest_FindCache_BySlot_ReturnsCorrectDescriptor():
    kind = BRepGraph_CacheDerivedState()
    registry = BRepGraph_CacheRegistry()
    slot = registry.RegisterCache(kind)
    found = registry.Cache(slot)
    assert found is not None
    assert found.ID() == kind.ID()
    assert found.Name().IsEqual(kind.Name())


def test_BRepGraph_CacheRegistryTest_Cache_InvalidSlot_ReturnsNull():
    assert BRepGraph_CacheRegistry().Cache(0) is None
