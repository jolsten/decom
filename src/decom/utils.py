def irange(start: int, stop: int) -> list[int]:
    if start <= stop:
        return list(range(start, stop + 1))
    return list(range(start, stop - 1, -1))

def hex2dec(val: str) -> int:
    return int(val, base=16)

def oct2dec(val: str) -> int:
    return int(val, base=8)

def bin2dec(val: str) -> int:
    return int(val, base=2)

def bit_mask(val: int) -> list[int]:
    bits = []
    i = 1
    while val > 0:
        if val % 2 == 1:
            bits.append(i)
        val = val >> 1
        i += 1
    return bits
