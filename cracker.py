"""Break a Caesar cipher: try all 26 keys and keep the one whose output looks most like English."""
from dataclasses import dataclass

from caesar import decrypt

# Relative frequency (%) of each letter in English text. Lewand, Cryptological Mathematics (2000), pp. 36-37.
ENGLISH_FREQ = {
    "a": 8.167, "b": 1.492, "c": 2.782, "d": 4.253, "e": 12.702, "f": 2.228,
    "g": 2.015, "h": 6.094, "i": 6.966, "j": 0.153, "k": 0.772, "l": 4.025,
    "m": 2.406, "n": 6.749, "o": 7.507, "p": 1.929, "q": 0.095, "r": 5.987,
    "s": 6.327, "t": 9.056, "u": 2.758, "v": 0.978, "w": 2.360, "x": 0.150,
    "y": 1.974, "z": 0.074,
}
_FREQ_TOTAL = sum(ENGLISH_FREQ.values())  # about 100.0; dividing by it keeps expected counts exact


@dataclass
class CrackResult:
    key: int
    plaintext: str
    score: float
    confident: bool


def _letters(text: str) -> list[str]:
    # Check the original character, not c.lower(): 'İ'.lower() is two characters and 'K' (Kelvin) becomes 'k'.
    return [c.lower() for c in text if "A" <= c <= "Z" or "a" <= c <= "z"]


def chi_squared(text: str) -> float:
    letters = _letters(text)
    if not letters:
        return float("inf")
    counts = dict.fromkeys(ENGLISH_FREQ, 0)
    for c in letters:
        counts[c] += 1
    score = 0.0
    for letter, freq in ENGLISH_FREQ.items():
        expected = len(letters) * freq / _FREQ_TOTAL
        score += (counts[letter] - expected) ** 2 / expected
    return score


def crack(ciphertext: str, min_letters: int = 20) -> CrackResult:
    key = min(range(26), key=lambda k: chi_squared(decrypt(ciphertext, k)))
    plaintext = decrypt(ciphertext, key)
    confident = len(_letters(ciphertext)) >= min_letters
    return CrackResult(key, plaintext, chi_squared(plaintext), confident)
