# Translated from OCCT src/FoundationClasses/TKernel/GTests/Standard_Dump_Test.cxx (LGPL-2.1 with the OCCT exception)
# DumpJson(stream) is bound as DumpJson() -> str, InitFromJson(stream, pos) as InitFromJson(TextIO, pos) -> (ok, pos);
# the AddValuesSeparator tests that pre-fill a C++ stream are not expressible (the binding returns a fresh string).
import io

from nanocct.Bnd import Bnd_Box
from nanocct.gp import gp_Ax3, gp_Dir, gp_Pnt
from nanocct.Standard import Standard_Dump


def test_Standard_DumpTest_AddValuesSeparator_EmptyStream():
    assert Standard_Dump.AddValuesSeparator_s() == ""


def test_Standard_DumpTest_gp_Pnt_DumpAndInit():
    p = gp_Pnt(1.5, 2.5, 3.5)
    s = p.DumpJson()
    assert '"gp_Pnt"' in s
    assert "[1.5, 2.5, 3.5]" in s

    q = gp_Pnt()
    ok, _ = q.InitFromJson(io.StringIO(s), 1)
    assert ok
    assert q.X() == p.X()
    assert q.Y() == p.Y()
    assert q.Z() == p.Z()


def test_Standard_DumpTest_gp_Ax3_DumpAndInit_MultipleSeparators():
    a = gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(gp_Dir.D.Z), gp_Dir(gp_Dir.D.X))
    s = a.DumpJson()
    assert ', "Direction"' in s
    assert ', "XDirection"' in s
    assert ', "YDirection"' in s
    assert ']"Direction"' not in s
    assert ']"XDirection"' not in s
    assert ']"YDirection"' not in s

    b = gp_Ax3()
    ok, _ = b.InitFromJson(io.StringIO(s), 1)
    assert ok
    assert a.Location().IsEqual(b.Location(), 1e-10)
    assert a.Direction().IsEqual(b.Direction(), 1e-10)


def test_Standard_DumpTest_Bnd_Box_ComplexDump():
    box = Bnd_Box(gp_Pnt(-5, -10, -15), gp_Pnt(20, 30, 40))
    box.SetGap(1.5)
    s = box.DumpJson()
    assert ', "CornerMax"' in s
    assert ', "Gap"' in s
    assert ', "Flags"' in s

    box2 = Bnd_Box()
    ok, _ = box2.InitFromJson(io.StringIO(s), 1)
    assert ok
    assert box.Get__float__float__float__float__float__float() == box2.Get__float__float__float__float__float__float()
    assert box.GetGap() == box2.GetGap()


def test_Standard_DumpTest_VoidBoxSerialization():
    s = Bnd_Box().DumpJson()
    assert s != ""
    box2 = Bnd_Box()
    ok, _ = box2.InitFromJson(io.StringIO(s), 1)
    assert ok
    assert box2.IsVoid()
