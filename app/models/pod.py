from pydantic import BaseModel


class Pod(BaseModel):
    name: str = ""
    namespace: str = ""
    kind: str = ""
    cluster: str = ""
