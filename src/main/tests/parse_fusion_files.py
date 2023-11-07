import json
from pathlib import Path
from main.flpp import flpp

FOLDER = Path("src/main/tests/examples").resolve()


def parse_examples(target_folder: Path):
    output_folder = target_folder / "output"
    output_folder.mkdir(exist_ok=True)

    for file in target_folder.iterdir():
        file_name = file.stem
        if not file_name.startswith("fusion_"):
            continue
        extension = file.suffix

        with open(str(file), "r", encoding="utf-8") as f:
            if extension == ".comp":
                lines = f.readlines()
                lines[0] = "{\n"
                text = "\n".join(lines)
            else:
                text = f.read()

        data = flpp.decode(text)
        if extension == ".masterprefs":
            data["Locked"] = False

        itermediate_file = output_folder / f"{file_name}_intermediate.json"

        with open(itermediate_file, "w", encoding="utf-8") as json_out:
            json.dump(data, json_out, indent=4, sort_keys=False)

        parsed_file = output_folder / f"{file_name}_parsed{extension}"

        with open(parsed_file, "w", encoding="utf-8") as out:
            if extension == ".comp":
                print("Composition", file=out, end="")
            upd = flpp.encode(data)
            out.write(upd)


if __name__ == "__main__":
    parse_examples(FOLDER)
