import sys, os

# Return module path taking into account possible frozen state
def getLocation():
    encoding = sys.getfilesystemencoding()
    if hasattr(sys, "frozen"):
        return os.path.dirname(sys.executable)
    return __file__