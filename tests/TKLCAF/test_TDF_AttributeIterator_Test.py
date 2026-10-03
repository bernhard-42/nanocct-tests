# Translated from OCCT src/ApplicationFramework/TKLCAF/GTests/TDF_AttributeIterator_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.TDataStd import TDataStd_Integer, TDataStd_Name, TDataStd_Real
from nanocct.TDF import TDF_AttributeIterator
from nanocct.TDocStd import TDocStd_Application


def test_TDF_AttributeIterator_Test_OCC24755_AttributeInsertionOrder():
    app = TDocStd_Application()
    doc = app.NewDocument__TDocStd_Document("BinOcaf")
    lab = doc.Main()
    TDataStd_Integer.Set_s(lab, 0)
    TDataStd_Name.Set_s(lab, "test")
    lab.AddAttribute(TDataStd_Real(), True)

    it = TDF_AttributeIterator(lab)
    assert it.More()
    assert it.Value().IsKind(TDataStd_Integer.get_type_descriptor_s())
    it.Next()
    assert it.More()
    assert it.Value().IsKind(TDataStd_Name.get_type_descriptor_s())
    it.Next()
    assert it.More()
    assert it.Value().IsKind(TDataStd_Real.get_type_descriptor_s())
    it.Next()
    assert not it.More()
