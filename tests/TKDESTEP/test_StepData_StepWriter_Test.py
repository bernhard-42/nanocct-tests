# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_StepWriter_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.StepData import StepData_StepWriter
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
