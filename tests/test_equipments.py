import pytest
from flask_migrate import Migrate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from apis.app import create_app
from apis.models.model import db
from apis.models.vessel import vessel
from apis.models.equipment import equipment
from sqlalchemy import func, or_


@pytest.fixture(scope="module")
def app():
    app = create_app(test_config=True)
    
    with app.app_context():
        db.create_all()
        Migrate(app, db)
        vessel_obj1 = vessel(code='MV102')
        vessel_obj2 = vessel(code='MV101')
        db.session.add(vessel_obj1)
        db.session.add(vessel_obj2)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

def test_insert_clean_db(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1
        assert query_results[0][0].vessel_id == 1
        assert query_results[0][0].code == '5310B9D7'
        assert query_results[0][0].location == 'brazil'
        assert query_results[0][0].active
        assert query_results[0][0].name == 'compressor'

def test_insert_without_vessel_code(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_code(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_location(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'name':'compressor'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_without_name(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil'})
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_replicated(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'REPEATED_CODE'
    assert result.status_code == 409
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_replicated_in_different_vessel(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV101', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'REPEATED_CODE'
    assert result.status_code == 409
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_no_vessel_in_system(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV109', 'code':'5310B9D7', 'location':'brazil', 'name':'compressor'})
    assert result.get_json().get('message') == 'NO_VESSEL'
    assert result.status_code == 409
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 1

def test_insert_second_equipment_in_a_vessel(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV102', 'code':'5310B9D8', 'location':'usa', 'name':'electric_panel'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 2
        assert query_results[0][0].vessel_id == 1
        assert query_results[0][0].code == '5310B9D7'
        assert query_results[0][0].location == 'brazil'
        assert query_results[0][0].active
        assert query_results[0][0].name == 'compressor'
        assert query_results[1][0].vessel_id == 1
        assert query_results[1][0].code == '5310B9D8'
        assert query_results[1][0].location == 'usa'
        assert query_results[1][0].active
        assert query_results[1][0].name == 'electric_panel'

def test_insert_second_equipment_in_a_different_vessel(app):
    result = app.test_client().post('/equipment/insert_equipment', json={'vessel_code':'MV101', 'code':'5310B9D9', 'location':'china', 'name':'compressor'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment)
        query_results = db.session.execute(query).all()
        assert len(query_results) == 3
        assert query_results[2][0].vessel_id == 2
        assert query_results[2][0].code == '5310B9D9'
        assert query_results[2][0].location == 'china'
        assert query_results[2][0].active
        assert query_results[2][0].name == 'compressor'

def test_update_an_equipment(app):
    result = app.test_client().put('/equipment/update_equipment_status', json={'code':'5310B9D7'})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment).filter(equipment.code=='5310B9D7')
        query_results = db.session.execute(query).all()
        assert not query_results[0][0].active

def test_update_an_equipment_without_code(app):
    result = app.test_client().put('/equipment/update_equipment_status')
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400

def test_update_an_equipment_not_in_system(app):
    result = app.test_client().put('/equipment/update_equipment_status', json={'code':'5312B9D5'})
    assert result.get_json().get('message') == 'NO_CODE'
    assert result.status_code == 409

def test_update_an_list_of_equipment(app):
    result = app.test_client().put('/equipment/update_equipment_status', json={'code':['5310B9D8', '5310B9D9']})
    assert result.get_json().get('message') == 'OK'
    assert result.status_code == 201
    with app.app_context():
        query = db.session.query(equipment).filter(or_(equipment.code=='5310B9D8', equipment.code=='5310B9D9'))
        query_results = db.session.execute(query).all()
        assert not query_results[0][0].active
        assert not query_results[1][0].active

def test_get_list_of_active_one_equipment(app):
    with app.app_context():
        vessel_obj = vessel(code='MV103')
        db.session.add(vessel_obj)
        db.session.commit()
        equipment_obj = equipment(vessel_id=3, code='5310B9D1', location='brazil', name='compressor', active=True)
        db.session.add(equipment_obj)
        db.session.commit()

    result = app.test_client().get('/equipment/active_equipments?vessel_code=MV103')
    assert len(result.get_json().get('equipments')) == 1
    assert result.get_json().get('equipments')[0].get('code') == '5310B9D1'
    assert result.get_json().get('equipments')[0].get('name') == 'compressor'
    assert result.get_json().get('equipments')[0].get('location') == 'brazil'
    assert result.status_code == 200

def test_get_list_of_active_two_equipment(app):
    with app.app_context():
        equipment_obj = equipment(vessel_id=3, code='5310B9D2', location='china', name='motor', active=True)
        db.session.add(equipment_obj)
        db.session.commit()

    result = app.test_client().get('/equipment/active_equipments?vessel_code=MV103')
    assert len(result.get_json().get('equipments')) == 2
    assert result.get_json().get('equipments')[0].get('code') == '5310B9D1'
    assert result.get_json().get('equipments')[0].get('name') == 'compressor'
    assert result.get_json().get('equipments')[0].get('location') == 'brazil'
    assert result.get_json().get('equipments')[1].get('code') == '5310B9D2'
    assert result.get_json().get('equipments')[1].get('name') == 'motor'
    assert result.get_json().get('equipments')[1].get('location') == 'china'
    assert result.status_code == 200

def test_get_list_of_active_equipment_no_vessel(app):
    result = app.test_client().get('/equipment/active_equipments?vessel_code=MV105')
    assert result.get_json().get('message') == 'NO_VESSEL'
    assert result.status_code == 409

def test_get_list_of_active_equipment_no_parameter(app):
    result = app.test_client().get('/equipment/active_equipments')
    assert result.get_json().get('message') == 'MISSING_PARAMETER'
    assert result.status_code == 400

def test_get_list_no_active_equipment_vessel(app):
    result = app.test_client().get('/equipment/active_equipments?vessel_code=MV102')
    assert len(result.get_json().get('equipments')) == 0
    assert result.status_code == 200

