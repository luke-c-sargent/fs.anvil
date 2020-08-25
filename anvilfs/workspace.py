import firecloud.api as fapi

from io import BytesIO
from os import SEEK_END, SEEK_SET

from .base import BaseAnVILFolder, BaseAnVILFile
from .bucket import WorkspaceBucket


class WorkspaceData(BaseAnVILFile):
    def __init__(self, name, data_dict):
        self.name = name
        self.buffer = self._dict_to_buffer(data_dict)
        self.last_modified = None
    
    def _dict_to_buffer(self, d):
        items = sorted(d.items())
        data = ("\t".join([k for k,v in items]) + 
            "\n" +
            "\t".join([v for k,v in items]))
        buffer = BytesIO(data.encode('utf-8'))
        position = buffer.tell()
        buffer.seek(0, SEEK_END)
        self.size = buffer.tell()
        buffer.seek(position, SEEK_SET)
        return buffer

    def get_bytes_handler(self):
        return self.buffer

class Workspace(BaseAnVILFolder):
    def __init__(self, namespace_reference,  workspace_name):
        self.namespace = namespace_reference
        resp = self.fetch_api_info(workspace_name)
        attributes = resp["workspace"]["attributes"]
        try:
            super().__init__(workspace_name, resp["workspace"]["lastModified"])
        except KeyError as e:
            print("Error: Workspace fetch_api_info({}) fetch failed".format(workspace_name))
        # bucket folder
        bucket_baf = BaseAnVILFolder("Other Data/")
        self[bucket_baf] = None
        # ref data folder
        ref_baf = BaseAnVILFolder("Reference Data/")
        self[ref_baf] = None
        refs = self.ref_extractor(attribs)
        for source in refs:
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

        # populate workspace data
        workspacedata = dict(attributes)
        blocklist_prefixes = [
            "referenceData_",
            "description"
        ]
        for datum in attributes:
            for blocked in blocklist_prefixes:
                if datum.startswith(blocked):
                    del workspacedata[datum]
        if workspacedata:
            bucket_baf[WorkspaceData("WorkspaceData.tsv", workspacedata)] = None
        bucket_baf[WorkspaceBucket(resp["workspace"]["bucketName"])] = None
        self.bucket_name = resp["workspace"]["bucketName"]
        # populate reference data

    def ref_extractor(self, attribs):
        # structure:
        # { "source": {
        #      "reftype": <files, str or list> }}
        result = {}
        for ref in [r for r in attribs if r.startswith("referenceData_")]:
            chunked = ref.split("_")
            source = chunked[1]
            if source not in result:
                result[source] = {}
            reftype = "_".join(chunked[2:])
            result[source].extend({
                reftype: attribs[ref]
            })
        return result

    def fetch_api_info(self, workspace_name):
        fields = "workspace.attributes,workspace.bucketName,workspace.lastModified"
        return fapi.get_workspace(namespace=self.namespace.name, workspace=workspace_name, fields=fields).json()
