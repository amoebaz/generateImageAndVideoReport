from pymongo import MongoClient

from collections import OrderedDict


def connect_to_database():
#    client = pymongo.MongoClient("mongodb://localhost:27017/")
#    db = client["imagesAndVideos"]

    db = MongoClient("mongodb://localhost:27017/")['imagesAndVideos']

    user_schema = {
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

    collection = 'metadata'
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

    print(query)

    try:
        db.create_collection(collection)
    except Exception as e:
        print(e)
        pass

    command_result = db.command(OrderedDict(query))

    print(command_result)
    return db['metadata']


def insert_data(collection, data):
    s = {}
    last_id = 0
    try:
        for x in collection.find({}, {"_miid":1}) \
            .sort("_miid", -1) \
            .limit(1):
            print(x['_miid'])
            last_id = int(x['_miid'])
    except Exception as e:
        print(e)
        pass
    s = {'_miid': last_id+1, '_field':str(data[1]), '_value':str(data[2])}
    collection.insert_one(s)
    
