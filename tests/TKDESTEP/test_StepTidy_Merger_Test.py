# Translated from OCCT src/DataExchange/TKDESTEP/GTests/StepTidy_Merger_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct.NCollection import NCollection_HArray1
from nanocct.STEPControl import STEPControl_Controller
from nanocct.StepGeom import StepGeom_Axis1Placement, StepGeom_CartesianPoint, StepGeom_Direction, StepGeom_Vector
from nanocct.StepTidy import StepTidy_DuplicateCleaner
from nanocct.TCollection import TCollection_HAsciiString
from nanocct.XSControl import XSControl_WorkSession


@pytest.fixture
def ws():
    STEPControl_Controller.Init_s()
    w = XSControl_WorkSession()
    w.SelectNorm("STEP")
    w.SetModel(w.NormAdaptor().NewModel())
    return w


def _name(name):
    if name is None:
        return TCollection_HAsciiString()
    return TCollection_HAsciiString(name)


def _add_direction(ws, name=None, xyz=(0.0, 0.0, 1.0)):
    d = StepGeom_Direction()
    ratios = NCollection_HArray1[float](1, 3)
    for i, v in enumerate(xyz, start=1):
        ratios.SetValue(i, v)
    d.Init(_name(name), ratios)
    ws.Model().AddWithRefs(d)
    return d


def _count(ws, cls):
    t = cls.get_type_descriptor_s()
    model = ws.Model()
    return sum(1 for i in range(1, model.NbEntities() + 1) if model.Value(i).IsKind(t))


def _perform_removal(ws):
    StepTidy_DuplicateCleaner(ws).Perform()


def test_StepTidy_DuplicateCleanerTest_DifferentEntities(ws):
    dir1 = _add_direction(ws, "dir1")
    dir2 = _add_direction(ws, "dir2")

    v1 = StepGeom_Vector()
    v1.Init(TCollection_HAsciiString(), dir1, 1.0)
    ws.Model().AddWithRefs(v1)
    v2 = StepGeom_Vector()
    v2.Init(TCollection_HAsciiString(), dir2, 1.0)
    ws.Model().AddWithRefs(v2)

    before = _count(ws, StepGeom_Direction)
    _perform_removal(ws)
    after = _count(ws, StepGeom_Direction)

    assert before == 2
    assert before == after


def test_StepTidy_DuplicateCleanerTest_EqualEntities(ws):
    dir1 = _add_direction(ws)
    dir2 = _add_direction(ws)

    location = StepGeom_CartesianPoint()
    coords = NCollection_HArray1[float](1, 3)
    coords.SetValue(1, 0.0)
    coords.SetValue(2, 0.0)
    coords.SetValue(3, 0.0)
    location.Init(TCollection_HAsciiString(), coords)
    ws.Model().AddWithRefs(location)

    a1 = StepGeom_Axis1Placement()
    a1.Init(TCollection_HAsciiString(), location, True, dir1)
    ws.Model().AddWithRefs(a1)
    a2 = StepGeom_Axis1Placement()
    a2.Init(TCollection_HAsciiString(), location, True, dir2)
    ws.Model().AddWithRefs(a2)

    before = _count(ws, StepGeom_Direction)
    _perform_removal(ws)
    after = _count(ws, StepGeom_Direction)

    assert before == 2
    assert after == 1
