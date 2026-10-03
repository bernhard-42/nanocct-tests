# Translated from OCCT src/ModelingAlgorithms/TKPrim/GTests/BRepPrimAPI_MakePrism_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from nanocct.BRepPrimAPI import BRepPrimAPI_MakePrism
from nanocct.gp import gp_Pnt, gp_Vec


def test_BRepPrimAPI_MakePrism_Test_OCC31294_GeneratedListForNonBaseShape():
    mk_vert = BRepBuilderAPI_MakeVertex(gp_Pnt(0.0, 0.0, 0.0))
    mk_dummy = BRepBuilderAPI_MakeVertex(gp_Pnt(0.0, 0.0, 0.0))
    mk_prism = BRepPrimAPI_MakePrism(mk_vert.Shape(), gp_Vec(0.0, 0.0, 1.0))
    assert mk_prism.Generated(mk_vert.Shape()).Extent() == 1
    assert mk_prism.Generated(mk_dummy.Shape()).Extent() == 0
