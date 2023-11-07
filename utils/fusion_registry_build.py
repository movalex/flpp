import json
import sys

try:
    import DaVinciResolveScript as bmd
except ImportError:
    print("RESOLVE_SCRIPT_API is not set. Trying to import fusionscript directly")
    try:
        import fusionscript as bmd
    except ImportError:
        print(
            "Unable to find Fusion script module."
            "Check the README and update PYTHONPATH accordingly"
        )
        sys.exit()

fu = bmd.scriptapp("Fusion")
reg = [i.ID for i in fu.GetRegList().values()]
with open("utils/fusion_registry_list.json", "w") as out:
    json.dump(reg, out)
