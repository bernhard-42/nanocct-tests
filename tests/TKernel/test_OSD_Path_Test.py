# Translated from OCCT src/FoundationClasses/TKernel/GTests/OSD_Path_Test.cxx (LGPL-2.1 with the OCCT exception)
from nanocct.OSD import OSD_Path, OSD_Process
from nanocct.TCollection import TCollection_AsciiString


def split(path):
    folder = TCollection_AsciiString()
    name = TCollection_AsciiString()
    OSD_Path.FolderAndFileFromPath_s(path, folder, name)
    return folder.ToCString(), name.ToCString()


def test_OSD_PathTest_DosAbsolutePaths():
    p = "c:\\folder\\file.png"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsDosPath_s(p)
    assert not OSD_Path.IsRelativePath_s(p)
    assert not OSD_Path.IsUnixPath_s(p)
    assert not OSD_Path.IsUncPath_s(p)
    assert OSD_Path.IsAbsolutePath_s("D:\\")
    assert OSD_Path.IsDosPath_s("D:\\")
    assert OSD_Path.IsAbsolutePath_s("c:\\file.png")
    assert OSD_Path.IsDosPath_s("c:\\file.png")


def test_OSD_PathTest_UncPaths():
    p = "\\\\share\\file.pdf"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsUncPath_s(p)
    assert not OSD_Path.IsDosPath_s(p)
    assert not OSD_Path.IsUnixPath_s(p)


def test_OSD_PathTest_NtExtendedPaths():
    p = "\\\\?\\C:\\documents\\file.docx"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsNtExtendedPath_s(p)
    assert not OSD_Path.IsUncPath_s(p)


def test_OSD_PathTest_UncExtendedPaths():
    p = "\\\\?\\UNC\\server\\share\\file.zip"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsUncPath_s(p)
    assert OSD_Path.IsNtExtendedPath_s(p)
    assert OSD_Path.IsUncExtendedPath_s(p)


def test_OSD_PathTest_RemoteProtocolPaths():
    p = "https://www.server.org/file.gif"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsRemoteProtocolPath_s(p)
    assert not OSD_Path.IsUnixPath_s(p)
    assert not OSD_Path.IsDosPath_s(p)
    for q in ("ftp://ftp.server.com/file.dat", "http://example.com/path"):
        assert OSD_Path.IsAbsolutePath_s(q)
        assert OSD_Path.IsRemoteProtocolPath_s(q)


def test_OSD_PathTest_ContentProtocolPaths():
    p = "content://file.jpg"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsRemoteProtocolPath_s(p)
    assert OSD_Path.IsContentProtocolPath_s(p)


def test_OSD_PathTest_UnixAbsolutePaths():
    p = "/home/username/file.txt"
    assert OSD_Path.IsAbsolutePath_s(p)
    assert OSD_Path.IsUnixPath_s(p)
    assert not OSD_Path.IsRelativePath_s(p)
    assert not OSD_Path.IsDosPath_s(p)
    for q in ("/", "/boot.bin"):
        assert OSD_Path.IsAbsolutePath_s(q)
        assert OSD_Path.IsUnixPath_s(q)


def test_OSD_PathTest_RelativePaths():
    for p in ("./subfolder/../file.txt", "../file.txt", ".", "..", "folder/file.txt", "file.txt"):
        assert OSD_Path.IsRelativePath_s(p)
        assert not OSD_Path.IsAbsolutePath_s(p)


def test_OSD_PathTest_FolderAndFileFromPath_UnixPaths():
    assert split("/home/username/file.txt") == ("/home/username/", "file.txt")
    assert split("/file.txt") == ("/", "file.txt")
    assert split("/home/username/") == ("/home/username/", "")


def test_OSD_PathTest_FolderAndFileFromPath_DosPaths():
    assert split("C:\\Users\\John\\document.txt") == ("C:\\Users\\John\\", "document.txt")
    assert split("C:\\file.txt") == ("C:\\", "file.txt")
    assert split("C:\\Program Files\\") == ("C:\\Program Files\\", "")


def test_OSD_PathTest_FolderAndFileFromPath_RelativePaths():
    assert split("folder/subfolder/file.txt") == ("folder/subfolder/", "file.txt")
    assert split("../folder/file.txt") == ("../folder/", "file.txt")
    assert split("file.txt") == ("", "file.txt")


def test_OSD_PathTest_FolderAndFileFromPath_ProtocolPaths():
    assert split("https://www.server.org/folder/file.gif") == ("https://www.server.org/folder/", "file.gif")
    assert split("content://path/file.jpg") == ("content://path/", "file.jpg")


def test_OSD_PathTest_EdgeCases():
    assert split("") == ("", "")
    assert split("/") == ("/", "")
    assert split("\\") == ("\\", "")
    assert split("/home/username/foldername") == ("/home/username/", "foldername")


def test_OSD_PathTest_MixedSeparators():
    folder, name = split("C:/Users/John\\Documents/file.txt")
    assert folder != "" and name != ""


def test_OSD_PathTest_OCC310_TrekAndUpTrek():
    path = OSD_Path(TCollection_AsciiString("/where/you/want/tmp/qwerty/tmp/"))
    assert path.Trek().ToCString() == "|where|you|want|tmp|qwerty|tmp|"
    path.UpTrek()
    assert path.Trek().ToCString() == "|where|you|want|tmp|qwerty|"


def test_OSD_PathTest_OCC309_CurrentDirectoryAndUpTrek():
    path = OSD_Process().CurrentDirectory()
    name1 = TCollection_AsciiString()
    path.SystemName(name1)
    assert not name1.IsEmpty()
    path.UpTrek()
    name2 = TCollection_AsciiString()
    path.SystemName(name2)
    assert not name2.IsEmpty()
    assert name1 != name2
    assert name2.Length() < name1.Length()
