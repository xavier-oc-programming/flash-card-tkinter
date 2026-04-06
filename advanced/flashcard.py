import csv
import random
from pathlib import Path


class FlashCard:
    """Pure logic: word list management, progress persistence."""

    _SAVED_FILE = "words_to_learn.csv"
    _ORIG_FILE = "french_words.csv"

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._saved_path = data_dir / self._SAVED_FILE
        self._orig_path = data_dir / self._ORIG_FILE
        self._words: list[dict] = self._load()
        self._current: dict = {}

    def _load(self) -> list[dict]:
        try:
            with self._saved_path.open(newline="", encoding="utf-8") as f:
                words = list(csv.DictReader(f))
            if words:
                return words
        except FileNotFoundError:
            pass
        with self._orig_path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def next_word(self) -> dict | None:
        """Return a random word dict, or None if the deck is exhausted."""
        if not self._words:
            return None
        self._current = random.choice(self._words)
        return self._current

    def mark_known(self) -> None:
        """Remove the current word from the deck and persist progress."""
        try:
            self._words.remove(self._current)
        except ValueError:
            pass
        with self._saved_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["French", "English"])
            writer.writeheader()
            writer.writerows(self._words)

    @property
    def remaining(self) -> int:
        return len(self._words)
