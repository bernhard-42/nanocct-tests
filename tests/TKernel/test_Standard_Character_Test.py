# Translated from OCCT src/FoundationClasses/TKernel/GTests/Standard_Character_Test.cxx (LGPL-2.1 with the OCCT exception)
import nanocct.Standard as S


def test_Standard_Character_Test_OCC29925_CharacterClassificationFunctions():
    # C++ loops over all 256 char values; a Python str converts to C char only for code points < 128
    for i in range(128):
        c = chr(i)
        S.IsAlphabetic(c)
        S.IsDigit(c)
        S.IsXDigit(c)
        S.IsAlphanumeric(c)
        S.IsControl(c)
        S.IsGraphic(c)
        S.IsLowerCase(c)
        S.IsPrintable(c)
        S.IsPunctuation(c)
        S.IsSpace(c)
        S.IsUpperCase(c)
        S.LowerCase(c)
        S.UpperCase(c)

    assert S.IsAlphabetic("A")
    assert S.IsAlphabetic("z")
    assert not S.IsAlphabetic("5")

    assert S.IsDigit("0")
    assert S.IsDigit("9")
    assert not S.IsDigit("A")

    assert S.IsSpace(" ")
    assert S.IsSpace("\t")
    assert not S.IsSpace("A")

    assert S.IsLowerCase("a")
    assert not S.IsLowerCase("A")

    assert S.IsUpperCase("A")
    assert not S.IsUpperCase("a")

    assert S.LowerCase("A") == "a"
    assert S.UpperCase("a") == "A"
