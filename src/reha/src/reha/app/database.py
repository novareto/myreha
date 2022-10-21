from pymongo import MongoClient
from reha.app.models import ModelInfo


class DatabaseConnection:

    def __init__(self, client: MongoClient, name: str = 'default'):
        self.client = client
        self.dbname = name

    @property
    def database(self):
        return self.client[self.dbname]

    def get_table(self, name):
        return self.database[name]

    def initialize(self, models):
        db = self.client[self.dbname]
        for model in models:
            if model.metadata.indexes:
                db[model.table].create_indexes([*model.metadata.indexes])
