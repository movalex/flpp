import unittest
from flpp import flpp


# Utility functions


def is_iterator(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def differ(value, origin):
    error_message = f"Value [{value}] does not match original: [{origin}]"

    if type(value) is not type(origin):
        raise AssertionError(
            "Types do not match: " f"{type(value)}, {type(origin)}"
        )

    if isinstance(origin, dict):
        for key, item in origin.items():
            try:
                differ(value[key], item)
            except KeyError:
                raise AssertionError(
                    f"{error_message}\nKey: {key}, item: {item}"
                )
        return

    if isinstance(origin, str):
        assert value == origin, error_message
        return

    if is_iterator(origin):
        for i in range(0, len(origin)):
            try:
                differ(value[i], origin[i])
            except IndexError:
                raise AssertionError(
                    f"{error_message}. Item {origin[i]} not found"
                )
        return

    assert value == origin, error_message


class TestUtilityFunctions(unittest.TestCase):
    def test_is_iterator(self):
        self.assertTrue(is_iterator(list()))
        self.assertFalse(is_iterator(int))

    def test_differ(self):
        # Same:
        differ(1, 1)
        differ([2, 3], [2, 3])
        differ({"1": 3, "4": "6"}, {"4": "6", "1": 3})
        differ("4", "4")

        # Different:
        self.assertRaises(AssertionError, differ, 1, 2)
        self.assertRaises(AssertionError, differ, [2, 3], [3, 2])
        self.assertRaises(
            AssertionError, differ, {"6": 4, "3": "1"}, {"4": "6", "1": 3}
        )
        self.assertRaises(AssertionError, differ, "4", "no")


class Testflpp(unittest.TestCase):
    def test_numbers(self):
        # Integer and float:
        self.assertEqual(flpp.decode("3"), 3)
        self.assertEqual(flpp.decode("4.1"), 4.1)
        self.assertEqual(flpp.encode(3), "3")
        self.assertEqual(flpp.encode(4.1), "4.1")

        # Negative float:
        self.assertEqual(flpp.decode("-0.45"), -0.45)
        self.assertEqual(flpp.encode(-0.45), "-0.45")

        # Scientific:
        self.assertEqual(flpp.decode("3e-7"), 3e-7)
        self.assertEqual(flpp.decode("-3.23e+17"), -3.23e17)
        self.assertEqual(flpp.encode(3e-7), "3e-07")
        self.assertEqual(flpp.encode(-3.23e17), "-3.23e+17")

        # Hex:
        self.assertEqual(flpp.decode("0x3a"), 0x3A)

        differ(
            flpp.decode(
                """{
            ID = 0x74fa4cae,
            Version = 0x07c2,
            Manufacturer = 0x21544948
        }"""
            ),
            {"ID": 0x74FA4CAE, "Version": 0x07C2, "Manufacturer": 0x21544948},
        )

    def test_bool(self):
        self.assertEqual(flpp.encode(True), "true")
        self.assertEqual(flpp.encode(False), "false")

        self.assertEqual(flpp.decode("true"), True)
        self.assertEqual(flpp.decode("false"), False)

    def test_nil(self):
        self.assertEqual(flpp.encode(None), "nil")
        self.assertEqual(flpp.decode("nil"), None)

    def test_table(self):
        # Bracketed string key:
        self.assertEqual(flpp.decode('{["10"] = 1}'), {"10": 1})

        # Values-only table:
        self.assertEqual(flpp.decode('{"10"}'), ["10"])

        # Last zero
        self.assertEqual(flpp.decode("{0, 1, 0}"), [0, 1, 0])

    def test_fusion_prefs(self):
        # named tables
        data = "{\n\tTools = ordered()\n\t{\n\t\tOCIOColorSpaceViewLUT3 = ViewOperator\n\t\t{\n\t\t\tNameSet = true\n\t\t}\n\t}\n}"
        self.assertEqual(flpp.encode(flpp.decode(data)), data)

        # exclamation values
        data = '{\n\t["!Left"] = {}\n}'
        self.assertEqual(flpp.encode(flpp.decode(data)), data)

        # key string starts with a number
        data = '{\n\t["3DHistogram"] = {}\n}'
        self.assertEqual(flpp.encode(flpp.decode(data)), data)

        # key is a bracketed number
        data = "{\n\tFloatView = {\n\t\t[1] = {\n\t\t\tTop = -1\n\t\t}\n\t}\n}"
        self.assertEqual(flpp.encode(flpp.decode(data)), data)

        # key is float [0.396758742692536254]
        data = "{\n\t[0.18476195900623] = {0.167478760189764}\n}"
        self.assertEqual(flpp.encode(flpp.decode(data)), data)

    def test_string(self):
        # Escape test:
        self.assertEqual(flpp.decode(r"'test\'s string'"), "test's string")

        # Strings inside double brackets
        longstr = ' ("word") . [ ["word"] . ["word"] . ("word" | "word" | "word" | "word") . ["word"] ] '
        self.assertEqual(flpp.decode("[[" + longstr + "]]"), longstr)
        self.assertEqual(
            flpp.decode("{ [0] = [[" + longstr + ']], [1] = "a"}'),
            {"[0]": longstr, "[1]": "a"},
        )

    def test_basic(self):
        # No data loss:
        data = '{ array = { 65, 23, 5 }, dict = { string = "value", array = { 3, 6, 4}, mixed = { 43, 54.3, false, string = "value", 9 } } }'
        d = flpp.decode(data)
        differ(d, flpp.decode(flpp.encode(d)))

    def test_unicode(self):
        self.assertEqual(flpp.encode("Привет"), '"Привет"')
        self.assertEqual(flpp.encode({"s": "Привет"}), '{\n\ts = "Привет"\n}')

    def test_consistency(self):
        def t(data):
            d = flpp.decode(data)
            self.assertEqual(d, flpp.decode(flpp.encode(d)))

        t(
            '{ 43, 54.3, false, string = "value", 9, [4] = 111, [1] = 222, [2.1] = "text" }'
        )
        t("{ 43, 54.3, false, 9, [5] = 111, [7] = 222 }")
        t("{ [7] = 111, [5] = 222, 43, 54.3, false, 9 }")
        t("{ 43, 54.3, false, 9, [4] = 111, [5] = 52.1 }")
        t("{ [5] = 111, [4] = 52.1, 43, [3] = 54.3, false, 9 }")
        t('{ [1] = 1, [2] = "2", 3, 4, [5] = 5 }')

    def test_comments(self):
        def t(data, res):
            self.assertEqual(flpp.decode(data), res)

        t(
            '-- starting comment\n{\n["multiline_string"] = "A multiline string where one of the lines starts with\n-- two dashes",\n-- middle comment\n["another_multiline_string"] = "A multiline string where one of the lines starts with\n-- two dashes\nfollowed by another line",\n["trailing_comment"] = "A string with" -- a trailing comment\n}\n-- ending comment',
            {
                "multiline_string": "A multiline string where one of the lines starts with\n-- two dashes",
                "another_multiline_string": "A multiline string where one of the lines starts with\n-- two dashes\nfollowed by another line",
                "trailing_comment": "A string with",
            },
        )
        t('"--3"', "--3")
        t(
            '{\n["string"] = "A text\n--[[with\ncomment]]\n",\n--[[\n["comented"] = "string\nnewline",\n]]}',
            {"string": "A text\n--[[with\ncomment]]\n"},
        )


if __name__ == "__main__":
    unittest.main()
