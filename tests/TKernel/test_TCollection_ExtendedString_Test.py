# Translated from OCCT src/FoundationClasses/TKernel/GTests/TCollection_ExtendedString_Test.cxx (LGPL-2.1 with the OCCT exception)
#
# Mapping notes: TCollection_ExtendedString(str) is the const char* constructor (UTF-8 bytes, each byte copied unless
# theIsMultiByte=True); a char16_t array is built with the (char16_t*, length) overload: E(s, len(s)).
# The single-character constructors (char, char16_t) are not bound separately; a one-character str goes through
# const char* (ASCII) or through (char16_t*, 1) for non-ASCII code units. Value() returns a one-character str.
# Skipped: AssignmentOperator (C++ operator=), WideCharConstructor (wchar_t), StringView_* (u16string_view),
# *_NullPointer / *_ZeroLength* with nullptr (pointer semantics), the ToUTF8CString parts (char* out buffer, not bound).

import pytest

from nanocct.NCollection import NCollection_DataMap
from nanocct.Standard import Standard_OutOfRange
from nanocct.TCollection import TCollection_AsciiString, TCollection_ExtendedString


def _u16(s):
    """A TCollection_ExtendedString from a char16_t array (the (char16_t*, length) constructor)."""
    return TCollection_ExtendedString(s, len(s))


def test_TCollection_ExtendedStringTest_DefaultConstructor():
    aString = TCollection_ExtendedString()
    assert aString.Length() == 0
    assert aString.IsEmpty() is True


def test_TCollection_ExtendedStringTest_ConstructorWithCString():
    aString = TCollection_ExtendedString("Test String")
    assert aString.Length() == 11
    assert aString.IsEmpty() is False


def test_TCollection_ExtendedStringTest_ConstructorWithChar():
    aString = TCollection_ExtendedString("A")
    assert aString.Length() == 1
    assert aString.IsEmpty() is False


def test_TCollection_ExtendedStringTest_ConstructorWithAsciiString():
    asciiString = TCollection_AsciiString("ASCII Test")
    extendedString = TCollection_ExtendedString(asciiString)
    assert extendedString.Length() == asciiString.Length()


def test_TCollection_ExtendedStringTest_CopyConstructor():
    aString1 = TCollection_ExtendedString("Original")
    aString2 = TCollection_ExtendedString(aString1)
    assert aString1.Length() == aString2.Length()
    assert aString1.IsEqual(aString2) is True


def test_TCollection_ExtendedStringTest_Concatenation():
    aString1 = TCollection_ExtendedString("Hello")
    aString2 = TCollection_ExtendedString(" World")
    aString3 = aString1 + aString2
    assert aString3.Length() == 11

    asciiResult = TCollection_AsciiString(aString3)
    assert asciiResult.ToCString() == "Hello World"

    aString1 += aString2
    assert aString1.IsEqual(aString3) is True


def test_TCollection_ExtendedStringTest_ConversionToFromAscii():
    asciiString = TCollection_AsciiString("Test String")
    extendedString = TCollection_ExtendedString(asciiString)
    convertedBack = TCollection_AsciiString(extendedString)
    assert convertedBack.ToCString() == asciiString.ToCString()


def test_TCollection_ExtendedStringTest_Comparison():
    aString1 = TCollection_ExtendedString("Test")
    aString2 = TCollection_ExtendedString("Test")
    aString3 = TCollection_ExtendedString("Different")

    assert aString1.IsEqual(aString2) is True
    assert (aString1 == aString2) is True
    assert aString1.IsDifferent(aString2) is False
    assert (aString1 != aString2) is False

    assert aString1.IsEqual(aString3) is False
    assert (aString1 == aString3) is False
    assert aString1.IsDifferent(aString3) is True
    assert (aString1 != aString3) is True

    aStringA = TCollection_ExtendedString("A")
    aStringZ = TCollection_ExtendedString("Z")

    assert aStringA.IsLess(aStringZ) is True
    assert (aStringA < aStringZ) is True
    assert aStringA.IsGreater(aStringZ) is False
    assert (aStringA > aStringZ) is False

    assert aStringZ.IsGreater(aStringA) is True
    assert (aStringZ > aStringA) is True
    assert aStringZ.IsLess(aStringA) is False
    assert (aStringZ < aStringA) is False


def test_TCollection_ExtendedStringTest_UnicodeSupport():
    unicodeString = _u16("A©™€")

    assert unicodeString.Length() == 4
    assert ord(unicodeString.Value(1)) == 0x0041
    assert ord(unicodeString.Value(2)) == 0x00A9
    assert ord(unicodeString.Value(3)) == 0x2122
    assert ord(unicodeString.Value(4)) == 0x20AC


def test_TCollection_ExtendedStringTest_HashCode():
    aString1 = TCollection_ExtendedString("Test")
    aString2 = TCollection_ExtendedString("Test")
    aString3 = TCollection_ExtendedString("Different")

    assert aString1.HashCode() == aString2.HashCode()
    assert aString1.HashCode() != aString3.HashCode()


def test_TCollection_ExtendedStringTest_Remove():
    aString = TCollection_ExtendedString("Hello World")
    aString.Remove(6, 6)
    asciiResult = TCollection_AsciiString(aString)
    assert asciiResult.ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_ToExtString():
    aString = TCollection_ExtendedString("Test String")
    extString = aString.ToExtString()
    assert extString[0] == "T"
    assert extString[1] == "e"
    assert extString[2] == "s"
    assert extString[3] == "t"


def test_TCollection_ExtendedStringTest_IsAscii():
    asciiString = TCollection_ExtendedString("Simple ASCII")
    assert asciiString.IsAscii() is True

    unicodeString = _u16("A€")
    assert unicodeString.IsAscii() is False


def test_TCollection_ExtendedStringTest_Cat():
    aString = TCollection_ExtendedString("Hello")

    result1 = aString.Cat(TCollection_ExtendedString(" World"))
    assert TCollection_AsciiString(result1).ToCString() == "Hello World"

    result2 = aString.Cat("!")
    assert TCollection_AsciiString(result2).ToCString() == "Hello!"

    result3 = aString + "!"
    assert TCollection_AsciiString(result3).ToCString() == "Hello!"


def test_TCollection_ExtendedStringTest_AssignCat_IntegerAndReal():
    anIntegerString = TCollection_ExtendedString("Value: ")
    anIntegerString.AssignCat(42)
    assert TCollection_AsciiString(anIntegerString).ToCString() == "Value: 42"

    aCharString = TCollection_ExtendedString("Value: ")
    aCharString += "!"
    assert TCollection_AsciiString(aCharString).ToCString() == "Value: !"

    anOperatorString = TCollection_ExtendedString("Value: ")
    anOperatorString += -7
    assert TCollection_AsciiString(anOperatorString).ToCString() == "Value: -7"

    aZeroString = TCollection_ExtendedString("Value: ")
    aZeroString += 0
    assert TCollection_AsciiString(aZeroString).ToCString() == "Value: 0"

    aRealString = TCollection_ExtendedString("Pi is approximately ")
    aRealString.AssignCat(3.14159)
    assert "3.14159" in TCollection_AsciiString(aRealString).ToCString()


def test_TCollection_ExtendedStringTest_Cat_IntegerAndReal():
    aString = TCollection_ExtendedString("Count: ")

    anIntegerResult = aString.Cat(42)
    assert TCollection_AsciiString(anIntegerResult).ToCString() == "Count: 42"

    aNegativeResult = aString + (-100)
    assert TCollection_AsciiString(aNegativeResult).ToCString() == "Count: -100"

    aZeroResult = aString.Cat(0)
    assert TCollection_AsciiString(aZeroResult).ToCString() == "Count: 0"

    aRealSource = TCollection_ExtendedString("Value: ")
    aRealResult = aRealSource + 3.14
    assert "3.14" in TCollection_AsciiString(aRealResult).ToCString()

    assert TCollection_AsciiString(aString).ToCString() == "Count: "


def test_TCollection_ExtendedStringTest_ChangeAll():
    aString = TCollection_ExtendedString("Helloo Woorld")
    aString.ChangeAll("o", "X")
    assert TCollection_AsciiString(aString).ToCString() == "HellXX WXXrld"


def test_TCollection_ExtendedStringTest_UTF8Conversion():
    # ToUTF8CString (char* out buffer) is not bound; only LengthOfCString is checked
    aString = TCollection_ExtendedString("Hello World")
    aBufferSize = aString.LengthOfCString()
    assert aBufferSize > 0
    assert aBufferSize == 11
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_UTF8ConversionUnicode():
    # ToUTF8CString (char* out buffer) is not bound; only LengthOfCString is checked
    aString = _u16("Héllo")
    aBufferSize = aString.LengthOfCString()
    assert aBufferSize > 5


def test_TCollection_ExtendedStringTest_NumericalConstructors():
    anIntString = TCollection_ExtendedString(42)
    assert TCollection_AsciiString(anIntString).ToCString() == "42"

    aRealString = TCollection_ExtendedString(3.14)
    assert "3.14" in TCollection_AsciiString(aRealString).ToCString()


def test_TCollection_ExtendedStringTest_FillerConstructor():
    aFilledString = TCollection_ExtendedString(5, "X")
    assert aFilledString.Length() == 5
    assert TCollection_AsciiString(aFilledString).ToCString() == "XXXXX"


def test_TCollection_ExtendedStringTest_ExtendedCharConstructor():
    aEuroChar = "€"
    aString = _u16(aEuroChar)

    assert aString.Length() == 1
    assert aString.IsAscii() is False
    assert aString.Value(1) == aEuroChar


def test_TCollection_ExtendedStringTest_UnicodeCharacters():
    aLatinA = "A"
    aLatinE = "é"
    aEuro = "€"
    aCJK = "中"

    aString = _u16(aLatinA + aLatinE + aEuro + aCJK)

    assert aString.Length() == 4
    assert aString.Value(1) == aLatinA
    assert aString.Value(2) == aLatinE
    assert aString.Value(3) == aEuro
    assert aString.Value(4) == aCJK
    assert aString.IsAscii() is False


def test_TCollection_ExtendedStringTest_AsciiDetection():
    anAsciiString = TCollection_ExtendedString("Simple ASCII")
    assert anAsciiString.IsAscii() is True

    aNonAsciiString = _u16("A€")
    assert aNonAsciiString.IsAscii() is False


def test_TCollection_ExtendedStringTest_EmptyStringHandling():
    # ToUTF8CString (char* out buffer) is not bound
    anEmptyString = TCollection_ExtendedString()
    assert anEmptyString.Length() == 0
    assert anEmptyString.IsEmpty() is True
    assert anEmptyString.LengthOfCString() == 0


def test_TCollection_ExtendedStringTest_ConversionRoundTrip():
    anOriginalStr = "Test conversion with special chars: !@#$%"

    anAsciiOriginal = TCollection_AsciiString(anOriginalStr)
    anExtendedConverted = TCollection_ExtendedString(anAsciiOriginal)
    anAsciiRoundTrip = TCollection_AsciiString(anExtendedConverted)

    assert anAsciiRoundTrip.ToCString() == anOriginalStr
    assert anExtendedConverted.Length() == anAsciiOriginal.Length()
    assert anAsciiRoundTrip.Length() == anAsciiOriginal.Length()


def test_TCollection_ExtendedStringTest_LargeStrings():
    aLargeSize = 1000
    aLargeString = TCollection_ExtendedString(aLargeSize, "A")

    assert aLargeString.Length() == aLargeSize
    assert aLargeString.Value(1) == "A"
    assert aLargeString.Value(aLargeSize) == "A"
    assert aLargeString.IsAscii() is True


def test_TCollection_ExtendedStringTest_MultiByteCString():
    aString = TCollection_ExtendedString("Multi-byte test", True)
    assert aString.Length() > 0
    assert aString.IsEmpty() is False


def test_TCollection_ExtendedStringTest_BoundaryValues():
    # OCCT's IsAnAscii considers 0x00-0xFF as ASCII
    aStringLastStandardAscii = _u16("\u007f")
    assert aStringLastStandardAscii.Length() == 1
    assert aStringLastStandardAscii.IsAscii() is True

    aStringLastOCCTAscii = _u16("ÿ")
    assert aStringLastOCCTAscii.Length() == 1
    assert aStringLastOCCTAscii.IsAscii() is True

    aStringFirstExtended = _u16("Ā")
    assert aStringFirstExtended.Length() == 1
    assert aStringFirstExtended.IsAscii() is False

    aStringMaxBMP = _u16("￿")
    assert aStringMaxBMP.Length() == 1
    assert aStringMaxBMP.IsAscii() is False


def test_TCollection_ExtendedStringTest_TestMem_LargeStringAllocation():
    aLargeSize = 1024 * 1024
    aString = TCollection_ExtendedString(aLargeSize, "A")
    assert aString.Length() == aLargeSize
    assert aString.IsEmpty() is False


def test_TCollection_ExtendedStringTest_OCC3277_CatOperation():
    anExtendedString = TCollection_ExtendedString()
    anInputString = TCollection_ExtendedString("TestString")

    aResult = anExtendedString.Cat(anInputString)

    assert aResult.Length() == anInputString.Length()
    assert aResult.IsEmpty() is False
    assert anInputString == aResult


def test_TCollection_ExtendedStringTest_LeftAdjust_RemovesLeadingSpaces():
    aString = TCollection_ExtendedString("   Hello World")
    aString.LeftAdjust()
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_LeftAdjust_NoLeadingSpaces():
    aString = TCollection_ExtendedString("Hello World")
    aString.LeftAdjust()
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_LeftAdjust_AllSpaces():
    aString = TCollection_ExtendedString("     ")
    aString.LeftAdjust()
    assert aString.IsEmpty() is True


def test_TCollection_ExtendedStringTest_LeftAdjust_EmptyString():
    aString = TCollection_ExtendedString()
    aString.LeftAdjust()
    assert aString.IsEmpty() is True


def test_TCollection_ExtendedStringTest_RightAdjust_RemovesTrailingSpaces():
    aString = TCollection_ExtendedString("Hello World   ")
    aString.RightAdjust()
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_RightAdjust_NoTrailingSpaces():
    aString = TCollection_ExtendedString("Hello World")
    aString.RightAdjust()
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_RightAdjust_AllSpaces():
    aString = TCollection_ExtendedString("     ")
    aString.RightAdjust()
    assert aString.IsEmpty() is True


def test_TCollection_ExtendedStringTest_LeftJustify_ExtendsWithFiller():
    aString = TCollection_ExtendedString("Hello")
    aString.LeftJustify(10, "-")
    assert aString.Length() == 10
    assert TCollection_AsciiString(aString).ToCString() == "Hello-----"


def test_TCollection_ExtendedStringTest_LeftJustify_NoChangeIfShorter():
    aString = TCollection_ExtendedString("Hello")
    aString.LeftJustify(3, "-")
    assert aString.Length() == 5
    assert TCollection_AsciiString(aString).ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_RightJustify_ExtendsWithFiller():
    aString = TCollection_ExtendedString("Hello")
    aString.RightJustify(10, "-")
    assert aString.Length() == 10
    assert TCollection_AsciiString(aString).ToCString() == "-----Hello"


def test_TCollection_ExtendedStringTest_RightJustify_NoChangeIfShorter():
    aString = TCollection_ExtendedString("Hello")
    aString.RightJustify(3, "-")
    assert aString.Length() == 5
    assert TCollection_AsciiString(aString).ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_Center_CentersWithFiller():
    aString = TCollection_ExtendedString("Hi")
    aString.Center(6, "-")
    assert aString.Length() == 6
    assert TCollection_AsciiString(aString).ToCString() == "--Hi--"


def test_TCollection_ExtendedStringTest_Center_OddWidth():
    aString = TCollection_ExtendedString("Hi")
    aString.Center(7, "-")
    assert aString.Length() == 7
    assert TCollection_AsciiString(aString).ToCString() == "--Hi---"


def test_TCollection_ExtendedStringTest_Center_NoChangeIfShorter():
    aString = TCollection_ExtendedString("Hello")
    aString.Center(3, "-")
    assert aString.Length() == 5


def test_TCollection_ExtendedStringTest_Capitalize_UppercasesFirstLetter():
    aString = TCollection_ExtendedString("hello WORLD")
    aString.Capitalize()
    assert TCollection_AsciiString(aString).ToCString() == "Hello world"


def test_TCollection_ExtendedStringTest_Capitalize_AlreadyCapitalized():
    aString = TCollection_ExtendedString("Hello")
    aString.Capitalize()
    assert TCollection_AsciiString(aString).ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_Capitalize_EmptyString():
    aString = TCollection_ExtendedString()
    aString.Capitalize()
    assert aString.IsEmpty() is True


def test_TCollection_ExtendedStringTest_Prepend_InsertsAtBeginning():
    aString = TCollection_ExtendedString("World")
    aPrefix = TCollection_ExtendedString("Hello ")
    aString.Prepend(aPrefix)
    assert TCollection_AsciiString(aString).ToCString() == "Hello World"


def test_TCollection_ExtendedStringTest_Prepend_EmptyPrefix():
    aString = TCollection_ExtendedString("Hello")
    aPrefix = TCollection_ExtendedString()
    aString.Prepend(aPrefix)
    assert TCollection_AsciiString(aString).ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_Prepend_ToEmptyString():
    aString = TCollection_ExtendedString()
    aPrefix = TCollection_ExtendedString("Hello")
    aString.Prepend(aPrefix)
    assert TCollection_AsciiString(aString).ToCString() == "Hello"


def test_TCollection_ExtendedStringTest_FirstLocationInSet_FindsCharacter():
    aString = TCollection_ExtendedString("Hello World")
    aSet = TCollection_ExtendedString("aeiou")
    assert aString.FirstLocationInSet(aSet, 1, aString.Length()) == 2


def test_TCollection_ExtendedStringTest_FirstLocationInSet_NotFound():
    aString = TCollection_ExtendedString("BCDFG")
    aSet = TCollection_ExtendedString("aeiou")
    assert aString.FirstLocationInSet(aSet, 1, aString.Length()) == 0


def test_TCollection_ExtendedStringTest_FirstLocationInSet_EmptySet():
    aString = TCollection_ExtendedString("Hello")
    aSet = TCollection_ExtendedString()
    assert aString.FirstLocationInSet(aSet, 1, aString.Length()) == 0


def test_TCollection_ExtendedStringTest_FirstLocationNotInSet_FindsCharacter():
    aString = TCollection_ExtendedString("aaaHello")
    aSet = TCollection_ExtendedString("a")
    assert aString.FirstLocationNotInSet(aSet, 1, aString.Length()) == 4


def test_TCollection_ExtendedStringTest_FirstLocationNotInSet_AllInSet():
    aString = TCollection_ExtendedString("aaa")
    aSet = TCollection_ExtendedString("a")
    assert aString.FirstLocationNotInSet(aSet, 1, aString.Length()) == 0


def test_TCollection_ExtendedStringTest_FirstLocationNotInSet_EmptySet():
    aString = TCollection_ExtendedString("Hello")
    aSet = TCollection_ExtendedString()
    assert aString.FirstLocationNotInSet(aSet, 1, aString.Length()) == 1


def test_TCollection_ExtendedStringTest_IntegerValue_ValidInteger():
    aString = TCollection_ExtendedString("12345")
    assert aString.IsIntegerValue() is True
    assert aString.IntegerValue() == 12345


def test_TCollection_ExtendedStringTest_IntegerValue_NegativeInteger():
    aString = TCollection_ExtendedString("-42")
    assert aString.IsIntegerValue() is True
    assert aString.IntegerValue() == -42


def test_TCollection_ExtendedStringTest_IntegerValue_NotAnInteger():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsIntegerValue() is False


def test_TCollection_ExtendedStringTest_IntegerValue_EmptyString():
    aString = TCollection_ExtendedString()
    assert aString.IsIntegerValue() is False
    assert aString.IntegerValue() == 0


def test_TCollection_ExtendedStringTest_RealValue_ValidReal():
    aString = TCollection_ExtendedString("3.14159")
    assert aString.IsRealValue(True) is True
    assert abs(aString.RealValue() - 3.14159) <= 0.00001


def test_TCollection_ExtendedStringTest_RealValue_Integer():
    aString = TCollection_ExtendedString("42")
    assert aString.IsRealValue(True) is True
    assert abs(aString.RealValue() - 42.0) <= 0.00001


def test_TCollection_ExtendedStringTest_RealValue_NotAReal():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsRealValue(True) is False


def test_TCollection_ExtendedStringTest_RealValue_EmptyString():
    aString = TCollection_ExtendedString()
    assert aString.IsRealValue() is False
    assert abs(aString.RealValue() - 0.0) <= 0.00001


def test_TCollection_ExtendedStringTest_IsSameString_CaseSensitiveMatch():
    aString1 = TCollection_ExtendedString("Hello")
    aString2 = TCollection_ExtendedString("Hello")
    assert aString1.IsSameString(aString2, True) is True


def test_TCollection_ExtendedStringTest_IsSameString_CaseSensitiveMismatch():
    aString1 = TCollection_ExtendedString("Hello")
    aString2 = TCollection_ExtendedString("hello")
    assert aString1.IsSameString(aString2, True) is False


def test_TCollection_ExtendedStringTest_IsSameString_CaseInsensitiveMatch():
    aString1 = TCollection_ExtendedString("Hello")
    aString2 = TCollection_ExtendedString("HELLO")
    assert aString1.IsSameString(aString2, False) is True


def test_TCollection_ExtendedStringTest_IsSameString_DifferentLengths():
    aString1 = TCollection_ExtendedString("Hello")
    aString2 = TCollection_ExtendedString("Hello World")
    assert aString1.IsSameString(aString2, False) is False


def test_TCollection_ExtendedStringTest_FillerConstructor_NegativeLength_Throws():
    with pytest.raises(Standard_OutOfRange):
        TCollection_ExtendedString(-5, "X")


def test_TCollection_ExtendedStringTest_FillerConstructor_ZeroLength():
    aString = TCollection_ExtendedString(0, "X")
    assert aString.IsEmpty() is True
    assert aString.Length() == 0


def test_TCollection_ExtendedStringTest_AssignCat_SelfAppend():
    aString = TCollection_ExtendedString("Hello")
    aString.AssignCat(aString)
    assert aString.Length() == 10
    assert TCollection_AsciiString(aString).ToCString() == "HelloHello"


def test_TCollection_ExtendedStringTest_AssignCat_SelfAppendMultiple():
    aString = TCollection_ExtendedString("AB")
    aString.AssignCat(aString)
    aString.AssignCat(aString)
    assert aString.Length() == 8
    assert TCollection_AsciiString(aString).ToCString() == "ABABABAB"


def test_TCollection_ExtendedStringTest_AssignCat_PointerIntoSelf():
    # ToExtString() returns a Python copy: the result is checked, not the aliasing
    aString = TCollection_ExtendedString("HelloWorld")
    aString.AssignCat(aString.ToExtString()[5:], 5)
    assert aString.Length() == 15
    assert TCollection_AsciiString(aString).ToCString() == "HelloWorldWorld"


def test_TCollection_ExtendedStringTest_AssignCat_PointerIntoSelfBeginning():
    aString = TCollection_ExtendedString("Hello")
    aString.AssignCat(aString.ToExtString(), 3)
    assert aString.Length() == 8
    assert TCollection_AsciiString(aString).ToCString() == "HelloHel"


def test_TCollection_ExtendedStringTest_Prepend_PointerIntoSelf():
    aString = TCollection_ExtendedString("HelloWorld")
    aString.Prepend(aString.ToExtString()[5:], 5)
    assert aString.Length() == 15
    assert TCollection_AsciiString(aString).ToCString() == "WorldHelloWorld"


def test_TCollection_ExtendedStringTest_Prepend_PointerIntoSelfBeginning():
    aString = TCollection_ExtendedString("Hello")
    aString.Prepend(aString.ToExtString(), 3)
    assert aString.Length() == 8
    assert TCollection_AsciiString(aString).ToCString() == "HelHello"


def test_TCollection_ExtendedStringTest_IsEqual_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsEqual("Hello", -1) is False


def test_TCollection_ExtendedStringTest_IsDifferent_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsDifferent("Hello", -1) is True


def test_TCollection_ExtendedStringTest_IsLess_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsLess("Hello", -1) is False


def test_TCollection_ExtendedStringTest_IsGreater_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.IsGreater("Hello", -1) is True


def test_TCollection_ExtendedStringTest_StartsWith_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.StartsWith("Hel", -1) is False


def test_TCollection_ExtendedStringTest_EndsWith_NegativeLength():
    aString = TCollection_ExtendedString("Hello")
    assert aString.EndsWith("llo", -1) is False


def test_TCollection_ExtendedStringTest_StartsWith_NoMatchLongerPrefix():
    aStr = TCollection_ExtendedString("hello")
    aPrefix = TCollection_ExtendedString("help")
    assert aStr.StartsWith(aPrefix) is False


def test_TCollection_ExtendedStringTest_StartsWith_Match():
    aStr = TCollection_ExtendedString("hello")
    aPrefix = TCollection_ExtendedString("he")
    assert aStr.StartsWith(aPrefix) is True


def test_TCollection_ExtendedStringTest_EndsWith_NoMatchMiddlePart():
    aStr = TCollection_ExtendedString("hello")
    aSuffix = TCollection_ExtendedString("ll")
    assert aStr.EndsWith(aSuffix) is False


def test_TCollection_ExtendedStringTest_EndsWith_Match():
    aStr = TCollection_ExtendedString("hello")
    aSuffix = TCollection_ExtendedString("lo")
    assert aStr.EndsWith(aSuffix) is True


def test_TCollection_ExtendedStringTest_OCC22744_NonAsciiCharIsNotAsciiAndCanBeUsedAsMapKey():
    anExtString = TCollection_ExtendedString()
    anExtString.Insert(1, "ༀ")

    assert anExtString.IsAscii() is False

    aMap = NCollection_DataMap[TCollection_ExtendedString, int]()
    aMap.Bind(anExtString, 0)
    assert aMap.Size() == 1
