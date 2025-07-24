from pydantic import BaseModel


class ExposedSecret(BaseModel):
    uid: str = ""
    namespace: str = ""
    cluster: str = ""
