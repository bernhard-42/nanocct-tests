# Translated from OCCT src/ApplicationFramework/TKLCAF/GTests/TDataStd_Attribute_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TDataStd
from nanocct.Standard import Standard_GUID
from nanocct.TDocStd import TDocStd_Application

_NAMES = [
    "AsciiString", "BooleanArray", "BooleanList", "ByteArray", "ExtStringArray", "ExtStringList",
    "Integer", "IntegerArray", "IntegerList", "Name", "Real", "RealArray", "RealList",
    "ReferenceArray", "ReferenceList",
]


def test_TDataStd_Attribute_Test_OCC29371_AttributeGUIDsNotNull():
    app = TDocStd_Application()
    doc = app.NewDocument__TDocStd_Document("BinOcaf")
    lab = doc.Main()
    null_guid = Standard_GUID("00000000-0000-0000-0000-000000000000")
    for name in _NAMES:
        att = getattr(TDataStd, "TDataStd_" + name)()
        lab.AddAttribute(att)
        assert null_guid != att.ID(), name
    app.Close(doc)
