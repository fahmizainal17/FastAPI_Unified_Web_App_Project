from pydantic import BaseModel, Field
from typing import List, Dict, Any
import pandas as pd

# Define schema to handle the input for process_file
class FileUpload(BaseModel):
    filename: str
    content_type: str

    # Validation to ensure the uploaded file is of the correct type
    @validator('content_type')
    def validate_mime_type(cls, v):
        if not v.startswith('text/csv'):
            raise ValueError('Invalid file type, must be a CSV')
        return v

# Define schema for the output of process_file
class ProcessFileOutput(BaseModel):
    df_complete: Dict[str, Any] = Field(default_factory=dict, description="Processed data with calls that have complete information.")
    phonenum_list: Dict[str, Any] = Field(default_factory=dict, description="List of phone numbers that have at least one user key press.")
    total_calls: int = Field(default=0, description="Total number of calls in the uploaded file.")
    total_pickup: int = Field(default=0, description="Total number of calls where a user key press was recorded.")
    df_merge: Dict[str, Any] = Field(default_factory=dict, description="Merged DataFrame output from merger function.")

# Schema for DataFrame list inputs used in the merger function
class DataFrameList(BaseModel):
    df_list: List[pd.DataFrame]  # Typing with pd.DataFrame directly, ensuring list of DataFrames is passed
    phonenum_list: List[pd.DataFrame]
