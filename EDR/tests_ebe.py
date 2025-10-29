import unittest
import bruteforcing
import ebe
import malwaressti
import xxe_detectorv1
#import sqli <-- Download required frameworks through pip.

class TestingMethods(unittest.TestCase):

    def test1(ebe1):
        log = ebe.log_errors_to_file("file.txt", "error")
        ebe1.assertNotEqual(log, True)

    def test2(ebe2):
        mess = ebe.show_message("message")
        ebe2.assertNotEqual(mess, "Not message")

    
if __name__ == "__main__":
    unittest.main()