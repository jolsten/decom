from decom.model import VarUIntArray

NUM_FRAMES = 10
SAMPLE_DATA = {}
for word_size in [8, 10, 12]:
    SAMPLE_DATA[word_size] = VarUIntArray(
        [[x % 2**word_size for x in range(1, 2**word_size + 1)]] * NUM_FRAMES,
        word_size=word_size,
    )
