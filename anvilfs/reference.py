from io import BytesIO

import firecloud.api as fapi
#from google.cloud import storage

from .base import BaseAnVILFolder, BaseAnVILFile

class ReferenceDataFolder(BaseAnVILFolder):
    def __init__(self, name, refs):
        super().__init__(name)

    def init_references(self, refs):
        for source in refs:
            # determine platform:
            # source, e.g. hg38
            source_baf = BaseAnVILFolder(source+"/")
            ref_baf[source_baf] = None
            # reftype, e.g. axiomPoly_resource_vcf
            for reftype in refs[source]:
                reftype_baf = BaseAnVILFolder(reftype+"/")
                source_baf[reftype_baf] = None
                contents = ReferenceDataFile.make_rdfs(refs[source][reftype])
                for c in contents:
                    reftype_baf[c] = None

        # determine largest common prefix
        # list resources by that prefix
        # iterate through resources to create objects
        # bind objects to appropriate folders

class ReferenceDataFile(BaseAnVILFile):
    def __init__(self, blob):
        print(blob)
        self.blob_handle = blob
        self.name = blob.name.split("/")[-1]
        self.last_modified = blob.updated
        self.size = blob.size
        self.is_dir = False

    @classmethod
    def make_rdfs(cls, objs):
        result = []
        # print(objs)
        # if isinstance(objs, str):
        #     objs = [objs]
        # elif isinstance(objs, dict):
        #     objs = objs["items"]
        for o in objs:
            result.append(cls(objs[o]))
        return result

    def get_bytes_handler(self):
        buffer = BytesIO()
        self.blob_handle.download_to_file(buffer)
        buffer.seek(0)
        return buffer

    # def resolve_url(self):
    #     # determine type
    #     scheme = self.url.split("://")[0]
    #     if scheme == "gs":
    #         self._resolve_google()
    #     elif scheme == "drs":
    #         self._resolve_drs(self.url)
    #     elif scheme == "http" or scheme == "https":
    #         self._resolve_http(self.url)
    #     else:
    #         raise Exception("{}: schema '{}' not supported".format(self.__class__.__name__, schema))

    # def _resolve_google(self):
    #     buffer = BytesIO()
    #     c = storage.Client()
    #     split = self.url[len("gs://"):].split("/", 1)
    #     bucket_name = split[0]
    #     blob_name = split[1]
    #     print(f"looking for blob {blob_name} from bucket {bucket_name}")
    #     bloblist = c.list_blobs(bucket_name, prefix=blob_name)
    #     for blob in bloblist:
    #         if blob.name == bucket_name:
    #             blob = bucket.blob(blob_name)
    #             break
    #     self.name = blob.name.split("/")[-1]
    #     self.size = blob.size
    #     self.last_modified = blob.updated
    #     self.blob_handle = blob

    # def _resolve_drs(self, url):
    #     pass
    #     # return buffer

    # def _resolve_http(self, url):
    #     pass
    #     # return buffer