import io

import pytest

from cli import main


def test_encrypt_prints_ciphertext_and_round_trip(capsys):
    assert main(["encrypt", "3", "Hello, World!"]) == 0
    out = capsys.readouterr().out
    assert "Ciphertext: Khoor, Zruog!" in out
    assert "Decrypted:  Hello, World!" in out


def test_negative_key_accepted(capsys):
    main(["decrypt", "-3", "Hello"])  # decrypting with -3 is encrypting with 3
    assert capsys.readouterr().out.strip() == "Khoor"


def test_text_from_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("Khoor\n"))
    main(["decrypt", "29"])
    assert capsys.readouterr().out.strip() == "Hello"


def test_crack_output(capsys):
    main(["crack", "Wkh txlfn eurzq ira mxpsv ryhu wkh odcb grj"])
    out = capsys.readouterr().out
    assert "Key:        3" in out
    assert "Confident:  yes" in out
    assert "Plaintext:  The quick brown fox jumps over the lazy dog" in out


@pytest.mark.parametrize("bad", ["abc", "3.5", ""])
def test_rejects_non_integer_key(bad, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["encrypt", bad, "Hello"])
    assert exc.value.code == 2
    assert "invalid int value" in capsys.readouterr().err
