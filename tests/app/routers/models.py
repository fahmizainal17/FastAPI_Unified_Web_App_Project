from pydantic import BaseModel
import pandas as pd

class Dataframe(BaseModel):
    df:pd.DataFrame
    class Config:
        arbitrary_types_allowed = True
