import json
import re
from pprint import pprint
from slpp import slpp
from pathlib import Path

FILE = "fusion_shared.prefs"
# FILE = "Fusion.prefs"

file_name = Path(FILE).stem
extension = Path(FILE).suffix


with open(str(FILE), "r", encoding="utf-8") as f:
    text = f.read()


data = slpp.decode(text)
data["Locked"] = False

with open(f"{file_name}_modified{extension}", "w", encoding="utf-8") as out:
    upd = slpp.encode(data)
    out.write(upd)

with open(f"{file_name}_modified.json", "w", encoding="utf-8") as out:
    json.dump(data, out, indent=4, sort_keys=False)
