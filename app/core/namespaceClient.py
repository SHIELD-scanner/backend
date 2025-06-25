import os

from app.core.databaseClient import DatabaseClient
from app.models.namespace import Namespace


class NamespaceClient(DatabaseClient):
    def __init__(self):
        super().__init__()

    def get_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["namespaces"]

    def get_all(self, cluster: str = None):
        query = {}
        if cluster:
            query["cluster"] = cluster
        items = self.get_collection().find(query, {"_id": 0})
        items_list = list(items)
        return [self._format_to_namespace(item) for item in items_list]

    def _format_to_namespace(self, item):
        if "_id" in item:
            item["_id"] = str(item["_id"])
        return Namespace(**item)
