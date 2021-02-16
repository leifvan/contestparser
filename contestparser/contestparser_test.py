import unittest
from typing import NamedTuple, List
from contestparser import LinearParser, ParseList


class TestParseList(unittest.TestCase):

    def test_fixed_length(self):
        text = ("3\n"
                "a b c\n"
                "d e f\n"
                "g h i\n")
        lines = [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']]
        parser = LinearParser.from_string(text)

        class Line(NamedTuple):
            items: List[str] = ParseList(fixed_length=3)

        class Doc(NamedTuple):
            num_lines: int
            lines: List[Line] = ParseList(length_parameter='num_lines')

        doc = parser.parse(Doc)
        self.assertEqual(doc.num_lines, 3)
        for doc_line, true_line in zip(doc.lines, lines):
            self.assertListEqual(doc_line.items, true_line)

    def test_length_parameter(self):
        text = ("3\n"
                "5 a b c d e\n"
                "2 a b\n"
                "6 a b c d e f\n")
        lines = [['a', 'b', 'c', 'd', 'e'], ['a', 'b'], ['a', 'b', 'c', 'd', 'e', 'f']]
        parser = LinearParser.from_string(text)

        class Line(NamedTuple):
            length: int
            items: List[str] = ParseList(length_parameter='length')

        class Doc(NamedTuple):
            num_lines: int
            lines: List[Line] = ParseList(length_parameter='num_lines')

        doc = parser.parse(Doc)
        self.assertEqual(doc.num_lines, 3)
        for doc_line, true_line in zip(doc.lines, lines):
            self.assertEqual(doc_line.length, len(true_line))
            self.assertListEqual(doc_line.items, true_line)

    def test_length_callable(self):
        text = ("3\n"
                "a b c\n"
                "d\n"
                "e f g h\n")
        lines = [['a', 'b', 'c'], ['d'], ['e', 'f', 'g', 'h']]
        length_iter = iter(len(l) for l in lines)
        parser = LinearParser.from_string(text)

        class Line(NamedTuple):
            items: List[str] = ParseList(length_callable=lambda: next(length_iter))

        class Doc(NamedTuple):
            num_lines: int
            lines: List[Line] = ParseList(length_parameter='num_lines')

        doc = parser.parse(Doc)
        self.assertEqual(doc.num_lines, 3)
        for doc_line, true_line in zip(doc.lines, lines):
            self.assertListEqual(doc_line.items, true_line)


class TestParserOnReplyChallenge(unittest.TestCase):
    def test_first_adventure(self):

        with open('testdata/first_adventure.in') as file:
            parser = LinearParser.from_file(file)

            class Counts(NamedTuple):
                num_providers: int
                num_services: int
                num_countries: int
                num_projects: int

            counts = parser.parse(Counts)
            parser.assert_linebreak()
            service_names = parser.parse_n(str, counts.num_services)
            parser.assert_linebreak()
            countries = parser.parse_n(str, counts.num_countries)
            parser.assert_linebreak()

            class Region(NamedTuple):
                name: str
                num_packages: int
                package_cost: float
                number_of_units: List[int] = ParseList(fixed_length=counts.num_services)
                latencies: List[int] = ParseList(fixed_length=counts.num_countries)

            class Provider(NamedTuple):
                name: str
                num_regions: int
                regions: List[Region] = ParseList(length_parameter='num_regions')

            providers = parser.parse_n(Provider, counts.num_providers)
            parser.assert_linebreak()

            class Project(NamedTuple):
                penalty: int
                country: str
                units_needed: List[int] = ParseList(fixed_length=counts.num_services)

            projects = parser.parse_n(Project, counts.num_projects)
            parser.assert_finished()


if __name__ == '__main__':
    unittest.main()
