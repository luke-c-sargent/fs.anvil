import firecloud.api as fapi

from .base import BaseAnVILFolder
from .bucket import WorkspaceBucket

class Workspace(BaseAnVILFolder):
    def __init__(self, namespace_reference,  workspace_name):
        self.namespace = namespace_reference
        resp = self.fetch_api_info(workspace_name)
        super().__init__(workspace_name, resp["workspace"]["lastModified"])
        self[BaseAnVILFolder("Other Data")] = WorkspaceBucket(resp["workspace"]["bucketName"])
        self.bucket_name = resp["workspace"]["bucketName"]

    def fetch_api_info(self, workspace_name):
        fields = "workspace.attributes,workspace.bucketName,workspace.lastModified"
        return fapi.get_workspace(namespace=self.namespace.name, workspace=workspace_name, fields=fields).json()

    def get_object_from_path(self, path):
        if not path:
            return self

    def get_info_from_path(self, path):
        return get_object_from_path(path).getinfo()