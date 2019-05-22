class Error(Exception):
    err_name = "Error"
    status_code = 500
    message = ""

    def __init__(self, message=None):
        if message is not None:
            self.message = message

    def to_dict(self):
        return {"message": self.message, "error_name": self.err_name}


# Exceptions which inherit from Error go here.
# Note that they will only be handled correctly if
# the included app errorhandler is used, or if whatever
# application mounts the blueprint implements a similar
# error handler.


class NoCollectionFoundError(Error):
    err_name = "NoCollectionFoundError"
    status_code = 404


class InvalidCollectionRecordError(Error):
    err_name = "InvalidCollectionRecordError"
    status_code = 500


class NoCollectionParameterError(Error):
    err_name = "NoCollectionParameterError"
    status_code = 500
    message = "You don't appear to have included " + \
        "a collection record query parameter (and no " + \
        "default is set)."


class IncompatibleRecordError(Error):
    err_name = "IncompatibleRecordError"
    status_code = 500
    message = "That record appears to be incompatible " + \
        "with this interface, sorry!"
