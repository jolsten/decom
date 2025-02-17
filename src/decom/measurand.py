from dataclasses import dataclass
from typing import Any, Optional

from lark import Token, Transformer

from decom.parameter import BaseParameter


class Interp:
    pass


class EUC:
    pass


class SamplingStrategy:
    pass


@dataclass
class Measurand:
    parameter: BaseParameter
    interp: Interp
    euc: EUC
    ss: SamplingStrategy


class MeasurandTransformer(Transformer):
    def measurand(
        self,
        parameter: BaseParameter,
        interp: Optional[Any] = None,
        euc: Optional[Any] = None,
        ss: Optional[Any] = None,
    ) -> Measurand:
        return Measurand(parameter=parameter, interp=interp, euc=euc, ss=ss)

    def interp(self, token: Token) -> str:
        return str(token)

    def euc(self, token: Token) -> str:
        print(token)
        return token
