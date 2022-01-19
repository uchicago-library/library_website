# MT 3/3/2021: The error handling for the digital collections site is getting
# hairy enough that I think it might be useful to start adopting a monadic
# error handling regimen.  This is a quick/simple sketch of a library that we
# can start using for that, should we decide to move toward that design.


from functools import reduce
import requests


class Result():

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

    class Validations():

        def check_type(result):
            try:
                (r, v) = result
                _ = r.is_ok
                _ = r.is_error
                return result
            except (TypeError, AttributeError, ValueError):
                return Result.error(
                    TypeError("Result: input must be a result tuple")
                )

    def is_ok(result, check_type=True):
        if check_type:
            (r, v) = Result.Validations.check_type(result)
            return r.is_ok
        else:
            (r, v) = result
            return r.is_ok

    def is_error(result, check_type=True):
        if check_type:
            (r, v) = Result.Validations.check_type(result)
            return r.is_error
        else:
            (r, v) = result
            return r.is_error

    def bind(mx, kleisli, check_type=True):
        if check_type:
            val = Result.Validations.check_type(mx)
        else:
            val = mx
        if Result.is_ok(val, check_type=check_type):
            (r, v) = val
            return kleisli(v)
        else:
            return val

    def map_error(f, result, check_type=True):
        if check_type:
            val = Result.Validations.check_type(result)
        else:
            val = result
        (r, v) = val
        if Result.is_ok(val):
            return result
        elif Result.is_error(val):
            return Result.error(f(v))
        else:
            return Result.error(
                Exception("Result: invalid data formatting")
            )


    def kleisli_fish(mf, mg, check_type=True):
        def partial(x):
            return Result.bind(mf(x),
                               mg,
                               check_type=check_type)
        return partial

    def multibind(mx, *kleislis, check_type=True):
        if check_type:
            return Result.bind(mx,
                               reduce(Result.kleisli_fish,
                                      kleislis),
                               check_type=check_type)
        else:
            return Result.bind(mx,
                               reduce(Result.kleisli_fish,
                                      kleislis),
                               check_type=check_type)

    def multimap(x, *kleislis, check_type=True):
        return Result.multibind(Result.pure(x),
                                *kleislis,
                                check_type=check_type)

    class Catch():

        def catch(f, x):
            try:
                val = f(x)
                return Result.ok(val)
            except Exception as e:
                return Result.error(e)

        def lookup(key, dct):
            def getter(key):
                def partial(dct):
                    return dct[key]
                return partial
            return Result.Catch.catch(getter(key), dct)

        def default(result, defval='', debug=False):
            (tag, val) = result
            if Result.is_ok(result, check_type=False):
                return val
            elif Result.is_error(result, check_type=False):
                if debug:
                    return val
                else:
                    return defval

        def get_request(url, **kwargs):
            return(Result.Catch.catch(requests.get,
                                      url,
                                      **kwargs))

    catch = Catch.catch
    lookup = Catch.lookup
    default = Catch.default
    get_request = Catch.get_request


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
