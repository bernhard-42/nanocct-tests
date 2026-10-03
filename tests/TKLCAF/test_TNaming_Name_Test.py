# Translated from OCCT src/ApplicationFramework/TKLCAF/GTests/TNaming_Name_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.NCollection import NCollection_Map
from nanocct.TDF import TDF_Data, TDF_Label
from nanocct.TNaming import TNaming_IDENTITY, TNaming_Name, TNaming_NamedShape


def test_TNaming_Name_Test_BUC60925_SolveWithEmptyNamedShape():
    df = TDF_Data()
    label = df.Root().FindChild(2, True)
    label_map = NCollection_Map[TDF_Label]()
    label_map.Add(label)
    ns = TNaming_NamedShape()
    nn = TNaming_Name()
    nn.Type(TNaming_IDENTITY)
    nn.Append(ns)
    assert not nn.Solve(label, label_map)
