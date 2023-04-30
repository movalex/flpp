import json
from flpp import flpp
from pathlib import Path

FILE = "Fusion.comp"

file_name = Path(FILE).stem
extension = Path(FILE).suffix

with open(str(FILE), "r", encoding="utf-8") as f:
    if extension == ".comp":
        lines = f.readlines()
        lines[0] = "{\n"
        text = "\n".join(lines)
    else:
        text = f.read()

data = flpp.decode(text)
# data["Locked"] = False
with open(f"{file_name}_modified.json", "w", encoding="utf-8") as out:
    json.dump(data, out, indent=4, sort_keys=False)

with open(f"{file_name}_modified{extension}", "w", encoding="utf-8") as out:
    if extension == ".comp":
        print("Composition", file=out, end="")
    upd = flpp.encode(data)
    out.write(upd)
