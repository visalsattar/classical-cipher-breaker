"""Caesar cipher: shift ASCII letters by a key and leave every other character alone."""


def shift_char(c: str, key: int) -> str:
    # Explicit ASCII ranges, not isalpha(): 'Ç'.isalpha() is True and would break the round trip.
    if "A" <= c <= "Z":
        base = ord("A")
    elif "a" <= c <= "z":
        base = ord("a")
    else:
        return c
    return chr((ord(c) - base + key) % 26 + base)


def encrypt(text: str, key: int) -> str:
    return "".join(shift_char(c, key) for c in text)


def decrypt(text: str, key: int) -> str:
    return encrypt(text, -key)
