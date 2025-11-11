import unittest
from src.trivial_tools import add, sub


class TestCalc(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)

    def test_sub(self):
        self.assertEqual(sub(1, 2), 3)


if __name__ == '__main__':
    unittest.main()
