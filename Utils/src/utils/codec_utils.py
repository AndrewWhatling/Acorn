import hashlib


def hash_encode(data: list[str]) -> str:
        """
        Encodes a list of strings into a hash value.

        Args:
            data (list[str]): String list to encode

        Returns:
            str: Hash value.
        """
        raw = ":".join([i for i in data])
        id = hashlib.sha1(raw.encode()).hexdigest()
        return id