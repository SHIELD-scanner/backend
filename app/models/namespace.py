from pydantic import BaseModel


class Namespace(BaseModel):
    cluster: str = ""
    name: str = ""
    _uid: str = ""