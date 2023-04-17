import unittest

from flpp import flpp

"""
Tests for flpp
"""


# Utility functions


def is_iterator(obj):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def differ(value, origin):
    if type(value) is not type(origin):
        raise AssertionError("Types does not match: "
                             f"{type(value)}, {type(origin)}")

    if isinstance(origin, dict):
        for key, item in origin.items():
            try:
                differ(value[key], item)
            except KeyError:
                raise AssertionError(
                    f"{value} not match original: {origin}; "
                    f"Key: {key}, item: {item}"
                )
        return

    if isinstance(origin, str):
        assert value == origin, f"{value} not match original: {origin}."
        return

    if is_iterator(origin):
        for i in range(0, len(origin)):
            try:
                differ(value[i], origin[i])
            except IndexError:
                raise AssertionError(
                    f"{value} not match original: {origin}. Item {origin[i]} not found"
                )
        return

    assert value == origin, "{0} not match original: {1}.".format(value, origin)


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

        # Fusion preferences table
        data = '{\n\tSubFrame = {\n\t\t{\n\t\t\tZoneInfo = {\n\t\t\t\tAuxRight = {\n\t\t\t\t\tExpanded = true\n\t\t\t\t},\n\t\t\t\t["!Left"] = {},\n\t\t\t\tAuxLeft = {\n\t\t\t\t\tExpanded = true\n\t\t\t\t},\n\t\t\t\tRight = {\n\t\t\t\t\tExpanded = true,\n\t\t\t\t\tAdjust = false\n\t\t\t\t},\n\t\t\t\tLeft = {\n\t\t\t\t\tExpanded = false\n\t\t\t\t},\n\t\t\t\t["!Right"] = {}\n\t\t\t},\n\t\t\tUseWindowsDefaults = false,\n\t\t\tWidth = 1920,\n\t\t\tLayout = {\n\t\t\t\t{\n\t\t\t\t\tID = "LayoutStrip",\n\t\t\t\t\tFixedY = 36,\n\t\t\t\t\tRatioX = 1,\n\t\t\t\t\tFlat = true\n\t\t\t\t},\n\t\t\t\t{\n\t\t\t\t\t{\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\t\tID = "Viewer1",\n\t\t\t\t\t\t\t\t\tRatioY = 1,\n\t\t\t\t\t\t\t\t\tRatioX = 0.5\n\t\t\t\t\t\t\t\t},\n\t\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\t\tID = "Viewer2",\n\t\t\t\t\t\t\t\t\tRatioX = 0.5\n\t\t\t\t\t\t\t\t},\n\t\t\t\t\t\t\t\tRatioX = 1,\n\t\t\t\t\t\t\t\tRatioY = 1,\n\t\t\t\t\t\t\t\tColumns = 2\n\t\t\t\t\t\t\t},\n\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\tID = "Time",\n\t\t\t\t\t\t\t\tFixedY = 83,\n\t\t\t\t\t\t\t\tFlat = true\n\t\t\t\t\t\t\t},\n\t\t\t\t\t\t\tRatioX = 1,\n\t\t\t\t\t\t\tRows = 2,\n\t\t\t\t\t\t\tRatioY = 100\n\t\t\t\t\t\t},\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\tID = "Nodes",\n\t\t\t\t\t\t\tRatioY = 0.999008919722497,\n\t\t\t\t\t\t\tRatioX = 1\n\t\t\t\t\t\t},\n\t\t\t\t\t\tRatioX = 1,\n\t\t\t\t\t\tRows = 2,\n\t\t\t\t\t\tRatioY = 100\n\t\t\t\t\t},\n\t\t\t\t\t{\n\t\t\t\t\t\tID = "Inspector",\n\t\t\t\t\t\tRatioY = 1,\n\t\t\t\t\t\tRatioX = 1\n\t\t\t\t\t},\n\t\t\t\t\tColumns = 2,\n\t\t\t\t\tRatioY = 1\n\t\t\t\t},\n\t\t\t\tRatioX = 1,\n\t\t\t\tRows = 2,\n\t\t\t\tRatioY = 1\n\t\t\t},\n\t\t\tLeft = 0,\n\t\t\tOpenOnNew = true,\n\t\t\tTop = 27,\n\t\t\tFrameTypeID = "ChildFrame",\n\t\t\tViewInfo = {\n\t\t\t\tViewer1 = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tRatioY = 1,\n\t\t\t\t\tRatioX = 0.5\n\t\t\t\t},\n\t\t\t\tInnerLeft = {},\n\t\t\t\tMainSplit = {\n\t\t\t\t\tRatioX = 100,\n\t\t\t\t\tRatioY = 0.999008919722498\n\t\t\t\t},\n\t\t\t\tCenterSplit = {\n\t\t\t\t\tRatioX = 1,\n\t\t\t\t\tRatioY = 100\n\t\t\t\t},\n\t\t\t\tViewer2 = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tAdjust = false,\n\t\t\t\t\tRatioY = 1,\n\t\t\t\t\tMRU = 1,\n\t\t\t\t\tRatioX = 0.5\n\t\t\t\t},\n\t\t\t\tComments = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tTime = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tPixelY = 83,\n\t\t\t\t\tAdjust = false,\n\t\t\t\t\tMRU = 1,\n\t\t\t\t\tRatioX = 1\n\t\t\t\t},\n\t\t\t\tInnerColumns = {\n\t\t\t\t\tRatioX = 100,\n\t\t\t\t\tRatioY = 2.0009910802775\n\t\t\t\t},\n\t\t\t\tKeyframes = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tLayoutStrip = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tRatioX = 1\n\t\t\t\t},\n\t\t\t\tInspector = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tRatioY = 1,\n\t\t\t\t\tRatioX = 1,\n\t\t\t\t\tPixelX = 420\n\t\t\t\t},\n\t\t\t\tMediaPool = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tClips = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tOuterColumns = {\n\t\t\t\t\tRatioX = 1,\n\t\t\t\t\tRatioY = 1\n\t\t\t\t},\n\t\t\t\tMetadata = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tActionStrip = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tEffects = {\n\t\t\t\t\tShow = false\n\t\t\t\t},\n\t\t\t\tOuterLeft = {},\n\t\t\t\tViewerSplit = {\n\t\t\t\t\tRatioX = 1,\n\t\t\t\t\tRatioY = 1\n\t\t\t\t},\n\t\t\t\tNodes = {\n\t\t\t\t\tShow = true,\n\t\t\t\t\tRatioY = 0.999008919722497,\n\t\t\t\t\tRatioX = 1\n\t\t\t\t},\n\t\t\t\tOuterRight = {\n\t\t\t\t\tPixelX = 420,\n\t\t\t\t\tRatioY = 100\n\t\t\t\t},\n\t\t\t\tInnerRight = {},\n\t\t\t\tSpline = {\n\t\t\t\t\tShow = false\n\t\t\t\t}\n\t\t\t},\n\t\t\tViews = ordered()\n\t\t\t{\n\t\t\t\tEffects = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tEffectView = "EffectView"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "EffectView"\n\t\t\t\t},\n\t\t\t\tNodes = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tFlowView = "FlowView"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "FlowView",\n\t\t\t\t\tNames = {\n\t\t\t\t\t\tFlowView = "FlowView"\n\t\t\t\t\t}\n\t\t\t\t},\n\t\t\t\tKeyframes = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tTimelineView = "TimelineView"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "TimelineView",\n\t\t\t\t\tNames = {\n\t\t\t\t\t\tTimelineView = "TimelineView"\n\t\t\t\t\t}\n\t\t\t\t},\n\t\t\t\tSpline = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tSplineView = "SplineEditorView"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "SplineView",\n\t\t\t\t\tNames = {\n\t\t\t\t\t\tSplineView = "SplineView"\n\t\t\t\t\t}\n\t\t\t\t},\n\t\t\t\tInspector = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tTools = "ControlView",\n\t\t\t\t\t\tModifiers = "ModifierView"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "Tools"\n\t\t\t\t},\n\t\t\t\tViewer1 = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tLeftView = "PreviewContainer"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "LeftView",\n\t\t\t\t\tNames = {\n\t\t\t\t\t\tLeftView = "LeftView"\n\t\t\t\t\t}\n\t\t\t\t},\n\t\t\t\tViewer2 = MultiView\n\t\t\t\t{\n\t\t\t\t\tViewList = ordered()\n\t\t\t\t\t{\n\t\t\t\t\t\tRightView = "PreviewContainer"\n\t\t\t\t\t},\n\t\t\t\t\tActive = "RightView",\n\t\t\t\t\tNames = {\n\t\t\t\t\t\tRightView = "RightView"\n\t\t\t\t\t}\n\t\t\t\t},\n\t\t\t\tTime = "TimeView",\n\t\t\t\tActionStrip = "ActionStripView",\n\t\t\t\tLayoutStrip = "LayoutStripView"\n\t\t\t},\n\t\t\tHeight = 1049,\n\t\t\tMode = 3,\n\t\t\tLayoutPreset = 0,\n\t\t\tPresetName = "Default"\n\t\t}\n\t},\n\tChildFrame = {}\n}'

        expected_result = {
            "SubFrame": {
                0: {
                    "ZoneInfo": {
                        "AuxRight": {"Expanded": True},
                        "!Left": {},
                        "AuxLeft": {"Expanded": True},
                        "Right": {"Expanded": True, "Adjust": False},
                        "Left": {"Expanded": False},
                        "!Right": {},
                    },
                    "UseWindowsDefaults": False,
                    "Width": 1920,
                    "Layout": {
                        0: {
                            "ID": "LayoutStrip",
                            "FixedY": 36,
                            "RatioX": 1,
                            "Flat": True,
                        },
                        1: {
                            0: {
                                0: {
                                    0: {
                                        0: {
                                            "ID": "Viewer1",
                                            "RatioY": 1,
                                            "RatioX": 0.5,
                                        },
                                        1: {"ID": "Viewer2", "RatioX": 0.5},
                                        "RatioX": 1,
                                        "RatioY": 1,
                                        "Columns": 2,
                                    },
                                    1: {"ID": "Time", "FixedY": 83, "Flat": True},
                                    "RatioX": 1,
                                    "Rows": 2,
                                    "RatioY": 100,
                                },
                                1: {
                                    "ID": "Nodes",
                                    "RatioY": 0.999008919722497,
                                    "RatioX": 1,
                                },
                                "RatioX": 1,
                                "Rows": 2,
                                "RatioY": 100,
                            },
                            1: {"ID": "Inspector", "RatioY": 1, "RatioX": 1},
                            "Columns": 2,
                            "RatioY": 1,
                        },
                        "RatioX": 1,
                        "Rows": 2,
                        "RatioY": 1,
                    },
                    "Left": 0,
                    "OpenOnNew": True,
                    "Top": 27,
                    "FrameTypeID": "ChildFrame",
                    "ViewInfo": {
                        "Viewer1": {"Show": True, "RatioY": 1, "RatioX": 0.5},
                        "InnerLeft": {},
                        "MainSplit": {"RatioX": 100, "RatioY": 0.999008919722498},
                        "CenterSplit": {"RatioX": 1, "RatioY": 100},
                        "Viewer2": {
                            "Show": True,
                            "Adjust": False,
                            "RatioY": 1,
                            "MRU": 1,
                            "RatioX": 0.5,
                        },
                        "Comments": {"Show": False},
                        "Time": {
                            "Show": True,
                            "PixelY": 83,
                            "Adjust": False,
                            "MRU": 1,
                            "RatioX": 1,
                        },
                        "InnerColumns": {"RatioX": 100, "RatioY": 2.0009910802775},
                        "Keyframes": {"Show": False},
                        "LayoutStrip": {"Show": True, "RatioX": 1},
                        "Inspector": {
                            "Show": True,
                            "RatioY": 1,
                            "RatioX": 1,
                            "PixelX": 420,
                        },
                        "MediaPool": {"Show": False},
                        "Clips": {"Show": False},
                        "OuterColumns": {"RatioX": 1, "RatioY": 1},
                        "Metadata": {"Show": False},
                        "ActionStrip": {"Show": False},
                        "Effects": {"Show": False},
                        "OuterLeft": {},
                        "ViewerSplit": {"RatioX": 1, "RatioY": 1},
                        "Nodes": {
                            "Show": True,
                            "RatioY": 0.999008919722497,
                            "RatioX": 1,
                        },
                        "OuterRight": {"PixelX": 420, "RatioY": 100},
                        "InnerRight": {},
                        "Spline": {"Show": False},
                    },
                    "Views": "ordered()",
                    10: {
                        "Effects": "MultiView",
                        1: {
                            "ViewList": "ordered()",
                            1: {"EffectView": "EffectView"},
                            "Active": "EffectView",
                        },
                        "Nodes": "MultiView",
                        3: {
                            "ViewList": "ordered()",
                            1: {"FlowView": "FlowView"},
                            "Active": "FlowView",
                            "Names": {"FlowView": "FlowView"},
                        },
                        "Keyframes": "MultiView",
                        5: {
                            "ViewList": "ordered()",
                            1: {"TimelineView": "TimelineView"},
                            "Active": "TimelineView",
                            "Names": {"TimelineView": "TimelineView"},
                        },
                        "Spline": "MultiView",
                        7: {
                            "ViewList": "ordered()",
                            1: {"SplineView": "SplineEditorView"},
                            "Active": "SplineView",
                            "Names": {"SplineView": "SplineView"},
                        },
                        "Inspector": "MultiView",
                        9: {
                            "ViewList": "ordered()",
                            1: {"Tools": "ControlView", "Modifiers": "ModifierView"},
                            "Active": "Tools",
                        },
                        "Viewer1": "MultiView",
                        11: {
                            "ViewList": "ordered()",
                            1: {"LeftView": "PreviewContainer"},
                            "Active": "LeftView",
                            "Names": {"LeftView": "LeftView"},
                        },
                        "Viewer2": "MultiView",
                        13: {
                            "ViewList": "ordered()",
                            1: {"RightView": "PreviewContainer"},
                            "Active": "RightView",
                            "Names": {"RightView": "RightView"},
                        },
                        "Time": "TimeView",
                        "ActionStrip": "ActionStripView",
                        "LayoutStrip": "LayoutStripView",
                    },
                    "Height": 1049,
                    "Mode": 3,
                    "LayoutPreset": 0,
                    "PresetName": "Default",
                }
            },
            "ChildFrame": {},
        }

        self.assertEqual(flpp.encode(expected_result), data)

    def test_string(self):
        # Escape test:
        self.assertEqual(flpp.decode(r"'test\'s string'"), "test's string")

        # Add escaping on encode:
        self.assertEqual(
            flpp.encode({"a": 'func("call()");'}), '{\n\ta = "func(\\"call()\\");"\n}'
        )

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
