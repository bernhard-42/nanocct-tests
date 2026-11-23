# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_FieldCopy_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.StepData import StepData_Field


def test_StepData_FieldCopyTest_CopyKeepsIndependentRealValuesAtNegativeBounds():
    source = StepData_Field()
    source.SetReal()
    source.SetList(2, -2)
    source.SetReal(-2, 1.5)
    source.SetReal(-1, 2.5)
    copy = StepData_Field()
    copy.CopyFrom(source)
    source.SetReal(-2, 3.5)
    assert copy.Lower() == -2
    assert copy.Length() == 2
    assert copy.Real(-2) == pytest.approx(1.5, rel=1e-15, abs=1e-300)
    assert copy.Real(-1) == pytest.approx(2.5, rel=1e-15, abs=1e-300)


def test_StepData_FieldCopyTest_CopyPreservesUnsetStringItems():
    source = StepData_Field()
    source.SetString()
    source.SetList(2, -1)
    source.SetString(0, "text")
    copy = StepData_Field()
    copy.CopyFrom(source)
    source.SetString(0, "changed")
    assert copy.IsSet(-1) is False
    assert copy.String(0) == "text"
