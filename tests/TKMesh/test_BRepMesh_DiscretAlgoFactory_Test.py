# Translated from OCCT src/ModelingAlgorithms/TKMesh/GTests/BRepMesh_DiscretAlgoFactory_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepMesh import BRepMesh_DiscretAlgoFactory, BRepMesh_DiscretFactory
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox


@pytest.fixture
def box():
    return BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape()


def test_BRepMesh_DiscretAlgoFactoryTest_Factories_AtLeastOneRegistered():
    assert BRepMesh_DiscretAlgoFactory.Factories_s().IsEmpty() is False


def test_BRepMesh_DiscretAlgoFactoryTest_DefaultFactory_ReturnsValid():
    assert BRepMesh_DiscretAlgoFactory.DefaultFactory_s() is not None


def test_BRepMesh_DiscretAlgoFactoryTest_FindFactory_FastDiscret():
    factory = BRepMesh_DiscretAlgoFactory.FindFactory_s("FastDiscret")
    assert factory is not None
    assert str(factory.Name()) == "FastDiscret"


def test_BRepMesh_DiscretAlgoFactoryTest_FindFactory_NonExistent_ReturnsNull():
    assert BRepMesh_DiscretAlgoFactory.FindFactory_s("NonExistentFactory") is None


def test_BRepMesh_DiscretAlgoFactoryTest_CreateAlgorithm_ReturnsValid(box):
    factory = BRepMesh_DiscretAlgoFactory.DefaultFactory_s()
    assert factory is not None
    assert factory.CreateAlgorithm(box, 0.1, 0.5) is not None


def test_BRepMesh_DiscretAlgoFactoryTest_CreateAlgorithm_CanMesh(box):
    factory = BRepMesh_DiscretAlgoFactory.DefaultFactory_s()
    assert factory is not None
    algo = factory.CreateAlgorithm(box, 0.1, 0.5)
    assert algo is not None
    algo.Perform()
    assert algo.IsDone() is True


def test_BRepMesh_DiscretAlgoFactoryTest_DiscretFactory_UsesRegistry(box):
    factory = BRepMesh_DiscretFactory.Get_s()
    algo = factory.Discret(box, 0.1, 0.5)
    assert algo is not None
    algo.Perform()
    assert algo.IsDone() is True


def test_BRepMesh_DiscretAlgoFactoryTest_DiscretFactory_SetDefaultName():
    factory = BRepMesh_DiscretFactory.Get_s()
    assert factory.SetDefaultName("FastDiscret") is True
    assert str(factory.DefaultName()) == "FastDiscret"


def test_BRepMesh_DiscretAlgoFactoryTest_RegisterFactory_Uniqueness():
    count = sum(1 for f in BRepMesh_DiscretAlgoFactory.Factories_s() if str(f.Name()) == "FastDiscret")
    assert count == 1
