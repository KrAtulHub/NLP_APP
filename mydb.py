import base64
import hashlib
import hmac
import json
import os
from typing import Any


class Database:
    DB_PATH = "database.json"
    PBKDF2_ITERATIONS = 210_000

    def _load(self) -> dict[str, Any]:
        if not os.path.exists(self.DB_PATH):
            return {}
        try:
            with open(self.DB_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        with open(self.DB_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.PBKDF2_ITERATIONS,
        )
        salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
        dk_b64 = base64.urlsafe_b64encode(dk).decode("ascii").rstrip("=")
        return f"pbkdf2_sha256${self.PBKDF2_ITERATIONS}${salt_b64}${dk_b64}"

    def _verify_password(self, password: str, stored: str) -> bool:
        if not isinstance(stored, str):
            return False

        # Backward compatibility: old format stored plain password.
        if not stored.startswith("pbkdf2_sha256$"):
            return hmac.compare_digest(stored, password)

        try:
            _, iters_s, salt_b64, dk_b64 = stored.split("$", 3)
            iters = int(iters_s)

            def _b64pad(s: str) -> str:
                return s + "=" * (-len(s) % 4)

            salt = base64.urlsafe_b64decode(_b64pad(salt_b64).encode("ascii"))
            expected = base64.urlsafe_b64decode(_b64pad(dk_b64).encode("ascii"))
            actual = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iters,
                dklen=len(expected),
            )
            return hmac.compare_digest(expected, actual)
        except Exception:
            return False

    def add_data(self, email: str, password: str) -> bool:
        email = (email or "").strip()
        password = password or ""
        if not email or not password:
            return False

        data = self._load()
        if email in data:
            return False

        data[email] = [self._hash_password(password)]
        self._save(data)
        return True

    def validate_login(self, email: str, password: str) -> bool:
        email = (email or "").strip()
        password = password or ""
        if not email or not password:
            return False

        data = self._load()
        if email not in data:
            return False

        stored_list = data.get(email)
        stored = stored_list[0] if isinstance(stored_list, list) and stored_list else ""
        ok = self._verify_password(password, stored)

        # If user logged in with an old plain-text password, upgrade it to hashed.
        if ok and isinstance(stored, str) and stored and not stored.startswith("pbkdf2_sha256$"):
            data[email] = [self._hash_password(password)]
            self._save(data)

        return ok