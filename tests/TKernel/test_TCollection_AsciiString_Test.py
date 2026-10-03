# Translated from OCCT src/FoundationClasses/TKernel/GTests/TCollection_AsciiString_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Mapping notes: Python str -> const char* (UTF-8), a one-character str also serves the char overloads.
# ToCString() returns a Python copy, so the "pointer into self" tests below check the results, not the aliasing.
# Skipped: MemoryAllocation, PaddingSafety (allocation / null terminator), AssignmentOperator and
# TemplateLiteral_Assignment (C++ operator=), StringView_* (std::string_view), MoveConstructor, MoveAssignment,
# the wchar_t parts of AssignCat_/Cat_ExtendedStringAndWideChar.

from nanocct.TCollection import (
    TCollection_AsciiString,
    TCollection_ExtendedString,
    TCollection_HAsciiString,
)


def test_TCollection_AsciiStringTest_DefaultConstructor():
    aString = TCollection_AsciiString()
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_AsciiStringTest_ConstructorWithCString():
    aString = TCollection_AsciiString("Test String")
    assert aString.Length() == 11
    assert aString.IsEmpty() is False
    assert aString.ToCString() == "Test String"


def test_TCollection_AsciiStringTest_ConstructorWithChar():
    aString = TCollection_AsciiString("A")
    assert aString.Length() == 1
    assert aString.IsEmpty() is False
    assert aString.ToCString() == "A"


def test_TCollection_AsciiStringTest_CopyConstructor():
    aString1 = TCollection_AsciiString("Original")
    aString2 = TCollection_AsciiString(aString1)
    assert aString1.ToCString() == aString2.ToCString()
    assert aString1.Length() == aString2.Length()


def test_TCollection_AsciiStringTest_Concatenation():
    aString1 = TCollection_AsciiString("Hello")
    aString2 = TCollection_AsciiString(" World")
    aString3 = aString1 + aString2
    assert aString3.ToCString() == "Hello World"

    aString1 += aString2
    assert aString1.ToCString() == "Hello World"

    aString1 += "!"
    assert aString1.ToCString() == "Hello World!"

    aString1 += " Test"
    assert aString1.ToCString() == "Hello World! Test"


def test_TCollection_AsciiStringTest_SubString():
    aString = TCollection_AsciiString("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    subString = aString.SubString(3, 8)
    assert subString.ToCString() == "CDEFGH"


def test_TCollection_AsciiStringTest_ChangeCase():
    aString = TCollection_AsciiString("Hello World")

    upperString = TCollection_AsciiString(aString)
    upperString.UpperCase()
    assert upperString.ToCString() == "HELLO WORLD"

    lowerString = TCollection_AsciiString(aString)
    lowerString.LowerCase()
    assert lowerString.ToCString() == "hello world"

    capitalizeString = TCollection_AsciiString(lowerString)
    capitalizeString.Capitalize()
    assert capitalizeString.ToCString() == "Hello world"


def test_TCollection_AsciiStringTest_SearchAndLocation():
    aString = TCollection_AsciiString("This is a test string for testing search functions")

    assert aString.Search("test") == 11
    assert aString.Search("nonexistent") == -1

    assert aString.SearchFromEnd("test") == 27

    assert aString.Location(TCollection_AsciiString("i"), 1, aString.Length()) == 3
    assert aString.Location(TCollection_AsciiString("i"), 4, aString.Length()) == 6


def test_TCollection_AsciiStringTest_RemoveAndInsert():
    aString = TCollection_AsciiString("Hello World")

    aString.Remove(6, 6)
    assert aString.ToCString() == "Hello"

    aString.Insert(6, " Universe")
    assert aString.ToCString() == "Hello Universe"

    aString.RemoveAll("e")
    assert aString.ToCString() == "Hllo Univrs"


def test_TCollection_AsciiStringTest_Comparison():
    aString1 = TCollection_AsciiString("Test")
    aString2 = TCollection_AsciiString("Test")
    aString3 = TCollection_AsciiString("Different")

    assert aString1.IsEqual(aString2) is True
    assert (aString1 == aString2) is True
    assert aString1.IsDifferent(aString2) is False
    assert (aString1 != aString2) is False

    assert aString1.IsEqual(aString3) is False
    assert (aString1 == aString3) is False
    assert aString1.IsDifferent(aString3) is True
    assert (aString1 != aString3) is True

    assert aString1.IsEqual("Test") is True
    assert (aString1 == "Test") is True
    assert aString1.IsEqual("Different") is False
    assert (aString1 == "Different") is False

    aStringA = TCollection_AsciiString("A")
    aStringZ = TCollection_AsciiString("Z")

    assert aStringA.IsLess(aStringZ) is True
    assert (aStringA < aStringZ) is True
    assert aStringA.IsGreater(aStringZ) is False
    assert (aStringA > aStringZ) is False

    assert aStringZ.IsGreater(aStringA) is True
    assert (aStringZ > aStringA) is True
    assert aStringZ.IsLess(aStringA) is False
    assert (aStringZ < aStringA) is False


def test_TCollection_AsciiStringTest_Token():
    aString = TCollection_AsciiString("This is a test string")

    assert aString.Token().ToCString() == "This"
    assert aString.Token(" ", 2).ToCString() == "is"
    assert aString.Token(" ", 3).ToCString() == "a"
    assert aString.Token(" ", 4).ToCString() == "test"
    assert aString.Token(" ", 5).ToCString() == "string"
    assert aString.Token(" ", 6).ToCString() == ""

    aStringWithSeps = TCollection_AsciiString("one,two;three:four")
    assert aStringWithSeps.Token(",;:", 1).ToCString() == "one"
    assert aStringWithSeps.Token(",;:", 2).ToCString() == "two"
    assert aStringWithSeps.Token(",;:", 3).ToCString() == "three"
    assert aStringWithSeps.Token(",;:", 4).ToCString() == "four"


def test_TCollection_AsciiStringTest_ValueConversion():
    intString = TCollection_AsciiString("12345")
    assert intString.IntegerValue() == 12345
    assert intString.IsIntegerValue() is True

    realString = TCollection_AsciiString("123.456")
    assert realString.RealValue() == 123.456
    assert realString.IsRealValue() is True

    invalidString = TCollection_AsciiString("not a number")
    assert invalidString.IsIntegerValue() is False
    assert invalidString.IsRealValue() is False


def test_TCollection_AsciiStringTest_HashCode():
    aString1 = TCollection_AsciiString("Test")
    aString2 = TCollection_AsciiString("Test")
    aString3 = TCollection_AsciiString("Different")

    assert aString1.HashCode() == aString2.HashCode()
    assert aString1.HashCode() != aString3.HashCode()


def test_TCollection_AsciiStringTest_Split():
    aString = TCollection_AsciiString("abcdefghij")
    remainder = aString.Split(5)

    assert aString.ToCString() == "abcde"
    assert remainder.ToCString() == "fghij"


def test_TCollection_AsciiStringTest_LengthConstructor():
    aSourceString = "This is a very long string"

    aString1 = TCollection_AsciiString(aSourceString, 4)
    assert aString1.Length() == 4
    assert aString1.ToCString() == "This"

    aString2 = TCollection_AsciiString(aSourceString, 7)
    assert aString2.Length() == 7
    assert aString2.ToCString() == "This is"

    aString3 = TCollection_AsciiString(aSourceString, 100)
    assert aString3.Length() == 26
    assert aString3.ToCString() == aSourceString


def test_TCollection_AsciiStringTest_ExtendedStringConversion():
    anExtString = TCollection_ExtendedString("Hello World")
    anAsciiString = TCollection_AsciiString(anExtString)

    assert anExtString.Length() == anAsciiString.Length()
    assert anAsciiString.ToCString() == "Hello World"


def test_TCollection_AsciiStringTest_NumericalConstructors():
    anIntString = TCollection_AsciiString(42)
    assert anIntString.ToCString() == "42"

    aRealString = TCollection_AsciiString(3.14)
    assert "3.14" in aRealString.ToCString()


def test_TCollection_AsciiStringTest_FillerConstructor():
    aFilledString = TCollection_AsciiString(5, "*")
    assert aFilledString.Length() == 5
    assert aFilledString.ToCString() == "*****"


def test_TCollection_AsciiStringTest_ConcatenationConstructors():
    aBaseString = TCollection_AsciiString("Hello")
    aStringWithChar = TCollection_AsciiString(aBaseString, "!")
    assert aStringWithChar.ToCString() == "Hello!"

    aStringWithCStr = TCollection_AsciiString(aBaseString, " World")
    assert aStringWithCStr.ToCString() == "Hello World"

    aSecondString = TCollection_AsciiString(" Universe")
    aCombinedString = TCollection_AsciiString(aBaseString, aSecondString)
    assert aCombinedString.ToCString() == "Hello Universe"


def test_TCollection_AsciiStringTest_EdgeCases():
    anEmptyString1 = TCollection_AsciiString()
    anEmptyString2 = TCollection_AsciiString("")

    assert anEmptyString1.IsEqual(anEmptyString2) is True
    assert anEmptyString1.Length() == 0
    assert anEmptyString1.IsEmpty() is True

    aNullCharString = TCollection_AsciiString("\0")
    assert aNullCharString.Length() == 0
    assert aNullCharString.IsEmpty() is True


def test_TCollection_AsciiStringTest_LargeStrings():
    aLargeSize = 1000
    aLargeString = TCollection_AsciiString(aLargeSize, "X")

    assert aLargeString.Length() == aLargeSize
    assert aLargeString.Value(1) == "X"
    assert aLargeString.Value(aLargeSize) == "X"


def test_TCollection_AsciiStringTest_AssignCat_BasicCases():
    aString = TCollection_AsciiString("Hello")

    aString.AssignCat(" World")
    assert aString.ToCString() == "Hello World"
    assert aString.Length() == 11

    aSuffix = TCollection_AsciiString("!")
    aString.AssignCat(aSuffix)
    assert aString.ToCString() == "Hello World!"
    assert aString.Length() == 12

    aString.AssignCat("?")
    assert aString.ToCString() == "Hello World!?"
    assert aString.Length() == 13


def test_TCollection_AsciiStringTest_AssignCat_EmptyStrings():
    aString = TCollection_AsciiString()

    aString.AssignCat("First")
    assert aString.ToCString() == "First"
    assert aString.Length() == 5

    aString.AssignCat("")
    assert aString.ToCString() == "First"
    assert aString.Length() == 5

    aString2 = TCollection_AsciiString("Test")
    aString2.AssignCat("\0")
    assert aString2.ToCString() == "Test"
    assert aString2.Length() == 4


def test_TCollection_AsciiStringTest_AssignCat_SelfReference():
    aString = TCollection_AsciiString("ABC")

    aString.AssignCat(aString.ToCString())
    assert aString.ToCString() == "ABCABC"
    assert aString.Length() == 6

    aString2 = TCollection_AsciiString("Hello")
    aSubStr = aString2.ToCString()[1:]  # "ello"
    aString2.AssignCat(aSubStr)
    assert aString2.ToCString() == "Helloello"
    assert aString2.Length() == 9


def test_TCollection_AsciiStringTest_AssignCat_IntegerAndReal():
    aString = TCollection_AsciiString("Value: ")

    aString.AssignCat(42)
    assert aString.ToCString() == "Value: 42"

    aString2 = TCollection_AsciiString("Pi is approximately ")
    aString2.AssignCat(3.14159)
    assert "3.14159" in aString2.ToCString()


def test_TCollection_AsciiStringTest_AssignCat_ExtendedStringAndWideChar():
    anExtendedTarget = TCollection_AsciiString("Value:")
    anExtendedSource = TCollection_ExtendedString(" OK")
    anExtendedTarget += anExtendedSource
    assert anExtendedTarget.ToCString() == "Value: OK"

    aNonAsciiChars = " €"
    aNonAsciiSource = TCollection_ExtendedString(aNonAsciiChars, len(aNonAsciiChars))  # char16_t*, length
    aReplacedTarget = TCollection_AsciiString("Value")
    aReplacedTarget.AssignCat(aNonAsciiSource, "?")
    assert aReplacedTarget.ToCString() == "Value ?"


def test_TCollection_AsciiStringTest_AssignCat_LargeStrings():
    aString = TCollection_AsciiString(100, "A")
    aSuffix = TCollection_AsciiString(100, "B")

    aString.AssignCat(aSuffix)
    assert aString.Length() == 200

    aPtr = aString.ToCString()
    assert aPtr[:100] == "A" * 100
    assert aPtr[100:200] == "B" * 100


def test_TCollection_AsciiStringTest_Insert_BasicCases():
    aString = TCollection_AsciiString("HelloWorld")
    aString.Insert(1, "Start")
    assert aString.ToCString() == "StartHelloWorld"

    aString2 = TCollection_AsciiString("AC")
    aString2.Insert(2, "B")
    assert aString2.ToCString() == "ABC"

    aString3 = TCollection_AsciiString("Hello")
    aString3.Insert(6, " World")
    assert aString3.ToCString() == "Hello World"


def test_TCollection_AsciiStringTest_Insert_EmptyStrings():
    aString = TCollection_AsciiString()
    aString.Insert(1, "First")
    assert aString.ToCString() == "First"
    assert aString.Length() == 5

    aString2 = TCollection_AsciiString("Test")
    aString2.Insert(3, "")
    assert aString2.ToCString() == "Test"
    assert aString2.Length() == 4


def test_TCollection_AsciiStringTest_Insert_SelfReference():
    aString = TCollection_AsciiString("XYZ")
    aString.Insert(1, aString.ToCString())
    assert aString.ToCString() == "XYZXYZ"
    assert aString.Length() == 6

    aString2 = TCollection_AsciiString("ABCD")
    aSubStr = aString2.ToCString()[1:]  # "BCD"
    aString2.Insert(2, aSubStr)
    assert aString2.ToCString() == "ABCDBCD"
    assert aString2.Length() == 7


def test_TCollection_AsciiStringTest_Insert_WithCharacter():
    aString = TCollection_AsciiString("Hllo")
    aString.Insert(2, "e")
    assert aString.ToCString() == "Hello"
    assert aString.Length() == 5

    aString2 = TCollection_AsciiString("ello")
    aString2.Insert(1, "H")
    assert aString2.ToCString() == "Hello"


def test_TCollection_AsciiStringTest_Insert_BoundaryConditions():
    aString = TCollection_AsciiString("Test")

    aString1 = TCollection_AsciiString(aString)
    aString1.Insert(1, ">")
    assert aString1.ToCString() == ">Test"

    aString2 = TCollection_AsciiString(aString)
    aString2.Insert(5, "<")
    assert aString2.ToCString() == "Test<"


def test_TCollection_AsciiStringTest_Insert_OverlapLeftSide():
    aString = TCollection_AsciiString("ABCDEFGH")
    aSource = aString.ToCString()
    aString.Insert(4, aSource, 3)
    assert aString.ToCString() == "ABCABCDEFGH"
    assert aString.Length() == 11


def test_TCollection_AsciiStringTest_Insert_OverlapRightSide():
    aString = TCollection_AsciiString("ABCDEFGH")
    aSource = aString.ToCString()[3:]  # "DEFGH"
    aString.Insert(2, aSource)
    assert aString.ToCString() == "ADEFGHBCDEFGH"
    assert aString.Length() == 13


def test_TCollection_AsciiStringTest_Insert_OverlapInsideShiftWindow():
    aString = TCollection_AsciiString("ABCDEFGH")
    aSource = aString.ToCString()[2:]  # "CDEFGH"
    aString.Insert(2, aSource, 3)
    assert aString.ToCString() == "ACDEBCDEFGH"
    assert aString.Length() == 11


def test_TCollection_AsciiStringTest_Insert_OverlapStartsBeforeShiftWindow():
    aString = TCollection_AsciiString("ABCDEFGH")
    aSource = aString.ToCString()[1:]  # "BCDEFGH"
    aString.Insert(4, aSource, 4)
    assert aString.ToCString() == "ABCBCDEDEFGH"
    assert aString.Length() == 12


def test_TCollection_AsciiStringTest_Insert_OverlapAtInsertionPoint():
    aString = TCollection_AsciiString("ABCDEFGH")
    aSource = aString.ToCString()[3:]  # "DEFGH"
    aString.Insert(4, aSource, 3)
    assert aString.ToCString() == "ABCDEFDEFGH"
    assert aString.Length() == 11


def test_TCollection_AsciiStringTest_Insert_OverlapComplex1():
    aString = TCollection_AsciiString("123456789")
    aSource = aString.ToCString()[3:]  # "456789"
    aString.Insert(1, aSource, 3)
    assert aString.ToCString() == "456123456789"
    assert aString.Length() == 12


def test_TCollection_AsciiStringTest_Insert_OverlapComplex2():
    aString = TCollection_AsciiString("XYZABC")
    aSource = aString.ToCString()
    aString.Insert(4, aSource, 2)
    assert aString.ToCString() == "XYZXYABC"
    assert aString.Length() == 8


def test_TCollection_AsciiStringTest_Insert_OverlapSpansEntireShiftWindow():
    aString = TCollection_AsciiString("ABCDEFGHIJK")
    aSource = aString.ToCString()[1:]  # "BCDEFGHIJK"
    aString.Insert(5, aSource, 7)
    assert aString.ToCString() == "ABCDBCDEFGHEFGHIJK"
    assert aString.Length() == 18


def test_TCollection_AsciiStringTest_Insert_OverlapSingleChar():
    aString = TCollection_AsciiString("ABC")
    aSource = aString.ToCString()[1:]  # "BC"
    aString.Insert(1, aSource, 1)
    assert aString.ToCString() == "BABC"
    assert aString.Length() == 4


def test_TCollection_AsciiStringTest_Insert_OverlapEndToBeginning():
    aString = TCollection_AsciiString("HELLO")
    aSource = aString.ToCString()[3:]  # "LO"
    aString.Insert(1, aSource)
    assert aString.ToCString() == "LOHELLO"
    assert aString.Length() == 7


def test_TCollection_AsciiStringTest_Insert_OverlapLargeString():
    aString = TCollection_AsciiString(50, "A")
    aString.SetValue(25, "MARKER")
    aSource = aString.ToCString()[20:]
    aString.Insert(10, aSource, 10)
    assert aString.Length() == 60
    assert "MARKER" in aString.ToCString()


def test_TCollection_AsciiStringTest_Cat_BasicCases():
    aString = TCollection_AsciiString("Hello")

    aResult1 = aString.Cat(" World")
    assert aResult1.ToCString() == "Hello World"
    assert aString.ToCString() == "Hello"

    aSuffix = TCollection_AsciiString("!")
    aResult2 = aString.Cat(aSuffix)
    assert aResult2.ToCString() == "Hello!"

    aResult3 = aString.Cat("?")
    assert aResult3.ToCString() == "Hello?"


def test_TCollection_AsciiStringTest_Cat_IntegerAndReal():
    aString = TCollection_AsciiString("Count: ")

    aResult1 = aString.Cat(42)
    assert aResult1.ToCString() == "Count: 42"

    aResult2 = aString.Cat(-100)
    assert aResult2.ToCString() == "Count: -100"

    aString2 = TCollection_AsciiString("Value: ")
    aResult3 = aString2.Cat(3.14)
    assert "3.14" in aResult3.ToCString()

    aResult4 = aString.Cat(0)
    assert aResult4.ToCString() == "Count: 0"


def test_TCollection_AsciiStringTest_Cat_ExtendedStringAndWideChar():
    aString = TCollection_AsciiString("Value:")
    anExtendedSource = TCollection_ExtendedString(" OK")
    anExtendedResult = aString + anExtendedSource
    assert anExtendedResult.ToCString() == "Value: OK"

    anAccentChars = " é"
    anAccentSource = TCollection_ExtendedString(anAccentChars, len(anAccentChars))  # char16_t*, length
    anUtf8Result = TCollection_AsciiString("Cafe").Cat(anAccentSource)
    assert anUtf8Result.Length() == 7
    aBytes = anUtf8Result.ToCString().encode("utf-8")
    assert aBytes[4] == ord(" ")
    assert aBytes[5] == 0xC3
    assert aBytes[6] == 0xA9

    assert aString.ToCString() == "Value:"


def test_TCollection_AsciiStringTest_Cat_EmptyStrings():
    aEmpty = TCollection_AsciiString()
    aResult1 = aEmpty.Cat("First")
    assert aResult1.ToCString() == "First"

    aString = TCollection_AsciiString("Test")
    aResult2 = aString.Cat("")
    assert aResult2.ToCString() == "Test"


def test_TCollection_AsciiStringTest_Cat_ChainedOperations():
    aString = TCollection_AsciiString("A")
    aResult = aString.Cat("B").Cat("C").Cat("D")
    assert aResult.ToCString() == "ABCD"


def test_TCollection_AsciiStringTest_Copy_BasicCases():
    aString = TCollection_AsciiString("Original")

    aString.Copy("NewValue")
    assert aString.ToCString() == "NewValue"
    assert aString.Length() == 8

    aSource = TCollection_AsciiString("Another")
    aString.Copy(aSource)
    assert aString.ToCString() == "Another"
    assert aString.Length() == 7


def test_TCollection_AsciiStringTest_Copy_ShorterAndLonger():
    aString = TCollection_AsciiString("LongString")

    aString.Copy("Short")
    assert aString.ToCString() == "Short"
    assert aString.Length() == 5

    aString.Copy("VeryLongStringHere")
    assert aString.ToCString() == "VeryLongStringHere"
    assert aString.Length() == 18


def test_TCollection_AsciiStringTest_Copy_EmptyString():
    aString = TCollection_AsciiString("Original")
    aString.Copy("")
    assert aString.ToCString() == ""
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_AsciiStringTest_Copy_SelfAssignment():
    aString = TCollection_AsciiString("Test")
    aString.Copy(aString.ToCString())
    assert aString.ToCString() == "Test"
    assert aString.Length() == 4


def test_TCollection_AsciiStringTest_Copy_MemoryReuse():
    aString = TCollection_AsciiString(100, "A")

    aString.Copy("Short")
    assert aString.ToCString() == "Short"
    assert aString.Length() == 5

    aString.Copy("Tiny")
    assert aString.ToCString() == "Tiny"
    assert aString.Length() == 4


def test_TCollection_AsciiStringTest_Search_BasicCases():
    aString = TCollection_AsciiString("This is a test string")

    assert aString.Search("This") == 1
    assert aString.Search("test") == 11
    assert aString.Search("string") == 16

    assert aString.Search("xyz") == -1
    assert aString.Search("notfound") == -1


def test_TCollection_AsciiStringTest_Search_EdgeCases():
    aString = TCollection_AsciiString("abcabc")

    assert aString.Search("abc") == 1

    assert aString.Search("a") == 1
    assert aString.Search("b") == 2
    assert aString.Search("c") == 3

    assert aString.Search("") == -1

    anEmpty = TCollection_AsciiString()
    assert anEmpty.Search("test") == -1


def test_TCollection_AsciiStringTest_Search_RepeatedPattern():
    aString = TCollection_AsciiString("aaaaaaa")
    assert aString.Search("aaa") == 1

    aString2 = TCollection_AsciiString("abcabcabc")
    assert aString2.Search("abc") == 1
    assert aString2.Search("abcabc") == 1


def test_TCollection_AsciiStringTest_SearchFromEnd_BasicCases():
    aString = TCollection_AsciiString("This is a test string with test")

    assert aString.SearchFromEnd("test") == 28
    assert aString.SearchFromEnd("string") == 16

    assert aString.SearchFromEnd("xyz") == -1


def test_TCollection_AsciiStringTest_SearchFromEnd_EdgeCases():
    aString = TCollection_AsciiString("abcabc")

    assert aString.SearchFromEnd("abc") == 4

    assert aString.SearchFromEnd("a") == 4
    assert aString.SearchFromEnd("c") == 6

    assert aString.SearchFromEnd("") == -1

    anEmpty = TCollection_AsciiString()
    assert anEmpty.SearchFromEnd("test") == -1


def test_TCollection_AsciiStringTest_Search_LongerThanString():
    aString = TCollection_AsciiString("Short")
    assert aString.Search("VeryLongSubstring") == -1


def test_TCollection_AsciiStringTest_IsSameString_CaseSensitive():
    aString1 = TCollection_AsciiString("Test")
    aString2 = TCollection_AsciiString("Test")
    aString3 = TCollection_AsciiString("test")
    aString4 = TCollection_AsciiString("Different")

    assert TCollection_AsciiString.IsSameString_s(aString1, aString2, True) is True
    assert TCollection_AsciiString.IsSameString_s(aString1, aString3, True) is False
    assert TCollection_AsciiString.IsSameString_s(aString1, aString4, True) is False


def test_TCollection_AsciiStringTest_IsSameString_CaseInsensitive():
    aString1 = TCollection_AsciiString("Test")
    aString2 = TCollection_AsciiString("TEST")
    aString3 = TCollection_AsciiString("test")
    aString4 = TCollection_AsciiString("TeSt")

    assert TCollection_AsciiString.IsSameString_s(aString1, aString2, False) is True
    assert TCollection_AsciiString.IsSameString_s(aString1, aString3, False) is True
    assert TCollection_AsciiString.IsSameString_s(aString1, aString4, False) is True


def test_TCollection_AsciiStringTest_IsSameString_EmptyStrings():
    aEmpty1 = TCollection_AsciiString()
    aEmpty2 = TCollection_AsciiString("")
    aNonEmpty = TCollection_AsciiString("Test")

    assert TCollection_AsciiString.IsSameString_s(aEmpty1, aEmpty2, True) is True
    assert TCollection_AsciiString.IsSameString_s(aEmpty1, aEmpty2, False) is True
    assert TCollection_AsciiString.IsSameString_s(aEmpty1, aNonEmpty, True) is False


def test_TCollection_AsciiStringTest_IsSameString_DifferentLengths():
    aString1 = TCollection_AsciiString("Short")
    aString2 = TCollection_AsciiString("VeryLong")

    assert TCollection_AsciiString.IsSameString_s(aString1, aString2, True) is False
    assert TCollection_AsciiString.IsSameString_s(aString1, aString2, False) is False


def test_TCollection_AsciiStringTest_IsSameString_WithCStrings():
    assert TCollection_AsciiString.IsSameString_s("Test", 4, "Test", 4, True) is True
    assert TCollection_AsciiString.IsSameString_s("Test", 4, "test", 4, True) is False
    assert TCollection_AsciiString.IsSameString_s("Test", 4, "test", 4, False) is True


def test_TCollection_AsciiStringTest_IsEqual_AllOverloads():
    aString = TCollection_AsciiString("Test")

    aString2 = TCollection_AsciiString("Test")
    assert aString.IsEqual(aString2) is True

    assert aString.IsEqual("Test") is True
    assert aString.IsEqual("Different") is False

    aString3 = TCollection_AsciiString("test")
    assert aString.IsEqual(aString3) is False


def test_TCollection_AsciiStringTest_IsDifferent_AllOverloads():
    aString = TCollection_AsciiString("Test")

    aString2 = TCollection_AsciiString("Different")
    assert aString.IsDifferent(aString2) is True

    assert aString.IsDifferent("Different") is True
    assert aString.IsDifferent("Test") is False


def test_TCollection_AsciiStringTest_IsLess_AllOverloads():
    aStringA = TCollection_AsciiString("Apple")
    aStringB = TCollection_AsciiString("Banana")

    assert aStringA.IsLess(aStringB) is True
    assert aStringB.IsLess(aStringA) is False

    assert aStringA.IsLess("Banana") is True
    assert aStringB.IsLess("Apple") is False

    assert aStringA.IsLess(aStringA) is False


def test_TCollection_AsciiStringTest_IsGreater_AllOverloads():
    aStringA = TCollection_AsciiString("Apple")
    aStringB = TCollection_AsciiString("Banana")

    assert aStringB.IsGreater(aStringA) is True
    assert aStringA.IsGreater(aStringB) is False

    assert aStringB.IsGreater("Apple") is True
    assert aStringA.IsGreater("Banana") is False

    assert aStringA.IsGreater(aStringA) is False


def test_TCollection_AsciiStringTest_Comparison_EmptyStrings():
    aEmpty = TCollection_AsciiString()
    aNonEmpty = TCollection_AsciiString("Test")

    assert aEmpty.IsEqual("") is True
    assert aEmpty.IsEqual(aNonEmpty) is False
    assert aEmpty.IsDifferent(aNonEmpty) is True
    assert aEmpty.IsLess(aNonEmpty) is True
    assert aEmpty.IsGreater(aNonEmpty) is False


def test_TCollection_AsciiStringTest_SetValue_BasicCases():
    aString = TCollection_AsciiString("Hello")

    aString.SetValue(1, "h")
    assert aString.ToCString() == "hello"

    aString.SetValue(5, "!")
    assert aString.ToCString() == "hell!"


def test_TCollection_AsciiStringTest_SetValue_WithString():
    aString = TCollection_AsciiString("AAAAA")

    aString.SetValue(2, "XYZ")
    assert aString.ToCString() == "AXYZA"

    aReplacement = TCollection_AsciiString("12")
    aString.SetValue(1, aReplacement)
    assert aString.ToCString() == "12YZA"


def test_TCollection_AsciiStringTest_SetValue_BoundaryConditions():
    aString = TCollection_AsciiString("Test")

    aString.SetValue(1, "X")
    assert aString.ToCString() == "Xest"

    aString.SetValue(4, "Y")
    assert aString.ToCString() == "XesY"


def test_TCollection_AsciiStringTest_SetValue_StringOverflow():
    aString = TCollection_AsciiString("AAAA")
    aString.SetValue(3, "XYZ")
    assert aString.ToCString() == "AAXYZ"
    assert aString.Length() == 5


def test_TCollection_AsciiStringTest_Remove_BasicCases():
    aString = TCollection_AsciiString("Hello World")
    aString.Remove(6, 6)
    assert aString.ToCString() == "Hello"
    assert aString.Length() == 5

    aString2 = TCollection_AsciiString("XYZTest")
    aString2.Remove(1, 3)
    assert aString2.ToCString() == "Test"

    aString3 = TCollection_AsciiString("TestXYZ")
    aString3.Remove(5, 3)
    assert aString3.ToCString() == "Test"


def test_TCollection_AsciiStringTest_Remove_EntireString():
    aString = TCollection_AsciiString("Test")
    aString.Remove(1, 4)
    assert aString.ToCString() == ""
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_AsciiStringTest_RemoveAll_SingleCharacter():
    aString = TCollection_AsciiString("Mississippi")

    aString.RemoveAll("s")
    assert aString.ToCString() == "Miiippi"

    aString.RemoveAll("i")
    assert aString.ToCString() == "Mpp"


def test_TCollection_AsciiStringTest_RemoveAll_NoOccurrence():
    aString = TCollection_AsciiString("Test")
    aString.RemoveAll("X")
    assert aString.ToCString() == "Test"
    assert aString.Length() == 4


def test_TCollection_AsciiStringTest_RemoveAll_AllCharacters():
    aString = TCollection_AsciiString("AAAA")
    aString.RemoveAll("A")
    assert aString.ToCString() == ""
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_AsciiStringTest_Trunc_BasicCases():
    aString = TCollection_AsciiString("Hello World")

    aString.Trunc(5)
    assert aString.ToCString() == "Hello"
    assert aString.Length() == 5

    aString.Trunc(0)
    assert aString.ToCString() == ""
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_AsciiStringTest_Trunc_NoChange():
    aString = TCollection_AsciiString("Test")
    aString.Trunc(4)
    assert aString.ToCString() == "Test"
    assert aString.Length() == 4


def test_TCollection_AsciiStringTest_TemplateLiteral_Constructor():
    aString = TCollection_AsciiString("Literal")
    assert aString.ToCString() == "Literal"
    assert aString.Length() == 7


def test_TCollection_AsciiStringTest_StressTest_MultipleOperations():
    aString = TCollection_AsciiString()

    for _ in range(10):
        aString.AssignCat("A")
    assert aString.Length() == 10

    for _ in range(5):
        aString.Insert(6, "B")
    assert aString.Length() == 15

    aString.RemoveAll("B")
    assert aString.Length() == 10
    assert aString.ToCString() == "AAAAAAAAAA"


def test_TCollection_AsciiStringTest_StressTest_LargeOperations():
    aLarge = TCollection_AsciiString(1000, "X")
    assert aLarge.Length() == 1000

    aCopy = TCollection_AsciiString()
    aCopy.Copy(aLarge)
    assert aCopy.Length() == 1000

    aLarge.AssignCat(aCopy)
    assert aLarge.Length() == 2000


def test_TCollection_AsciiStringTest_EdgeCase_NullCharacterHandling():
    aString = TCollection_AsciiString("\0")
    assert aString.IsEmpty() is True
    assert aString.Length() == 0


def test_TCollection_AsciiStringTest_EdgeCase_ConsecutiveOperations():
    aString = TCollection_AsciiString("Test")

    aString.Copy("A")
    aString.Copy("BB")
    aString.Copy("CCC")
    assert aString.ToCString() == "CCC"

    aString.AssignCat("D")
    aString.AssignCat("E")
    aString.AssignCat("F")
    assert aString.ToCString() == "CCCDEF"


def test_TCollection_AsciiStringTest_AssignCat_MultipleInLoop():
    aDef = TCollection_AsciiString()

    aDef.AssignCat("Enum")
    aDef.AssignCat(f" [in {0}-{1}]")
    assert aDef.ToCString() == "Enum [in 0-1]"

    for i in range(2):
        anEnva = "Off" if i == 0 else "On"
        aDef.AssignCat(f" {i}:{anEnva}")
    assert aDef.ToCString() == "Enum [in 0-1] 0:Off 1:On"

    aDef.AssignCat(" , alpha: ")
    aDef.AssignCat("On")
    aDef.AssignCat(f"On:{1} ")
    aDef.AssignCat("Off")
    aDef.AssignCat(f"Off:{0} ")

    aResult = aDef.ToCString()
    assert "Enum" in aResult
    assert "[in 0-1]" in aResult
    assert "0:Off" in aResult
    assert "1:On" in aResult
    assert "alpha:" in aResult


def test_TCollection_AsciiStringTest_BUC60724_EmptyStringInitialization():
    aString1 = TCollection_AsciiString("")
    assert aString1.ToCString() is not None
    assert aString1.Length() == 0
    assert aString1.ToCString() == ""

    aString2 = TCollection_AsciiString("\0")
    assert aString2.ToCString() is not None
    assert aString2.Length() == 0
    assert aString2.ToCString() == ""


def test_TCollection_AsciiStringTest_BUC60773_HAsciiStringInitialization():
    anHAscii = TCollection_HAsciiString()
    assert anHAscii is not None

    aStr = anHAscii.ToCString()
    assert aStr is not None

    aAscii = TCollection_AsciiString(aStr)
    assert aAscii.Length() == 0
    assert aAscii.IsEmpty() is True


def test_TCollection_AsciiStringTest_OCC6794_LargeConcatenation():
    aNb = 10000
    aC = "a"

    anAscii = TCollection_AsciiString()
    for _ in range(aNb):
        anAscii += TCollection_AsciiString(aC)

    assert anAscii.Length() == aNb
    assert anAscii.IsEmpty() is False


def test_TCollection_AsciiStringTest_OCC11758_ComprehensiveConstructorsAndMethods():
    theStr = "0123456789"

    for i in range(5):
        a = TCollection_AsciiString(theStr[i:])
        assert a.ToCString() == theStr[i:]

        b = TCollection_AsciiString(theStr[i:], 3)
        assert b.Length() == 3
        assert b.ToCString()[:3] == theStr[i:i + 3]

        c = TCollection_AsciiString(i)
        assert c.IsIntegerValue() is True
        assert c.IntegerValue() == i

        d = TCollection_AsciiString(0.1 * i)
        assert d.IsRealValue(True) is True
        assert TCollection_AsciiString("3.3!").IsRealValue(True) is False
        assert TCollection_AsciiString("3.3!").IsRealValue(False) is True
        assert TCollection_AsciiString(3.3).ToCString() == "3.3"

        e = TCollection_AsciiString(d)
        assert e.ToCString() == d.ToCString()
        assert e.Length() == d.Length()

        f = TCollection_AsciiString(e, "\a")
        assert f.Length() == e.Length() + 1
        assert f.ToCString()[:e.Length()] == e.ToCString()
        assert f.Value(f.Length()) == "\a"

        g = TCollection_AsciiString(f, theStr)
        assert g.Length() == f.Length() + len(theStr)
        assert g.ToCString()[:f.Length()] == f.ToCString()
        assert g.Search(theStr) == f.Length() + 1

        h = TCollection_AsciiString(d, a)
        assert h.Length() == d.Length() + a.Length()
        assert h.ToCString()[:d.Length()] == d.ToCString()
        assert h.ToCString()[d.Length():d.Length() + a.Length()] == a.ToCString()

        c.AssignCat(a.ToCString())
        assert c.Length() == 1 + a.Length()
        assert c.Search(a) == 2

        dl = d.Length()
        d.AssignCat(a)
        assert d.Length() == dl + a.Length()
        assert d.Search(a) == dl + 1

        capitalize = TCollection_AsciiString("aBC")
        capitalize.Capitalize()
        assert capitalize.ToCString() == "Abc"

        # Copy assignment (C++ operator=) -> Copy()
        d.Copy(theStr[i:])
        assert d.ToCString() == theStr[i:]

        d.Copy(h)
        assert d.ToCString() == h.ToCString()

        dl = d.Length()
        d.Insert(2, theStr)
        assert d.Length() == dl + len(theStr)
        assert d.ToCString()[1:1 + len(theStr)] == theStr

        d.Copy(theStr)
        d.Insert(i + 1, "i")
        assert d.Length() == len(theStr) + 1
        assert d.Value(i + 1) == "i"
        assert d.ToCString()[i + 1:] == theStr[i:]

        d.Copy(theStr)
        d.Insert(i + 1, TCollection_AsciiString("i"))
        assert d.Length() == len(theStr) + 1
        assert d.Value(i + 1) == "i"
        assert d.ToCString()[i + 1:] == theStr[i:]

        assert d.IsDifferent(theStr) is True
        assert d.IsDifferent("theStr") is True
        assert d.IsDifferent("") is True
        assert d.IsDifferent(d.ToCString()) is False


def test_TCollection_AsciiStringTest_UsefullLength_EmptyString():
    aStr = TCollection_AsciiString()
    assert aStr.UsefullLength() == 0


def test_TCollection_AsciiStringTest_UsefullLength_AsciiNoTrailing():
    aStr = TCollection_AsciiString("Hello")
    assert aStr.UsefullLength() == 5


def test_TCollection_AsciiStringTest_UsefullLength_TrailingSpaces():
    aStr = TCollection_AsciiString("Hello   ")
    assert aStr.UsefullLength() == 5


def test_TCollection_AsciiStringTest_UsefullLength_TrailingControlChars():
    aStr = TCollection_AsciiString("Hello")
    aStr += "\t"
    aStr += "\n"
    aStr += "\r"
    assert aStr.UsefullLength() == 5


def test_TCollection_AsciiStringTest_UsefullLength_AllSpaces():
    aStr = TCollection_AsciiString("     ")
    assert aStr.UsefullLength() == 0


def test_TCollection_AsciiStringTest_UsefullLength_AllControlChars():
    aStr = TCollection_AsciiString("\t\n\r")
    assert aStr.UsefullLength() == 0


def test_TCollection_AsciiStringTest_UsefullLength_SingleChar():
    aStr = TCollection_AsciiString("A")
    assert aStr.UsefullLength() == 1


def test_TCollection_AsciiStringTest_UsefullLength_SingleSpace():
    aStr = TCollection_AsciiString(" ")
    assert aStr.UsefullLength() == 0


def test_TCollection_AsciiStringTest_UsefullLength_MixedTrailing():
    aStr = TCollection_AsciiString("Part Name  \t\n")
    assert aStr.UsefullLength() == 9


def test_TCollection_AsciiStringTest_UsefullLength_Utf8AtEnd():
    # "Hello" + U+4E16 U+754C, 3 UTF-8 bytes each
    aStr = TCollection_AsciiString("Hello世界")
    assert aStr.UsefullLength() == 11


def test_TCollection_AsciiStringTest_UsefullLength_Utf8ThenSpaces():
    aStr = TCollection_AsciiString("Привет   ")
    assert aStr.UsefullLength() == 12


def test_TCollection_AsciiStringTest_UsefullLength_Utf8Only():
    aStr = TCollection_AsciiString("日本")
    assert aStr.UsefullLength() == 6


def test_TCollection_AsciiStringTest_UsefullLength_Utf8FourByteAtEnd():
    aStr = TCollection_AsciiString("Test\U0001f600")
    assert aStr.UsefullLength() == 8


def test_TCollection_AsciiStringTest_UsefullLength_Utf8ThenControlChars():
    aStr = TCollection_AsciiString("Ä")
    aStr += "\t"
    aStr += "\n"
    assert aStr.UsefullLength() == 2
