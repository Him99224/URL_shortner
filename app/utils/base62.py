import secrets
import string

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)

def encode_base62(number:int)-> str:
    """
    Encodes a positive integer into a Base62 string.
    """
    if number==0:
        raise ValueError("Number must be greater than 0.")
    base62id:str=""
    while number:
        base62id+=ALPHABET[number%BASE]
        number//=BASE
    return base62id[::-1]