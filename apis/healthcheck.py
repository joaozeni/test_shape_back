from flask import Blueprint

healthcheck_blueprint = Blueprint('healthcheck', __name__)


@healthcheck_blueprint.route('/', methods=['GET'])
def healthcheck():

    """Checks if the system is alive
        ---
        responses:
          200:
            description: OK if the system is alive
    """
    return 'OK', 200

