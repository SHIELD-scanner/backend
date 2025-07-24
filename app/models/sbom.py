from pydantic import BaseModel


class SBOM(BaseModel):
    uid: str = ""
    namespace: str = ""
    cluster: str = ""
