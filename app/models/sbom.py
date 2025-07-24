from pydantic import BaseModel


class Sbom(BaseModel):
    uid: str = ""
    namespace: str = ""
    cluster: str = ""
