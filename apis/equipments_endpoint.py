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
            description: returns OK if the equipment was correctly inserted
          400:
            description: returns MISSING_PARAMETER if any parameter is not sent
          400:
            description: returns WRONG_FORMAT if any parameter are sent in the wrong format
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
    
    if type(vessel_code) != str or type(code) != str or type(name) != str or type(location) != str:
        return {'message':'WRONG_FORMAT'}, 400
    
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

@equipments_blueprint.route('/update_equipment_status', methods=['PUT'])
def update_equipment_status():
    """Set a equipment or a list of those to inactive
        ---
        parameters:
            - name: code
              in: body
              type: string
              required: true
        responses:
          201:
            description: returns OK if the equipments were correctly updated
          400:
            description: returns MISSING_PARAMETER if any parameter is not sent
          400:
            description: returns WRONG_FORMAT if any parameter are sent in the wrong format
          409:
            description: returns NO_CODE if the equipment code is not already in the system
    """
    req_json = request.get_json()
    if not req_json or not req_json.get('code'):
        return {'message':'MISSING_PARAMETER'}, 400
    
    code = req_json.get('code')
    
    if type(code) != str and type(code) != list:
        return {'message':'WRONG_FORMAT'}, 400

    if type(code) == str:
        code = [code]
    
    equipment_in_the_system = db.session.query(equipment.id).filter(equipment.code.in_(code)).count()
    if not equipment_in_the_system:
        return {'message':'NO_CODE'}, 409

    update_equipments = db.session.query(equipment).filter(equipment.code.in_(code)).update({'active':False})
    db.session.commit()

    return {'message':'OK'}, 201

@equipments_blueprint.route('/active_equipments', methods=['GET'])
def active_equipment():
    """Return the list of active equipments of a vessel
        ---
        parameters:
            - name: vessel_code
              in: query
              type: string
              required: true
        responses:
          200:
            description: returns a json with equipments key and a list of equipments
          400:
            description: returns MISSING_PARAMETER if the vessel_code is not sent
          400:
            description: returns WRONG_FORMAT if any parameter are sent in the wrong format
          409:
            description: returns NO_VESSEL if the vessel is not already in the system
    """
    req_args = request.args
    if not req_args or not req_args.get('vessel_code'):
        return {'message':'MISSING_PARAMETER'}, 400
    
    vessel_code = req_args.get('vessel_code')
    
    vessel_query = db.session.query(vessel.id).filter(vessel.code==vessel_code)
    query_results = db.session.execute(vessel_query).all()
    if not len(query_results):
        return {'message':'NO_VESSEL'}, 409
    
    equipments = db.session.query(equipment).filter(equipment.vessel_id==query_results[0][0]).filter(equipment.active==True).all()

    equipment_json = {'equipments':[]}

    for equipment_obj in equipments:
        equipment_json['equipments'].append({'code':equipment_obj.code, 'name':equipment_obj.name, 'location':equipment_obj.location})

    return equipment_json, 200

