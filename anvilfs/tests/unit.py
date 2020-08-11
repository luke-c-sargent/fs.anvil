from ..base import BaseAnVILResource, BaseAnVILFile, BaseAnVILFolder
from ..bucket import WorkspaceBucket, WorkspaceBucketFile
from ..namespace import Namespace
from ..workspace import Workspace

from .testutils import success, failure, RESULTS


from fs.enums import ResourceType


# base anvil resource # -------------------------
def test_base_getinfo():
    DESC = "BaseAnVILResource getinfo() is abstract"
    bar = BaseAnVILResource()
    bar.name = "test"
    try:
        bar.getinfo()
    except NotImplementedError as e:
        success(DESC)
        return
    failure(DESC)

def test_base_hash():
    DESC = "BaseAnVILResource hash()"
    bar = BaseAnVILResource()
    bar.name = "hasher"
    if bar.__hash__() == hash(("hasher", "BaseAnVILResource")):
        success(DESC)
    else:
        failure(DESC)

# base anvil file # -------------------------
def test_base_file_getinfo():
    DESC = "BaseAnVILFile getinfo()"
    name = "a"
    size = "1"
    last_mod = "lastmodstring"
    r_dict = {"basic": {
                "name": name,
                "is_dir": False,
            },
            "details": {
                "type": ResourceType.file,
                "size": size,
                "modified": last_mod
            }
        }
    baf = BaseAnVILFile(name, size, last_mod)
    if baf.getinfo().raw == r_dict:
        success(DESC)
    else:
        failure(DESC)

def test_base_file_open_bin():
    DESC = "BaseAnVILFile open_bin() is abstract"
    baf = BaseAnVILFile("a", 1)
    try:
        baf.open_bin()
    except NotImplementedError as e:
        success(DESC)
        return
    failure(DESC)

def test_base_file_eq():
    DESC = "BaseAnVILFile __eq__()"
    name = "a"
    size = 999
    last_mod = "yes"
    baf1 = BaseAnVILFile(name, size, last_mod)
    baf2 = BaseAnVILFile(name, size, last_mod)
    if baf1 == baf2:
        success(DESC)
    else:
        failure(DESC)

# base anvil folder # -------------------------
def test_base_folder_getinfo():
    DESC = "BaseAnVILFolder getinfo()"
    # folders end with '/' to differentiate between same-named files
    name = "a/"
    last_mod = "lastmodstring"
    r_dict = {
        "basic": {
            "name": name,
            "is_dir": True,
        },
        "details": {
            "type": ResourceType.directory,
            "modified": last_mod
        }
    }
    baf = BaseAnVILFolder(name, last_mod)
    if baf.getinfo().raw == r_dict:
        success(DESC)
    else:
        failure(DESC)

def test_base_folder_hash():
    DESC = "BaseAnVILFolder __hash__()"
    name = "a/"
    last_mod = "yes"
    baf = BaseAnVILFolder(name, last_mod)
    if hash((name, "BaseAnVILFolder", last_mod)) == baf.__hash__():
        success(DESC)
    else:
        failure(DESC)

def test_base_folder_get():
    DESC = "BaseAnVILFolder __getitem__()"
    baf = BaseAnVILFolder("A","B")
    baf.filesystem["X"] = "Y"
    if baf["X"] == "Y":
        success(DESC)
    else:
        failure(DESC)

def test_base_folder_set():
    DESC = "BaseAnVILFolder __setitem__()"
    baf = BaseAnVILFolder("A","B")
    baf["X"] = "Y"
    if baf.filesystem["X"] == "Y":
        success(DESC)
    else:
        failure(DESC)

def test_base_folder_gofp():
    DESC = "BaseAnVILFolder get_object_from_path()"
    baf = BaseAnVILFolder("Place","Holder")
    # TODO - objects not strings
    baf.filesystem["A"] = {"B": {"C":"D"}}
    fi = baf.get_object_from_path("A/B/C")
    fo = baf.get_object_from_path("A/B/")
    if fi == "D" and fo == {"C":"D"}:
        success(DESC)
    else:
        failure(DESC)

# Namespace # -------------------------
def test_ns_init(ns_name):
    DESC = "Namespace __init__()"
    ns = Namespace(ns_name)
    if ns.name != ns_name + "/":
        failure(DESC + ": name")
    if ns.__hash__() != hash((ns_name+"/", "Namespace", None)):
        failure(DESC + ": hash")

def test_ns_fetch_workspace(ns_name, ws_name):
    DESC = "Namespace fetch_workspace()"
    ns = Namespace(ns_name)
    ws = ns.fetch_workspace(ws_name)
    if ws.name[:-1] != ws_name:
        failure(DESC + ": ws name")
    if ns[ws_name] != ws:
        failure(DESC + ": ws obj equivalence")
    success(DESC)

# Workspace # --------------------------
def test_ws_init(ns_name, ws_name):
    DESC = "Workspace __init__()"
    ns = Namespace(ns_name)
    ws = Workspace(ns, ws_name)
    if not isinstance(ws["Other Data/"], WorkspaceBucket):
        failure(DESC + ": WorkspaceBucket not present")
    else:
        success(DESC)

def test_ws_fetchinfo(ns_name, ws_name):
    DESC = "Workspace fetch_api_info()"
    ns = Namespace(ns_name)
    ws = Workspace(ns, ws_name)
    info = ws.fetch_api_info(ws_name)
    if "workspace" not in info:
        failure(DESC + ": fetched info incomplete")
    else:
        success(DESC)

# WorkspaceBucket # ----------------------

def test_bucket_init(bucket_name):
    DESC = "WorkspaceBucket __init__()"
    wsb = WorkspaceBucket(bucket_name)
    if wsb.name != "Files/":
        failure(DESC + ": name mismatch")
    else:
        success(DESC)

def test_bucket_insert(bucket_name):
    DESC = "WorkspaceBucket insert_file()"
    wsb = WorkspaceBucket(bucket_name)
    class FakeBlob:
        def __init__(self):
            self.name = "afile/in/the/bucket.nfo"
            self.size = 1
            self.updated = "some time"
        def __eq__(self, second):
            return (self.name == second.name
                    and self.size == second.size
                    and self.updated == second.updated)

    wsb.insert_file(FakeBlob())
    wsbf = WorkspaceBucketFile(FakeBlob())
    fake_insert = wsb["afile/"]["in/"]["the/"]["bucket.nfo"]
    if fake_insert != wsbf:
        failure(DESC + ": object mismatch")
    else:
        success(DESC)
    

# path that == bucket location to be pruned
BUCKET_PREFIX="Other Data/Files/"


def run_all(anvil, files, folders):
    ns_name = anvil.namespace.name[:-1]
    ws_name = anvil.workspace.name[:-1]
    bucket_name = anvil.workspace.bucket_name
    print(" - UNIT TESTING")
    # BaseAnVILResource
    test_base_getinfo()
    test_base_hash()
    # BaseAnVILFile
    test_base_file_getinfo()
    test_base_file_open_bin()
    test_base_file_eq()
    # BaseAnVILFolder
    test_base_folder_getinfo()
    test_base_folder_hash()
    test_base_folder_get()
    test_base_folder_set()
    test_base_folder_gofp()
    # Namespace
    test_ns_init(ns_name)
    test_ns_fetch_workspace(ns_name, ws_name)
    # Workspace
    test_ws_init(ns_name, ws_name)
    test_ws_fetchinfo(ns_name, ws_name)
    test_ws_fetchinfo(ns_name, ws_name)
    # Bucket
    test_bucket_init(bucket_name)
    test_bucket_insert(bucket_name)

    # summary
    print("\nUnit Test Summary:\n\t{}".format(RESULTS))