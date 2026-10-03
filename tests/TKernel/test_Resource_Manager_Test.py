# Translated from OCCT src/FoundationClasses/TKernel/GTests/Resource_Manager_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.OSD import OSD_Environment
from nanocct.Resource import Resource_Manager
from nanocct.TCollection import TCollection_AsciiString


def write_resource_file(directory, file_name, key, value):
    directory.mkdir(parents=True, exist_ok=True)
    (directory / file_name).write_text(f"{key} : {value}\n")


def set_env(name, directory):
    env = OSD_Environment(TCollection_AsciiString(name))
    env.SetValue(TCollection_AsciiString(str(directory)))
    env.Build()


def test_Resource_ManagerTest_OCC27849_PathsWithSpecialChars(tmp_path):
    name = "TestResource"
    key = "test.resource"
    for rel in ("path", "path.with.dots", "path with spaces", "nested/dirs/path with spaces"):
        d = tmp_path / rel
        write_resource_file(d, name, key, "ok")
        set_env("CSF_TestResourceDefaults", d)
        manager = Resource_Manager(name)
        assert manager.Find(key), str(d)
        assert manager.Value(key) == "ok"


def test_Resource_ManagerTest_OCC181_SaveToExistingDirectory(tmp_path):
    name = "OCC181"
    source = tmp_path / "source"
    save = tmp_path / "save_flat"
    write_resource_file(source, name, "test.key", "test_value")
    save.mkdir(parents=True)

    set_env("CSF_" + name + "UserDefaults", source)
    manager = Resource_Manager(name)
    set_env("CSF_" + name + "UserDefaults", save)
    assert manager.Save()
    assert (save / name).exists()


def test_Resource_ManagerTest_OCC181_SaveToNestedNonExistentDirectory(tmp_path):
    name = "OCC181"
    source = tmp_path / "source2"
    save = tmp_path / "nested" / "deep" / "dir"
    write_resource_file(source, name, "test.key", "test_value")

    set_env("CSF_" + name + "UserDefaults", source)
    manager = Resource_Manager(name)
    set_env("CSF_" + name + "UserDefaults", save)
    assert manager.Save()
    assert (save / name).exists()
