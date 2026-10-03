# Translated from OCCT src/ModelingAlgorithms/TKShHealing/GTests/ShapeUpgrade_FaceDivide_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct import TopoDS
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.ShapeUpgrade import ShapeUpgrade_FaceDivide
from nanocct.TopAbs import TopAbs_FACE
from nanocct.TopExp import TopExp_Explorer


def test_ShapeUpgrade_FaceDivideTest_Perform_WithoutContext_DoesNotCrash():
    for i in range(10):
        size = 10.0 + i * 0.5
        box = BRepPrimAPI_MakeBox(size, size + 5, size + 10).Shape()
        exp = TopExp_Explorer(box, TopAbs_FACE)
        assert exp.More(), "No faces found in box"
        divider = ShapeUpgrade_FaceDivide(TopoDS.Face(exp.Current()))
        divider.Perform()  # EXPECT_NO_THROW


# Perform_Parallel_DoesNotCrash: skipped (OSD_Parallel threading test)
