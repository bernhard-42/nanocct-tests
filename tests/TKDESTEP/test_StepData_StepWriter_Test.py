# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_StepWriter_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.NCollection import NCollection_HArray1
from nanocct.StepData import StepData_SelectArrReal, StepData_SelectInt, StepData_StepModel, StepData_StepWriter
from nanocct.TCollection import TCollection_AsciiString


def _clean(text):
    return StepData_StepWriter.CleanTextForSend_s(TCollection_AsciiString(text)).ToCString()


def test_StepData_StepWriterTest_CleanTextForSend_BasicEscaping():
    assert _clean("text with 'single quotes'") == "text with ''single quotes''"
    assert _clean("path\\with\\backslashes") == "path\\\\with\\\\backslashes"
    assert _clean("line1\nline2") == "line1\\N\\line2"
    assert _clean("text\twith\ttabs") == "text\\T\\with\\T\\tabs"


def test_StepData_StepWriterTest_CleanTextForSend_ControlDirectivePreservation():
    assert _clean("text with \\XA7\\ section sign") == "text with \\XA7\\ section sign"
    assert _clean("\\X2\\03C0\\X0\\ is pi") == "\\X2\\03C0\\X0\\ is pi"
    assert _clean("emoji \\X4\\001F600\\X0\\ face") == "emoji \\X4\\001F600\\X0\\ face"
    assert _clean("text with \\S\\ directive") == "text with \\S\\ directive"
    assert _clean("\\PA\\ code page setting") == "\\PA\\ code page setting"


def test_StepData_StepWriterTest_CleanTextForSend_ExistingDirectivePreservation():
    assert _clean("line1\\N\\line2") == "line1\\N\\line2"
    assert _clean("text\\T\\with\\T\\tab") == "text\\T\\with\\T\\tab"


def test_StepData_StepWriterTest_CleanTextForSend_MixedContent():
    assert _clean("see \\XA7\\ section and 'quotes'") == "see \\XA7\\ section and ''quotes''"
    assert _clean("\\XA7\\ and path\\file") == "\\XA7\\ and path\\\\file"
    assert _clean("prefix \\X2\\03B103B2\\X0\\ 'text' with\ttab") == "prefix \\X2\\03B103B2\\X0\\ ''text'' with\\T\\tab"


def test_StepData_StepWriterTest_CleanTextForSend_EdgeCases():
    assert _clean("") == ""
    assert _clean("''") == "''''"
    assert _clean("\\XA7\\") == "\\XA7\\"
    assert _clean("\\XA7\\\\XB6\\") == "\\XA7\\\\XB6\\"


def test_StepData_StepWriterTest_CleanTextForSend_MalformedInput():
    assert _clean("incomplete \\X and 'quotes'") == "incomplete \\\\X and ''quotes''"
    assert _clean("partial \\XA and more") == "partial \\\\XA and more"


def test_StepData_StepWriterTest_CleanTextForSend_HexSequenceDetection():
    assert _clean("\\X2\\03B103B203B3\\X0\\") == "\\X2\\03B103B203B3\\X0\\"
    assert _clean("\\X4\\001F600001F638\\X0\\") == "\\X4\\001F600001F638\\X0\\"
    assert _clean("start \\X2\\03C0\\X0\\ end") == "start \\X2\\03C0\\X0\\ end"


def test_StepData_StepWriterTest_SendSelect_UnavailableValuesKeepParameterPositions():
    writer = StepData_StepWriter(StepData_StepModel())
    wrong_array_type = StepData_SelectInt()
    wrong_array_type.SetKind(8)             # The writer uses kind 8 for real array SELECT values.
    unsupported = StepData_SelectInt()
    unsupported.SetKind(257)
    null_array = StepData_SelectArrReal()
    writer.StartEntity(TCollection_AsciiString("TEST"))
    writer.Send(9)
    writer.SendSelect(None, None)
    writer.SendSelect(wrong_array_type, None)
    writer.SendSelect(unsupported, None)
    writer.SendSelect(null_array, None)
    writer.SendEnum("")
    writer.Send(10)
    writer.EndEntity()
    assert writer.Line(1).ToCString() == "TEST(9,$,$,$,$,$,10);"


def test_StepData_StepWriterTest_SendSelect_RealArrayUsesDeclaredBounds():
    array = NCollection_HArray1[float](-2, 0)
    array.SetValue(-2, 1.0)
    array.SetValue(-1, 2.0)
    array.SetValue(0, 3.0)
    select = StepData_SelectArrReal()
    select.SetArrReal(array)
    model = StepData_StepModel()
    writer = StepData_StepWriter(model)
    writer.StartEntity(TCollection_AsciiString("TEST"))
    writer.Send(9)
    writer.SendSelect(select, None)
    writer.Send(10)
    writer.EndEntity()
    assert writer.Line(1).ToCString() == "TEST(9,(1.,2.,3.),10);"
    select.SetName("VALUES")
    named = StepData_StepWriter(model)
    named.StartEntity(TCollection_AsciiString("TEST"))
    named.SendSelect(select, None)
    named.EndEntity()
    assert named.Line(1).ToCString() == "TEST(VALUES((1.,2.,3.)));"
