"""Small debug helpers kept out of the UI layer."""


def log(message: str, enabled: bool = False) -> None:
    if enabled:
        print(f"[Molder V2] {message}")
