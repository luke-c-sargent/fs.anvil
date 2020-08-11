RESULTS = {
    "success": 0,
    "failure": 0
}

def success(test_desc):
    print("SUCCESS: {}".format(test_desc))
    RESULTS["success"] += 1

def failure(test_desc):
    print("FAILURE: {}".format(test_desc))
    RESULTS["failure"] += 1