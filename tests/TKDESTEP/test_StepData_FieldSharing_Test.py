# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_FieldSharing_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.Interface import Interface_EntityIterator
from nanocct.NCollection import NCollection_HArray1, NCollection_HArray2
from nanocct.Standard import Standard_Transient
from nanocct.StepData import StepData_ESDescr, StepData_FieldListN, StepData_Simple


def _values(iterator):
    iterator.Start()
    out = []
    while iterator.More():
        out.append(iterator.Value())
        iterator.Next()
    return out


def test_StepData_FieldSharingTest_FieldListFillSharedTraversesEntityAggregates():
    e1, e2, e3, e4 = (Standard_Transient() for _ in range(4))
    fields = StepData_FieldListN(3)
    fields.CField(1).SetEntity(e1)
    fields.CField(2).SetEntity()
    fields.CField(2).SetList(2, -1)
    fields.CField(2).SetEntity(-1, e2)
    fields.CField(2).SetEntity(0, e3)
    fields.CField(3).SetEntity()
    fields.CField(3).SetList2(1, 1, 2, -3)
    array = fields.CField(3).Transient()
    assert isinstance(array, NCollection_HArray2[Standard_Transient])
    array.SetValue(2, -3, e4)
    iterator = Interface_EntityIterator()
    fields.FillShared(iterator)
    assert iterator.NbEntities() == 4
    values = _values(iterator)
    assert values[0] is e1 and values[1] is e2 and values[2] is e3 and values[3] is e4


def test_StepData_FieldSharingTest_SimpleSharedTraversesFieldsAndSkipsNullEntities():
    description = StepData_ESDescr("TEST_ENTITY")
    description.SetNbFields(2)
    entity = StepData_Simple(description)
    scalar_entity, array_entity = Standard_Transient(), Standard_Transient()
    entity.CFieldNum(1).SetEntity(scalar_entity)
    array = NCollection_HArray1[Standard_Transient](-1, 0)
    array.SetValue(-1, array_entity)
    entity.CFieldNum(2).Set(array)
    iterator = Interface_EntityIterator()
    entity.Shared(iterator)
    assert iterator.NbEntities() == 2
    values = _values(iterator)
    assert values[0] is scalar_entity and values[1] is array_entity
