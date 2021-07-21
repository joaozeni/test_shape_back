from flask import Blueprint, request, jsonify
from sqlalchemy import func, extract, and_

from apis.models.equipment import equipment
from apis.models.vessel import vessel
from apis.models.model import db


equipments_blueprint = Blueprint('equipments', __name__)


@equipments_blueprint.route('/insert_equipment', methods=['POST'])
def insert_equipment():

    """Insert a new equipment
        ---
        parameters:
            - name: vessel_code
              in: body
              type: string
              required: true
            - name: code
              in: body
              type: string
              required: true
            - name: name
              in: body
              type: string
              required: true
            - name: location
              in: body
              type: string
              required: true
        responses:
          201:
            description: returns OK if the vessel was correctly inserted
          400:
            description: returns MISSING_PARAMETER if any parameter is not sent
          409:
            description: returns REPEATED_CODE if the equipment code is already in the system
          409:
            description: returns NO_VESSEL if the vessel code is not already in the system
    """
    req_json = request.get_json()
    if not req_json or not req_json.get('vessel_code') or not req_json.get('code') or not req_json.get('name') or not req_json.get('location'):
        return {'message':'MISSING_PARAMETER'}, 400
    
    vessel_code = req_json.get('vessel_code')
    code = req_json.get('code')
    name = req_json.get('name')
    location = req_json.get('location')
    
    vessel_query = db.session.query(vessel.id).filter(vessel.code==vessel_code)
    query_results = db.session.execute(vessel_query).all()
    if not len(query_results):
        return {'message':'NO_VESSEL'}, 409
    
    equipment_in_the_system = db.session.query(equipment.id).filter(equipment.code==code).count()
    if equipment_in_the_system:
        return {'message':'REPEATED_CODE'}, 409

    equipment_obj = equipment(vessel_id=query_results[0][0], code=code, name=name, location=location, active=True)
    db.session.add(equipment_obj)
    db.session.commit()

    return {'message':'OK'}, 201
