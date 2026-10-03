# Translated from OCCT src/ModelingAlgorithms/TKBool/GTests/BRepAlgoAPI_Section_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepAlgoAPI import BRepAlgoAPI_Section
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeSphere
from nanocct.gp import gp_Pnt


def test_BRepAlgoAPI_SectionTest_OCCN2_CylinderSphereSectionIsDone():
    cyl = BRepPrimAPI_MakeCylinder(50.0, 200.0).Shape()
    sphere = BRepPrimAPI_MakeSphere(gp_Pnt(60.0, 0.0, 100.0), 50.0).Shape()
    section = BRepAlgoAPI_Section(cyl, sphere)
    assert section.IsDone()
    assert not section.Shape().IsNull()
