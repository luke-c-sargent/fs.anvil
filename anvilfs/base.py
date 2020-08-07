from io import BytesIO

from fs.enums import ResourceType
from fs.errors import DirectoryExpected, ResourceNotFound, FileExpected
from fs.info import Info

class BaseAnVILResource:
    def getinfo(self):
        raise NotImplementedError("Method getinfo() not implemented")
    
    def __hash__(self):
        return hash((self.name, self.__class__.__name__))
    
    def __eq__(self, other):
        return self.getinfo().raw == other.getinfo().raw
    
    def __ne__(self, other):
        return not(self == other)


class BaseAnVILFile(BaseAnVILResource):
    def __init__(self, name, size, last_modified):
        self.name = name
        self.size = size
        self.last_modified = last_modified

    def getinfo(self):
        result = {
            "basic": {
                "name": self.name,
                "is_dir": False,
            },
            "details": {
                "type": ResourceType.file,
                "size": self.size,
                "modified": self.last_modified
            }
        }
        return Info(result)

    def open_bin(self):
        raise NotImplementedError("Method open_bin() not implemented")

class BaseAnVILFolder(BaseAnVILResource):
    def __init__(self, name, last_modified = None):
        if name[-1] != "/": # required since anvil supports names the same as their containing directories
            self.name = name + "/"
        else:
            self.name = name
        self.last_modified = last_modified
        self.filesystem = {}

    def __hash__(self):
        return hash((self.name, "dir", self.last_modified))

    def __eq__(self, other):
        return (self.name, self.last_modified) == (other.name, other.last_modified)

    


    # allow dictionary-style access
    def __getitem__(self, key):
        return self.filesystem[key]
    
    def __setitem__(self, key, val):
        self.filesystem[key] = val

    def getinfo(self):
        _result = {
            "basic": {
                "name": self.name,
                "is_dir": True,
            },
            "details": {
                "type": ResourceType.directory,
                "modified": self.last_modified
            }
        }