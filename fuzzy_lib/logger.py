"""Простой логгер в файл."""
import datetime


class Logger:
    def __init__(self, path="fuzzy_log.txt"):
        self.path = path

    def log(self, msg: str):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
