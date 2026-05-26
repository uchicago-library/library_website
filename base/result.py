"""
This module provides monadic error handling utility functions.
For background, please see:

https://en.wikipedia.org/wiki/Monad_(functional_programming)
"""


def ok(x):
    """
    Create a success value.

    Args:
        x : any piece of data.

    Returns:
        The input value as a success result.
    """
    return {"ok": x}


def error(msg):
    """
    Create a failure value.

    Args:
        msg: an error message.

    Returns:
        A failure result with an error message.
    """
    return {"error": msg}


def is_ok(result):
    """
    Predicate for success results.

    Args:
        result: any result value.

    Returns:
        A bool.
    """
    match result:
        case {"ok": _}:
            return True
        case _:
            return False


def is_error(result):
    """
    Predicate for failure results.

    Args:
        result: any result value.

    Returns:
        A bool.
    """
    match result:
        case {"error": _}:
            return True
        case _:
            return False


class InvalidResult(Exception):
    """
    Exception for data that fails to match either
    { "ok": _ } or {"error": _ }.
    """

    def __init__(self, msg="invalid result value "):
        self.msg = msg
        super().__init__(self.msg)


def rmap(f, result):
    """
    Apply a function inside of a result value.

    Args:
        f: a function with the data inside the result as an input.
        result: any result value.

    Returns:
        The return type of f, as a monadic result value.
    """
    match result:
        case {"ok": x}:
            return ok(f(x))
        case {"error": msg}:
            return {"error": msg}
        case other:
            msg = "invalid result value: %s" % str(other)
            raise InvalidResult(msg)


def product(result1, result2):
    """
    Tuple up result values.

    Args:
        result1: any result value.
        result2: any result value.

    Returns:
        A tuple of the two inputs, as a monadic result value.
    """
    match (result1, result2):
        case ({"ok": ok1}, {"ok": ok2}):
            return {"ok": (ok1, ok2)}
        case ({"error": msg}, _):
            return {"error": msg}
        case (_, {"error": msg}):
            return {"error": msg}
        case (one, two):
            msg = "invalid results: %s and %s" % (str(one), str(two))
            raise InvalidResult(msg)


def bind(result, k):
    """
    Monadic bind for results.

    Args:
        result: any result value.
        k: a Kleisli arrow function.

    Returns:
        The return of k.
    """
    match result:
        case {"ok": x}:
            return k(x)
        case {"error": msg}:
            return {"error": msg}
        case other:
            msg = "invalid result value: %s" % str(other)
            raise InvalidResult(msg)
