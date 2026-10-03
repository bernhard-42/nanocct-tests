# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AdvApp2Var_Iso_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.AdvApp2Var import AdvApp2Var_Iso
from nanocct.GeomAbs import GeomAbs_IsoU, GeomAbs_IsoV


def test_AdvApp2Var_IsoTest_ConstructorWithOrders_AssignsOrdersByIsoType():
    u = AdvApp2Var_Iso(GeomAbs_IsoU, 3, 1)
    assert u.Type() == GeomAbs_IsoU
    assert u.UOrder() == 3
    assert u.VOrder() == 1
    assert u.Constante() == 0.5
    assert (u.U0(), u.U1(), u.V0(), u.V1(), u.T0(), u.T1()) == (0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
    assert u.Position() == 0
    v = AdvApp2Var_Iso(GeomAbs_IsoV, 3, 1)
    assert v.Type() == GeomAbs_IsoV
    assert v.UOrder() == 3
    assert v.VOrder() == 1
