# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_List_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: STL algorithm tests, allocator tests (OCC25348, custom allocators), Emplace* (not bound,
# custom C++ element types), initializer lists, move constructor/assignment, const iterators.

from nanocct.NCollection import NCollection_List

ListInt = NCollection_List[int]


def make(*values):
    a_list = ListInt()
    for v in values:
        a_list.Append(v)
    return a_list


def iter_values(a_list):
    it = ListInt.Iterator(a_list)
    values = []
    while it.More():
        values.append(it.Value())
        it.Next()
    return values


def test_NCollection_ListTest_DefaultConstructor():
    a_list = ListInt()
    assert a_list.IsEmpty()
    assert a_list.Size() == 0
    assert a_list.Extent() == 0


def test_NCollection_ListTest_Append():
    a_list = ListInt()
    assert a_list.Append(10) == 10
    assert a_list.Append(20) == 20
    assert a_list.Append(30) == 30
    assert not a_list.IsEmpty()
    assert a_list.Size() == 3
    assert a_list.First() == 10
    assert a_list.Last() == 30


def test_NCollection_ListTest_Prepend():
    a_list = ListInt()
    assert a_list.Prepend(30) == 30
    assert a_list.Prepend(20) == 20
    assert a_list.Prepend(10) == 10
    assert not a_list.IsEmpty()
    assert a_list.Size() == 3
    assert a_list.First() == 10
    assert a_list.Last() == 30


def test_NCollection_ListTest_IteratorAccess():
    a_list = make(10, 20, 30)
    it = ListInt.Iterator(a_list)
    expected = [10, 20, 30]
    index = 0
    while it.More():
        assert it.Value() == expected[index]
        it.Next()
        index += 1
    assert index == 3


def test_NCollection_ListTest_STLIterators():
    # Python iteration stands in for begin()/end() and the range-based for loop
    a_list = make(10, 20, 30)
    expected = [10, 20, 30]
    index = 0
    for value in a_list:
        assert value == expected[index]
        index += 1
    assert index == 3


def test_NCollection_ListTest_RemoveFirst():
    a_list = make(10, 20, 30)
    a_list.RemoveFirst()
    assert a_list.Size() == 2
    assert a_list.First() == 20
    a_list.RemoveFirst()
    assert a_list.Size() == 1
    assert a_list.First() == 30
    a_list.RemoveFirst()
    assert a_list.IsEmpty()


def test_NCollection_ListTest_Remove():
    a_list = make(10, 20, 30)
    it = ListInt.Iterator(a_list)
    it.Next()
    a_list.Remove(it)
    assert a_list.Size() == 2
    assert a_list.First() == 10
    assert a_list.Last() == 30
    assert it.Value() == 30


def test_NCollection_ListTest_RemoveByValue():
    a_list = make(10, 20, 10, 30)
    assert a_list.Remove(10) is True
    assert a_list.Size() == 3
    assert a_list.First() == 20
    assert a_list.Remove(50) is False
    assert a_list.Size() == 3
    assert a_list.Remove(10) is True
    assert a_list.Size() == 2
    it = ListInt.Iterator(a_list)
    assert it.Value() == 20
    it.Next()
    assert it.Value() == 30


def test_NCollection_ListTest_Clear():
    a_list = make(10, 20, 30)
    a_list.Clear()
    assert a_list.IsEmpty()
    assert a_list.Size() == 0


def test_NCollection_ListTest_Assignment():
    # operator= has no Python spelling; the copy constructor gives the same deep copy
    a_list1 = make(10, 20, 30)
    a_list2 = ListInt(a_list1)
    assert a_list1.Size() == a_list2.Size()
    assert iter_values(a_list1) == iter_values(a_list2)
    # `aList1.First() = 100` is not expressible for int; replace the first element instead
    a_list1.RemoveFirst()
    a_list1.Prepend(100)
    assert a_list1.First() == 100
    assert a_list2.First() == 10


def test_NCollection_ListTest_AssignMethod():
    a_list1 = make(10, 20, 30)
    a_list2 = make(40)
    a_list2.Assign(a_list1)
    assert a_list1.Size() == a_list2.Size()
    assert iter_values(a_list2) == [10, 20, 30]


def test_NCollection_ListTest_AppendList():
    a_list1 = make(10, 20)
    a_list2 = make(30, 40)
    a_list1.Append(a_list2)
    assert a_list1.Size() == 4
    assert a_list2.IsEmpty()
    assert iter_values(a_list1) == [10, 20, 30, 40]


def test_NCollection_ListTest_PrependList():
    a_list1 = make(30, 40)
    a_list2 = make(10, 20)
    a_list1.Prepend(a_list2)
    assert a_list1.Size() == 4
    assert a_list2.IsEmpty()
    assert iter_values(a_list1) == [10, 20, 30, 40]


def test_NCollection_ListTest_InsertBefore():
    a_list = make(10, 30)
    it = ListInt.Iterator(a_list)
    it.Next()
    assert a_list.InsertBefore(20, it) == 20
    assert a_list.Size() == 3
    assert iter_values(a_list) == [10, 20, 30]


def test_NCollection_ListTest_InsertAfter():
    a_list = make(10, 30)
    it = ListInt.Iterator(a_list)
    assert a_list.InsertAfter(20, it) == 20
    assert a_list.Size() == 3
    assert iter_values(a_list) == [10, 20, 30]


def test_NCollection_ListTest_InsertList():
    a_list1 = make(10, 40)
    a_list2 = make(20, 30)
    it = ListInt.Iterator(a_list1)
    it.Next()
    a_list1.InsertBefore(a_list2, it)
    assert a_list1.Size() == 4
    assert a_list2.IsEmpty()
    assert iter_values(a_list1) == [10, 20, 30, 40]


def test_NCollection_ListTest_Reverse():
    a_list = make(10, 20, 30)
    a_list.Reverse()
    assert a_list.First() == 30
    assert a_list.Last() == 10
    assert iter_values(a_list) == [30, 20, 10]


def test_NCollection_ListTest_Exchange():
    a_list1 = make(10, 20)
    a_list2 = make(30, 40, 50)
    a_list1.Exchange(a_list2)
    assert a_list1.Size() == 3
    assert a_list1.First() == 30
    assert a_list1.Last() == 50
    assert a_list2.Size() == 2
    assert a_list2.First() == 10
    assert a_list2.Last() == 20


def test_NCollection_ListTest_ExchangeWithEmpty():
    a_list1 = make(10, 20)
    a_list2 = ListInt()
    a_list1.Exchange(a_list2)
    assert a_list1.IsEmpty()
    assert a_list2.Size() == 2
    assert a_list2.First() == 10
    assert a_list2.Last() == 20
