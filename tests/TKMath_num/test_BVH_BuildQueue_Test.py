# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_BuildQueue_Test.cxx (LGPL-2.1 with the OCCT exception)
# C++ Fetch(bool& wasBusy) is in/out: the binding takes wasBusy and returns (item, wasBusy).
import pytest

from nanocct.BVH import BVH_BuildQueue


def test_BVH_BuildQueueTest_DefaultConstructor():
    q = BVH_BuildQueue()
    assert q.Size() == 0
    assert not q.HasBusyThreads()


def test_BVH_BuildQueueTest_EnqueueSingle():
    q = BVH_BuildQueue()
    q.Enqueue(42)
    assert q.Size() == 1


def test_BVH_BuildQueueTest_EnqueueMultiple():
    q = BVH_BuildQueue()
    q.Enqueue(1)
    q.Enqueue(2)
    q.Enqueue(3)
    assert q.Size() == 3


def test_BVH_BuildQueueTest_FetchFromEmptyQueue():
    q = BVH_BuildQueue()
    result, was_busy = q.Fetch(False)
    assert result == -1
    assert not was_busy
    assert not q.HasBusyThreads()


def test_BVH_BuildQueueTest_FetchSingleItem():
    q = BVH_BuildQueue()
    q.Enqueue(42)
    result, was_busy = q.Fetch(False)
    assert result == 42
    assert was_busy
    assert q.HasBusyThreads()
    assert q.Size() == 0


def test_BVH_BuildQueueTest_FetchFIFOOrder():
    q = BVH_BuildQueue()
    q.Enqueue(10)
    q.Enqueue(20)
    q.Enqueue(30)
    assert q.Fetch(False) == (10, True)
    assert q.Fetch(False) == (20, True)
    assert q.Fetch(False) == (30, True)
    assert q.Fetch(False) == (-1, False)


def test_BVH_BuildQueueTest_ThreadCountTracking():
    q = BVH_BuildQueue()
    q.Enqueue(1)
    q.Enqueue(2)
    assert not q.HasBusyThreads()
    _, was_busy = q.Fetch(False)
    assert was_busy
    assert q.HasBusyThreads()
    _, was_busy = q.Fetch(was_busy)
    assert was_busy
    assert q.HasBusyThreads()
    _, was_busy = q.Fetch(was_busy)
    assert not was_busy
    assert not q.HasBusyThreads()


def test_BVH_BuildQueueTest_AlternatingEnqueueFetch():
    q = BVH_BuildQueue()
    q.Enqueue(1)
    assert q.Size() == 1
    assert q.Fetch(False)[0] == 1
    assert q.Size() == 0
    q.Enqueue(2)
    assert q.Size() == 1
    assert q.Fetch(False)[0] == 2
    assert q.Size() == 0


def test_BVH_BuildQueueTest_LargeQueue():
    q = BVH_BuildQueue()
    count = 1000
    for i in range(count):
        q.Enqueue(i)
    assert q.Size() == count
    for i in range(count):
        assert q.Fetch(False)[0] == i
    assert q.Size() == 0


def test_BVH_BuildQueueTest_NegativeValues():
    q = BVH_BuildQueue()
    q.Enqueue(-1)
    q.Enqueue(-100)
    q.Enqueue(0)
    assert q.Fetch(False)[0] == -1
    assert q.Fetch(False)[0] == -100
    assert q.Fetch(False)[0] == 0


def test_BVH_BuildQueueTest_RepeatedFetchFromEmpty():
    q = BVH_BuildQueue()
    for _ in range(10):
        result, was_busy = q.Fetch(False)
        assert result == -1
        assert not was_busy
    assert not q.HasBusyThreads()


def test_BVH_BuildQueueTest_EnqueueZero():
    q = BVH_BuildQueue()
    q.Enqueue(0)
    assert q.Size() == 1
    assert q.Fetch(False) == (0, True)


def test_BVH_BuildQueueTest_DuplicateValues():
    q = BVH_BuildQueue()
    q.Enqueue(5)
    q.Enqueue(5)
    q.Enqueue(5)
    assert q.Size() == 3
    assert q.Fetch(False)[0] == 5
    assert q.Fetch(False)[0] == 5
    assert q.Fetch(False)[0] == 5


def test_BVH_BuildQueueTest_SingleThreadWorkflow():
    q = BVH_BuildQueue()
    q.Enqueue(0)
    node, was_busy = q.Fetch(False)
    assert node == 0
    assert was_busy
    q.Enqueue(1)
    q.Enqueue(2)
    assert q.Size() == 2
    assert q.Fetch(False)[0] == 1
    assert q.Fetch(False)[0] == 2
    node, was_busy = q.Fetch(False)
    assert node == -1
    assert not was_busy
