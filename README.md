# Classical Cipher Breaker

A Caesar cipher and a frequency-analysis cracker in Python 3.11, standard library only. The cracker recovers the key from ciphertext alone, which is the point of the project: Caesar is not encryption you can rely on, and this repo shows why. Built for Project 2 of the DecodeLabs Cybersecurity internship.

## Usage

```bash
python cli.py encrypt 3 "Attack at dawn!"
# Ciphertext: Dwwdfn dw gdzq!
# Decrypted:  Attack at dawn!
```

```bash
python cli.py decrypt 3 "Dwwdfn dw gdzq!"
# Attack at dawn!
```

```bash
python cli.py crack "Wkh txlfn eurzq ira mxpsv ryhu wkh odcb grj"
# Key:        3
# Score:      ...
# Confident:  yes
# Plaintext:  The quick brown fox jumps over the lazy dog
```

```bash
echo "Khoor" | python cli.py decrypt 3      # text can also come from stdin
```

The key can be any integer. `-3` shifts left, and `29` gives the same result as `3`. A key that is not an integer is rejected with an error and exit code 2.

## How the cipher works

Each ASCII letter is turned into a number from 0 to 25, the key is added, and the result is wrapped with `% 26`:

```
E(x) = (x + k) mod 26        D(x) = (x - k) mod 26
```

Upper and lower case are kept. Every other character (spaces, digits, punctuation, accented letters, emoji) passes through unchanged. Decryption is encryption with the negated key.

## How the cracker works

The cracker decrypts the ciphertext with all 26 keys and scores each candidate with Pearson's chi-squared statistic against standard English letter frequencies:

```
chi² = Σ (observed_i - expected_i)² / expected_i     for i = a..z
expected_i = (number of letters in the text) × (English frequency of letter i)
```

A lower score means the letter counts are closer to normal English. The key with the lowest score wins. The result also reports `confident = False` when the ciphertext has fewer than 20 letters, because the statistic is unreliable on that little data.

Letter frequencies come from Robert Lewand, *Cryptological Mathematics* (2000), pp. 36–37 (E 12.702%, T 9.056%, ... Z 0.074%).

## Security note

Caesar has 26 keys and only 25 of them change the text. Trying them all takes microseconds, and the cracker above does it automatically. It also keeps the letter pattern of the original, so frequency analysis works even without brute force. Caesar does not protect data in transit or at rest. Real systems use vetted ciphers such as AES-GCM through TLS or a maintained library, never a home-made scheme.

## Known limits

- **Short texts:** with only a few letters, the chi-squared score can pick the wrong key. `confident` warns about this but the cracker still returns its best guess.
- **Non-English text:** the scores assume English. Text in another language, or English with an unusual letter mix, can be cracked wrongly.
- **Non-ASCII letters ignored:** only A–Z and a–z are shifted and counted. Letters such as `Ç` or `é` stay as they are, which leaks part of the plaintext.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -q
```
