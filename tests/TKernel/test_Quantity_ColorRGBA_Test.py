# Translated from OCCT src/FoundationClasses/TKernel/GTests/Quantity_ColorRGBA_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Quantity import Quantity_Color, Quantity_ColorRGBA, Quantity_TOC_RGB


def near(a, b, tol=0.001):
    return abs(a - b) < tol


def rgb(c):
    r = c.GetRGB()
    return r.Red(), r.Green(), r.Blue()


def test_Quantity_ColorRGBATest_BasicConstruction():
    c1 = Quantity_ColorRGBA()
    r, g, b = rgb(c1)
    assert near(1.0, r) and near(1.0, g) and near(0.0, b)
    assert near(1.0, c1.Alpha())

    c2 = Quantity_ColorRGBA(Quantity_Color(0.5, 0.6, 0.7, Quantity_TOC_RGB), 0.8)
    r, g, b = rgb(c2)
    assert near(0.5, r) and near(0.6, g) and near(0.7, b)
    assert near(0.8, c2.Alpha())

    c3 = Quantity_ColorRGBA(0.3, 0.4, 0.5, 0.6)
    r, g, b = rgb(c3)
    assert near(0.3, r) and near(0.4, g) and near(0.5, b)
    assert near(0.6, c3.Alpha())


def test_Quantity_ColorRGBATest_ConstexprGetters():
    c = Quantity_ColorRGBA(0.2, 0.4, 0.6, 0.8)
    assert near(0.8, c.Alpha())


def test_Quantity_ColorRGBATest_SetValues():
    c = Quantity_ColorRGBA()
    c.SetValues(0.1, 0.2, 0.3, 0.4)
    r, g, b = rgb(c)
    assert near(0.1, r) and near(0.2, g) and near(0.3, b)
    assert near(0.4, c.Alpha())


def test_Quantity_ColorRGBATest_HexColorParsing_RGB():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#FF0000", c, True)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.01) and near(0.0, g, 0.01) and near(0.0, b, 0.01)

    assert Quantity_ColorRGBA.ColorFromHex_s("00FF00", c, True)
    r, g, b = rgb(c)
    assert near(0.0, r, 0.01) and near(1.0, g, 0.01) and near(0.0, b, 0.01)

    assert Quantity_ColorRGBA.ColorFromHex_s("#0000FF", c, True)
    r, g, b = rgb(c)
    assert near(0.0, r, 0.01) and near(0.0, g, 0.01) and near(1.0, b, 0.01)


def test_Quantity_ColorRGBATest_HexColorParsing_RGBA():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#FF000080", c, False)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.01) and near(0.0, g, 0.01) and near(0.0, b, 0.01)
    assert near(0.5, c.Alpha(), 0.02)


def test_Quantity_ColorRGBATest_HexColorParsing_ShortRGB():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#F00", c, True)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.1) and near(0.0, g, 0.1) and near(0.0, b, 0.1)

    assert Quantity_ColorRGBA.ColorFromHex_s("#FFF", c, True)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.1) and near(1.0, g, 0.1) and near(1.0, b, 0.1)


def test_Quantity_ColorRGBATest_HexColorParsing_ShortRGBA():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#F008", c, False)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.1) and near(0.0, g, 0.1) and near(0.0, b, 0.1)
    assert near(0.5, c.Alpha(), 0.1)


def test_Quantity_ColorRGBATest_HexColorParsing_Invalid():
    c = Quantity_ColorRGBA()
    assert not Quantity_ColorRGBA.ColorFromHex_s("", c, True)
    assert not Quantity_ColorRGBA.ColorFromHex_s("#FFFF", c, True)
    assert not Quantity_ColorRGBA.ColorFromHex_s("#GGGGGG", c, True)
    assert not Quantity_ColorRGBA.ColorFromHex_s("#FF0000FF", c, True)


def test_Quantity_ColorRGBATest_HexColorParsing_MixedCase():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#FfAa00", c, True)
    r, g, b = rgb(c)
    assert near(1.0, r, 0.01)
    assert near(0.402, g, 0.01)
    assert near(0.0, b, 0.01)


def test_Quantity_ColorRGBATest_HexColorParsing_SpecificValues():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#102030", c, True)
    r, g, b = rgb(c)
    assert near(0.00518, r, 0.0001)
    assert near(0.01444, g, 0.0001)
    assert near(0.02956, b, 0.0001)


def test_Quantity_ColorRGBATest_EqualityComparison():
    c1 = Quantity_ColorRGBA(0.5, 0.6, 0.7, 0.8)
    c2 = Quantity_ColorRGBA(0.5, 0.6, 0.7, 0.8)
    c3 = Quantity_ColorRGBA(0.5, 0.6, 0.7, 0.9)
    assert c1.IsEqual(c2)
    assert not c1.IsEqual(c3)


def test_Quantity_ColorRGBATest_RGBAccess():
    c = Quantity_ColorRGBA(0.2, 0.4, 0.6, 0.8)
    r, g, b = rgb(c)
    assert near(0.2, r) and near(0.4, g) and near(0.6, b)

    c.ChangeRGB().SetValues(0.3, 0.5, 0.7, Quantity_TOC_RGB)
    r, g, b = rgb(c)
    assert near(0.3, r) and near(0.5, g) and near(0.7, b)
    assert near(0.8, c.Alpha())


def test_Quantity_ColorRGBATest_SetAlpha():
    c = Quantity_ColorRGBA(0.5, 0.5, 0.5, 1.0)
    assert near(1.0, c.Alpha())
    c.SetAlpha(0.5)
    assert near(0.5, c.Alpha())
    r, g, b = rgb(c)
    assert near(0.5, r) and near(0.5, g) and near(0.5, b)


def test_Quantity_ColorRGBATest_EdgeCases():
    t = Quantity_ColorRGBA(0.0, 0.0, 0.0, 0.0)
    assert near(0.0, t.Alpha())
    o = Quantity_ColorRGBA(1.0, 1.0, 1.0, 1.0)
    assert near(1.0, o.Alpha())
    assert near(1.0, o.GetRGB().Red())


def test_Quantity_ColorRGBATest_ComponentOrder():
    c = Quantity_ColorRGBA()
    assert Quantity_ColorRGBA.ColorFromHex_s("#123456", c, True)
    r, g, b = rgb(c)
    assert near(0.00605, r, 0.0001)
    assert near(0.03434, g, 0.0001)
    assert near(0.09306, b, 0.0001)
