
from unittest import TestCase

# from grep import grep, parse_args
import grep

lst = []


def save_to_list(line):
    lst.append(line)

# вместо grep.output
grep.output = save_to_list


class GrepBaseTest(TestCase):

    lines = ['baab', 'bbb', 'ccc', 'A']

    def tearDown(self):
        global lst
        lst.clear()

    def test_base_scenario(self):
        print("test_base_scenario-01")
        params = grep.parse_args(['aa'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab'])

    def test_base_scenario_multi(self):
        print("test_base_scenario_multi")
        params = grep.parse_args(['b'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'bbb'])

    def test_base_scenario_count(self):
        print("test_base_scenario_count")
        params = grep.parse_args(['-c', 'a'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['1'])

    def test_base_scenario_invert(self):
        print("test_base_scenario_invert")
        params = grep.parse_args(['-v', 'b'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['ccc', 'A'])

    def test_base_scenario_case(self):
        print("test_base_scenario_case")
        params = grep.parse_args(['-i', 'a'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'A'])


class GrepPatternTest(TestCase):

    lines = ['baab', 'abbb', 'fc', 'AA']

    def tearDown(self):
        global lst
        lst.clear()

    def test_question_base(self):
        print("test_question_base")
        params = grep.parse_args(['?b'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'abbb'])

    def test_question_start(self):
        print("test_question_start")
        params = grep.parse_args(['?a'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab'])

    def test_queston_end(self):
        print("test_queston_end")
        params = grep.parse_args(['c?'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, [])

    def test_queston_double(self):
        print("test_queston_double")
        params = grep.parse_args(['b??b'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab'])

    def test_queston_count(self):
        print("test_queston_count")
        params = grep.parse_args(['???'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'abbb'])

    def test_asterics(self):
        print("test_asterics")
        params = grep.parse_args(['b*b'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'abbb'])

    def test_asterics_all(self):
        print("test_asterics_all")
        params = grep.parse_args(['***'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, self.lines)

class GrepContextTest(TestCase):

    lines = ['vr','baab', 'abbb', 'fc', 'bbb', 'cc']

    def tearDown(self):
        global lst
        lst.clear()

    def test_context_base(self):
        print("test_context_base")
        params = grep.parse_args(['-C1','aa'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['vr', 'baab', 'abbb'])

    def test_context_intersection(self):
        print("test_context_intersection")
        params = grep.parse_args(['-C1','ab'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['vr', 'baab', 'abbb', 'fc'])

    def test_context_intersection_hard(self):
        print("test_context_intersection_hard")
        params = grep.parse_args(['-C2','bbb'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, self.lines)

    def test_before(self):
        print("test_before")
        params = grep.parse_args(['-B1','bbb'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['baab', 'abbb', 'fc', 'bbb'])

    def test_after(self):
        print("test_after")
        params = grep.parse_args(['-A1','bbb'])
        grep.grep(self.lines, params)
        self.assertEqual(lst, ['abbb', 'fc', 'bbb', 'cc'])

