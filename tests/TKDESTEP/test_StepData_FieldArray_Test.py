# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepData_FieldArray_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.NCollection import NCollection_HArray2
from nanocct.Standard import Standard_Transient
from nanocct.StepData import StepData_Field, StepData_StepModel, StepData_StepWriter
from nanocct.TCollection import TCollection_AsciiString


def test_StepData_FieldArrayTest_WritesIntegerRowsInDeclaredOrder():
    array = NCollection_HArray2[int](-2, -1, 4, 6)
    for row, base in ((-2, 10), (-1, 20)):
        for col in (4, 5, 6):
            array.SetValue(row, col, base + col - 3)
    field = StepData_Field()
    field.Set(array)
    assert field.Lower(1) == -2
    assert field.Lower(2) == 4
    assert field.Length(1) == 2
    assert field.Length(2) == 3
    assert field.Integer(-1, 6) == 23
    writer = StepData_StepWriter(StepData_StepModel())
    writer.StartEntity(TCollection_AsciiString("TEST"))
    writer.SendField(field, None)
    writer.EndEntity()
    assert writer.Line(1).ToCString() == "TEST(((11,12,13),(21,22,23)));"


def test_StepData_FieldArrayTest_KeepsRealValuesAndEntityBounds():
    reals = NCollection_HArray2[float](-1, 0, 3, 5)
    reals.SetValue(0, 5, 2.5)
    real_field = StepData_Field()
    real_field.Set(reals)
    assert real_field.Kind() == 5                   # Legacy Real kind.
    assert real_field.Lower(1) == -1
    assert real_field.Lower(2) == 3
    assert real_field.Length(1) == 2
    assert real_field.Length(2) == 3
    assert real_field.Real(0, 5) == pytest.approx(2.5, rel=1e-15, abs=1e-300)
    items = NCollection_HArray2[Standard_Transient](-1, 0, 3, 5)
    entity = Standard_Transient()
    items.SetValue(0, 5, entity)
    entity_field = StepData_Field()
    entity_field.Set(items)
    assert entity_field.Lower(1) == -1
    assert entity_field.Lower(2) == 3
    assert entity_field.Length(1) == 2
    assert entity_field.Length(2) == 3
    assert entity_field.ItemKind(-1, 3) == 0
    assert entity_field.ItemKind(0, 5) == 7         # Legacy Entity kind.
    assert entity_field.Entity(0, 5) is entity
