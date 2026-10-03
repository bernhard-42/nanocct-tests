# Translated from OCCT src/ApplicationFramework/TKCAF/GTests/TNaming_NamedShape_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.TDocStd import TDocStd_Application
from nanocct.TNaming import (
    TNaming_Builder,
    TNaming_DELETE,
    TNaming_GENERATED,
    TNaming_Iterator,
    TNaming_MODIFY,
    TNaming_NamedShape,
    TNaming_NewShapeIterator,
    TNaming_PRIMITIVE,
    TNaming_SELECTED,
)


class _Fixture:
    def __init__(self):
        self.app = TDocStd_Application()
        self.doc = self.app.NewDocument__TDocStd_Document("BinOcaf")
        self.doc.SetUndoLimit(10)
        self.label = self.doc.Main().FindChild(1)


@pytest.fixture
def fx():
    return _Fixture()


def _box(dx, dy, dz):
    return BRepPrimAPI_MakeBox(dx, dy, dz).Shape()


def _ns(label):
    found, ns = label.FindAttribute(TNaming_NamedShape.GetID_s())
    assert found
    return ns


def test_TNaming_NamedShapeTest_Generated_Primitive(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 20.0, 30.0))
    assert _ns(fx.label).Evolution() == TNaming_PRIMITIVE


def test_TNaming_NamedShapeTest_Generated_FromOld(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0))
    assert _ns(fx.label).Evolution() == TNaming_GENERATED


def test_TNaming_NamedShapeTest_Modify_Shape(fx):
    b = TNaming_Builder(fx.label)
    b.Modify(_box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0))
    assert _ns(fx.label).Evolution() == TNaming_MODIFY


def test_TNaming_NamedShapeTest_Delete_Shape(fx):
    b = TNaming_Builder(fx.label)
    b.Delete(_box(10.0, 20.0, 30.0))
    assert _ns(fx.label).Evolution() == TNaming_DELETE


def test_TNaming_NamedShapeTest_Select_Shape(fx):
    b = TNaming_Builder(fx.label)
    b.Select(_box(10.0, 20.0, 30.0), _box(50.0, 50.0, 50.0))
    assert _ns(fx.label).Evolution() == TNaming_SELECTED


def test_TNaming_NamedShapeTest_NamedShape_ReturnsAttribute(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 20.0, 30.0))
    ns = b.NamedShape()
    assert ns is not None
    assert ns == _ns(fx.label)


def test_TNaming_NamedShapeTest_IsEmpty_NewAttribute(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 10.0, 10.0))
    ns = _ns(fx.label)
    assert not ns.IsEmpty()
    ns.Clear()
    assert ns.IsEmpty()


def test_TNaming_NamedShapeTest_Evolution_ReflectsBuilder(fx):
    old, new = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    b = TNaming_Builder(fx.label)
    b.Modify(old, new)
    assert _ns(fx.label).Evolution() == TNaming_MODIFY
    label2 = fx.doc.Main().FindChild(2)
    b2 = TNaming_Builder(label2)
    b2.Generated(old, new)
    assert _ns(label2).Evolution() == TNaming_GENERATED


def test_TNaming_NamedShapeTest_Get_ReturnsPrimitiveShape(fx):
    box = _box(10.0, 20.0, 30.0)
    b = TNaming_Builder(fx.label)
    b.Generated(box)
    result = _ns(fx.label).Get()
    assert not result.IsNull()
    assert result.IsSame(box)


def test_TNaming_NamedShapeTest_Version_SetAndGet(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 10.0, 10.0))
    ns = _ns(fx.label)
    ns.SetVersion(42)
    assert ns.Version() == 42
    ns.SetVersion(0)
    assert ns.Version() == 0


def test_TNaming_NamedShapeTest_Clear_EmptiesAttribute(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 20.0, 30.0))
    ns = _ns(fx.label)
    assert not ns.IsEmpty()
    ns.Clear()
    assert ns.IsEmpty()
    assert ns.Get().IsNull()


def test_TNaming_NamedShapeTest_Iterator_TraversesPairs(fx):
    old, new = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    b = TNaming_Builder(fx.label)
    b.Generated(old, new)
    ns = _ns(fx.label)
    count = 0
    it = TNaming_Iterator(ns)
    while it.More():
        assert it.OldShape().IsSame(old)
        assert it.NewShape().IsSame(new)
        count += 1
        it.Next()
    assert count == 1


def test_TNaming_NamedShapeTest_Iterator_IsModification(fx):
    old, new = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0)
    b = TNaming_Builder(fx.label)
    b.Modify(old, new)
    ns = _ns(fx.label)
    it = TNaming_Iterator(ns)
    while it.More():
        assert it.IsModification()
        assert it.Evolution() == TNaming_MODIFY
        it.Next()

    label2 = fx.doc.Main().FindChild(2)
    b2 = TNaming_Builder(label2)
    b2.Generated(old, new)
    ns2 = _ns(label2)
    it2 = TNaming_Iterator(ns2)
    while it2.More():
        assert not it2.IsModification()
        assert it2.Evolution() == TNaming_GENERATED
        it2.Next()


def test_TNaming_NamedShapeTest_Iterator_MultipleShapes(fx):
    b = TNaming_Builder(fx.label)
    b.Generated(_box(10.0, 10.0, 10.0))
    b.Generated(_box(20.0, 20.0, 20.0))
    b.Generated(_box(30.0, 30.0, 30.0))
    ns = _ns(fx.label)
    count = 0
    it = TNaming_Iterator(ns)
    while it.More():
        assert it.OldShape().IsNull()
        assert not it.NewShape().IsNull()
        count += 1
        it.Next()
    assert count == 3


def test_TNaming_NamedShapeTest_NewShapeIterator_FollowsModification(fx):
    box1, box2, box3 = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0), _box(30.0, 30.0, 30.0)
    main = fx.doc.Main()
    b1 = TNaming_Builder(main.FindChild(1))
    b1.Generated(box1)
    b2 = TNaming_Builder(main.FindChild(2))
    b2.Modify(box1, box2)
    b3 = TNaming_Builder(main.FindChild(3))
    b3.Modify(box2, box3)

    it = TNaming_NewShapeIterator(box1, main)
    assert it.More()
    assert it.Shape().IsSame(box2)
    assert it.IsModification()

    it2 = TNaming_NewShapeIterator(box2, main)
    assert it2.More()
    assert it2.Shape().IsSame(box3)


def test_TNaming_NamedShapeTest_NewShapeIterator_MultipleBranches(fx):
    box1, mod1, mod2 = _box(10.0, 10.0, 10.0), _box(20.0, 20.0, 20.0), _box(30.0, 30.0, 30.0)
    main = fx.doc.Main()
    b1 = TNaming_Builder(main.FindChild(1))
    b1.Generated(box1)
    b2 = TNaming_Builder(main.FindChild(2))
    b2.Modify(box1, mod1)
    b3 = TNaming_Builder(main.FindChild(3))
    b3.Modify(box1, mod2)

    count = 0
    it = TNaming_NewShapeIterator(box1, main)
    while it.More():
        s = it.Shape()
        assert s.IsSame(mod1) or s.IsSame(mod2)
        count += 1
        it.Next()
    assert count == 2


def test_TNaming_NamedShapeTest_UndoRedo_RestoresNamedShape(fx):
    box = _box(10.0, 20.0, 30.0)
    fx.doc.NewCommand()
    b = TNaming_Builder(fx.label)
    b.Generated(box)
    del b
    fx.doc.CommitCommand()

    ns = _ns(fx.label)
    assert not ns.IsEmpty()
    assert ns.Get().IsSame(box)

    fx.doc.Undo()
    found, _ = fx.label.FindAttribute(TNaming_NamedShape.GetID_s())
    assert not found

    fx.doc.Redo()
    ns_redo = _ns(fx.label)
    assert not ns_redo.IsEmpty()
    assert ns_redo.Get().IsSame(box)
