from slpp import slpp

FILE = "fusion_shared.prefs"

with open(str(FILE), "r") as f:
    text = f.read()

data = slpp.decode(text)
print(data)

data["Locked"] = False
with open("fusion_shared_out.prefs", "w") as out:
    out.write(slpp.encode(data))
