import os

from app.core.databaseClient import DatabaseClient
from app.models.exposedsecret import ExposedSecret


class ExposedsecretClient(DatabaseClient):
    def __init__(self):
        super().__init__()

    def get_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["exposedsecretreports"]

    def get_all(self, namespace: str = None, cluster: str = None):
        query = {}
        if namespace:
            query["_namespace"] = namespace
        if cluster:
            query["_cluster"] = cluster

        items = self.get_collection().find(query, {"_id": 0})
        formatted_items = (self._format(item) for item in items)
        return [item for item in formatted_items if item is not None]

    def get_by_uid(self, uid: str):
        item = self.get_collection().find_one({"_uid": uid}, {"_id": 0})
        return self._format(item)

    def _format(self, item):
        if item is None:
            return None

        return ExposedSecret(
            uid=item.get("_uid", ""),
            namespace=item.get("_namespace", ""),
            cluster=item.get("_cluster", ""),
        )
