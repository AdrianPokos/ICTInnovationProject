import unittest
import bruteforcing
import ebe
import malwaressti
import xxe_detectorv1
#import sqli <-- Download required frameworks through pip.

class TestingMethods(unittest.TestCase):

    def test1(brute1):
        count = bruteforcing.is_ip_blocked(0)
        brute1.assertEqual(count, 0)

    def test2(brute2):
        user = bruteforcing.is_user_locked("username")
        brute2.assertEqual(user, False)

    def test3(brute3):
        count = bruteforcing.record_failed_attempt(0, "username")
        brute3.assertEqual(count, (1, 1))

    def test4(brute4):
        user = bruteforcing.lock_user("username")
        brute4.assertNotEqual(user, "username", 10)

    def test5(brute5):
        verify = bruteforcing.verify_credentials("username", "password")
        brute5.assertNotEqual(verify, "password")

    def test6(brute6):
        verify = bruteforcing.simulate_login_attempt(0, "username", "password", True)
        brute6.assertNotEqual(verify, "too many requests from this IP, try later")


if __name__ == "__main__":
    unittest.main()