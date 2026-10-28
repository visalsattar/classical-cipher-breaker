import pytest

from caesar import decrypt, encrypt, shift_char

SAMPLE = "Hello, World! 123 Çaylak 🙂 end."


@pytest.mark.parametrize("key", range(-30, 31))
def test_round_trip_every_key(key):
    assert decrypt(encrypt(SAMPLE, key), key) == SAMPLE


def test_known_value():
    assert encrypt("Attack at Dawn!", 3) == "Dwwdfn dw Gdzq!"


def test_wraps_around_end_of_alphabet():
    assert encrypt("xyz XYZ", 3) == "abc ABC"


@pytest.mark.parametrize("c", list(" ,.!?-'0123456789\nÇçéßİ🙂"))
def test_non_ascii_letters_unchanged(c):
    assert shift_char(c, 7) == c


def test_key_29_equals_key_3():
    assert encrypt(SAMPLE, 29) == encrypt(SAMPLE, 3)


def test_negative_key_shifts_left():
    assert encrypt("abc", -3) == "xyz"
