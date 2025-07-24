import os

from app.core.databaseClient import DatabaseClient
from app.models.exposedsecret import Exposedsecret


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
        items_list = list(items)

        all_items = []
        for item in items_list:
            exposedsecret = self._format(item)
            if isinstance(exposedsecret, list):
                all_items.extend(exposedsecret)
            elif exposedsecret is not None:
                all_items.append(exposedsecret)

        return all_items

    def get_by_uid(self, uid: str):
        item = self.get_collection().find_one({"_uid": uid}, {"_id": 0})

        if item:
            exposedsecret = self._format(item)
            if isinstance(exposedsecret, list):
                for s in exposedsecret:
                    if s.uid == uid:
                        return s
            else:
                return exposedsecret

        return None

    def _format(self, item):
        if item is None:
            return None

        return (
            Exposedsecret(
                **{
                    "uid": item.get("_uid", ""),
                    "namespace": item.get("_namespace", ""),
                    "cluster": item.get("_cluster", ""),
                }
            )
            if item
            else None
        )
