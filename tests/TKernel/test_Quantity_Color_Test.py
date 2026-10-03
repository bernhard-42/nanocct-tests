# Translated from OCCT src/FoundationClasses/TKernel/GTests/Quantity_Color_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Quantity import (
    NCollection_Vec3__float,
    Quantity_Color,
    Quantity_NOC_BLUE,
    Quantity_NOC_GREEN,
    Quantity_NOC_RED,
    Quantity_NOC_YELLOW,
    Quantity_TOC_RGB,
)


def near(a, b, tol=0.001):
    return abs(a - b) < tol


def comps(v):
    return v.x(), v.y(), v.z()


def test_Quantity_ColorTest_BasicConstruction():
    c1 = Quantity_Color()
    assert near(1.0, c1.Red())
    assert near(1.0, c1.Green())
    assert near(0.0, c1.Blue())

    c2 = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    assert near(0.5, c2.Red())
    assert near(0.6, c2.Green())
    assert near(0.7, c2.Blue())

    c3 = Quantity_Color(Quantity_NOC_RED)
    assert near(1.0, c3.Red())
    assert near(0.0, c3.Green())
    assert near(0.0, c3.Blue())


def test_Quantity_ColorTest_ConstexprGetters():
    c = Quantity_Color(0.3, 0.5, 0.7, Quantity_TOC_RGB)
    assert near(0.3, c.Red())
    assert near(0.5, c.Green())
    assert near(0.7, c.Blue())


def test_Quantity_ColorTest_EqualityComparison():
    c1 = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    c2 = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    c3 = Quantity_Color(0.5, 0.6, 0.8, Quantity_TOC_RGB)

    assert c1.IsEqual(c2)
    assert c1 == c2
    assert not c1.IsDifferent(c2)
    assert not (c1 != c2)

    assert not c1.IsEqual(c3)
    assert not (c1 == c3)
    assert c1.IsDifferent(c3)
    assert c1 != c3


def test_Quantity_ColorTest_DistanceCalculation():
    c1 = Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)
    c2 = Quantity_Color(0.3, 0.4, 0.0, Quantity_TOC_RGB)
    assert near(0.5, c1.Distance(c2))
    assert near(0.25, c1.SquareDistance(c2))


def test_Quantity_ColorTest_RGB_to_HLS_Conversion():
    red = Quantity_Color(Quantity_NOC_RED)
    h, l, s = comps(Quantity_Color.Convert_sRGB_To_HLS_s(red.Rgb()))
    assert near(0.0, h, 1.0)
    assert near(1.0, l)
    assert near(1.0, s)

    gray = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)
    _, l, s = comps(Quantity_Color.Convert_sRGB_To_HLS_s(gray.Rgb()))
    assert near(0.5, l)
    assert near(0.0, s)


def test_Quantity_ColorTest_LinearRGB_to_Lab_Conversion():
    white = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
    L, a, b = comps(Quantity_Color.Convert_LinearRGB_To_Lab_s(white.Rgb()))
    assert near(100.0, L, 1.0)
    assert near(0.0, a, 5.0)
    assert near(0.0, b, 5.0)

    black = Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)
    L, _, _ = comps(Quantity_Color.Convert_LinearRGB_To_Lab_s(black.Rgb()))
    assert near(0.0, L, 1.0)


def test_Quantity_ColorTest_Lab_to_Lch_Conversion():
    lab = NCollection_Vec3__float(50.0, 25.0, 25.0)
    L, C, H = comps(Quantity_Color.Convert_Lab_To_Lch_s(lab))
    assert near(50.0, L)
    assert near(35.36, C, 0.1)
    assert near(45.0, H, 1.0)


def test_Quantity_ColorTest_Lch_to_Lab_RoundTrip():
    lab1 = NCollection_Vec3__float(50.0, 25.0, 25.0)
    lch = Quantity_Color.Convert_Lab_To_Lch_s(lab1)
    lab2 = Quantity_Color.Convert_Lch_To_Lab_s(lch)
    for x, y in zip(comps(lab1), comps(lab2)):
        assert near(x, y, 0.01)


def test_Quantity_ColorTest_Lab_to_RGB_RoundTrip():
    orig = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    lab = Quantity_Color.Convert_LinearRGB_To_Lab_s(orig.Rgb())
    r, g, b = comps(Quantity_Color.Convert_Lab_To_LinearRGB_s(lab))
    assert near(orig.Red(), r, 0.01)
    assert near(orig.Green(), g, 0.01)
    assert near(orig.Blue(), b, 0.01)


def test_Quantity_ColorTest_DeltaE2000_Calculation():
    c1 = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    c2 = Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB)
    assert near(0.0, c1.DeltaE2000(c2), 0.01)
    c3 = Quantity_Color(0.3, 0.4, 0.5, Quantity_TOC_RGB)
    assert c1.DeltaE2000(c3) > 0.0


def test_Quantity_ColorTest_NamedColors():
    red = Quantity_Color(Quantity_NOC_RED)
    assert near(1.0, red.Red())
    assert near(0.0, red.Green())
    assert near(0.0, red.Blue())

    green = Quantity_Color(Quantity_NOC_GREEN)
    assert near(0.0, green.Red())
    assert green.Green() > 0.5
    assert near(0.0, green.Blue())

    blue = Quantity_Color(Quantity_NOC_BLUE)
    assert near(0.0, blue.Red())
    assert near(0.0, blue.Green())
    assert near(1.0, blue.Blue())


def test_Quantity_ColorTest_SetValues():
    c = Quantity_Color()
    c.SetValues(0.2, 0.4, 0.6, Quantity_TOC_RGB)
    assert near(0.2, c.Red())
    assert near(0.4, c.Green())
    assert near(0.6, c.Blue())

    c.SetValues(Quantity_NOC_YELLOW)
    assert near(1.0, c.Red())
    assert near(1.0, c.Green())
    assert near(0.0, c.Blue())


def test_Quantity_ColorTest_HLS_Extraction():
    red = Quantity_Color(Quantity_NOC_RED)
    hue = red.Hue()
    assert near(0.0, hue, 5.0) or near(360.0, hue, 5.0)
    assert near(1.0, red.Light(), 0.01)
    assert near(1.0, red.Saturation(), 0.01)


def test_Quantity_ColorTest_EpsilonThreadSafety():
    orig = Quantity_Color.Epsilon_s()
    try:
        Quantity_Color.SetEpsilon_s(0.0002)
        assert near(0.0002, Quantity_Color.Epsilon_s())
    finally:
        Quantity_Color.SetEpsilon_s(orig)
    assert near(orig, Quantity_Color.Epsilon_s())


def test_Quantity_ColorTest_ColorNameString():
    assert Quantity_Color.StringName_s(Quantity_NOC_RED) == "RED"
    assert Quantity_Color.StringName_s(Quantity_NOC_BLUE) == "BLUE"


def test_Quantity_ColorTest_EdgeCases():
    black = Quantity_Color(0.0, 0.0, 0.0, Quantity_TOC_RGB)
    assert near(0.0, black.Red())
    assert near(0.0, black.Green())
    assert near(0.0, black.Blue())

    white = Quantity_Color(1.0, 1.0, 1.0, Quantity_TOC_RGB)
    assert near(1.0, white.Red())
    assert near(1.0, white.Green())
    assert near(1.0, white.Blue())

    c1 = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)
    c2 = Quantity_Color(0.50001, 0.50001, 0.50001, Quantity_TOC_RGB)
    assert c1.IsEqual(c2)
