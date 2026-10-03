# Translated from OCCT src/FoundationClasses/TKMath/GTests/BVH_RadixSorter_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BVH import EncodeMortonCode as enc

MAX30 = 0x3FFFFFFF


def test_BVH_RadixSorterTest_EncodeMortonCode_Origin():
    assert enc(0, 0, 0) == 0


def test_BVH_RadixSorterTest_EncodeMortonCode_SingleBits():
    assert enc(1, 0, 0) == 1
    assert enc(0, 1, 0) == 2
    assert enc(0, 0, 1) == 4
    assert enc(1, 1, 1) == 7


def test_BVH_RadixSorterTest_EncodeMortonCode_Interleaving():
    assert enc(2, 0, 0) == 8
    assert enc(0, 2, 0) == 16
    assert enc(0, 0, 2) == 32


def test_BVH_RadixSorterTest_EncodeMortonCode_MaxValues():
    assert enc(1023, 1023, 1023) == MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_Symmetry():
    c1 = enc(100, 200, 300)
    c2 = enc(200, 100, 300)
    c3 = enc(100, 300, 200)
    assert c1 != c2
    assert c1 != c3
    assert c2 != c3


def test_BVH_RadixSorterTest_EncodeMortonCode_Ordering():
    c000 = enc(0, 0, 0)
    assert enc(1, 0, 0) - c000 < enc(0, 0, 1023) - c000


def test_BVH_RadixSorterTest_EncodeMortonCode_MidValues():
    c = enc(512, 512, 512)
    assert 0 < c <= MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_PowersOfTwo():
    c4 = enc(4, 0, 0)
    c8 = enc(8, 0, 0)
    c16 = enc(16, 0, 0)
    assert c8 == c4 * 8
    assert c16 == c8 * 8


def test_BVH_RadixSorterTest_EncodeMortonCode_ConsistentEncoding():
    for _ in range(100):
        assert enc(100, 200, 300) == enc(100, 200, 300)


def test_BVH_RadixSorterTest_EncodeMortonCode_BoundaryValues():
    c1022 = enc(1022, 1022, 1022)
    c1023 = enc(1023, 1023, 1023)
    assert c1022 < c1023
    assert c1023 == MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_SmallValues():
    c2 = enc(2, 2, 2)
    c3 = enc(3, 3, 3)
    assert c2 < 100
    assert c3 < 100
    assert c2 < c3


def test_BVH_RadixSorterTest_EncodeMortonCode_SingleAxisValues():
    cx = enc(255, 0, 0)
    cy = enc(0, 255, 0)
    cz = enc(0, 0, 255)
    assert cx != cy
    assert cy != cz
    assert cx != cz


def test_BVH_RadixSorterTest_EncodeMortonCode_SequentialXValues():
    prev = enc(0, 500, 500)
    for x in range(1, 11):
        cur = enc(x, 500, 500)
        assert cur > prev
        prev = cur


def test_BVH_RadixSorterTest_EncodeMortonCode_SequentialYValues():
    prev = enc(500, 0, 500)
    for y in range(1, 11):
        cur = enc(500, y, 500)
        assert cur > prev
        prev = cur


def test_BVH_RadixSorterTest_EncodeMortonCode_SequentialZValues():
    prev = enc(500, 500, 0)
    for z in range(1, 11):
        cur = enc(500, 500, z)
        assert cur > prev
        prev = cur


def test_BVH_RadixSorterTest_EncodeMortonCode_ZeroInDimensions():
    cxy = enc(100, 100, 0)
    cxz = enc(100, 0, 100)
    cyz = enc(0, 100, 100)
    assert cxy != cxz
    assert cxy != cyz
    assert cxz != cyz
    assert cxy > 0
    assert cxz > 0
    assert cyz > 0


def test_BVH_RadixSorterTest_EncodeMortonCode_UpperByteBits():
    c256 = enc(256, 0, 0)
    c512 = enc(512, 0, 0)
    c768 = enc(768, 0, 0)
    assert c256 > 0
    assert c512 > c256
    assert c768 > c512


def test_BVH_RadixSorterTest_EncodeMortonCode_AllOnes():
    c = enc(255, 255, 255)
    assert 0 < c < MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_LocalityPreservation():
    center = enc(512, 512, 512)
    d1 = abs(enc(513, 512, 512) - center)
    d2 = abs(enc(512, 513, 512) - center)
    dfar = abs(enc(0, 0, 0) - center)
    assert d1 < dfar
    assert d2 < dfar


def test_BVH_RadixSorterTest_EncodeMortonCode_BitPattern3():
    assert enc(3, 0, 0) == 9


def test_BVH_RadixSorterTest_EncodeMortonCode_BitPattern7():
    assert enc(7, 0, 0) == 73


def test_BVH_RadixSorterTest_EncodeMortonCode_XYEqual():
    assert enc(1, 1, 0) == 3
    assert enc(2, 2, 0) == 24
    assert enc(4, 4, 0) == 192


def test_BVH_RadixSorterTest_EncodeMortonCode_AllAxesEqual():
    assert enc(1, 1, 1) == 7
    assert enc(2, 2, 2) == 56


def test_BVH_RadixSorterTest_EncodeMortonCode_HalfMax():
    c = enc(512, 512, 512)
    assert c > 0x1FFFFFFF
    assert c <= MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_QuarterMax():
    c = enc(256, 256, 256)
    assert 0 < c < MAX30


def test_BVH_RadixSorterTest_EncodeMortonCode_DifferentScales():
    assert enc(200, 200, 200) > enc(100, 100, 100)


def test_BVH_RadixSorterTest_EncodeMortonCode_AdjacentCells():
    assert enc(101, 100, 100) - enc(100, 100, 100) == 1


def test_BVH_RadixSorterTest_EncodeMortonCode_AdjacentCellsY():
    assert enc(100, 101, 100) - enc(100, 100, 100) == 2


def test_BVH_RadixSorterTest_EncodeMortonCode_AdjacentCellsZ():
    assert enc(100, 100, 101) - enc(100, 100, 100) == 4


def test_BVH_RadixSorterTest_EncodeMortonCode_MonotonicX():
    prev = 0
    for x in range(100):
        c = enc(x, 0, 0)
        assert c >= prev
        prev = c


def test_BVH_RadixSorterTest_EncodeMortonCode_MonotonicY():
    prev = 0
    for y in range(100):
        c = enc(0, y, 0)
        assert c >= prev
        prev = c


def test_BVH_RadixSorterTest_EncodeMortonCode_MonotonicZ():
    prev = 0
    for z in range(100):
        c = enc(0, 0, z)
        assert c >= prev
        prev = c


def test_BVH_RadixSorterTest_EncodeMortonCode_NoOverflow():
    assert enc(1023, 1023, 1023) & 0xC0000000 == 0


def test_BVH_RadixSorterTest_EncodeMortonCode_UniqueForDifferentInputs():
    codes = [enc(100, 200, 300), enc(100, 200, 301), enc(100, 201, 300), enc(101, 200, 300)]
    assert len(set(codes)) == 4


def test_BVH_RadixSorterTest_EncodeMortonCode_SpecificPattern():
    c = enc(5, 3, 6)
    assert 0 < c <= MAX30
    assert c == enc(5, 3, 6)
