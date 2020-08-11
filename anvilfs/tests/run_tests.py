#!/usr/bin/env python3



from .testconfig import config
from .unit import run_all as run_all_unit_tests
# from .integration import run_all as run_all_integration_tests

# setup
if "anvil" not in locals():
    from ..anvilfs import AnVILFS
    from google.cloud import storage
    anvil = AnVILFS(config["namespace_name"], 
                    config["workspace_name"])
    bucket_name = anvil.workspace.bucket_name
    blobs = storage.Client().get_bucket(bucket_name).list_blobs()
    files = []
    folders = []
    bucketfolder_prefix = "Other Data/Files/"
    for blob in blobs:
        files.append(bucketfolder_prefix+blob.name)
        split = blob.name.split("/")
        for i in range(len(split[:-1])):
            segment = bucketfolder_prefix + "/".join(split[i:-1])
            if segment not in folders:
                folders.append(segment)
    print("discovered files: \n{}".format(files))
    print("discovered folders: \n{}\n".format(folders))

if __name__ == "__main__":
    run_all_unit_tests(anvil, files, folders)
    # run_all_integration_tests(anvil, files, folders)