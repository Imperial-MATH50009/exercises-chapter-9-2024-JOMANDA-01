"""Giving basic expressions."""
import numbers
from functools import singledispatch


class Expression:
    """All expressions."""

    def __init__(self, *operands):
        """Sharing operands, as it is quite common."""
        self.precedence = -1
        self.operands = operands

    def __add__(self, other):
        """+."""
        if isinstance(other, Expression):
            return Add(self, other)

        elif isinstance(other, numbers.Number):
            return Add(self, Number(other))

        else:
            return NotImplemented

    def __radd__(self, other):
        """Numbers add expression."""
        return Add(Number(other), self)

    def __sub__(self, other):
        """-."""
        if isinstance(other, Expression):
            return Sub(self, other)

        elif isinstance(other, numbers.Number):
            return Sub(self, Number(other))

        else:
            return NotImplemented

    def __rsub__(self, other):
        """2-a."""
        return Sub(Number(other), self)

    def __mul__(self, other):
        """*."""
        if isinstance(other, Expression):
            return Mul(self, other)

        elif isinstance(other, numbers.Number):
            return Mul(self, Number(other))

        else:
            return NotImplemented

    def __rmul__(self, other):
        """2*a."""
        return Mul(Number(other), self)

    def __pow__(self, other):
        """^."""
        if isinstance(other, Expression):
            return Pow(self, other)

        elif isinstance(other, numbers.Number):
            return Pow(self, Number(other))

        else:
            return NotImplemented

    def __rpow__(self, other):
        """2^a."""
        return Pow(Number(other), self)

    def __truediv__(self, other):
        """/."""
        if isinstance(other, Expression):
            return Div(self, other)

        elif isinstance(other, numbers.Number):
            return Div(self, Number(other))

        else:
            return NotImplemented

    def __rtruediv__(self, other):
        """2/a."""
        return Div(Number(other), self)


class Operator(Expression):
    """Add, Sub, Mul, Div, Pow."""

    def __repr__(self):
        """a+2 -> Add(a,2)."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """Remember the brackets."""
        first = 0
        last = 0
        le = ("", "(")
        ri = ("", ")")
        if isinstance((self.operands)[0], Expression):
            if self.precedence > (self.operands)[0].precedence:
                first = 1
            else:
                pass
        else:
            pass
        if isinstance((self.operands)[1], Expression):
            if self.precedence > (self.operands)[1].precedence:
                last = 1
            else:
                pass
        else:
            pass

        return le[first] + str((self.operands)[0]) + ri[first] + \
            self.symbol + le[last] + str((self.operands)[1]) + \
            ri[last]


class Add(Operator):
    """+."""

    symbol = " + "

    def __init__(self, *operands):
        """Low priority."""
        self.precedence = 0
        self.operands = operands


class Sub(Operator):
    """-."""

    symbol = " - "

    def __init__(self, *operands):
        """Low priority."""
        self.precedence = 0
        self.operands = operands


class Mul(Operator):
    """*."""

    symbol = " * "

    def __init__(self, *operands):
        """Medium priority."""
        self.precedence = 1
        self.operands = operands


class Div(Operator):
    """*."""

    symbol = " / "

    def __init__(self, *operands):
        """Medium priority."""
        self.precedence = 1
        self.operands = operands


class Pow(Operator):
    """^."""

    symbol = " ^ "

    def __init__(self, *operands):
        """High priority."""
        self.precedence = 2
        self.operands = operands


class Terminal(Expression):
    """Symbol and Number."""

    def __init__(self, value):
        """Give value instead of operands."""
        self.operands = ()
        self.value = value
        self.precedence = 2

    def __repr__(self):
        """Trivial."""
        return repr(self.value)

    def __str__(self):
        """Trivial."""
        return str(self.value)


class Number(Terminal):
    """Identify numbers."""

    def _validate(self, value):
        if isinstance(value, numbers.Number):
            pass


class Symbol(Terminal):
    """Identify symbols."""

    def _validate(self, value):
        if isinstance(value, str):
            pass


def postvisitor(expr, fn, **kwargs):
    """Visit an Expression in postorder applying a function to every node.

    Parameters
    ----------
    expr: Expression
        The expression to be visited.
    fn: function(node, *o, **kwargs)
        A function to be applied at each node. The function should take
        the node to be visited as its first argument, and the results of
        visiting its operands as any further positional arguments. Any
        additional information that the visitor requires can be passed in
        as keyword arguments.
    **kwargs:
        Any additional keyword arguments to be passed to fn.
    """
    return visit(expr, fn, **kwargs)


def visit(expr, visitor, **kwargs):
    """Avoid recursion."""
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)

        if unvisited_children:
            stack.append(e)
            # Not ready to visit this node yet.
            # Need to visit children before e.
            for k in unvisited_children:
                stack.append(k)
        else:
            # Any children of e have been visited, so we can visit it.
            visited[e] = \
                visitor(e, *(visited[o] for o in e.operands), **kwargs)

    # When the stack is empty, we have visited every subexpression,
    # including expr itself.
    return visited[expr]


@singledispatch
def differentiate(expr, *var, **kwargs):
    """Differentiate an expression node.

    Parameters
    ----------
    expr: Expression
        The expression node to be evaluated.
    *o: numbers.Number
        The results of evaluating the operands of expr.
    **kwargs:
        Any keyword arguments required to evaluate specific types of
        expression.
    symbol_map: dict
        A dictionary mapping Symbol names to numerical values, for
        example:

        {'x': 1}
    """
    raise NotImplementedError(
        f"Cannot evaluate a {type(expr).__name__}")


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return Number(0.0)


@differentiate.register(Symbol)
def _(expr, *o, **kwargs):
    if kwargs['var'] == expr.value:
        return Number(1.0)
    else:
        return Number(0.0)


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return postvisitor(expr.operands[0], differentiate, **kwargs) + \
     postvisitor(expr.operands[1], differentiate, **kwargs)


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return postvisitor(expr.operands[0], differentiate, **kwargs) - \
        postvisitor(expr.operands[1], differentiate, **kwargs)


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    m = expr.operands[0]
    n = expr.operands[1]
    dm = postvisitor(m, differentiate, **kwargs)
    dn = postvisitor(n, differentiate, **kwargs)
    if (isinstance(m, Number) and isinstance(n, Symbol)):
        return Add(dm * n, Number(m.value * dn.value))
    elif (isinstance(n, Number) and isinstance(m, Symbol)):
        return Add(Number(dm.value * n.value), m * dn)
    else:
        return Add(dm * n, dn * m)


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (postvisitor(expr.operands[0], differentiate, **kwargs) *
            expr.operands[1] - expr.operands[0] *
            postvisitor(expr.operands[1], differentiate, **kwargs))\
        / Pow((expr.operands[1]), Number(2))


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return expr.operands[1] * \
        (expr.operands[0] ** (expr.operands[1] - Number(1)))
