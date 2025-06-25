import os

from pymongo import MongoClient

from app.models.vulnerability import Vulnerability


class DatabaseClient:
    def __init__(self):
        self.client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))

    def get_namespace_collection(self):
        return self.client[os.getenv("MONGODB_DB", "trivy")]["namespaces"]

    def get_pods_collection(self):
        return self.client[os.getenv("MONGODB_DB", "trivy")]["pods"]

    def get_reports_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["reports"]

    def get_vulnerabilities_collection(self):
        return self.client[os.getenv("MONGODB_DB", "shield")]["vulnerabilities"]

    def close(self):
        self.client.close()

    def format_item_to_vulnerability(self, item):
        if "_id" in item:
            item["_id"] = str(item["_id"])
        if "pod_id" in item:
            item["pod_id"] = str(item["pod_id"])
        if "vulnerabilityID" in item:
            item["vulnerabilityID"] = str(item["vulnerabilityID"])
        # Ensure 'links' is a list for Pydantic validation
        if "links" in item and item["links"] is None:
            item["links"] = []
        return Vulnerability(**item)

    def get_vulnerabilities(self):
        items = self.get_vulnerabilities_collection().find({})
        items_list = list(items)
        return [self.format_item_to_vulnerability(item) for item in items_list]

    def get_vulnerability_by_hash(self, hash: str):
        item = self.get_vulnerabilities_collection().find_one(
            {"hash": hash}, {"_id": 0}
        )
        return self.format_item_to_vulnerability(item)
