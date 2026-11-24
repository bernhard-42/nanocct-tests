# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_UBTree_Test.cxx (LGPL-2.1 with the OCCT exception)
# NCollection_EBTree<int, TestBnd1D> (TestBnd1D is the test's own 1D interval) is not bound: substituted by
# IMeshData.NCollection_EBTree__int__Bnd_Box2d in all translated cases, with the interval [Min, Max] mapped to the
# box [Min, Max] x [0, 0]. The bounding type only shapes the tree; the tested object bookkeeping (Add, Contains,
# Remove, FindNode, IsEmpty) is unchanged.
# Not translated: all NCollection_UBTreeTest cases (EmptyTree, AddAndSelect_SingleObject,
# AddAndSelect_MultipleObjects, StopSelector, Clear, ManyObjects, DeepUnbalancedTree, MoveConstructor,
# MoveAssignment) and NCollection_EBTreeTest SelectAfterRemove: Select needs a Python subclass of the abstract
# UBTree::Selector (no trampolines). NCollection_EBTreeTest MoveConstructor, MoveAssignment: move semantics (not
# bound), and Select as above.
from nanocct.Bnd import Bnd_Box2d
from nanocct.IMeshData import NCollection_EBTree__int__Bnd_Box2d as EBTree


def _bnd(theMin, theMax):
    aBox = Bnd_Box2d()
    aBox.Update(theMin, 0.0, theMax, 0.0)
    return aBox


def test_NCollection_EBTreeTest_AddContainsRemove():
    aTree = EBTree()
    assert aTree.IsEmpty()

    aTree.Add(1, _bnd(0.0, 2.0))
    aTree.Add(2, _bnd(3.0, 5.0))
    aTree.Add(3, _bnd(4.0, 6.0))

    assert aTree.Contains(1)
    assert aTree.Contains(2)
    assert aTree.Contains(3)
    assert not aTree.Contains(4)

    assert not aTree.Add(1, _bnd(0.0, 2.0))

    assert aTree.Remove(2)
    assert not aTree.Contains(2)
    assert aTree.Contains(1)
    assert aTree.Contains(3)

    assert not aTree.Remove(4)


def test_NCollection_EBTreeTest_RemoveRoot():
    aTree = EBTree()
    aTree.Add(1, _bnd(0.0, 5.0))
    assert aTree.Contains(1)

    assert aTree.Remove(1)
    assert aTree.IsEmpty()


def test_NCollection_EBTreeTest_FindNode():
    aTree = EBTree()
    aTree.Add(1, _bnd(0.0, 2.0))
    aTree.Add(2, _bnd(3.0, 5.0))

    aNode = aTree.FindNode(1)
    assert aNode.IsLeaf()
    assert aNode.Object() == 1


def test_NCollection_EBTreeTest_RemoveAll():
    aTree = EBTree()
    aTree.Add(1, _bnd(0.0, 2.0))
    aTree.Add(2, _bnd(3.0, 5.0))
    aTree.Add(3, _bnd(4.0, 6.0))

    assert aTree.Remove(1)
    assert aTree.Remove(2)
    assert aTree.Remove(3)
    assert aTree.IsEmpty()
