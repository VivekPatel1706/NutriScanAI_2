from pymongo import MongoClient, DESCENDING, ASCENDING

def verify_credentials(url, db, collection, username, password):
    try:
        client = MongoClient(url)

        db = client[db]
        collection = db[collection]

        user = collection.find_one({'username': username, 'password': password})

        return user is not None

    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
        return False

def retrieve_data(url, db_name, collection_name, single=False, field=None, sort_by=None, ascending=True, limit=None):
    try:
        client = MongoClient(url)
        db = client[db_name]
        collection = db[collection_name]
        
        sort_order = ASCENDING if ascending else DESCENDING

        if field:
            documents = collection.distinct(field)
        elif single:
            documents = collection.find_one()
        else:
            query = collection.find()
            if limit:
                query = query.limit(limit)
            if sort_by:
                query = query.sort(sort_by, sort_order)
            documents = list(query)

        return documents

    except Exception as e:
        print(f"Error while retrieving data: {e}")
        return None


def insert_data(url, db, collection, object):
    try:
        client = MongoClient(url)

        db = client[db]
        collection = db[collection]

        collection.insert_one(object)

        return True
    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
        return False

def retrive_count(url, db, collection, obj):
    try:
        client = MongoClient(url)

        db = client[db]
        collection = db[collection]

        count = collection.count_documents(obj)

        return count
    except ConnectionError as e:
        print(f"Could not connect to MongoDB: {e}")
        return False
