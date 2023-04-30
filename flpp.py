import re
import sys
from numbers import Number

"""
TODO:
* generate fusion tools registry for the NAMED_TABLES automatically
* do not parse floating number keys
"""

ERRORS = {
    "unexp_end_string": "Unexpected end of string while parsing Lua string.",
    "unexp_end_table": "Unexpected end of table while parsing Lua string.",
    "mfnumber_minus": "Malformed number (no digits after initial minus).",
    "mfnumber_dec_point": "Malformed number (no digits after decimal point).",
    "mfnumber_sci": "Malformed number (bad scientific format).",
}

NAMED_TABLES = (
    "ordered()",
    "ViewOperator",
    "Input",
    "FuID",
    "MultiView",
    # Fusion comp nodes
    "Blur",
    "BrightnessContrast",
    "Clip",
    "ColorCorrector",
    "ColorCurves",
    "CoordSpace",
    "Displace3D",
    "FastNoise",
    "Fuse.Grade",
    "Loader",
    "LUTBezier",
    "ImagePlane3D",
    "Note",
    "OperatorInfo",
    "SplineEditorView",
    "StickyNoteInfo",
    "TimelineView",
    "Transform",
    "ViewLUTOp",
)


class ParseError(Exception):
    pass


class FLPP:
    def __init__(self):
        self.text = ""
        self.ch = ""
        self.at = 0
        self.len = 0
        self.depth = 0
        self.space = re.compile("\s", re.M)
        self.newline = "\n"
        self.tab = "\t"
        self.named_table_pattern = self.build_escaped_regex(NAMED_TABLES)

    def build_escaped_regex(self, patterns: tuple):
        table_pattern = "|".join([re.escape(pattern) for pattern in patterns])
        return re.compile(f'"({table_pattern})"' + "\,(\n\t+\{)")

    def decode(self, text):
        if not text or not isinstance(text, str):
            return
        self.text = text
        self.at, self.ch, self.depth = 0, "", 0
        self.len = len(text)
        self.next_chr()
        result = self.item()
        return result

    def encode(self, obj):
        self.depth = 0
        return self._encode(obj)

    def _check_length(self, obj) -> bool:
        length_numbers = [
            x
            for x in obj
            if isinstance(x, Number) or (isinstance(x, str) and len(x) < 10)
        ]
        return len(length_numbers) == len(obj)

    def _build_keys(self, obj: dict):
        for key in obj.keys():
            if isinstance(key, int):
                yield key
            elif (
                isinstance(key, str)
                and ":" in key
                or re.search("^[0-9]|^!|\.", key)
            ):
                # parse bracketed keys, such as ["Gamut.SLogVersion"] or ["!Left"]
                yield f'["{key}"]'
            else:
                yield f"{key}"

    def _build_content(self, indent, key_list, obj):
        result = ""
        for (_, value), key in zip(obj.items(), key_list):
            try:
                int(key)
                # remove temporary numeric keys
                result = f"{indent}{self._encode(value)}"
            except ValueError:
                result = f"{indent}{key} = {self._encode(value)}"
            yield result

    def _encode(self, obj):
        s = ""
        # print(f"encoding: {obj}")
        tab = self.tab
        newline = self.newline

        if isinstance(obj, str):
            s += f'"{obj}"'
        elif isinstance(obj, bytes):
            s += '"{}"'.format("".join(r"\x{:02x}".format(c) for c in obj))
        elif isinstance(obj, bool):
            s += str(obj).lower()
        elif obj is None:
            s += "nil"
        elif isinstance(obj, Number):
            s += str(obj)
        elif isinstance(obj, (list, tuple, dict)):
            self.depth += 1
            if len(obj) == 0 or (
                not isinstance(obj, dict) and self._check_length(obj)
            ):
                newline = tab = ""
            indent = tab * self.depth
            s += "{%s" % newline
            if isinstance(obj, dict):
                key_list = self._build_keys(obj)
                contents = self._build_content(indent, key_list, obj)
                s += (f",{newline}").join(list(contents))
            else:
                s += (f",{newline}").join(
                    [indent + self._encode(element) for element in obj]
                )
            self.depth -= 1
            s += f"{newline}{tab * self.depth}" + "}"

        # remove commas from the named tables, like ordered(), MultiView etc.
        output = self.named_table_pattern.sub(r"\1\2", s)
        return output

    def white(self):
        while self.ch:
            if self.space.match(self.ch):
                self.next_chr()
            else:
                break
        self.comment()

    def comment(self):
        if self.ch == "-" and self.next_is("-"):
            self.next_chr()
            multiline = (
                self.next_chr() and self.ch == "[" and self.next_is("[")
            )
            while self.ch:
                if multiline:
                    if self.ch == "]" and self.next_is("]"):
                        self.next_chr()
                        self.next_chr()
                        self.white()
                        break
                # `--` is a comment, skip to next new line
                elif re.match("\n", self.ch):
                    self.white()
                    break
                self.next_chr()

    def next_is(self, value):
        if self.at >= self.len:
            return False
        return self.text[self.at] == value

    def prev_is(self, value: str):
        if self.at < 2:
            return False
        return self.text[self.at - 2] == value

    def next_chr(self):
        if self.at >= self.len:
            self.ch = None
            return None
        self.ch = self.text[self.at]
        self.at += 1
        return True

    def item(self):
        self.white()
        if not self.ch:
            return
        if self.ch == "{":
            return self.table_object()
        if self.ch == "[":
            self.next_chr()
        if self.ch in ['"', "'", "["]:
            return self.string(self.ch)
        if self.ch.isdigit() or self.ch == "-":
            # handle braketed key format in the FloatView settings
            if self.prev_is("["):
                return f"[{self.number()}]"
            return self.number()
        return self.word()

    def string(self, end=None):
        s = ""
        start = self.ch
        if end == "[":
            end = "]"
        if start in ['"', "'", "["]:
            double = start == "[" and self.prev_is(start)
            while self.next_chr():
                if self.ch == end and (not double or self.next_is(end)):
                    self.next_chr()
                    if start != "[" or self.ch == "]":
                        if double:
                            self.next_chr()
                        return s
                if self.ch == "\\" and start == end:
                    self.next_chr()
                    if self.ch != end:
                        s += "\\"
                s += self.ch
        raise ParseError(ERRORS["unexp_end_string"])

    @staticmethod
    def table_object_keys(table_object):
        return [
            key
            for key in table_object
            if isinstance(key, (str, float, bool, tuple))
        ]

    def _empty_keys_to_list(self, table_object: dict):
        empty_keys_values = []
        for key in table_object:
            empty_keys_values.insert(key, table_object[key])
        return empty_keys_values

    def table_object(self):
        output = {}
        key = None
        idx = 0
        self.depth += 1
        self.next_chr()
        self.white()
        if self.ch and self.ch == "}":
            self.depth -= 1
            self.next_chr()
            return output
        else:
            while self.ch:
                self.white()
                if self.ch == "{":
                    output[idx] = self.table_object()
                    idx += 1
                    continue
                elif self.ch == "}":
                    self.depth -= 1
                    self.next_chr()
                    if key is not None:  # see last zero test
                        output[idx] = key
                    # fix Loader clip parsing
                    if output.get(1) == "Clip":
                        output = {0: "Clip", 1: output[0]}
                    elif len(self.table_object_keys(output)) == 0:
                        output = self._empty_keys_to_list(output)
                    return output
                else:
                    if self.ch == ",":
                        self.next_chr()
                        continue
                    else:
                        key = self.item()
                        if self.ch == "]":
                            self.next_chr()
                    self.white()
                    ch = self.ch
                    if ch in ("=", ","):
                        self.next_chr()
                        self.white()
                        if ch == "=":
                            output[key] = self.item()
                        else:
                            output[idx] = key
                        idx += 1
                        key = None
        raise ParseError(ERRORS["unexp_end_table"])

    bool_words = {"true": True, "false": False, "nil": None}

    def word(self):
        result_string = ""
        if self.ch != "\n":
            result_string = self.ch
        self.next_chr()
        while (
            self.ch is not None
            and (self.ch.isalnum() or self.ch in ("(", ")", "_", "."))
            and not result_string in self.bool_words
        ):
            result_string += self.ch
            self.next_chr()
        return self.bool_words.get(result_string, result_string)

    def number(self):
        def next_digit(err):
            n = self.ch
            self.next_chr()
            if not self.ch or not self.ch.isdigit():
                raise ParseError(err)
            return n

        num = ""
        try:
            if self.ch == "-":
                num += next_digit(ERRORS["mfnumber_minus"])
            num += self.digit()
            if num == "0" and self.ch in ["x", "X"]:
                num += self.ch
                self.next_chr()
                num += self.hex()
            else:
                if self.ch and self.ch == ".":
                    num += next_digit(ERRORS["mfnumber_dec_point"])
                    num += self.digit()
                if self.ch and self.ch in ["e", "E"]:
                    num += self.ch
                    self.next_chr()
                    if not self.ch or self.ch not in ("+", "-"):
                        raise ParseError(ERRORS["mfnumber_sci"])
                    num += next_digit(ERRORS["mfnumber_sci"])
                    num += self.digit()
        except ParseError:
            t, e = sys.exc_info()[:2]
            print(e)
            return 0
        try:
            return int(num, 0)
        except:
            pass
        return float(num)

    def digit(self):
        num = ""
        while self.ch and self.ch.isdigit():
            num += self.ch
            self.next_chr()
        return num

    def hex(self):
        num = ""
        while self.ch and (self.ch in "ABCDEFabcdef" or self.ch.isdigit()):
            num += self.ch
            self.next_chr()
        return num


flpp = FLPP()

__all__ = ["flpp"]
