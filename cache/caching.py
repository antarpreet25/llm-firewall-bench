import hashlib
import json

# prompt: str, sysprompt: str, model : str, max_tokens : int, temp: float
def hash_params(conf: dict, prompt : str) -> str:
    """
    Hashes the given dictionary using SHA-256 and returns the hexadecimal digest.
    
    Args:
        conf (dict): The dictionary to hash.
        prompt (str): The prompt string to include in the hash.
    """

    # return hashed fingerprint
    payload = {**conf, "prompt": prompt}
    config = json.dumps(payload, sort_keys=True)

    return hashlib.sha256(config.encode()).hexdigest()
