"""
Elliptic Curve Cryptography Implementation

Educational implementation of elliptic curve cryptography (ECC) providing:
- Elliptic curve point arithmetic (addition, scalar multiplication)
- Support for standard curves (secp256k1, P-256)
- Elliptic Curve Diffie-Hellman (ECDH) key exchange
- Elliptic Curve Digital Signature Algorithm (ECDSA)

This implementation focuses on understanding ECC concepts and cryptographic protocols.
For production use, rely on established libraries like cryptography, ecdsa, or tinyec.
"""

import hashlib
import secrets
from typing import Optional, Tuple, Dict
from dataclasses import dataclass


@dataclass
class CurveParameters:
    """Parameters defining an elliptic curve y² = x³ + ax + b (mod p)"""
    name: str
    p: int      # Prime modulus
    a: int      # Curve parameter a
    b: int      # Curve parameter b
    G: Tuple[int, int]  # Generator point
    n: int      # Order of generator point
    h: int      # Cofactor


# Standard curve definitions
CURVES = {
    'secp256k1': CurveParameters(
        name='secp256k1',
        # Used by Bitcoin and Ethereum
        p=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
        a=0,
        b=7,
        G=(0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
           0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8),
        n=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
        h=1
    ),
    'P-256': CurveParameters(
        name='P-256',
        # NIST P-256, widely used in TLS
        p=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
        a=0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC,
        b=0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
        G=(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
           0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5),
        n=0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
        h=1
    )
}


class Point:
    """
    Represents a point on an elliptic curve.

    The point at infinity is represented by x=None, y=None.
    """

    def __init__(self, curve: CurveParameters, x: Optional[int] = None, y: Optional[int] = None):
        """
        Initialize a point on the elliptic curve.

        Args:
            curve: The elliptic curve parameters
            x: X-coordinate (None for point at infinity)
            y: Y-coordinate (None for point at infinity)
        """
        self.curve = curve
        self.x = x
        self.y = y

        # Verify point is on curve (unless it's the point at infinity)
        if not self.is_at_infinity():
            if not self._is_on_curve():
                raise ValueError(f"Point ({x}, {y}) is not on curve {curve.name}")

    def is_at_infinity(self) -> bool:
        """Check if this is the point at infinity (identity element)."""
        return self.x is None and self.y is None

    def _is_on_curve(self) -> bool:
        """Verify the point satisfies the curve equation y² = x³ + ax + b (mod p)."""
        if self.is_at_infinity():
            return True

        left = (self.y * self.y) % self.curve.p
        right = (self.x**3 + self.curve.a * self.x + self.curve.b) % self.curve.p
        return left == right

    def __add__(self, other: 'Point') -> 'Point':
        """
        Add two points on the elliptic curve using the group law.

        This is the fundamental operation in elliptic curve cryptography.
        """
        if not isinstance(other, Point):
            raise TypeError("Can only add Point objects")

        if self.curve.name != other.curve.name:
            raise ValueError("Points must be on the same curve")

        # Handle point at infinity (identity element)
        if self.is_at_infinity():
            return other
        if other.is_at_infinity():
            return self

        # Handle point doubling (P + P)
        if self.x == other.x:
            if self.y == other.y:
                return self._double()
            else:
                # P + (-P) = point at infinity
                return Point(self.curve)

        # General point addition
        p = self.curve.p

        # Calculate slope: λ = (y2 - y1) / (x2 - x1) mod p
        slope = ((other.y - self.y) * pow(other.x - self.x, -1, p)) % p

        # Calculate result point
        x3 = (slope * slope - self.x - other.x) % p
        y3 = (slope * (self.x - x3) - self.y) % p

        return Point(self.curve, x3, y3)

    def _double(self) -> 'Point':
        """Double a point (P + P = 2P) using the tangent line method."""
        if self.is_at_infinity():
            return self

        p = self.curve.p

        # Calculate slope: λ = (3x² + a) / (2y) mod p
        numerator = (3 * self.x * self.x + self.curve.a) % p
        denominator = (2 * self.y) % p
        slope = (numerator * pow(denominator, -1, p)) % p

        # Calculate result point
        x3 = (slope * slope - 2 * self.x) % p
        y3 = (slope * (self.x - x3) - self.y) % p

        return Point(self.curve, x3, y3)

    def __mul__(self, scalar: int) -> 'Point':
        """
        Scalar multiplication: compute scalar * Point using double-and-add algorithm.

        This is the key operation for ECC - it's easy to compute but hard to reverse (ECDLP).
        """
        if not isinstance(scalar, int):
            raise TypeError("Scalar must be an integer")

        if scalar < 0:
            raise ValueError("Scalar must be non-negative")

        if scalar == 0:
            return Point(self.curve)  # Point at infinity

        # Use binary expansion for efficient computation
        result = Point(self.curve)  # Start with point at infinity
        addend = self

        while scalar:
            if scalar & 1:  # If bit is 1, add current point
                result = result + addend
            addend = addend._double()  # Double for next bit
            scalar >>= 1

        return result

    def __rmul__(self, scalar: int) -> 'Point':
        """Support scalar * Point syntax."""
        return self.__mul__(scalar)

    def __eq__(self, other) -> bool:
        """Check if two points are equal."""
        if not isinstance(other, Point):
            return False
        return (self.curve.name == other.curve.name and
                self.x == other.x and
                self.y == other.y)

    def __str__(self) -> str:
        """String representation of the point."""
        if self.is_at_infinity():
            return "Point(∞)"
        return f"Point({hex(self.x)[:10]}..., {hex(self.y)[:10]}...)"

    def __repr__(self) -> str:
        """Formal string representation."""
        return f"Point(curve={self.curve.name}, x={self.x}, y={self.y})"


class EllipticCurve:
    """
    Represents an elliptic curve for cryptographic operations.
    """

    def __init__(self, curve_name: str = 'secp256k1'):
        """
        Initialize an elliptic curve.

        Args:
            curve_name: Name of the curve ('secp256k1' or 'P-256')
        """
        if curve_name not in CURVES:
            raise ValueError(f"Unknown curve: {curve_name}. Available: {list(CURVES.keys())}")

        self.params = CURVES[curve_name]
        self.G = Point(self.params, *self.params.G)

    @property
    def name(self) -> str:
        """Get the curve name."""
        return self.params.name

    def generate_private_key(self) -> int:
        """
        Generate a random private key.

        Returns a random integer in [1, n-1] where n is the order of the generator.
        """
        return secrets.randbelow(self.params.n - 1) + 1

    def get_public_key(self, private_key: int) -> Point:
        """
        Derive the public key from a private key.

        Public key = private_key * G (generator point)
        """
        if not 1 <= private_key < self.params.n:
            raise ValueError(f"Private key must be in range [1, {self.params.n - 1}]")

        return private_key * self.G

    def __str__(self) -> str:
        """String representation of the curve."""
        return f"EllipticCurve({self.params.name})"


class ECDH:
    """
    Elliptic Curve Diffie-Hellman key exchange.

    Allows two parties to establish a shared secret over an insecure channel.
    """

    def __init__(self, curve_name: str = 'secp256k1'):
        """Initialize ECDH with specified curve."""
        self.curve = EllipticCurve(curve_name)

    def generate_keypair(self) -> Tuple[int, Point]:
        """
        Generate a private/public key pair.

        Returns:
            (private_key, public_key) tuple
        """
        private_key = self.curve.generate_private_key()
        public_key = self.curve.get_public_key(private_key)
        return private_key, public_key

    def compute_shared_secret(self, private_key: int, other_public_key: Point) -> bytes:
        """
        Compute the shared secret using your private key and other party's public key.

        Args:
            private_key: Your private key
            other_public_key: The other party's public key

        Returns:
            Shared secret as bytes (hash of x-coordinate)
        """
        # Shared point = private_key * other_public_key
        shared_point = private_key * other_public_key

        if shared_point.is_at_infinity():
            raise ValueError("Shared secret computation resulted in point at infinity")

        # Use x-coordinate as shared secret (hashed for uniform distribution)
        shared_x = shared_point.x.to_bytes(32, 'big')
        return hashlib.sha256(shared_x).digest()


class ECDSA:
    """
    Elliptic Curve Digital Signature Algorithm.

    Provides digital signatures for message authentication and non-repudiation.
    """

    def __init__(self, curve_name: str = 'secp256k1'):
        """Initialize ECDSA with specified curve."""
        self.curve = EllipticCurve(curve_name)

    def generate_keypair(self) -> Tuple[int, Point]:
        """
        Generate a private/public key pair for signing.

        Returns:
            (private_key, public_key) tuple
        """
        private_key = self.curve.generate_private_key()
        public_key = self.curve.get_public_key(private_key)
        return private_key, public_key

    def sign(self, message: bytes, private_key: int) -> Tuple[int, int]:
        """
        Sign a message with a private key.

        Args:
            message: Message to sign
            private_key: Private signing key

        Returns:
            (r, s) signature tuple
        """
        n = self.curve.params.n

        # Hash the message
        message_hash = int.from_bytes(hashlib.sha256(message).digest(), 'big')

        # Generate random k for this signature
        while True:
            k = secrets.randbelow(n - 1) + 1

            # Calculate r = (k * G).x mod n
            point = k * self.curve.G
            r = point.x % n

            if r == 0:
                continue

            # Calculate s = k⁻¹(hash + r * private_key) mod n
            k_inv = pow(k, -1, n)
            s = (k_inv * (message_hash + r * private_key)) % n

            if s == 0:
                continue

            return (r, s)

    def verify(self, message: bytes, signature: Tuple[int, int], public_key: Point) -> bool:
        """
        Verify a signature on a message.

        Args:
            message: The signed message
            signature: (r, s) signature tuple
            public_key: Public verification key

        Returns:
            True if signature is valid, False otherwise
        """
        r, s = signature
        n = self.curve.params.n

        # Verify r and s are in valid range
        if not (1 <= r < n and 1 <= s < n):
            return False

        # Hash the message
        message_hash = int.from_bytes(hashlib.sha256(message).digest(), 'big')

        # Calculate w = s⁻¹ mod n
        w = pow(s, -1, n)

        # Calculate u1 = hash * w mod n and u2 = r * w mod n
        u1 = (message_hash * w) % n
        u2 = (r * w) % n

        # Calculate point = u1 * G + u2 * public_key
        point = u1 * self.curve.G + u2 * public_key

        if point.is_at_infinity():
            return False

        # Verify r == point.x mod n
        return r == (point.x % n)


def demonstrate_ecc():
    """Demonstrate elliptic curve cryptography functionality."""
    print("Elliptic Curve Cryptography Demonstration")
    print("=" * 50)

    # Basic curve operations
    print("\n1. Elliptic Curve: secp256k1 (Bitcoin)")
    curve = EllipticCurve('secp256k1')
    print(f"   Curve: {curve.name}")
    print(f"   Generator point order: {curve.params.n}")
    print(f"   Prime modulus: {hex(curve.params.p)[:20]}...")

    # Key generation
    print("\n2. Key Generation")
    private_key = curve.generate_private_key()
    public_key = curve.get_public_key(private_key)
    print(f"   Private key: {hex(private_key)[:20]}...")
    print(f"   Public key: {public_key}")

    # ECDH key exchange
    print("\n3. ECDH Key Exchange")
    ecdh = ECDH('secp256k1')

    # Alice generates keypair
    alice_private, alice_public = ecdh.generate_keypair()
    print(f"   Alice public: {alice_public}")

    # Bob generates keypair
    bob_private, bob_public = ecdh.generate_keypair()
    print(f"   Bob public: {bob_public}")

    # Both compute shared secret
    alice_shared = ecdh.compute_shared_secret(alice_private, bob_public)
    bob_shared = ecdh.compute_shared_secret(bob_private, alice_public)

    print(f"   Alice shared secret: {alice_shared.hex()[:32]}...")
    print(f"   Bob shared secret: {bob_shared.hex()[:32]}...")
    print(f"   Secrets match: {alice_shared == bob_shared}")

    # ECDSA signing
    print("\n4. ECDSA Digital Signatures")
    ecdsa = ECDSA('secp256k1')

    # Generate signing keypair
    signing_key, verifying_key = ecdsa.generate_keypair()

    # Sign a message
    message = b"Hello, Elliptic Curves!"
    signature = ecdsa.sign(message, signing_key)
    print(f"   Message: {message.decode()}")
    print(f"   Signature (r): {hex(signature[0])[:20]}...")
    print(f"   Signature (s): {hex(signature[1])[:20]}...")

    # Verify signature
    is_valid = ecdsa.verify(message, signature, verifying_key)
    print(f"   Signature valid: {is_valid}")

    # Try verifying with wrong message
    wrong_message = b"Wrong message"
    is_valid_wrong = ecdsa.verify(wrong_message, signature, verifying_key)
    print(f"   Wrong message valid: {is_valid_wrong}")

    print("\n" + "=" * 50)
    print("ECC demonstration complete!")


if __name__ == "__main__":
    demonstrate_ecc()
