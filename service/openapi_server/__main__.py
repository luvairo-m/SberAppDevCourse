#!/usr/bin/env python3

import connexion
from connexion.exceptions import Unauthorized
from connexion.jsonifier import Jsonifier
from connexion.problem import problem

from openapi_server import encoder


def unauthorized_response(_request, error):
    response = error.to_problem()
    response.headers["WWW-Authenticate"] = 'Bearer realm="workshop"'
    return response


def not_found_response(_request, error):
    return problem(
        status=404,
        title="Not Found",
        detail=error.detail,
        headers={"Cache-Control": "no-store"},
    )


def main():
    app = connexion.FlaskApp(__name__, specification_dir='./openapi/')
    app.add_error_handler(Unauthorized, unauthorized_response)
    app.add_error_handler(404, not_found_response)
    app.add_api('openapi.yaml',
                arguments={'title': 'API автомастерской'},
                pythonic_params=True,
                jsonifier=Jsonifier(cls=encoder.JSONEncoder))

    app.run(port=8080)


if __name__ == '__main__':
    main()
