# Translated from OCCT src/ModelingData/TKBRep/GTests/BRepTools_Test.cxx (LGPL-2.1 with the OCCT exception)
# Not translated: ParallelRead_IdenticalMass and ParallelRead_RepeatedRuns: they read from OSD_Parallel::For with a C++
# lambda (C++ threading). Not translated either: the C++ stream state the other cases check -- fail() -- because a
# Python file-like object has none and the binding's stream exists only during the call (R-STREAM-IN).
import io

from nanocct.BRep import BRep_Builder
from nanocct.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from nanocct.BRepTools import BRepTools
from nanocct.gp import gp_Pnt
from nanocct.TopoDS import TopoDS_Shape
from nanocct.TopTools import TopTools_LocationSet


def test_BRepToolsTest_OversizedRealTokenRejectsShapeRead():
    edge = BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, 0), gp_Pnt(1, 0, 0)).Edge()
    record = BRepTools.Write_s(edge)
    prefix = "Curves 1\n1 "
    position = record.find(prefix)
    assert position >= 0
    position += len(prefix)
    record = record[:position] + "0" * 512 + record[position:]

    read = TopoDS_Shape()
    BRepTools.Read_s(read, io.StringIO(record), BRep_Builder())   # EXPECT_NO_THROW
    assert read.IsNull()


def test_BRepToolsTest_OversizedLocationValueDoesNotAddTransform():
    locations = TopTools_LocationSet()
    header = "Locations 1\n1\n"
    record = header + "0" * 510 + "1 0 0 4\n0 1 0 0\n0 0 1 0\n"

    locations.Read(io.StringIO(record))
    assert not locations.Location(1).IsIdentity()
    assert locations.Location(1).Transformation().TranslationPart().X() == 4.0

    record = record[: len(header)] + "0" + record[len(header):]
    locations.Read(io.StringIO(record))   # EXPECT_NO_THROW
    assert locations.Location(1).IsIdentity()
