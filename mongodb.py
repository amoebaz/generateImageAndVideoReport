from pymongo import MongoClient

from collections import OrderedDict
from datetime import datetime

class MongoDB():

    db_name = None
    collection_metadata = None
    collection_project = None
    collection_file = None


    def __init__(self, db_name):
        self.db_name = db_name


    def connect_to_database(self):
    #    client = pymongo.MongoClient("mongodb://localhost:27017/")
    #    db = client["imagesAndVideos"]
        db = MongoClient("mongodb://localhost:27017/")[self.db_name]


        # Project schema
        project_schema = {
            '_pid': {
                'type': 'int',
                'required': True
            },
            '_name': {
                'type': 'string',
                'required': True
            },
            '_date': { 
                'type': 'string',
                'required': True
            }
        }

        self.create_schema(db, 'project', project_schema)
        self.collection_project = db['project']

        # File schema
        file_schema = {
            '_fid': {
                'type': 'int',
                'required': True
            },
            '_pid': {
                'type': 'int',
                'required': True
            },
            '_name': {
                'type': 'string',
                'required': True
            },
            '_type': {
                'type': 'string',
                'required': True
            },
            '_fullpath': {
                'type': 'string',
                'required': True
            },
            '_value': { 
                'type': 'string',
                'required': False
            },
            '_selected': { 
                'type': 'bool',
                'required': False,
                'default': 'true'
            }    }

        self.create_schema(db, 'file', file_schema)
        self.collection_file = db['file']

        # Metadata schema definition and creation
        metadata_schema = {
            '_fid': {
                'type': 'int',
                'required': True
            },
            '_miid': {
                'type': 'int',
                'required': True
            },
            '_field': {
                'type': 'string',
                'required': True
            },
            '_value': { 
                'type': 'string',
                'required': False
            }
        }

        self.create_schema(db, 'metadata', metadata_schema)
        self.collection_metadata = db['metadata']

        return db['metadata']

    def create_schema(self, db, collection, user_schema):
        validator = {'$jsonSchema': {'bsonType': 'object', 'properties': {}}}
        required = []
    #    collection_metadata = db["metadata"]

        for field_key in user_schema:
            field = user_schema[field_key]
            properties = {'bsonType': field['type']}
            minimum = field.get('minlength')

            if type(minimum) == int:
                properties['minimum'] = minimum

            if field.get('required') is True: required.append(field_key)

            validator['$jsonSchema']['properties'][field_key] = properties

        if len(required) > 0:
            validator['$jsonSchema']['required'] = required

        query = [('collMod', collection),
                ('validator', validator)]

        #print(query)

        try:
            db.create_collection(collection)
        except Exception as e:
            print(e)
            pass

        command_result = db.command(OrderedDict(query))
        return command_result

    def insert_project(self, project_name):
        #print("--------------")
        #print(self.collection_project)
        #print("--------------")
        s = {}
        last_id = 0
        try:
            for x in self.collection_project.find({}, {"_pid":1}) \
                .sort("_pid", -1) \
                .limit(1):
#                print(x['_pid'])
                last_id = int(x['_pid'])
        except Exception as e:
            print("[insert_project] " + str(e))
            pass
#        d = datetime.strptime(datetime.now(), "%Y-%m-%dT%H:%M:%S.000Z")
        d = datetime.now
        s = {'_pid': last_id+1, '_name':str(project_name), '_date':str(d)}
        self.collection_project.insert_one(s)
        return last_id+1

    def insert_file(self, project_id, file_name, file_type):
        s = {}
        last_id = 0
        try:
            for x in self.collection_file.find({}, {"_fid":1}) \
                .sort("_fid", -1) \
                .limit(1):
#                print(x['_fid'])
                last_id = int(x['_fid'])
        except Exception as e:
            print("[insert_file] " + str(e))
            pass

        fileName = file_name.split("/")[-1]

        s = {'_fid': last_id+1, '_pid': project_id, '_name':str(fileName), '_type': str(file_type), '_fullpath':str(file_name)}
        self.collection_file.insert_one(s)
        return last_id+1

    def insert_metadata(self, fid, data):
        s = {}
        last_id = 0
        try:
            for x in self.collection_metadata.find({}, {"_miid":1}) \
                .sort("_miid", -1) \
                .limit(1):
#                print(x['_miid'])
                last_id = int(x['_miid'])
        except Exception as e:
            print("[insert_metadata] " + str(e))
            pass
        s = {'_fid': fid, '_miid': last_id+1, '_field':str(data[1]), '_value':str(data[2])}
        self.collection_metadata.insert_one(s)
        
