from flask import Blueprint, request, jsonify
from sqlalchemy import func, extract, and_

from apis.models.vessel import vessel
from apis.models.model import db


vessels_blueprint = Blueprint('vessels', __name__)


@vessels_blueprint.route('/insert_vessel', methods=['POST'])
def insert_vessel():

    """Insert a new vessel
        ---
        parameters:
            - name: code
              in: body
              type: string
              required: true
        responses:
          201:
            description: returns OK if the vessel was correctly inserted
          400:
            description: returns MISSING_PARAMETER if the vessel code is not sent
          400:
            description: returns WRONG_FORMAT if any parameter are sent in the wrong format
          409:
            description: returns FAIL if the vessel code is already in the system
    """
    req_json = request.get_json()
    if not req_json or not req_json.get('code'):
        return {'message':'MISSING_PARAMETER'}, 400
    
    code = req_json.get('code')
    
    if type(code) != str:
        return {'message':'WRONG_FORMAT'}, 400
    
    in_the_system = db.session.query(vessel.id).filter(vessel.code==code).count()
    
    if in_the_system:
        return {'message':'FAIL'}, 409

    vessel_obj = vessel(code=code)
    db.session.add(vessel_obj)
    db.session.commit()

    return {'message':'OK'}, 201
