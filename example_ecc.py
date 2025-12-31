"""
Elliptic Curve Cryptography Examples

Demonstrates practical applications of ECC including:
- Key generation
- Elliptic Curve Diffie-Hellman (ECDH) key exchange
- Elliptic Curve Digital Signature Algorithm (ECDSA)
- Multiple curve support (secp256k1, P-256)
"""

from elliptic_curve import EllipticCurve, ECDH, ECDSA, Point, CURVES


def example_basic_curve_operations():
    """Demonstrate basic elliptic curve point arithmetic."""
    print("=" * 60)
    print("Example 1: Basic Elliptic Curve Operations")
    print("=" * 60)

    # Create curve instance
    curve = EllipticCurve('secp256k1')
    print(f"\nUsing curve: {curve.name}")
    print(f"Prime modulus (p): {hex(curve.params.p)[:40]}...")
    print(f"Curve equation: y² = x³ + {curve.params.a}x + {curve.params.b} (mod p)")

    # Generator point
    G = curve.G
    print(f"\nGenerator point G:")
    print(f"  x: {hex(G.x)[:40]}...")
    print(f"  y: {hex(G.y)[:40]}...")

    # Point addition and scalar multiplication
    print(f"\nPoint operations:")
    point_2G = 2 * G
    point_3G = 3 * G
    point_5G = point_2G + point_3G

    print(f"  2G + 3G = 5G")
    print(f"  5G.x: {hex(point_5G.x)[:40]}...")

    # Verify that 5 * G equals 2 * G + 3 * G
    direct_5G = 5 * G
    print(f"  Verification: 2G + 3G == 5G: {point_5G == direct_5G}")

    print()


def example_key_generation():
    """Demonstrate public/private key generation."""
    print("=" * 60)
    print("Example 2: Key Generation")
    print("=" * 60)

    curve = EllipticCurve('secp256k1')

    print("\nGenerating keypair...")
    private_key = curve.generate_private_key()
    public_key = curve.get_public_key(private_key)

    print(f"\nPrivate key (secret):")
    print(f"  {hex(private_key)}")

    print(f"\nPublic key (can be shared):")
    print(f"  x: {hex(public_key.x)[:40]}...")
    print(f"  y: {hex(public_key.y)[:40]}...")

    # Verify relationship: public_key = private_key * G
    computed_public = private_key * curve.G
    print(f"\nVerification: public_key == private_key * G: {public_key == computed_public}")

    print()


def example_ecdh_key_exchange():
    """Demonstrate ECDH key exchange between Alice and Bob."""
    print("=" * 60)
    print("Example 3: ECDH Key Exchange")
    print("=" * 60)

    print("\nScenario: Alice and Bob want to establish a shared secret")
    print("over an insecure channel (e.g., the internet).\n")

    ecdh = ECDH('secp256k1')

    # Alice generates her keypair
    print("Step 1: Alice generates her keypair")
    alice_private, alice_public = ecdh.generate_keypair()
    print(f"  Alice's private key: {hex(alice_private)[:40]}... (kept secret)")
    print(f"  Alice's public key: {hex(alice_public.x)[:40]}... (sent to Bob)")

    # Bob generates his keypair
    print("\nStep 2: Bob generates his keypair")
    bob_private, bob_public = ecdh.generate_keypair()
    print(f"  Bob's private key: {hex(bob_private)[:40]}... (kept secret)")
    print(f"  Bob's public key: {hex(bob_public.x)[:40]}... (sent to Alice)")

    # Both compute shared secret
    print("\nStep 3: Both compute shared secret")
    alice_shared = ecdh.compute_shared_secret(alice_private, bob_public)
    bob_shared = ecdh.compute_shared_secret(bob_private, alice_public)

    print(f"  Alice computes: private_alice * public_bob")
    print(f"  Alice's shared secret: {alice_shared.hex()}")

    print(f"\n  Bob computes: private_bob * public_alice")
    print(f"  Bob's shared secret: {bob_shared.hex()}")

    print(f"\nStep 4: Verify shared secrets match")
    print(f"  Secrets match: {alice_shared == bob_shared}")

    if alice_shared == bob_shared:
        print("\n✓ Success! Alice and Bob can now use this shared secret")
        print("  for symmetric encryption (e.g., AES)")

    print()


def example_ecdsa_signatures():
    """Demonstrate ECDSA digital signatures."""
    print("=" * 60)
    print("Example 4: ECDSA Digital Signatures")
    print("=" * 60)

    print("\nScenario: Alice wants to sign a message to prove she wrote it")
    print("and Bob wants to verify the signature.\n")

    ecdsa = ECDSA('secp256k1')

    # Alice generates signing keypair
    print("Step 1: Alice generates signing keypair")
    alice_private, alice_public = ecdsa.generate_keypair()
    print(f"  Private key (signing): {hex(alice_private)[:40]}... (kept secret)")
    print(f"  Public key (verification): {hex(alice_public.x)[:40]}... (shared)")

    # Alice signs a message
    message = b"I, Alice, authorize payment of 100 BTC to Bob"
    print(f"\nStep 2: Alice signs the message")
    print(f"  Message: {message.decode()}")

    signature = ecdsa.sign(message, alice_private)
    r, s = signature
    print(f"  Signature (r, s):")
    print(f"    r: {hex(r)[:40]}...")
    print(f"    s: {hex(s)[:40]}...")

    # Bob verifies the signature
    print(f"\nStep 3: Bob verifies the signature using Alice's public key")
    is_valid = ecdsa.verify(message, signature, alice_public)
    print(f"  Signature valid: {is_valid}")

    if is_valid:
        print("\n✓ Success! Bob can be certain:")
        print("  1. The message was signed by Alice (authentication)")
        print("  2. The message has not been modified (integrity)")
        print("  3. Alice cannot deny signing it (non-repudiation)")

    # Try to forge signature
    print(f"\nStep 4: Eve tries to modify the message")
    forged_message = b"I, Alice, authorize payment of 100 BTC to Eve"
    print(f"  Forged message: {forged_message.decode()}")

    is_forged_valid = ecdsa.verify(forged_message, signature, alice_public)
    print(f"  Forged signature valid: {is_forged_valid}")

    if not is_forged_valid:
        print("\n✓ The forgery is detected! The signature doesn't match.")

    print()


def example_multiple_curves():
    """Demonstrate using different elliptic curves."""
    print("=" * 60)
    print("Example 5: Multiple Curve Support")
    print("=" * 60)

    curves_to_test = ['secp256k1', 'P-256']

    for curve_name in curves_to_test:
        print(f"\n{curve_name}:")
        print("-" * 40)

        curve = EllipticCurve(curve_name)
        params = CURVES[curve_name]

        print(f"  Use case: {get_curve_use_case(curve_name)}")
        print(f"  Prime (p): {hex(params.p)[:40]}...")
        print(f"  Curve: y² = x³ + {params.a}x + {params.b}")
        print(f"  Generator order (n): {hex(params.n)[:40]}...")

        # Test key generation
        private = curve.generate_private_key()
        public = curve.get_public_key(private)
        print(f"  Sample public key x: {hex(public.x)[:40]}...")

    print()


def get_curve_use_case(curve_name):
    """Get typical use case for a curve."""
    use_cases = {
        'secp256k1': 'Bitcoin, Ethereum, and cryptocurrencies',
        'P-256': 'TLS, government applications (NIST standard)'
    }
    return use_cases.get(curve_name, 'General purpose')


def example_connection_to_moonshine():
    """Explain the connection between ECC and the Monster group."""
    print("=" * 60)
    print("Example 6: Connection to Monstrous Moonshine")
    print("=" * 60)

    print("""
Mathematical Connection:
------------------------
While this repository implements both the Monster group and elliptic
curve cryptography, they are connected through deep mathematics:

1. Elliptic Curves in Different Contexts:
   • Moonshine: Uses modular forms and the j-invariant of elliptic
     curves over complex numbers to study the Monster group
   • ECC: Uses the group law on elliptic curves over finite fields
     for cryptography

2. The j-Invariant:
   • In moonshine: The j-function's Fourier coefficients mysteriously
     relate to Monster group character dimensions
   • In cryptography: The j-invariant classifies elliptic curves and
     is used in curve generation

3. Representation Theory:
   • Monster: Has a 196,883-dimensional representation
   • ECC: Often uses 256-bit curves (different mathematical object,
     but both involve large-dimensional spaces)

Example j-Invariant Calculation:
--------------------------------
For an elliptic curve y² = x³ + ax + b, the j-invariant is:

    j = 1728 × (4a³) / (4a³ + 27b²)
    """)

    # Calculate j-invariant for secp256k1
    params = CURVES['secp256k1']
    a, b, p = params.a, params.b, params.p

    # j-invariant for y² = x³ + 7 (a=0, b=7)
    numerator = (1728 * 4 * a**3) % p
    denominator = (4 * a**3 + 27 * b**2) % p

    if denominator != 0:
        j_invariant = (numerator * pow(denominator, -1, p)) % p
        print(f"For secp256k1 (y² = x³ + 7):")
        print(f"  j-invariant (mod p): {hex(j_invariant)[:40]}...")
    else:
        print(f"For secp256k1: j-invariant = 0 (supersingular curve)")

    print("""
This mathematical connection shows how abstract algebra and number
theory unite seemingly different areas of mathematics!
    """)


def main():
    """Run all ECC examples."""
    print("\n" + "=" * 60)
    print("ELLIPTIC CURVE CRYPTOGRAPHY EXAMPLES")
    print("=" * 60)
    print()

    # Run examples
    example_basic_curve_operations()
    example_key_generation()
    example_ecdh_key_exchange()
    example_ecdsa_signatures()
    example_multiple_curves()
    example_connection_to_moonshine()

    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
