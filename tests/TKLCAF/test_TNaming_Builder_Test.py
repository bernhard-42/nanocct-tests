# Translated from OCCT src/ApplicationFramework/TKLCAF/GTests/TNaming_Builder_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.TDocStd import TDocStd_Document
from nanocct.TNaming import TNaming_Builder
from nanocct.TopAbs import TopAbs_FORWARD, TopAbs_REVERSED


def test_TNaming_Builder_Test_OCC361_ShapeOrientationPreservation():
    doc = TDocStd_Document("BinOcaf")
    box = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 100, 100, 100).Shape()
    box.Orientation(TopAbs_FORWARD)
    label = doc.Main()
    builder = TNaming_Builder(label)
    builder.Generated(box)
    box1 = box.Reversed()
    box1.Orientation(TopAbs_REVERSED)
    label.ForgetAllAttributes()
    builder2 = TNaming_Builder(label)
    builder2.Generated(box1)
    box = builder2.NamedShape().Get()
    assert box.Orientation() == TopAbs_REVERSED
