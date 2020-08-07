from google.cloud import storage

from .base import BaseAnVILFolder, BaseAnVILFile

class WorkspaceBucket(BaseAnVILFolder):
    def __init__(self, bucket_name):
        super().__init__("Files")
        self.bucket_name = bucket_name
        google_bucket = storage.Client().get_bucket(bucket_name)
        blobs = google_bucket.list_blobs()
        for blob in blobs:
            self.insert_file(blob)

    def insert_file(self, bucket_blob):
        # name relative to the path from workspace bucket
        bucketfile_name = bucket_blob.name
        idx = bucketfile_name.find('/')
        if idx < 0: # idx of -1 means char not found
            self[WorkspaceBucketFile(bucket_blob)] = None


class WorkspaceBucketFile(BaseAnVILFile):
    def __init__(self, blob):
        self.name = blob.name
        self.size = blob.size
        self.last_modified = blob.updated
        self.blob_handle = blob
        self.is_dir = False