import json
import re
from pprint import pprint
from flpp import flpp
from pathlib import Path

FILE = "Fusion.prefs"

file_name = Path(FILE).stem
extension = Path(FILE).suffix

with open(str(FILE), "r", encoding="utf-8") as f:
    text = f.read()

data = flpp.decode(text)
# data["Locked"] = False

with open(f"{file_name}_modified{extension}", "w", encoding="utf-8") as out:
    upd = flpp.encode(data)
    out.write(upd)

with open(f"{file_name}_modified.json", "w", encoding="utf-8") as out:
    json.dump(data, out, indent=4, sort_keys=False)
