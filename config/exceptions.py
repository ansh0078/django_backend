from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Wraps DRF's default exception handler to always return a consistent
    { "success": false, "message": str, "errors": {...} } shape, so the
    Flutter client can parse errors uniformly regardless of which endpoint failed.
    """
    response = exception_handler(exc, context)

    if response is not None:
        errors = response.data
        message = "Request failed"

        if isinstance(errors, dict):
            # pull out first message for a friendly top-level "message"
            for key, value in errors.items():
                if isinstance(value, list) and value:
                    message = str(value[0])
                elif isinstance(value, str):
                    message = value
                break
        elif isinstance(errors, list) and errors:
            message = str(errors[0])

        response.data = {
            "success": False,
            "message": message,
            "errors": errors,
        }
        return response

    # Unhandled exceptions (500s) - never leak stack traces to the client
    return Response(
        {"success": False, "message": "Internal server error", "errors": {}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
