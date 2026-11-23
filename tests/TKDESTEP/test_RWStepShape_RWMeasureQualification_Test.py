# Translated from OCCT src/DataExchange/TKDESTEP/GTests/RWStepShape_RWMeasureQualification_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Interface import Interface_EntityIterator, Interface_GeneralLib
from nanocct.NCollection import NCollection_HArray1
from nanocct.StepAP214 import StepAP214_Protocol
from nanocct.StepBasic import StepBasic_MeasureWithUnit
from nanocct.STEPControl import STEPControl_Controller
from nanocct.StepData import StepData_StepModel
from nanocct.StepShape import StepShape_MeasureQualification, StepShape_TypeQualifier, StepShape_ValueQualifier
from nanocct.TCollection import TCollection_HAsciiString


def test_StepDimTol_ReferencesTest_MeasureQualification_SharesQualifiedMeasure():
    STEPControl_Controller.Init_s()
    measure = StepBasic_MeasureWithUnit()
    qualifier_type = StepShape_TypeQualifier()
    qualifier_type.Init(TCollection_HAsciiString("minimum"))
    value = StepShape_ValueQualifier()
    value.SetValue(qualifier_type)
    qualifiers = NCollection_HArray1[StepShape_ValueQualifier](1, 1)
    qualifiers.SetValue(1, value)
    qualification = StepShape_MeasureQualification()
    qualification.Init(TCollection_HAsciiString(), TCollection_HAsciiString(), measure, qualifiers)
    shared = Interface_EntityIterator()
    protocol = StepAP214_Protocol()
    found, general, case = Interface_GeneralLib(protocol).Select(qualification)
    assert found is True
    general.FillSharedCase(case, qualification, shared)
    has_measure = False
    while shared.More():
        has_measure = has_measure or shared.Value() is measure
        shared.Next()
    assert has_measure is True
    # Model traversal must also discover the dependency through the protocol.
    model = StepData_StepModel()
    model.SetProtocol(protocol)
    model.AddWithRefs(qualification)
    assert model.Number(measure) > 0
