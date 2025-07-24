from pydantic import BaseModel


class Exposedsecret(BaseModel):
    uid: str = ""
    namespace: str = ""
    cluster: str = ""
