# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AdvApp2Var_Node_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.AdvApp2Var import AdvApp2Var_Node


def test_AdvApp2Var_NodeTest_Constructor_InitializesValuesToZero():
    node = AdvApp2Var_Node(1, 2)
    for u in range(0, 2):
        for v in range(0, 3):
            p = node.Point(u, v)
            assert (p.X(), p.Y(), p.Z()) == (0.0, 0.0, 0.0)
            assert node.Error(u, v) == 0.0
