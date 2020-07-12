from django.http import HttpResponseBadRequest, HttpResponseNotModified


class BadRequest(Exception):
    status_code = HttpResponseBadRequest.status_code


class NotModified(Exception):
    status_code = HttpResponseNotModified.status_code


class Forbidden(Exception):
    pass


class BadParameters(Exception):
    pass
