# Translated from OCCT src/ModelingAlgorithms/TKOffset/GTests/BRepOffsetAPI_MakeThickSolid_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepCheck import BRepCheck_Analyzer
from nanocct.BRepGProp import BRepGProp
from nanocct.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.GProp import GProp_GProps
from nanocct.NCollection import NCollection_List
from nanocct.Precision import Precision
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer
from nanocct.TopoDS import TopoDS_Shape


def _box(size):
    maker = BRepPrimAPI_MakeBox(size, size, size)
    box = maker.Shape()
    assert maker.IsDone()
    return box


def _first_face(shape):
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    assert exp.More()
    return TopoDS.Face(exp.Current())


def _hollow(box):
    faces = NCollection_List[TopoDS_Shape]()
    faces.Append(_first_face(box))
    maker = BRepOffsetAPI_MakeThickSolid()
    maker.MakeThickSolidByJoin(box, faces, -1.0, Precision.Confusion_s())
    maker.Build()
    assert maker.IsDone()
    return maker.Shape()


def _volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def test_BRepOffsetAPI_MakeThickSolidTest_HollowBox():
    result = _hollow(_box(20.0))
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepOffsetAPI_MakeThickSolidTest_HollowBoxVolume():
    box = _box(20.0)
    orig_volume = _volume(box)
    result = _hollow(box)
    assert not result.IsNull()
    assert _volume(result) < orig_volume


def _thicken_first_face(offset):
    face = _first_face(_box(10.0))
    maker = BRepOffsetAPI_MakeThickSolid()
    maker.MakeThickSolidBySimple(face, offset)
    maker.Build()
    assert maker.IsDone()
    return face, maker.Shape()


def test_BRepOffsetAPI_MakeThickSolidTest_MakeThickSolidBySimple():
    _, result = _thicken_first_face(2.0)
    assert not result.IsNull()
    assert BRepCheck_Analyzer(result).IsValid()


def test_BRepOffsetAPI_MakeThickSolidTest_ThickSolidLargerVolume():
    face, result = _thicken_first_face(2.0)
    face_props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face, face_props)
    assert not result.IsNull()
    assert abs(_volume(result)) > face_props.Mass() * 2.0 * 0.5
