from backend.tina.store.mongo_store_base import MongoDBStoreBase

store = MongoDBStoreBase()


def test():
    result = store.find_many("messages", {})
    print(result)


if __name__ == '__main__':
    test()
