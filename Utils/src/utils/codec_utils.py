import hashlib


def hash_encode(data: list[str]):
        raw = ":".join([i for i in data])
        id = hashlib.sha1(raw.encode()).hexdigest()
        return id