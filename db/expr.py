from typing import Optional, Union


Param = Optional[Union[int, str, float]]


class Expr:
    def to_sql(self, params: list[Param]) -> str:
        raise NotImplementedError()


class Field(Expr):
    # todo: 3.11: LiteralString
    def __init__(self, name: str):
        self.name = name

    def to_sql(self, params: list[Param]) -> str:
        return self.name


class Value(Expr):
    def __init__(self, value: Param) -> None:
        self.value = value

    def to_sql(self, params: list[Param]) -> str:
        params.append(self.value)
        return "?"


class BinOper(Expr):
    OPERATOR: str

    def __init__(self, lhs: Expr, rhs: Expr):
        self.lhs = lhs
        self.rhs = rhs

    def to_sql(self, params: list[Param]) -> str:
        lhs = self.lhs.to_sql(params)
        rhs = self.rhs.to_sql(params)
        return f"{lhs} {self.OPERATOR} {rhs}"


class Eq(BinOper):
    OPERATOR = "="


class Gte(BinOper):
    OPERATOR = ">="


class Combinable(Expr):
    SEP: str
    EMPTY: str

    def __init__(self, *expressions: Expr):
        self.expressions = expressions

    def to_sql(self, params: list[Param]) -> str:
        if not self.expressions:
            return self.EMPTY
        return self.SEP.join(
            expr.to_sql(params)
            for expr
            in self.expressions
        )


class All(Combinable):
    SEP = " AND "
    EMPTY = "true"


class Order:
    ORD: str

    def __init__(self, field: str):
        self.field = field

    def to_sql(self) -> str:
        return f"{self.field} {self.ORD}"


class Asc(Order):
    ORD = "ASC"


class Desc(Order):
    ORD = "DESC"
