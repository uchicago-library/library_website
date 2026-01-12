# MT 3/3/2021: The error handling for the digital collections site is getting
# hairy enough that I think it might be useful to start adopting a monadic
# error handling regimen.  This is a quick/simple sketch of a library that we
# can start using for that, should we decide to move toward that design.


from functools import reduce

import requests


class Either:

    class Ok:

        def __init__(self):
            self.is_ok = True
            self.is_error = False

        def __repr__(self):
            return "ok"

    class Error:

        def __init__(self):
            self.is_error = True
            self.is_ok = False

        def __repr__(self):
            return "error"

    def ok(val):
        return (Either.Ok(), val)

    def error(val):
        return (Either.Error(), val)

    def bind(mx, kleisli):
        if mx[0].is_ok:
            return kleisli(mx[1])
        elif mx[0].is_error:
            return mx
        else:
            raise Exception("Either: invalid data formatting")

    def kleisli_fish(mf, mg):
        def partial(x):
            return Either.bind(mf(x), mg)

        return partial

    def multibind(mx, *kleislis):
        return Either.bind(mx, reduce(Either.kleisli_fish, kleislis))

    def get(url):
        try:
            r = requests.get(url)
            return Either.ok(r)
        except Exception as e:
            return Either.error(e)

    def map_error(either, f):
        if either.is_ok:
            return either
        elif either.is_error:
            return Either.error(f(either[1]))
        else:
            raise Exception("Either: invalid data formatting")


class Examples:
    """
    Namespace class containing values for testing only.
    """

    def safeDiv(n, m):
        if m == 0:
            return Either.error("Error: divide by zero")
        else:
            return Either.ok(int(n / m))

    def isEven(n):
        if n % 2 == 0:
            return Either.ok(n)
        else:
            return Either.error("Error: must be even")

    def isPositive(n):
        if n > 0:
            return Either.ok(n)
        else:
            return Either.error("Error: must be positive")
