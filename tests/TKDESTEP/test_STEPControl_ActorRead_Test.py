# Translated from OCCT src/DataExchange/TKDESTEP/GTests/STEPControl_ActorRead_Test.cxx (LGPL-2.1 with the OCCT exception)
import pytest

from nanocct import TopoDS
from nanocct.BRep import BRep_Tool
from nanocct.gp import gp_Pnt
from nanocct.Interface import Interface_HGraph
from nanocct.NCollection import NCollection_HArray1
from nanocct.StepAP214 import StepAP214_Protocol
from nanocct.StepBasic import StepBasic_NamedUnit, StepBasic_SiUnitAndLengthUnit, StepBasic_spMilli, StepBasic_sunMetre
from nanocct.STEPControl import STEPControl_ActorRead, STEPControl_Controller
from nanocct.StepData import StepData_Factors, StepData_StepModel
from nanocct.StepGeom import (StepGeom_Axis2Placement3d, StepGeom_CartesianPoint,
                              StepGeom_GeometricRepresentationContextAndGlobalUnitAssignedContext)
from nanocct.StepRepr import (StepRepr_ConstructiveGeometryRepresentation,
                              StepRepr_ConstructiveGeometryRepresentationRelationship, StepRepr_MappedItem,
                              StepRepr_RepresentationItem, StepRepr_RepresentationMap)
from nanocct.StepShape import StepShape_ShapeRepresentation
from nanocct.TCollection import TCollection_HAsciiString
from nanocct.TopAbs import TopAbs_VERTEX
from nanocct.Transfer import Transfer_TransientProcess
from nanocct.TransferBRep import TransferBRep


def _context(millimeters):
    unit = StepBasic_SiUnitAndLengthUnit()
    unit.Init(millimeters, StepBasic_spMilli, StepBasic_sunMetre)
    units = NCollection_HArray1[StepBasic_NamedUnit](1, 1)
    units.SetValue(1, unit)
    context = StepGeom_GeometricRepresentationContextAndGlobalUnitAssignedContext()
    context.Init(TCollection_HAsciiString(), TCollection_HAsciiString(), 3, units)
    return context


def _items(item):
    items = NCollection_HArray1[StepRepr_RepresentationItem](1, 1)
    items.SetValue(1, item)
    return items


def test_STEPControl_ActorReadTest_ConstructivePoints_UseTheirRepresentationUnitsAndReadSetting():
    STEPControl_Controller.Init_s()
    for read_constructive in (False, True):
        model = StepData_StepModel()
        model.SetProtocol(StepAP214_Protocol())
        model.SetLocalLengthUnit(1.0)
        model.InternalParameters.ReadRelationship = True
        model.InternalParameters.ReadConstrRelation = read_constructive
        name = TCollection_HAsciiString()
        origin = StepGeom_CartesianPoint()
        origin.Init3D(name, 0, 0, 0)
        axis = StepGeom_Axis2Placement3d()
        axis.Init(name, origin, False, None, False, None)
        root = StepShape_ShapeRepresentation()
        root.Init(name, _items(axis), _context(True))
        representation_map = StepRepr_RepresentationMap()
        representation_map.Init(axis, root)
        mapped = StepRepr_MappedItem()
        mapped.Init(name, representation_map, axis)
        model.AddWithRefs(mapped)
        points = []
        for i in range(2):
            point = StepGeom_CartesianPoint()
            point.Init3D(name, i + 1, 0, 0)
            points.append(point)
            representation = StepRepr_ConstructiveGeometryRepresentation()
            representation.Init(name, _items(point), _context(i == 1))
            relation = StepRepr_ConstructiveGeometryRepresentationRelationship()
            relation.Init(name, name, root, representation)
            model.AddWithRefs(relation)
        process = Transfer_TransientProcess()
        process.SetGraph(Interface_HGraph(model))
        actor = STEPControl_ActorRead(model)
        actor.TransferShape(mapped, process, StepData_Factors())
        for i in range(2):
            shape = TransferBRep.ShapeResult_s(process, points[i])
            if read_constructive is False:
                assert shape.IsNull() is True, (read_constructive, i)
                continue
            assert shape.IsNull() is False, i
            assert shape.ShapeType() == TopAbs_VERTEX, i
            assert BRep_Tool.Pnt_s(TopoDS.Vertex(shape)).X() == pytest.approx(1000.0 if i == 0 else 2.0, abs=1.e-10), i


def test_STEPControl_ActorReadTest_StandalonePoint_UsesExplicitFactors():
    STEPControl_Controller.Init_s()
    model = StepData_StepModel()
    model.SetProtocol(StepAP214_Protocol())
    point = StepGeom_CartesianPoint()
    point.Init3D(TCollection_HAsciiString(), 2, 3, 4)
    representation = StepRepr_ConstructiveGeometryRepresentation()
    representation.Init(TCollection_HAsciiString(), _items(point), _context(False))
    model.AddWithRefs(representation)
    process = Transfer_TransientProcess()
    process.SetGraph(Interface_HGraph(model))
    actor = STEPControl_ActorRead(model)
    factors = StepData_Factors()
    actor.PrepareUnits(representation, process, factors)
    shape = TransferBRep.ShapeResult_s(actor.TransferShape(point, process, factors))
    assert shape.IsNull() is False
    assert shape.ShapeType() == TopAbs_VERTEX
    assert BRep_Tool.Pnt_s(TopoDS.Vertex(shape)).Distance(gp_Pnt(2000, 3000, 4000)) < 1.e-10
