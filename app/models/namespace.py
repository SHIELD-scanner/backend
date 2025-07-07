from pydantic import BaseModel


class Namespace(BaseModel):
    cluster: str = ""
    name: str = ""
