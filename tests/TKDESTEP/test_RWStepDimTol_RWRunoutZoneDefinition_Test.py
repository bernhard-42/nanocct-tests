# Translated from OCCT src/DataExchange/TKDESTEP/GTests/RWStepDimTol_RWRunoutZoneDefinition_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Interface import Interface_EntityIterator, Interface_GeneralLib
from nanocct.NCollection import NCollection_HArray1
from nanocct.StepAP214 import StepAP214_Protocol
from nanocct.StepBasic import StepBasic_LengthMeasureWithUnit, StepBasic_PlaneAngleMeasureWithUnit
from nanocct.STEPControl import STEPControl_Controller
from nanocct.StepData import StepData_StepModel, StepData_StepWriter, StepData_WriterLib
from nanocct.StepDimTol import (StepDimTol_DatumReferenceModifierWithValue, StepDimTol_Distance,
                                StepDimTol_RunoutZoneDefinition, StepDimTol_RunoutZoneOrientation, StepDimTol_ToleranceZone)
from nanocct.StepRepr import StepRepr_ShapeAspect
from nanocct.TCollection import TCollection_AsciiString


def test_StepDimTol_ReferencesTest_RunoutZone_WritesAndSharesOrientation():
    STEPControl_Controller.Init_s()
    protocol = StepAP214_Protocol()
    zone = StepDimTol_ToleranceZone()
    orientation = StepDimTol_RunoutZoneOrientation()
    angle = StepBasic_PlaneAngleMeasureWithUnit()
    orientation.Init(angle)
    boundaries = NCollection_HArray1[StepRepr_ShapeAspect](1, 1)
    boundaries.SetValue(1, StepRepr_ShapeAspect())
    definition = StepDimTol_RunoutZoneDefinition()
    definition.Init(zone, boundaries, orientation)
    model = StepData_StepModel()
    model.AddEntity(zone)
    model.AddEntity(boundaries.Value(1))
    model.AddEntity(orientation)
    writer = StepData_StepWriter(model)
    writer.StartEntity(TCollection_AsciiString("RUNOUT_ZONE_DEFINITION"))
    found, module, case = StepData_WriterLib(protocol).Select(definition)
    assert found is True
    module.WriteStep(case, writer, definition)
    writer.EndEntity()
    assert writer.Line(1).ToCString() == "RUNOUT_ZONE_DEFINITION(#1,(#2),#3);"
    shared = Interface_EntityIterator()
    found, general, general_case = Interface_GeneralLib(protocol).Select(definition)
    assert found is True
    general.FillSharedCase(general_case, definition, shared)
    has_orientation = False
    while shared.More():
        has_orientation = has_orientation or shared.Value() is orientation
        shared.Next()
    assert has_orientation is True
    referenced = StepData_StepModel()
    referenced.AddWithRefs(definition, protocol)
    assert referenced.Number(orientation) > 0
    assert referenced.Number(angle) > 0


def test_StepDimTol_ReferencesTest_DatumModifier_AddWithRefsIncludesLengthMeasure():
    STEPControl_Controller.Init_s()
    protocol = StepAP214_Protocol()
    measure = StepBasic_LengthMeasureWithUnit()
    modifier = StepDimTol_DatumReferenceModifierWithValue()
    modifier.Init(StepDimTol_Distance, measure)
    model = StepData_StepModel()
    model.AddWithRefs(modifier, protocol)
    number = model.Number(measure)
    assert number > 0
    found, module, case = StepData_WriterLib(protocol).Select(modifier)
    assert found is True
    writer = StepData_StepWriter(model)
    writer.StartEntity(TCollection_AsciiString("DATUM_REFERENCE_MODIFIER_WITH_VALUE"))
    module.WriteStep(case, writer, modifier)
    writer.EndEntity()
    assert writer.Line(1).ToCString() == f"DATUM_REFERENCE_MODIFIER_WITH_VALUE(.DISTANCE.,#{number});"
