# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_SelectMember_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.StepData import StepData_Field, StepData_LFalse, StepData_LTrue, StepData_LUnknown, StepData_SelectInt


def test_StepData_SelectMemberTest_LogicalSelectPreservesAllValues():
    select = StepData_SelectInt()
    field = StepData_Field()
    field.SetSelectMember(select)
    for value in (StepData_LFalse, StepData_LTrue, StepData_LUnknown):
        field.SetLogical(value)
        assert select.Logical() == value
        assert field.Logical() == value
