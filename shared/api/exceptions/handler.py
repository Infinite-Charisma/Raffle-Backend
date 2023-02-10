from flask import jsonify

from .api_exception import ApiException


def handle_api_exception(e: ApiException):
    return jsonify({
        "code": e.code,
        "reason": e.reason
    }), e.code


def handle_exception(e: Exception):
    return jsonify({
        "code": 500,
        "reason": str(e)
    }), 500
