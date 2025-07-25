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
            query["_cluster"] = cluster

        items = self.get_collection().find(query, {"_id": 0})
        formatted_items = (self._format_to_namespace(item) for item in items)
        return [item for item in formatted_items if item is not None]

    def _format_to_namespace(self, item):
        if item is None:
            return None

        return Namespace(
            cluster=item.get("_cluster", ""),
            name=item.get("_name", ""),
            uid=item.get("_uid", ""),
        )
