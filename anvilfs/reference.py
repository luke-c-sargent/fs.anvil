from io import BytesIO

import firecloud.api as fapi
from google.cloud import storage

from .base import BaseAnVILFolder, BaseAnVILFile

class ReferenceDataFile(BaseAnVILFile):
    def __init__(self, name, url, size, last_modified=None):
        self.name = name
        self.url = url
        self.last_modified

    @classmethod
    def make_rdfs(cls, objs):
        result = []
        if isinstance(objs, str):
            objs = [objs]
        elif isinstance(objs, dict):
            objs = objs["items"]
        for o in objs:
            name = o.split("/")[-1]
            result.append(cls(name, o))
        return result

    def get_bytes_handler(self):
        return resolve_url()

    def resolve_url(self):
        # determine type
        scheme = self.url.split("://")[0]
        if scheme == "gs":
            self._resolve_google(self.url)
        elif scheme == "drs":
            self._resolve_drs(self.url)
        elif scheme == "http" or scheme == "https":
            self._resolve_http(self.url)
        else:
            raise Exception("{}: schema '{}' not supported".format(self.__class__.__name__, schema))

    def _resolve_google(self, url):
        buffer = BytesIO()
        c = storage.Client()
        c.download_blob_to_file(url, buffer)
        return buffer

    def _resolve_drs(self, url):
        pass
        # return buffer

    def _resolve_http(self, url):
        pass
        # return buffer