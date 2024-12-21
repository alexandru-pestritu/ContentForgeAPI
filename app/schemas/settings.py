from pydantic import BaseModel, Field, ValidationError
from typing import Any, Optional, Union

class SettingBase(BaseModel):
    key: str
    value: Any
    type: str
    description: Optional[str] = None

    @staticmethod
    def validate_value(setting_type: str, value: Union[str, Any]):
        """
        Validate the value based on the setting type.
        """
        try:
            if setting_type == "integer":
                if not isinstance(value, int):
                    value = int(value)
            elif setting_type == "float":
                if not isinstance(value, float):
                    value = float(value)
            elif setting_type == "boolean":
                if not isinstance(value, bool):
                    if isinstance(value, str):
                        value = value.lower() in ["true", "1", "yes"]
                    else:
                        raise ValueError("Value must be a boolean")
            elif setting_type == "string":
                if not isinstance(value, str):
                    value = str(value)
            else:
                raise ValueError(f"Unsupported setting type: {setting_type}")
        except ValueError:
            raise ValueError(f"Value must be a valid {setting_type}")

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    value: Any

class SettingResponse(SettingBase):
    id: int

    class Config:
        from_attributes = True
