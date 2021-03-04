# MT 3/3/2021: The error handling for the digital collections site is getting
# hairy enough that I think it might be useful to start adopting a monadic
# error handling regimen.  This is a quick/simple sketch of a library that we
# can start using for that, should we decide to move toward that design.


from functools import reduce


class Ok():

    def __init__(self):
        self.is_ok = True
        self.is_error = False

    def __repr__(self):
        return "ok"


class Error():

    def __init__(self):
        self.is_error = True
        self.is_ok = False

    def __repr__(self):
        return "error"


def ok(val):
    return (Ok(), val)


def error(val):
    return (Error(), val)


def bind(mx, kleisli):
    if mx[0].is_ok:
        return kleisli(mx[1])
    elif mx[0].is_error:
        return mx
    else:
        raise Exception("Either: invalid data formatting")


def kleisli_fish(mf, mg):
    def partial(x):
        return bind(mf(x), mg)
    return partial


def multibind(mx, *kleislis):
    return bind(mx, reduce(kleisli_fish, kleislis))


class Examples():
    """
    Namespace class containing values for testing only.
    """
    def safeDiv(n, m):
        if m == 0:
            return error("Error: divide by zero")
        else:
            return ok(int(n / m))

    def isEven(n):
        if n % 2 == 0:
            return ok(n)
        else:
            return error("Error: must be even")

    def isPositive(n):
        if n > 0:
            return ok(n)
        else:
            return error("Error: must be positive")
