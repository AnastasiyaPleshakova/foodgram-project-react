from rest_framework import status
from rest_framework.exceptions import APIException, _get_error_details


class ChangeResponseStatusValidationError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]
        self.detail = _get_error_details(detail, code)
