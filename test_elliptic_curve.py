"""
Tests for Elliptic Curve Cryptography implementation.
"""

import unittest
from elliptic_curve import (
    Point, EllipticCurve, ECDH, ECDSA, CURVES, CurveParameters
)


class TestPoint(unittest.TestCase):
    """Test Point operations on elliptic curves."""

    def setUp(self):
        """Set up test curve and points."""
        self.curve_params = CURVES['secp256k1']
        self.curve = EllipticCurve('secp256k1')

    def test_point_at_infinity(self):
        """Test point at infinity (identity element)."""
        infinity = Point(self.curve_params)
        self.assertTrue(infinity.is_at_infinity())

    def test_point_on_curve(self):
        """Test that generator point is on curve."""
        G = Point(self.curve_params, *self.curve_params.G)
        self.assertFalse(G.is_at_infinity())
        self.assertTrue(G._is_on_curve())

    def test_invalid_point(self):
        """Test that invalid point raises ValueError."""
        with self.assertRaises(ValueError):
            Point(self.curve_params, 1, 1)  # Not on curve

    def test_point_addition_identity(self):
        """Test that P + 0 = P (identity element)."""
        G = Point(self.curve_params, *self.curve_params.G)
        infinity = Point(self.curve_params)

        result1 = G + infinity
        result2 = infinity + G

        self.assertEqual(result1, G)
        self.assertEqual(result2, G)

    def test_point_doubling(self):
        """Test point doubling (P + P = 2P)."""
        G = Point(self.curve_params, *self.curve_params.G)

        # Double the generator
        doubled = G + G

        # Should equal 2 * G
        self.assertEqual(doubled, 2 * G)
        self.assertFalse(doubled.is_at_infinity())

    def test_point_inverse(self):
        """Test that P + (-P) = 0 (point at infinity)."""
        G = Point(self.curve_params, *self.curve_params.G)

        # Create inverse point (same x, negated y)
        neg_G = Point(self.curve_params, G.x, (-G.y) % self.curve_params.p)

        result = G + neg_G
        self.assertTrue(result.is_at_infinity())

    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        G = Point(self.curve_params, *self.curve_params.G)

        # Test various scalars
        result1 = 1 * G
        self.assertEqual(result1, G)

        result0 = 0 * G
        self.assertTrue(result0.is_at_infinity())

        # Test that n * G = 0 (G has order n)
        n = self.curve_params.n
        result_n = n * G
        self.assertTrue(result_n.is_at_infinity())

    def test_scalar_multiplication_associativity(self):
        """Test that (a + b) * G = a * G + b * G."""
        G = Point(self.curve_params, *self.curve_params.G)

        a = 123
        b = 456

        result1 = (a + b) * G
        result2 = a * G + b * G

        self.assertEqual(result1, result2)

    def test_scalar_multiplication_commutativity(self):
        """Test that a * (b * G) = b * (a * G) = (a * b) * G."""
        G = Point(self.curve_params, *self.curve_params.G)

        a = 17
        b = 29

        result1 = a * (b * G)
        result2 = b * (a * G)
        result3 = (a * b) * G

        self.assertEqual(result1, result2)
        self.assertEqual(result2, result3)


class TestEllipticCurve(unittest.TestCase):
    """Test EllipticCurve class."""

    def test_curve_initialization_secp256k1(self):
        """Test initialization with secp256k1."""
        curve = EllipticCurve('secp256k1')
        self.assertEqual(curve.name, 'secp256k1')
        self.assertFalse(curve.G.is_at_infinity())

    def test_curve_initialization_p256(self):
        """Test initialization with P-256."""
        curve = EllipticCurve('P-256')
        self.assertEqual(curve.name, 'P-256')
        self.assertFalse(curve.G.is_at_infinity())

    def test_invalid_curve_name(self):
        """Test that invalid curve name raises ValueError."""
        with self.assertRaises(ValueError):
            EllipticCurve('invalid-curve')

    def test_private_key_generation(self):
        """Test private key generation."""
        curve = EllipticCurve('secp256k1')

        # Generate multiple keys
        keys = [curve.generate_private_key() for _ in range(10)]

        # All should be in valid range
        for key in keys:
            self.assertGreater(key, 0)
            self.assertLess(key, curve.params.n)

        # Should be random (unlikely to get duplicates)
        self.assertEqual(len(set(keys)), len(keys))

    def test_public_key_derivation(self):
        """Test public key derivation from private key."""
        curve = EllipticCurve('secp256k1')

        private_key = 12345
        public_key = curve.get_public_key(private_key)

        # Public key should be on the curve
        self.assertTrue(public_key._is_on_curve())
        self.assertFalse(public_key.is_at_infinity())

        # Should equal private_key * G
        expected = private_key * curve.G
        self.assertEqual(public_key, expected)

    def test_invalid_private_key(self):
        """Test that invalid private key raises ValueError."""
        curve = EllipticCurve('secp256k1')

        with self.assertRaises(ValueError):
            curve.get_public_key(0)  # Too small

        with self.assertRaises(ValueError):
            curve.get_public_key(curve.params.n)  # Too large


class TestECDH(unittest.TestCase):
    """Test ECDH key exchange."""

    def setUp(self):
        """Set up ECDH instance."""
        self.ecdh = ECDH('secp256k1')

    def test_keypair_generation(self):
        """Test ECDH keypair generation."""
        private_key, public_key = self.ecdh.generate_keypair()

        # Private key should be in valid range
        self.assertGreater(private_key, 0)
        self.assertLess(private_key, self.ecdh.curve.params.n)

        # Public key should be on curve
        self.assertTrue(public_key._is_on_curve())
        self.assertFalse(public_key.is_at_infinity())

    def test_shared_secret_agreement(self):
        """Test that both parties compute the same shared secret."""
        # Alice generates keypair
        alice_private, alice_public = self.ecdh.generate_keypair()

        # Bob generates keypair
        bob_private, bob_public = self.ecdh.generate_keypair()

        # Both compute shared secret
        alice_shared = self.ecdh.compute_shared_secret(alice_private, bob_public)
        bob_shared = self.ecdh.compute_shared_secret(bob_private, alice_public)

        # Shared secrets should match
        self.assertEqual(alice_shared, bob_shared)

    def test_different_keypairs_different_secrets(self):
        """Test that different keypairs produce different shared secrets."""
        # Party A
        a_private, a_public = self.ecdh.generate_keypair()

        # Party B
        b_private, b_public = self.ecdh.generate_keypair()

        # Party C
        c_private, c_public = self.ecdh.generate_keypair()

        # A-B shared secret
        ab_shared = self.ecdh.compute_shared_secret(a_private, b_public)

        # A-C shared secret
        ac_shared = self.ecdh.compute_shared_secret(a_private, c_public)

        # Should be different
        self.assertNotEqual(ab_shared, ac_shared)

    def test_shared_secret_deterministic(self):
        """Test that shared secret computation is deterministic."""
        alice_private, alice_public = self.ecdh.generate_keypair()
        bob_private, bob_public = self.ecdh.generate_keypair()

        # Compute shared secret multiple times
        shared1 = self.ecdh.compute_shared_secret(alice_private, bob_public)
        shared2 = self.ecdh.compute_shared_secret(alice_private, bob_public)

        self.assertEqual(shared1, shared2)


class TestECDSA(unittest.TestCase):
    """Test ECDSA digital signatures."""

    def setUp(self):
        """Set up ECDSA instance."""
        self.ecdsa = ECDSA('secp256k1')
        self.message = b"Test message for signing"

    def test_keypair_generation(self):
        """Test ECDSA keypair generation."""
        private_key, public_key = self.ecdsa.generate_keypair()

        # Private key should be in valid range
        self.assertGreater(private_key, 0)
        self.assertLess(private_key, self.ecdsa.curve.params.n)

        # Public key should be on curve
        self.assertTrue(public_key._is_on_curve())
        self.assertFalse(public_key.is_at_infinity())

    def test_sign_and_verify(self):
        """Test signing and verification."""
        private_key, public_key = self.ecdsa.generate_keypair()

        # Sign message
        signature = self.ecdsa.sign(self.message, private_key)
        r, s = signature

        # Signature should be in valid range
        self.assertGreater(r, 0)
        self.assertLess(r, self.ecdsa.curve.params.n)
        self.assertGreater(s, 0)
        self.assertLess(s, self.ecdsa.curve.params.n)

        # Verify signature
        is_valid = self.ecdsa.verify(self.message, signature, public_key)
        self.assertTrue(is_valid)

    def test_verify_wrong_message(self):
        """Test that verification fails with wrong message."""
        private_key, public_key = self.ecdsa.generate_keypair()

        # Sign original message
        signature = self.ecdsa.sign(self.message, private_key)

        # Try to verify different message
        wrong_message = b"Different message"
        is_valid = self.ecdsa.verify(wrong_message, signature, public_key)
        self.assertFalse(is_valid)

    def test_verify_wrong_public_key(self):
        """Test that verification fails with wrong public key."""
        private_key1, public_key1 = self.ecdsa.generate_keypair()
        private_key2, public_key2 = self.ecdsa.generate_keypair()

        # Sign with key 1
        signature = self.ecdsa.sign(self.message, private_key1)

        # Try to verify with key 2
        is_valid = self.ecdsa.verify(self.message, signature, public_key2)
        self.assertFalse(is_valid)

    def test_verify_invalid_signature(self):
        """Test that verification fails with invalid signature."""
        private_key, public_key = self.ecdsa.generate_keypair()

        # Create invalid signature
        invalid_signature = (12345, 67890)

        is_valid = self.ecdsa.verify(self.message, invalid_signature, public_key)
        self.assertFalse(is_valid)

    def test_signature_randomness(self):
        """Test that signing same message twice produces different signatures."""
        private_key, public_key = self.ecdsa.generate_keypair()

        # Sign same message twice
        sig1 = self.ecdsa.sign(self.message, private_key)
        sig2 = self.ecdsa.sign(self.message, private_key)

        # Signatures should be different (due to random k)
        self.assertNotEqual(sig1, sig2)

        # But both should verify
        self.assertTrue(self.ecdsa.verify(self.message, sig1, public_key))
        self.assertTrue(self.ecdsa.verify(self.message, sig2, public_key))


class TestCurveProperties(unittest.TestCase):
    """Test mathematical properties of the curves."""

    def test_secp256k1_parameters(self):
        """Test secp256k1 curve parameters."""
        params = CURVES['secp256k1']

        # Check curve equation y² = x³ + 7 (a=0, b=7)
        self.assertEqual(params.a, 0)
        self.assertEqual(params.b, 7)

        # Generator should be on curve
        x, y = params.G
        left = (y * y) % params.p
        right = (x**3 + params.a * x + params.b) % params.p
        self.assertEqual(left, right)

    def test_p256_parameters(self):
        """Test P-256 curve parameters."""
        params = CURVES['P-256']

        # Generator should be on curve
        x, y = params.G
        left = (y * y) % params.p
        right = (x**3 + params.a * x + params.b) % params.p
        self.assertEqual(left, right)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
