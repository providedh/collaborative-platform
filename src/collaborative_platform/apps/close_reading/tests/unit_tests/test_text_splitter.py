import pytest

from apps.close_reading.text_splitter import TextSplitter


class TestTextSplitter:
    def test_split_text_to_parts(self):
        text_to_split = "text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text"
        expected = ['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ',
                    '</tag_1>', ' text']

        result = TextSplitter().split(text_to_split)

        assert result == expected

    test_parameters_names = "parts, expected"
    test_parameters_list = [
        (['text '],
         ["text "]),
        (['text ', '<tag_1>'],
         ["text ", "<tag_1>"]),
        (['text ', '<tag_1>', ' text '],
         ["text ", "<tag_1>", " text "]),
        (['text ', '<tag_1>', ' text ', '<tag_2>'],
         ["text ", "<tag_1>", " text ", "<tag_2>"]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text '],
         ["text ", "<tag_1>", " text ", "<tag_2>", " text "]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>'],
         ["text ", "<tag_1>", " text ", "<tag_2>", " text <tag_3/>"]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text '],
         ["text ", "<tag_1>", " text ", "<tag_2>", " text <tag_3/> text "]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>'],
         ["text ", "<tag_1>", " text <tag_2> text <tag_3/> text </tag_2>"]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text '],
         ["text ", "<tag_1>", " text <tag_2> text <tag_3/> text </tag_2> text "]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>'],
         ["text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1>"]),
        (['text ', '<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>',
          ' text'], ["text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text"]),
        (['<tag_1>', ' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         ["<tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text"]),
        ([' text ', '<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         [" text <tag_2> text <tag_3/> text </tag_2> text ", "</tag_1>", " text"]),
        (['<tag_2>', ' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         ["<tag_2> text <tag_3/> text </tag_2> text ", "</tag_1>", " text"]),
        ([' text ', '<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         [" text <tag_3/> text ", "</tag_2>", " text ", "</tag_1>", " text"]),
        (['<tag_3/>', ' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         ["<tag_3/> text ", "</tag_2>", " text ", "</tag_1>", " text"]),
        ([' text ', '</tag_2>', ' text ', '</tag_1>', ' text'],
         [" text ", "</tag_2>", " text ", "</tag_1>", " text"]),
        (['</tag_2>', ' text ', '</tag_1>', ' text'],
         ["</tag_2>", " text ", "</tag_1>", " text"]),
        ([' text ', '</tag_1>', ' text'],
         [" text ", "</tag_1>", " text"]),
        (['</tag_1>', ' text'],
         ["</tag_1>", " text"]),
        ([' text'],
         [" text"]),
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_join_parts(self, parts, expected):
        result = TextSplitter().join(parts)

        assert result == expected

    test_parameters_names = "text, expected"
    test_parameters_list = [
        ("text ", True),
        ("text <tag_1>", False),
        ("text <tag_1> text ", False),
        ("text <tag_1> text <tag_2>", False),
        ("text <tag_1> text <tag_2> text ", False),
        ("text <tag_1> text <tag_2> text <tag_3/>", False),
        ("text <tag_1> text <tag_2> text <tag_3/> text ", False),
        ("text <tag_1> text <tag_2> text <tag_3/> text </tag_2>", False),
        ("text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text ", False),
        ("text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1>", True),
        ("text <tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text", True),
        ("<tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text", True),
        (" text <tag_2> text <tag_3/> text </tag_2> text </tag_1> text", False),
        ("<tag_2> text <tag_3/> text </tag_2> text </tag_1> text", False),
        (" text <tag_3/> text </tag_2> text </tag_1> text", False),
        ("<tag_3/> text </tag_2> text </tag_1> text", False),
        (" text </tag_2> text </tag_1> text", False),
        ("</tag_2> text </tag_1> text", False),
        (" text </tag_1> text", False),
        ("</tag_1> text", False),
        (" text", True),
        ("<tag_1> text <tag_2> text <tag_3/> text </tag_2> text </tag_1>", True),
        (" text <tag_2> text <tag_3/> text </tag_2> text </tag_1>", False),
        (" text <tag_2> text <tag_3/> text </tag_2> text ", True),
        ("<tag_2> text <tag_3/> text </tag_2> text ", True),
        ("<tag_2> text <tag_3/> text </tag_2>", True),
        (" text <tag_3/> text </tag_2>", False),
        (" text <tag_3/> text ", True),
        ("<tag_3/> text ", True),
        ("<tag_3/>", True),
    ]

    @pytest.mark.parametrize(test_parameters_names, test_parameters_list)
    def test_is_autonomic_part(self, text, expected):
        result = TextSplitter().is_autonomic_part(text)

        assert result == expected
