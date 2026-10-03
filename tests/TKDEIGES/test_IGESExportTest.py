# Translated from OCCT src/DataExchange/TKDEIGES/GTests/IGESExportTest.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.BRepPrimAPI import BRepPrimAPI_MakeBox
from nanocct.gp import gp_Pnt
from nanocct.IGESControl import IGESControl_Writer
from nanocct.IGESData import IGESData_IGESEntity
from nanocct.IGESGeom import IGESGeom_Line
from nanocct.Transfer import Transfer_SimpleBinderOfTransient


def test_IGESExportTest_SharedCurvesBRepMode():
    solid = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 1, 1, 1).Solid()

    brep_mode = 1
    writer = IGESControl_Writer("MM", brep_mode)
    writer.AddShape(solid)

    fp = writer.TransferProcess()
    model = writer.Model()

    n_lines = 0
    for i in range(1, fp.NbMapped() + 1):
        binder = fp.MapItem(i)
        if not isinstance(binder, Transfer_SimpleBinderOfTransient):
            continue
        ent = binder.Result()
        if not isinstance(ent, IGESData_IGESEntity):
            continue
        if not isinstance(ent, IGESGeom_Line):
            continue
        n_lines += 1
        assert model.DNum(ent) != 0
    assert n_lines > 0  # sanity for the translation: the loop body ran
