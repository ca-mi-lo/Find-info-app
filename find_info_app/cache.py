from _typeshed import ReadableBuffer
import os
from pathlib import Path
from typing import Any
from base64 import urlsafe_b64encode, urlsafe_b64decode
import zlib
import pickle


class Cache:
    """Abstract Cache"""

    def __init__(self) -> None:
        pass

    def put(self, key: str, obj: Any):
        pass

    def get(self, key: str) -> None:
        return None

    def has(self, key: str) -> bool:
        return False

    def delete(self, key: str):
        pass

    def compress(self, data: ReadableBuffer) -> bytes:
        return zlib.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)

    def serialize(self, obj: Any) -> bytes:
        pickled = pickle.dumps(obj)
        compressed = self.compress(pickled)
        return compressed

    def deserialize(self, data: bytes) -> Any:
        pickled = self.decompress(data)
        obj = pickle.loads(pickled)
        return obj

    def encode(self, name: str) -> str:
        return urlsafe_b64encode(name.encode()).decode()

    def decode(self, name: str) -> str:
        return urlsafe_b64decode(name).decode()


class DiskCache(Cache):
    """File Disk Cache"""

    def __init__(self, path: str) -> None:
        self.root = Path(path)
        super().__init__()

    def path(self, key: str) -> Path:
        return self.root / self.encode(key)

    def put(self, key: str, obj: Any) -> None:
        path = self.path(key)
        data = self.serialize(obj)
        with open(path, "wb") as f:
            f.write(data)

    def get(self, key: str) -> Any:
        path = self.path(key)
        with open(path, "rb") as f:
            data = f.read()
        obj = self.deserialize(data)
        return obj

    def has(self, key: str) -> bool:
        path = self.path(key)
        return path.exists()

    def delete(self, key: str):
        path = self.path(key)
        path.unlink()


def get_cache() -> Cache:
    mode = os.getenv("CACHE_MODE", "").upper()
    path = os.getenv("CACHE_PATH", "")
    if mode == "Disk":
        return DiskCache(path)
    else:
        return Cache()
