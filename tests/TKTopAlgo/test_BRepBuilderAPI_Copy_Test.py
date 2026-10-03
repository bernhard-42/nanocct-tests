# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/BRepBuilderAPI_Copy_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepBuilderAPI import BRepBuilderAPI_Copy
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.GProp import GProp_GProps
from nanocct.Precision import Precision


def _box():
    mk = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0)
    box = mk.Shape()
    assert mk.IsDone()
    return box


def _volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def test_BRepBuilderAPI_CopyTest_CopyIsValid():
    copy = BRepBuilderAPI_Copy(_box()).Shape()
    assert not copy.IsNull()
    assert BRepCheck_Analyzer(copy).IsValid()


def test_BRepBuilderAPI_CopyTest_CopyVolume():
    box = _box()
    copy = BRepBuilderAPI_Copy(box).Shape()
    assert not copy.IsNull()
    assert abs(_volume(copy) - _volume(box)) <= Precision.Confusion_s()


def test_BRepBuilderAPI_CopyTest_CopyIsDistinct():
    box = _box()
    copy = BRepBuilderAPI_Copy(box).Shape()
    assert not copy.IsNull()
    assert not copy.IsEqual(box)


def test_BRepBuilderAPI_CopyTest_CopyGeomTrue():
    box = _box()
    copy = BRepBuilderAPI_Copy(box, True).Shape()
    assert not copy.IsNull()
    assert abs(_volume(copy) - _volume(box)) <= Precision.Confusion_s()


def test_BRepBuilderAPI_CopyTest_CopyGeomFalse():
    copy = BRepBuilderAPI_Copy(_box(), False).Shape()
    assert not copy.IsNull()
    assert BRepCheck_Analyzer(copy).IsValid()
