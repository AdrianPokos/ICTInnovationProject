import unittest
import bruteforcing
import ebe
import malwaressti
import xxe_detectorv1
#import sqli <-- Download required frameworks through pip.

class TestingMethods(unittest.TestCase):

    def test1(ssti1):
        paths = malwaressti.scan_directory("bad_path")
        ssti1.assertNotEqual(paths, "bad_path")

    def test2(ssti2):
        detect = malwaressti.detect_and_remove_suspicious_files("bad_path")
        ssti2.assertNotEqual(detect, "bad_path")


if __name__ == "__main__":
    unittest.main()