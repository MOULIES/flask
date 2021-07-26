import pytest
from carreseller import app, db
from flask import Flask, session
from .models import User, Car
from difflib import SequenceMatcher
import string
import base64, json
import random
import os
from  .config import TestingConfig

class Test_API:

    client = app.test_client()
    word = ''.join( random.choice(string.ascii_lowercase)  for i in range(10) )
    r1 = random.randint(0,10)

    @pytest.fixture(autouse=True, scope="session")
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()
        yield db
        db.drop_all()

    def test_register_success(self):
        url = "/register"
        payload = '{"name": "'+self.word +'", "password": "' + self.word + '","license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = { "Content-Type" : "application/json" , 'cache-control':'no-cache'}
        response = self.client.post(url, data = payload , headers = headers)
        assert response.status_code == 201
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "User registration successful")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def testLogin(self):
        url ='/login'
        user_credentials = self.word+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('UTF-8')).decode("UTF-8")
        print(user_credentials)
        response = self.client.get(url, headers ={ 'Authorization' : "Basic "+ valid_credentials })
        assert response.status_code == 200
        assert response.json['token']

    def test_user_update_success(self):
        url = '/login'
        user_credentials = self.word+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode("utf-8")
        # print(user_credentials)
        response = self.client.get(url, headers ={'Authorization':"Basic "+valid_credentials})
        assert response.status_code == 200
        token = response.json['token']

        url = '/user/update'
        payload = '{"name": "testtest", "license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = {"Content-Type": "application/json", 'x-access-token': ""+token}
        response = self.client.put(url, data = payload , headers = headers)
        assert response.status_code == 200
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Profile update success")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_user_update_failed_without_token(self):
        url = '/user/update'
        payload = '{"name": "testtest", "license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = {"Content-Type": "application/json"  }
        response = self.client.put(url, data = payload , headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_user_update_failed_with_invalid_token(self):
        url = '/user/update'
        token = 'tests'
        payload = '{"name": "testtest", "license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.put(url, data = payload , headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_user_delete_failure_without_invalid_token(self):
        url = '/user/delete'
        token ='testest'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.delete(url,  headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8


    def test_user_delete_failure_without_missing_token(self):
        url = '/user/delete'
        headers = {"Content-Type": "application/json" }
        response = self.client.delete(url,  headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8
    #
    def test_car_create_success(self):
        url = '/login'
        user_credentials = 'testtest'+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode('UTF-8')
        response = self.client.get(url, headers = {'Authorization': "Basic "+valid_credentials})
        assert response.status_code == 200
        assert response.json['token']
        token = response.json['token']

        url = '/car/create'
        payload = '{"maker":"'+ self.word + '" , "model":"' + self.word + '" , "subModel":"' + self.word + '" , "yearOfMaking":"'+ str(self.r1) + '" , "price":"' + str(self.r1)+ '" , "registration":"' + self.word +'"}'
        headers = {"Content-Type": "application/json" , 'cache-control':'no-cache' , 'x-access-token': ""+token}
        response = self.client.post(url, data = payload , headers = headers)
        assert response.status_code == 201
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Car registration successful")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_car_create_with_missing_and_invalid_tokens(self):
        url = '/car/create'
        payload = '{"name": "testtest", "license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = { "Content-Type": "application/json"  }
        response = self.client.post(url, data = payload , headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8

        token = 'tests'
        # payload = '{"name": "testtest", "license": "' + self.word + '", "mobile":"'+self.word+'"}'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.post(url, data = payload , headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_search_by_registrations(self):
        url = '/login'
        user_credentials = 'testtest'+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode('UTF-8')
        response = self.client.get(url, headers = {'Authorization': "Basic "+valid_credentials})
        assert response.status_code == 200
        assert response.json['token']
        token = response.json['token']

        url = '/car/search?keyword='+self.word
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 200

    def test_search_with_missing_and_invalid_tokens(self):
        url = '/car/search?keyword='+self.word
        headers = {"Content-Type": "application/json"}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8

        token = 'tests'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8


    def test_search_by_maker_and_model(self):
        url = '/login'
        user_credentials = 'testtest'+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode('UTF-8')
        response = self.client.get(url, headers = {'Authorization': "Basic "+valid_credentials})
        assert response.status_code == 200
        assert response.json['token']
        token = response.json['token']

        url = '/car/filter?maker='+self.word+'&model='+ self.word
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 200

    def test_filter_with_missing_and_invalid_tokens(self):
        url = '/car/filter?maker='+self.word+'&model='+ self.word
        headers = {"Content-Type": "application/json"}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8

        token = 'tests'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.get(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8

    def test_car_delete_success(self):
        url = '/login'
        user_credentials = 'testtest'+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode('UTF-8')
        response = self.client.get(url, headers = {'Authorization': "Basic "+valid_credentials})
        assert response.status_code == 200
        assert response.json['token']
        token = response.json['token']

        url = '/car/delete/1'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.delete(url, headers = headers)
        assert response.status_code == 204

    def test_delete_car_with_missing_and_invalid_tokens(self):
        url = '/car/delete/1'
        headers = {"Content-Type": "application/json"}
        response = self.client.delete(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is missing")
        match = round(s.ratio(), 3)
        assert match > 0.8

        token = 'tests'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.delete(url, headers = headers)
        assert response.status_code == 401
        s = SequenceMatcher(lambda x: x == " ", response.json['Message'].strip(), "Token is invalid")
        match = round(s.ratio(), 3)
        assert match > 0.8


    def test_user_delete_success(self):
        url = '/login'
        user_credentials = 'testtest'+":"+self.word
        valid_credentials = base64.b64encode(user_credentials.encode('utf-8')).decode('UTF-8')
        response = self.client.get(url, headers = {'Authorization': "Basic "+valid_credentials})
        assert response.status_code == 200
        assert response.json['token']
        token = response.json['token']

        url = '/user/delete'
        headers = {"Content-Type": "application/json" , 'x-access-token': ""+token}
        response = self.client.delete(url, headers = headers)
        assert response.status_code == 204
