# Translated from OCCT src/ModelingData/TKGeomBase/GTests/AdvApp2Var_Context_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.AdvApp2Var import AdvApp2Var_Context
from nanocct.NCollection import NCollection_HArray1, NCollection_HArray2


def test_AdvApp2Var_ContextTest_Tolerances_AreAggregatedAndRescaledForBorderConstraints():
    tols = []
    for v in (6.0, 12.0, 18.0):
        t = NCollection_HArray1[float](1, 1)
        t.SetValue(1, v)
        tols.append(t)
    tofs = []
    for _ in range(3):
        t = NCollection_HArray2[float](1, 1, 1, 4)
        t.Init(100.0)
        tofs.append(t)
    ctx = AdvApp2Var_Context(0, 0, 0, 2, 2, 0, 1, 1, 1, *tols, *tofs)
    assert ctx.TotalNumberSSP() == 3
    assert ctx.TotalDimension() == 6
    itol = ctx.IToler()
    assert itol is not None
    assert [itol.Value(i) for i in (1, 2, 3)] == [3.0, 6.0, 9.0]
    ftol, ctol = ctx.FToler(), ctx.CToler()
    assert ftol is not None
    assert ctol is not None
    for j in range(1, 5):
        for i, exp in ((1, 1.0), (2, 2.0), (3, 3.0)):
            assert ftol.Value(i, j) == exp
            assert ctol.Value(i, j) == exp
