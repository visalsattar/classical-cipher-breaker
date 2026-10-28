# Learning notes

Read this until you can explain every line without looking. Interviewers ask "walk me through your code," and "Claude wrote it" is not an answer.

## caesar.py

### `shift_char(c, key)`

```python
if "A" <= c <= "Z":
    base = ord("A")
```
Strings compare by code point, so `"A" <= c <= "Z"` is true only for the 26 ASCII capitals. `ord("A")` is 65, the number the uppercase alphabet starts at.

```python
elif "a" <= c <= "z":
    base = ord("a")
```
Same for lowercase. `ord("a")` is 97.

```python
else:
    return c
```
Anything else (space, digit, punctuation, `Ç`, emoji) is returned unchanged.

```python
return chr((ord(c) - base + key) % 26 + base)
```
Read it inside out:
1. `ord(c) - base` turns the letter into a position 0–25 (`'D'` → 68 − 65 = 3).
2. `+ key` shifts the position.
3. `% 26` wraps it back into 0–25 (`'Y'` with key 3: 24 + 3 = 27, 27 % 26 = 1).
4. `+ base` turns the position back into a code point of the same case.
5. `chr()` turns the code point into a character (`'B'`).

### `encrypt(text, key)`

```python
return "".join(shift_char(c, key) for c in text)
```
Shift every character and glue the results into one string. `"".join` on a generator avoids building the string with repeated `+=`.

### `decrypt(text, key)`

```python
return encrypt(text, -key)
```
Shifting forward by `key` and then back by `key` cancels out, so decryption is encryption with the opposite key. One function to test instead of two.

## cracker.py

### `ENGLISH_FREQ` and `_FREQ_TOTAL`
Percentages from Lewand's table. They add up to about 100.0, not exactly 100, so the code divides by their real sum. That keeps the expected counts exact.

### `CrackResult`
A dataclass holding the four results. It is clearer than returning a tuple where the caller has to remember the order.

### `_letters(text)`

```python
return [c.lower() for c in text if "A" <= c <= "Z" or "a" <= c <= "z"]
```
Keeps only ASCII letters, lowercased. The range check runs on the original character on purpose. `"İ".lower()` returns two characters (`i` plus a combining dot), and the string `"i̇"` sorts between `"a"` and `"z"`, so checking after `.lower()` would let it in. The Kelvin sign `K` lowercases to an ASCII `k` and would also slip through.

### `chi_squared(text)`

```python
letters = _letters(text)
if not letters:
    return float("inf")
```
No letters means no evidence. Infinity means "worst possible score," so a candidate with no letters never wins.

```python
counts = dict.fromkeys(ENGLISH_FREQ, 0)
for c in letters:
    counts[c] += 1
```
Count how often each letter appears.

```python
for letter, freq in ENGLISH_FREQ.items():
    expected = len(letters) * freq / _FREQ_TOTAL
    score += (counts[letter] - expected) ** 2 / expected
```
For each letter, compare how often it appears with how often it would appear in English text of the same length. Squaring makes every difference positive. Dividing by `expected` means missing a common letter like `e` counts for less than seeing a rare letter like `z` many times, which is what makes wrong keys score badly.

### `crack(ciphertext, min_letters=20)`

```python
key = min(range(26), key=lambda k: chi_squared(decrypt(ciphertext, k)))
```
Try every key from 0 to 25, score each decryption, keep the key with the lowest score. This is brute force with a scoring function in place of a human reading 26 outputs.

```python
plaintext = decrypt(ciphertext, key)
confident = len(_letters(ciphertext)) >= min_letters
return CrackResult(key, plaintext, chi_squared(plaintext), confident)
```
Rebuild the winning plaintext and flag whether there was enough text to trust the statistics.

## cli.py

- `build_parser()` defines three subcommands. `type=int` makes argparse reject `abc` or `3.5` itself, printing `invalid int value` and exiting with code 2, the Unix convention for bad usage.
- argparse accepts `-3` as a positional value because the parser has no option that looks like a negative number.
- `text` is optional (`nargs="?"`). If it is missing, the text is read from stdin, so `cat secret.txt | python cli.py crack` works. One trailing newline is stripped so `echo` input round-trips cleanly.
- `main(argv)` takes an argument list so tests can call it directly instead of spawning a process.

## Why `(x - n) % 26` is never negative in Python but can be in C or JavaScript

Python's `%` returns a result with the same sign as the divisor. The divisor is 26, so the result is always in 0–25: `(0 - 3) % 26 == 23`.

C (since C99), Java and JavaScript truncate division toward zero, so `%` takes the sign of the dividend: `(0 - 3) % 26 == -3` in C and JavaScript. `chr(-3 + 65)` would then give the wrong character. The portable fix is `((x - n) % 26 + 26) % 26`.

## Why `isalpha()` is the wrong check here

`isalpha()` and `isupper()` are Unicode-aware. `"Ç".isupper()` is `True`. If the code used it, `Ç` (code point 199) would go through the formula with base 65 and come out as some ASCII capital. That is still a letter, so decryption would shift it back as an ASCII letter and never return `Ç`. The round trip breaks. The cipher only defines a mapping for the 26 ASCII letters, so the check must be exactly those ranges.

In the password checker (Project 1) Unicode-awareness was correct, because the goal there was classifying characters, not doing arithmetic on them.

## Interview questions

**1. How does your cracker find the key without knowing it?**
It decrypts with all 26 keys and scores each output with chi-squared against English letter frequencies. Real English has a recognisable shape (lots of e, t, a; almost no q, z), and only the correct key produces text with that shape. The lowest score wins.

**2. When does it fail, and how would you know?**
On short texts, there aren't enough letters for the counts to look like English, so a wrong key can score lower. Non-English text or very unusual English (a pangram, a list of names) can fail too. The `confident` flag covers the short-text case. A stronger check would also compare the best score with the second-best: a small gap means low confidence. It would also check the plaintext against a dictionary.

**3. Caesar has only 26 keys, so why bother with frequency analysis instead of printing all 26 and reading them?**
Reading 26 outputs only works for a human with one message. Scoring automates it, works on thousands of messages, and is the same idea that breaks harder ciphers. A general substitution cipher has 26! keys (about 4 × 10²⁶), so brute force is impossible, but frequency analysis still breaks it, because the cipher keeps the letter pattern. Vigenère is broken by finding the key length and then running this exact Caesar cracker on each column.
