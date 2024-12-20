from pydantic import BaseModel, Field, ValidationError
from typing import Any, Optional

class SettingBase(BaseModel):
    key: str
    value: Any
    type: str
    description: Optional[str] = None

    @staticmethod
    def validate_value(setting_type: str, value: Any):
        """
        Validate the value based on the setting type.
        """
        if setting_type == "integer" and not isinstance(value, int):
            raise ValueError("Value must be an integer")
        elif setting_type == "float" and not isinstance(value, float):
            raise ValueError("Value must be a float")
        elif setting_type == "string" and not isinstance(value, str):
            raise ValueError("Value must be a string")
        elif setting_type == "boolean" and not isinstance(value, bool):
            raise ValueError("Value must be a boolean")

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: Any

class SettingResponse(SettingBase):
    id: int

    class Config:
        orm_mode = True
