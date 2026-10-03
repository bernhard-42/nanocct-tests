# Translated from OCCT src/FoundationClasses/TKernel/GTests/NCollection_Sequence_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: AllocatorTest, MoveOperations, STL algorithm tests, Emplace* (not bound, custom C++ element types).

from nanocct.NCollection import NCollection_Sequence
from nanocct.TCollection import TCollection_AsciiString

SeqInt = NCollection_Sequence[int]


def make(*values):
    a_seq = SeqInt()
    for v in values:
        a_seq.Append(v)
    return a_seq


def test_NCollection_SequenceTest_BasicFunctions():
    a_seq = SeqInt()
    assert a_seq.IsEmpty()
    assert a_seq.Size() == 0
    assert a_seq.Length() == 0

    a_seq.Append(10)
    a_seq.Append(20)
    a_seq.Append(30)
    assert a_seq.Size() == 3
    assert not a_seq.IsEmpty()

    assert a_seq(1) == 10
    assert a_seq(2) == 20
    assert a_seq(3) == 30
    assert a_seq.First() == 10
    assert a_seq.Last() == 30

    assert a_seq.Lower() == 1
    assert a_seq.Upper() == 3


def test_NCollection_SequenceTest_ModifyingOperations():
    a_seq = SeqInt()
    a_seq.Prepend(100)
    a_seq.Prepend(200)
    assert a_seq.Size() == 2
    assert a_seq.First() == 200
    assert a_seq.Last() == 100

    a_seq.SetValue(1, 210)
    assert a_seq(1) == 210

    # `ChangeValue(2) = 110` is not expressible for int; item assignment is the Python spelling
    a_seq[2] = 110
    assert a_seq(2) == 110

    a_seq.InsertBefore(1, 300)
    assert a_seq.Size() == 3
    assert [a_seq(i) for i in (1, 2, 3)] == [300, 210, 110]

    a_seq.InsertAfter(2, 400)
    assert a_seq.Size() == 4
    assert [a_seq(i) for i in (1, 2, 3, 4)] == [300, 210, 400, 110]

    a_seq.Remove(3)
    assert a_seq.Size() == 3
    assert [a_seq(i) for i in (1, 2, 3)] == [300, 210, 110]

    a_seq.Append(500)
    a_seq.Append(600)
    assert a_seq.Size() == 5

    a_seq.Remove(2, 4)
    assert a_seq.Size() == 2
    assert a_seq(1) == 300
    assert a_seq(2) == 600


def test_NCollection_SequenceTest_IteratorFunctions():
    a_seq = make(10, 20, 30)
    it = SeqInt.Iterator(a_seq)
    assert it.More()
    assert it.Value() == 10
    it.Next()
    assert it.More()
    assert it.Value() == 20
    it.Next()
    assert it.More()
    assert it.Value() == 30
    it.Next()
    assert not it.More()

    # `aModIt.ChangeValue() = 15` is not expressible for int: the in-place modification is
    # tested on a sequence of TCollection_AsciiString instead
    a_str_seq = NCollection_Sequence[TCollection_AsciiString]()
    for s in ("10", "20", "30"):
        a_str_seq.Append(TCollection_AsciiString(s))
    mod_it = NCollection_Sequence[TCollection_AsciiString].Iterator(a_str_seq)
    mod_it.ChangeValue().Copy(TCollection_AsciiString("15"))
    mod_it.Next()
    mod_it.ChangeValue().Copy(TCollection_AsciiString("25"))
    assert a_str_seq(1).ToCString() == "15"
    assert a_str_seq(2).ToCString() == "25"
    assert a_str_seq(3).ToCString() == "30"

    # Python iteration stands in for the range-based for loop
    expected = [10, 20, 30]
    index = 0
    for item in a_seq:
        assert item == expected[index]
        index += 1
    assert index == 3


def test_NCollection_SequenceTest_CopyAndAssignment():
    a_seq1 = make(10, 20, 30)

    a_seq2 = SeqInt(a_seq1)
    assert a_seq2.Size() == 3
    assert [a_seq2(i) for i in (1, 2, 3)] == [10, 20, 30]

    # operator= has no Python spelling; Assign() is what it calls
    a_seq3 = SeqInt()
    a_seq3.Assign(a_seq1)
    assert a_seq3.Size() == 3
    assert [a_seq3(i) for i in (1, 2, 3)] == [10, 20, 30]

    a_seq1.SetValue(2, 25)
    assert a_seq1(2) == 25
    assert a_seq2(2) == 20
    assert a_seq3(2) == 20


def test_NCollection_SequenceTest_CombiningSequences():
    a_seq1 = make(10, 20)
    a_seq2 = make(30, 40)

    a_seq3 = SeqInt(a_seq1)
    a_seq3.Append(a_seq2)
    assert a_seq3.Size() == 4
    assert [a_seq3(i) for i in (1, 2, 3, 4)] == [10, 20, 30, 40]
    assert a_seq2.IsEmpty()

    a_seq2.Append(50)
    a_seq2.Append(60)
    a_seq4 = make(70)
    a_seq4.Prepend(a_seq2)
    assert a_seq4.Size() == 3
    assert [a_seq4(i) for i in (1, 2, 3)] == [50, 60, 70]
    assert a_seq2.IsEmpty()

    a_seq2.Append(80)
    a_seq2.Append(90)
    a_seq5 = make(100, 110)
    a_seq5.InsertAfter(1, a_seq2)
    assert a_seq5.Size() == 4
    assert [a_seq5(i) for i in (1, 2, 3, 4)] == [100, 80, 90, 110]
    assert a_seq2.IsEmpty()


def test_NCollection_SequenceTest_AdvancedOperations():
    a_seq = make(10, 20, 30, 40, 50)

    a_seq.Exchange(2, 4)
    assert [a_seq(i) for i in range(1, 6)] == [10, 40, 30, 20, 50]

    a_seq.Reverse()
    assert [a_seq(i) for i in range(1, 6)] == [50, 20, 30, 40, 10]

    a_seq2 = SeqInt()
    a_seq.Split(2, a_seq2)
    assert a_seq.Size() == 1
    assert a_seq(1) == 50
    assert a_seq2.Size() == 4
    assert [a_seq2(i) for i in range(1, 5)] == [20, 30, 40, 10]

    a_seq.Clear()
    assert a_seq.IsEmpty()
    assert a_seq.Size() == 0


def test_NCollection_SequenceTest_ComplexTypeSequence():
    # the test's own TestClass is replaced by TCollection_AsciiString (a bound class element type)
    SeqStr = NCollection_Sequence[TCollection_AsciiString]
    a_seq = SeqStr()
    a = TCollection_AsciiString("First")
    b = TCollection_AsciiString("Second")
    c = TCollection_AsciiString("Third")
    a_seq.Append(a)
    a_seq.Append(b)
    a_seq.Append(c)

    assert a_seq.Size() == 3
    assert a_seq(1).ToCString() == "First"
    assert a_seq(2).ToCString() == "Second"
    assert a_seq(3).ToCString() == "Third"

    # `aSeq.ChangeValue(2) = TestClass(...)`: assign through the returned reference
    a_seq.ChangeValue(2).Copy(TCollection_AsciiString("Modified"))
    assert a_seq(2).ToCString() == "Modified"

    a_seq.Remove(1)
    assert a_seq.Size() == 2
    assert a_seq.First().ToCString() == "Modified"


def test_NCollection_SequenceTest_OCC26448_PrependEmptySequence():
    SeqDbl = NCollection_Sequence[float]
    a_nseq1, a_nseq2 = SeqDbl(), SeqDbl()
    a_nseq1.Append(11.0)
    a_nseq1.Prepend(a_nseq2)
    assert a_nseq1.Size() == 1
    assert a_nseq1.First() == 11.0

    a_tseq1, a_tseq2 = SeqDbl(), SeqDbl()
    a_tseq1.Append(11.0)
    a_tseq1.Prepend(a_tseq2)
    assert a_tseq1.Size() == 1
    assert a_tseq1.First() == 11.0
