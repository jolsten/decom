import numpy as np

from decom import utils


class UintXArray(np.ndarray):
    def __new__(cls, input_array, word_size: int):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        dtype = utils.word_size_to_uint(word_size)
        obj = np.asarray(input_array, dtype=dtype).view(cls)

        # add the new attribute to the created instance
        obj.word_size = word_size

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.word_size = getattr(obj, "word_size", None)

    def __array_wrap__(self, obj, context=None, return_scalar=False):
        if obj is self:  # for in-place operations
            result = obj
        else:
            result = obj.view(type(self))

        result = super().__array_wrap__(obj, context, return_scalar)

        if context is not None:
            func, args, out_i = context
            input_args = args[: func.nin]

            if func is np.invert:
                # Ensure the inverted result doesn't contain bits which should be unused
                result = np.bitwise_and(result.view(np.ndarray), 2**self.word_size - 1)
                result = self.__class__(result, word_size=self.word_size)

        return result
