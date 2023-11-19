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


def main():
    fu = bmd.scriptapp("Fusion")
    try:
        reg_list = fu.GetRegList()
        reg = [i.ID for i in reg_list.values()]
        with open("src/main/utils/fusion_registry_list.json", "w") as out:
            json.dump(reg, out)
    except AttributeError:
        print("No Fusion instance found")


if __name__ == "__main__":
    main()
