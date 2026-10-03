# Translated from OCCT src/ApplicationFramework/TKCAF/GTests/TNaming_Tool_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from nanocct.NCollection import NCollection_Map
from nanocct.TDF import TDF_Data
from nanocct.TNaming import TNaming_Builder, TNaming_NamedShape, TNaming_Tool


@pytest.fixture
def root():
    data = TDF_Data()
    root = data.Root()
    yield root
    del data


def _box(dx, dy, dz):
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape()


def _sphere(r):
    return BRepPrimAPI_MakeSphere(r).Shape()


def _ns(label):
    found, ns = label.FindAttribute(TNaming_NamedShape.GetID_s())
    assert found
    return ns


def _generated(label, shape):
    b = TNaming_Builder(label)
    b.Generated(shape)
    return b


def test_TNaming_ToolTest_GetShape_Primitive(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    got = TNaming_Tool.GetShape_s(_ns(label))
    assert not got.IsNull()
    assert got.IsSame(box)


def test_TNaming_ToolTest_OriginalShape_Modification(root):
    box1, box2 = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    label = root.FindChild(1)
    b = TNaming_Builder(label)
    b.Modify(box1, box2)
    orig = TNaming_Tool.OriginalShape_s(_ns(label))
    assert not orig.IsNull()
    assert orig.IsSame(box1)


def test_TNaming_ToolTest_CurrentShape_NoModification(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    cur = TNaming_Tool.CurrentShape_s(_ns(label))
    assert not cur.IsNull()
    assert cur.IsSame(box)


def test_TNaming_ToolTest_CurrentShape_WithModification(root):
    box1, box2 = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    label1 = root.FindChild(1)
    _generated(label1, box1)
    ns1 = _ns(label1)
    label2 = root.FindChild(2)
    b2 = TNaming_Builder(label2)
    b2.Modify(box1, box2)
    assert not TNaming_Tool.CurrentShape_s(ns1).IsNull()


def test_TNaming_ToolTest_HasLabel_ExistingShape(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    assert TNaming_Tool.HasLabel_s(label, box)


def test_TNaming_ToolTest_HasLabel_NonExistingShape(root):
    box, sphere = _box(10.0, 20.0, 30.0), _sphere(15.0)
    label = root.FindChild(1)
    _generated(label, box)
    assert not TNaming_Tool.HasLabel_s(label, sphere)


def test_TNaming_ToolTest_NamedShape_RetrieveByShape(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    ns = TNaming_Tool.NamedShape_s(box, label)
    assert ns is not None
    assert TNaming_Tool.GetShape_s(ns).IsSame(box)


def test_TNaming_ToolTest_NamedShape_NonExistingShape(root):
    box, sphere = _box(10.0, 20.0, 30.0), _sphere(15.0)
    label = root.FindChild(1)
    _generated(label, box)
    assert TNaming_Tool.NamedShape_s(sphere, label) is None


def test_TNaming_ToolTest_CurrentNamedShape_Simple(root):
    label = root.FindChild(1)
    _generated(label, _box(10.0, 20.0, 30.0))
    assert TNaming_Tool.CurrentNamedShape_s(_ns(label)) is not None


def test_TNaming_ToolTest_Label_RetrieveLabel(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    got, _trans_def = TNaming_Tool.Label_s(label, box)
    assert not got.IsNull()
    assert got.IsEqual(label)


def test_TNaming_ToolTest_GeneratedShape_Simple(root):
    old, new = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    label = root.FindChild(1)
    b = TNaming_Builder(label)
    b.Generated(old, new)
    gen = TNaming_Tool.GeneratedShape_s(old, _ns(label))
    assert not gen.IsNull()
    assert gen.IsSame(new)


def test_TNaming_ToolTest_MultipleShapes_GetShape(root):
    boxes = [_box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0), _box(30.0, 30.0, 30.0)]
    labels = [root.FindChild(i) for i in (1, 2, 3)]
    builders = [_generated(lab, box) for lab, box in zip(labels, boxes)]
    for lab, box in zip(labels, boxes):
        assert TNaming_Tool.GetShape_s(_ns(lab)).IsSame(box)
    del builders


def test_TNaming_ToolTest_ValidUntil_SimpleCase(root):
    box = _box(10.0, 20.0, 30.0)
    label = root.FindChild(1)
    _generated(label, box)
    assert TNaming_Tool.ValidUntil_s(label, box) >= 0


def test_TNaming_ToolTest_DeletedShape_CurrentShape(root):
    box = _box(10.0, 20.0, 30.0)
    label1 = root.FindChild(1)
    _generated(label1, box)
    label2 = root.FindChild(2)
    b2 = TNaming_Builder(label2)
    b2.Delete(box)
    ns1 = _ns(label1)
    TNaming_Tool.CurrentShape_s(ns1)
    TNaming_Tool.CurrentShape_s(ns1)


def test_TNaming_ToolTest_EmptyLabel_HasLabel(root):
    box = _box(10.0, 20.0, 30.0)
    empty = root.FindChild(99)
    assert not TNaming_Tool.HasLabel_s(empty, box)


def test_TNaming_ToolTest_Collect_SimpleCase(root):
    label = root.FindChild(1)
    _generated(label, _box(10.0, 20.0, 30.0))
    labels = NCollection_Map[TNaming_NamedShape]()
    TNaming_Tool.Collect_s(_ns(label), labels)


def test_TNaming_ToolTest_NamedShape_MissingUsedShapes():
    data = TDF_Data()
    root = data.Root()
    assert TNaming_Tool.NamedShape_s(_box(10.0, 20.0, 30.0), root) is None
