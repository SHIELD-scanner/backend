import os

from app.core.databaseClient import DatabaseClient
from app.models.sbom import Sbom


class SbomClient(DatabaseClient):
    def __init__(self):
        super().__init__()

    def get_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["sbomreports"]

    def get_all(self, namespace: str = None, cluster: str = None):
        query = {}
        if namespace:
            query["_namespace"] = namespace
        if cluster:
            query["_cluster"] = cluster

        items = self.get_collection().find(query, {"_id": 0})
        print(items)
        items_list = list(items)

        all_items = []
        for item in items_list:
            sbom = self._format(item)
            if isinstance(sbom, list):
                all_items.extend(sbom)
            elif sbom is not None:
                all_items.append(sbom)

        return all_items

    def get_by_uid(self, uid: str):

        item = self.get_collection().find_one({"_uid": uid}, {"_id": 0})

        if item:
            sbom = self._format(item)
            if isinstance(sbom, list):
                # If _format returns a list, find the item with matching uid
                for s in sbom:
                    if s.uid == uid:
                        return s
            else:
                return sbom

        return None

    def _format(self, item):
        if item is None:
            return None

        return (
            Sbom(
                **{
                    "uid": item.get("_uid", ""),
                    "namespace": item.get("_namespace", ""),
                    "cluster": item.get("_cluster", ""),
                }
            )
            if item
            else None
        )
