"""Command line: encrypt, decrypt or crack Caesar text. Text comes from an argument or stdin."""
import argparse
import sys

from caesar import decrypt, encrypt
from cracker import crack


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cli.py", description="Caesar cipher with a frequency-analysis cracker.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("encrypt", "decrypt"):
        p = sub.add_parser(name, help=f"{name} text with a shift key")
        p.add_argument("key", type=int, help="shift key, any integer (3, -3 and 29 all work)")
        p.add_argument("text", nargs="?", help="text to process; read from stdin if omitted")
    p = sub.add_parser("crack", help="recover the key and plaintext without knowing the key")
    p.add_argument("text", nargs="?", help="ciphertext; read from stdin if omitted")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)  # a non-integer key exits here with code 2
    text = args.text if args.text is not None else sys.stdin.read().rstrip("\n")

    if args.command == "encrypt":
        ciphertext = encrypt(text, args.key)
        print(f"Ciphertext: {ciphertext}")
        print(f"Decrypted:  {decrypt(ciphertext, args.key)}")
    elif args.command == "decrypt":
        print(decrypt(text, args.key))
    else:
        result = crack(text)
        print(f"Key:        {result.key}")
        print(f"Score:      {result.score:.1f} (chi-squared, lower is more English-like)")
        print(f"Confident:  {'yes' if result.confident else 'no (too few letters to trust the result)'}")
        print(f"Plaintext:  {result.plaintext}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
