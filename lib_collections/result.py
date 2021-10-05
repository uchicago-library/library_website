# MT 3/3/2021: The error handling for the digital collections site is getting
# hairy enough that I think it might be useful to start adopting a monadic
# error handling regimen.  This is a quick/simple sketch of a library that we
# can start using for that, should we decide to move toward that design.


from functools import reduce
import requests


class Result:

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
        return (Result.Ok(), val)

    pure = ok

    def error(val):
        return (Result.Error(), val)

    def is_ok(result):
        (r, v) = result
        return r.is_ok

    def is_error(result):
        (r, v) = result
        return r.is_error

    def bind(mx, kleisli):
        if Result.is_ok(mx):
            (r, v) = mx
            return kleisli(v)
        elif Result.is_error(mx):
            return mx
        else:
            raise Exception("Result: invalid data formatting")

    def kleisli_fish(mf, mg):
        def partial(x):
            return Result.bind(mf(x), mg)
        return partial

    def multibind(mx, *kleislis):
        return Result.bind(mx, reduce(Result.kleisli_fish, kleislis))

    def multimap(x, *kleislis):
        return Result.multibind(Result.pure(x), *kleislis)

    def get(url):
        try:
            r = requests.get(url)
            return Result.ok(r)
        except Exception as e:
            return Result.error(e)

    def map_error(result, f):
        (r, v) = result
        if result.is_ok:
            return result
        elif result.is_error:
            return Result.error(f(v))
        else:
            raise Exception("Result: invalid data formatting")


class Examples():
    """
    Namespace class containing values for testing only.
    """
    def safeDiv(n, m):
        if m == 0:
            return Result.error("Error: divide by zero")
        else:
            return Result.ok(int(n / m))

    def isEven(n):
        if n % 2 == 0:
            return Result.ok(n)
        else:
            return Result.error("Error: must be even")

    def isPositive(n):
        if n > 0:
            return Result.ok(n)
        else:
            return Result.error("Error: must be positive")
