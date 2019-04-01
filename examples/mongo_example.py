import random
import string
import sys

from bson.objectid import ObjectId
from pymongo import MongoClient


if __name__ == '__main__':
    client = MongoClient('some-mongo', 27017)
    coll = client['test-database']['test-collection']

    cmd = sys.argv[1]

    if cmd == 'write':
        data = {
            'random-string': ''.join(
                random.choices(string.ascii_letters + string.digits, k=10))
        }
        print(f'Inserting data: {data}')
        data_id = coll.insert_one(data).inserted_id
        print(f'Data inserted with id: {data_id}')
    elif cmd == 'read':
        _id = sys.argv[2]
        print(f'Retrieving data with _id: {_id}')
        data = coll.find_one({'_id': ObjectId(_id)})
        print(f'Retrieved data: {data}')
    elif cmd == 'list':
        print('Retrieving all data')
        for d in coll.find():
            print(f'Retrieved data: {d}')
    else:
        raise ValueError('Invalid command')
