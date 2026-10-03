# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_Tree_Test.cxx (LGPL-2.1 with the OCCT exception)
# Child<K>(node) is a C++ template (not bound); it reads NodeInfoBuffer()[node][K + 1], i.e. .y() / .z().
# ChangeChild<0>(node) writes the same slot as BegPrimitive(node) -> SetBegPrimitive.
from nanocct.BOPTools import BVH_Tree__double__2__BVH_BinaryTree as Tree2
from nanocct.BVH import BVH_Tree__double__3__BVH_BinaryTree as Tree3
from nanocct.BVH import BVH_Vec2d, BVH_Vec3d as V
from nanocct.Bnd import BVH_Box__double__3 as Box3

TOL = 1e-7


def near(a, b, tol=TOL):
    assert abs(a - b) <= tol, (a, b)


def child(tree, node, k):
    info = tree.NodeInfoBuffer()[node]
    return info.y() if k == 0 else info.z()


def test_BVH_TreeTest_DefaultConstructor():
    t = Tree3()
    assert t.Length() == 0
    assert t.Depth() == 0


def test_BVH_TreeTest_AddLeafNode():
    t = Tree3()
    idx = t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 10)
    assert idx == 0
    assert t.Length() == 1
    assert t.IsOuter(0)
    assert t.BegPrimitive(0) == 0
    assert t.EndPrimitive(0) == 10
    assert t.NbPrimitives(0) == 11


def test_BVH_TreeTest_AddInnerNode():
    t = Tree3()
    l1 = t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 5)
    l2 = t.AddLeafNode(V(2.0, 0.0, 0.0), V(3.0, 1.0, 1.0), 6, 10)
    root = t.AddInnerNode(V(0.0, 0.0, 0.0), V(3.0, 1.0, 1.0), l1, l2)
    assert t.Length() == 3
    assert not t.IsOuter(root)
    assert child(t, root, 0) == l1
    assert child(t, root, 1) == l2


def test_BVH_TreeTest_MinMaxPoints():
    t = Tree3()
    t.AddLeafNode(V(1.0, 2.0, 3.0), V(4.0, 5.0, 6.0), 0, 0)
    near(t.MinPoint(0).x(), 1.0)
    near(t.MinPoint(0).y(), 2.0)
    near(t.MinPoint(0).z(), 3.0)
    near(t.MaxPoint(0).x(), 4.0)
    near(t.MaxPoint(0).y(), 5.0)
    near(t.MaxPoint(0).z(), 6.0)


def test_BVH_TreeTest_Clear():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    t.AddLeafNode(V(1.0, 0.0, 0.0), V(2.0, 1.0, 1.0), 1, 1)
    assert t.Length() == 2
    t.Clear()
    assert t.Length() == 0
    assert t.Depth() == 0


def test_BVH_TreeTest_Reserve():
    t = Tree3()
    t.Reserve(100)
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    assert t.Length() == 1


def test_BVH_TreeTest_SetOuterInner():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    assert t.IsOuter(0)
    t.SetInner(0)
    assert not t.IsOuter(0)
    t.SetOuter(0)
    assert t.IsOuter(0)


def test_BVH_TreeTest_Level():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    assert t.Level(0) == 0
    t.SetLevel(0, 5)  # C++: aTree.Level(0) = 5
    assert t.Level(0) == 5


def test_BVH_TreeTest_AddLeafNodeWithBox():
    t = Tree3()
    idx = t.AddLeafNode(Box3(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0)), 0, 5)
    assert idx == 0
    assert t.IsOuter(0)
    assert t.BegPrimitive(0) == 0
    assert t.EndPrimitive(0) == 5


def test_BVH_TreeTest_AddInnerNodeWithBox():
    t = Tree3()
    l1 = t.AddLeafNode(Box3(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0)), 0, 5)
    l2 = t.AddLeafNode(Box3(V(2.0, 0.0, 0.0), V(3.0, 1.0, 1.0)), 6, 10)
    root = t.AddInnerNode(Box3(V(0.0, 0.0, 0.0), V(3.0, 1.0, 1.0)), l1, l2)
    assert not t.IsOuter(root)
    assert child(t, root, 0) == l1
    assert child(t, root, 1) == l2


def test_BVH_TreeTest_EstimateSAH():
    t = Tree3()
    l1 = t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    l2 = t.AddLeafNode(V(2.0, 0.0, 0.0), V(3.0, 1.0, 1.0), 1, 1)
    t.AddInnerNode(V(0.0, 0.0, 0.0), V(3.0, 1.0, 1.0), l1, l2)
    assert t.EstimateSAH() > 0.0


def test_BVH_TreeTest_NbPrimitives():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 5, 15)
    assert t.NbPrimitives(0) == 11


def test_BVH_TreeTest_SinglePrimitive():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 7, 7)
    assert t.NbPrimitives(0) == 1
    assert t.BegPrimitive(0) == 7
    assert t.EndPrimitive(0) == 7


def test_BVH_TreeTest_Tree2D():
    t = Tree2()
    t.AddLeafNode(BVH_Vec2d(0.0, 0.0), BVH_Vec2d(1.0, 1.0), 0, 5)
    assert t.Length() == 1
    near(t.MinPoint(0).x(), 0.0)
    near(t.MinPoint(0).y(), 0.0)


def test_BVH_TreeTest_MultipleLeaves():
    t = Tree3()
    for i in range(10):
        t.AddLeafNode(V(i * 1.0, 0.0, 0.0), V(i * 1.0 + 1.0, 1.0, 1.0), i, i)
    assert t.Length() == 10
    for i in range(10):
        assert t.IsOuter(i)
        assert t.BegPrimitive(i) == i
        assert t.EndPrimitive(i) == i


def test_BVH_TreeTest_DeepTree():
    t = Tree3()
    l1 = t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    l2 = t.AddLeafNode(V(1.0, 0.0, 0.0), V(2.0, 1.0, 1.0), 1, 1)
    l3 = t.AddLeafNode(V(2.0, 0.0, 0.0), V(3.0, 1.0, 1.0), 2, 2)
    l4 = t.AddLeafNode(V(3.0, 0.0, 0.0), V(4.0, 1.0, 1.0), 3, 3)
    i1 = t.AddInnerNode(V(0.0, 0.0, 0.0), V(2.0, 1.0, 1.0), l1, l2)
    i2 = t.AddInnerNode(V(2.0, 0.0, 0.0), V(4.0, 1.0, 1.0), l3, l4)
    root = t.AddInnerNode(V(0.0, 0.0, 0.0), V(4.0, 1.0, 1.0), i1, i2)
    assert t.Length() == 7
    assert not t.IsOuter(root)
    assert not t.IsOuter(i1)
    assert not t.IsOuter(i2)
    assert t.IsOuter(l1)
    assert t.IsOuter(l4)


def test_BVH_TreeTest_ModifyPrimitiveIndices():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 5)
    t.SetBegPrimitive(0, 10)
    t.SetEndPrimitive(0, 20)
    assert t.BegPrimitive(0) == 10
    assert t.EndPrimitive(0) == 20
    assert t.NbPrimitives(0) == 11


def test_BVH_TreeTest_ModifyMinMaxPoints():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    # C++: aTree.MinPoint(0) = BVH_Vec3d(...)  (non-const reference)
    t.MinPoint(0).SetValues(-1.0, -1.0, -1.0)
    t.MaxPoint(0).SetValues(2.0, 2.0, 2.0)
    near(t.MinPoint(0).x(), -1.0)
    near(t.MaxPoint(0).x(), 2.0)


def test_BVH_TreeTest_ChangeChild():
    t = Tree3()
    l1 = t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    l2 = t.AddLeafNode(V(1.0, 0.0, 0.0), V(2.0, 1.0, 1.0), 1, 1)
    l3 = t.AddLeafNode(V(2.0, 0.0, 0.0), V(3.0, 1.0, 1.0), 2, 2)
    root = t.AddInnerNode(V(0.0, 0.0, 0.0), V(2.0, 1.0, 1.0), l1, l2)
    assert child(t, root, 0) == l1
    assert child(t, root, 1) == l2
    t.SetBegPrimitive(root, l3)  # C++: aTree.ChangeChild<0>(aRoot) = aLeaf3
    assert child(t, root, 0) == l3
    assert child(t, root, 1) == l2


def test_BVH_TreeTest_NodeInfoBuffer():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 5, 10)
    assert len(t.NodeInfoBuffer()) == 1


def test_BVH_TreeTest_MinMaxPointBuffers():
    t = Tree3()
    t.AddLeafNode(V(0.0, 0.0, 0.0), V(1.0, 1.0, 1.0), 0, 0)
    assert len(t.MinPointBuffer()) == 1
    assert len(t.MaxPointBuffer()) == 1
