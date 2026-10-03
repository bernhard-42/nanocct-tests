# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AdvApp2Var_Network_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.AdvApp2Var import AdvApp2Var_Network, AdvApp2Var_Patch
from nanocct.NCollection import NCollection_Sequence


def _seq(typ, items):
    s = NCollection_Sequence[typ]()
    for it in items:
        s.Append(it)
    return s


def _net(patches, us, vs):
    return AdvApp2Var_Network(_seq(AdvApp2Var_Patch, [AdvApp2Var_Patch(*p) for p in patches]),
                              _seq(float, us), _seq(float, vs))


def _orders(p):
    return (p.UOrder(), p.VOrder())


def test_AdvApp2Var_NetworkTest_UpdateInV_PreservesPatchOrdersPerColumn():
    nw = _net([(0.0, 1.0, 0.0, 1.0, 0, 1), (1.0, 2.0, 0.0, 1.0, 2, 3)], [0.0, 1.0, 2.0], [0.0, 1.0])
    nw.UpdateInV(0.5)
    assert nw.NbPatch() == 4
    assert nw.NbPatchInU() == 2
    assert nw.NbPatchInV() == 2
    assert nw.VParameter(2) == 0.5
    bl, br, tl, tr = nw.Patch(1, 1), nw.Patch(2, 1), nw.Patch(1, 2), nw.Patch(2, 2)
    assert _orders(bl) == (0, 1)
    assert _orders(br) == (2, 3)
    assert _orders(tl) == (0, 1)
    assert _orders(tr) == (2, 3)
    assert (bl.V0(), bl.V1()) == (0.0, 0.5)
    assert (tl.V0(), tl.V1()) == (0.5, 1.0)


def test_AdvApp2Var_NetworkTest_UpdateInU_PreservesPatchOrdersPerRow():
    nw = _net([(0.0, 1.0, 0.0, 1.0, 0, 1), (1.0, 2.0, 0.0, 1.0, 2, 3),
               (0.0, 1.0, 1.0, 2.0, 4, 5), (1.0, 2.0, 1.0, 2.0, 6, 7)], [0.0, 1.0, 2.0], [0.0, 1.0, 2.0])
    nw.UpdateInU(0.5)
    assert nw.NbPatch() == 6
    assert nw.NbPatchInU() == 3
    assert nw.NbPatchInV() == 2
    assert nw.UParameter(2) == 0.5
    exp = {(1, 1): (0, 1), (2, 1): (0, 1), (3, 1): (2, 3), (1, 2): (4, 5), (2, 2): (4, 5), (3, 2): (6, 7)}
    for (i, j), orders in exp.items():
        assert _orders(nw.Patch(i, j)) == orders
    bl, bm = nw.Patch(1, 1), nw.Patch(2, 1)
    assert (bl.U0(), bl.U1()) == (0.0, 0.5)
    assert (bm.U0(), bm.U1()) == (0.5, 1.0)
