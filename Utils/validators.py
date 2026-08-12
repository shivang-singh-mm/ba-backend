from marshmallow import ValidationError
from flask import request


def validate_request(schema_class):
    """
    Validate incoming JSON request body against a Marshmallow schema.

    Returns:
        Validated data dict on success.
    Raises:
        ValidationError if validation fails.
    """
    schema = schema_class()
    data = request.get_json(silent=True) or {}
    return schema.load(data)


def validate_query_params(schema_class):
    """
    Validate query string parameters against a Marshmallow schema.

    Returns:
        Validated args dict on success.
    Raises:
        ValidationError if validation fails.
    """
    schema = schema_class()
    return schema.load(request.args.to_dict())
