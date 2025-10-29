import unittest
import bruteforcing
import ebe
import malwaressti
import xxe_detectorv1
#import sqli <-- Download required frameworks through pip.

class TestingMethods(unittest.TestCase):

    def test1(xxe1):
        scans = xxe_detectorv1.scan("text.txt")
        xxe1.assertEqual(scans, {'severity': 'LOW', 'indicators': [], 'length': 8})

    def test2(xxe2):
        passes = xxe_detectorv1.safe_parse("text.txt")
        xxe2.assertEqual(passes, {'parsed': False, 'error': 'syntax error: line 1, column 0'})
    

if __name__ == "__main__":
    unittest.main()