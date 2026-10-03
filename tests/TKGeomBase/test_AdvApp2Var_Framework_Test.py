# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AdvApp2Var_Framework_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.AdvApp2Var import AdvApp2Var_Framework, AdvApp2Var_Iso, AdvApp2Var_Node
from nanocct.GeomAbs import GeomAbs_IsoU, GeomAbs_IsoV
from nanocct.gp import gp_XY
from nanocct.NCollection import NCollection_Sequence

IsoStrip = NCollection_Sequence[AdvApp2Var_Iso]
IsoGrid = NCollection_Sequence[IsoStrip]


def _grid(rows):
    grid = IsoGrid()
    for row in rows:
        strip = IsoStrip()
        for args in row:
            strip.Append(AdvApp2Var_Iso(*args, 0, 0, 0))
        grid.Append(strip)
    return grid


def _u_frontier():
    return _grid([[(GeomAbs_IsoV, 30.0, 0.0, 1.0, 0.0, 1.0), (GeomAbs_IsoV, 40.0, 0.0, 1.0, 0.0, 1.0)],
                  [(GeomAbs_IsoV, 30.0, 1.0, 2.0, 0.0, 1.0), (GeomAbs_IsoV, 40.0, 1.0, 2.0, 0.0, 1.0)]])


def _v_frontier():
    return _grid([[(GeomAbs_IsoU, 10.0, 0.0, 1.0, 0.0, 1.0), (GeomAbs_IsoU, 20.0, 0.0, 1.0, 0.0, 1.0)],
                  [(GeomAbs_IsoU, 10.0, 0.0, 1.0, 1.0, 2.0), (GeomAbs_IsoU, 20.0, 0.0, 1.0, 1.0, 2.0)]])


def _nodes():
    s = NCollection_Sequence[AdvApp2Var_Node]()
    for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
        s.Append(AdvApp2Var_Node(gp_XY(x, y), 0, 0))
    return s


def _framework():
    return AdvApp2Var_Framework(_nodes(), _u_frontier(), _v_frontier())


def _check_iso(iso, typ, const, t0, t1):
    assert iso.Type() == typ
    assert iso.Constante() == const
    assert iso.T0() == t0
    assert iso.T1() == t1


def test_AdvApp2Var_FrameworkTest_IsoLookup_ReturnsMatchingIso():
    fw = _framework()
    _check_iso(fw.IsoU(20.0, 0.0, 1.0), GeomAbs_IsoU, 20.0, 0.0, 1.0)
    _check_iso(fw.IsoV(1.0, 2.0, 40.0), GeomAbs_IsoV, 40.0, 1.0, 2.0)


def test_AdvApp2Var_FrameworkTest_NodeIndexMapping_UsesGridLayout():
    fw = _framework()
    assert fw.FirstNode(GeomAbs_IsoU, 2, 1) == 2
    assert fw.LastNode(GeomAbs_IsoU, 2, 1) == 5
    assert fw.FirstNode(GeomAbs_IsoV, 2, 1) == 4
    assert fw.LastNode(GeomAbs_IsoV, 2, 1) == 5


def test_AdvApp2Var_FrameworkTest_UpdateInU_InsertsCutIsoAndNodes():
    fw = _framework()
    fw.UpdateInU(0.5)
    _check_iso(fw.IsoU(0.5, 0.0, 1.0), GeomAbs_IsoU, 0.5, 0.0, 1.0)
    bottom, top = fw.Node(0.5, 0.0), fw.Node(0.5, 1.0)
    assert bottom is not None
    assert top is not None
    assert (bottom.Coord().X(), bottom.Coord().Y()) == (0.5, 0.0)
    assert (top.Coord().X(), top.Coord().Y()) == (0.5, 1.0)
    assert fw.FirstNode(GeomAbs_IsoU, 2, 1) == 2
    assert fw.LastNode(GeomAbs_IsoU, 2, 1) == 6
