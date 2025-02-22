from typing import Any, Callable, Optional, Union

from lark import Token, Transformer, v_args

from decom.measurand.measurand import EUC, Measurand
from decom.measurand.parameter import Parameter
from decom.parsers.calculator import Number


@v_args(inline=True)
class MeasurandTransformer(Transformer):
    def measurand(
        self,
        parameter: Parameter,
        interp: Optional[Any] = None,
        euc: Optional[Any] = None,
        ss: Optional[Any] = None,
    ) -> Measurand:
        return Measurand(parameter=parameter, interp=interp, euc=euc, ss=ss)

    def interp(self, token: Token) -> str:
        return str(token)

    def euc(self, *args: list[Union[Callable, Number]]) -> str:
        if len(args) == 1:
            return EUC(scale_factor=args[0])
        elif len(args) == 2:
            return EUC(scale_factor=args[0], scaled_bias=args[1])
        elif len(args) == 3:
            return EUC(data_bias=args[0], scale_factor=args[1], scaled_bias=args[2])
        raise ValueError
