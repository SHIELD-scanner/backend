import os

from pymongo import MongoClient


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
