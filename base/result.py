############ monadic error handling utility functions ################


def ok(x):
    return { "ok": x }


def error(msg):
    return { "error": msg }


def is_ok(result):
    match result:
        case { "ok": _ }:
            return True
        case _:
            return False


def is_error(result):
    match result:
        case { "error": _ }:
            return True
        case _:
            return False


class InvalidResult(Exception):
    def __init__(self, msg="invalid result value "):
        self.msg = msg
        super().__init__(self.msg)


def rmap(f, result):
    match result:
        case { "ok": x }:
            return ok(f(x))
        case { "error": msg }:
            return { "error": msg }
        case other:
            msg = "invalid result value: %s" % str(other)
            raise InvalidResult(msg)


def product(result1, result2):
    match (result1, result2):
        case ({ "ok": ok1 }, {"ok": ok2 }):
            return { "ok": (ok1, ok2) }
        case ({ "error": msg }, _):
            return { "error": msg }
        case (_, { "error": msg }):
            return { "error": msg }
        case (one, two):
            msg = "invalid results: %s and %s" % (str(one),
                                                   str(two))
            raise InvalidResult(msg)


def bind(result, k):
    match result:
        case { "ok": x }:
            return k(x)
        case { "error": msg }:
            return { "error": msg }
        case other:
            msg = "invalid result value: %s" % str(other)
            raise InvalidResult(msg)
