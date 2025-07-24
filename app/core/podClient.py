import os

from app.core.databaseClient import DatabaseClient
from app.models.pod import Pod


class PodClient(DatabaseClient):
    def __init__(self):
        super().__init__()

    def get_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["pods"]

    def get_all(self, namespace: str = None, cluster: str = None):
        query = {}
        if namespace:
            query["namespace"] = namespace
        if cluster:
            query["cluster"] = cluster

        items = self.get_collection().find(query, {"_id": 0})
        formatted_items = (self._format_to_pod(item) for item in items)
        return [item for item in formatted_items if item is not None]

    def get_by_name(self, cluster: str, namespace: str, name: str):
        item = self.get_collection().find_one(
            {"name": name, "namespace": namespace, "cluster": cluster}, {"_id": 0}
        )
        return self._format_to_pod(item)

    def get_by_namespace(self, cluster: str, namespace: str):
        items = self.get_collection().find(
            {"namespace": namespace, "cluster": cluster}, {"_id": 0}
        )
        formatted_items = (self._format_to_pod(item) for item in items)
        return [item for item in formatted_items if item is not None]

    def get_by_cluster(self, cluster: str):
        items = self.get_collection().find({"cluster": cluster}, {"_id": 0})
        formatted_items = (self._format_to_pod(item) for item in items)
        return [item for item in formatted_items if item is not None]

    def _format_to_pod(self, item):
        if item is None:
            return None

        if "_id" in item:
            item["_id"] = str(item["_id"])

        return Pod(**item)
