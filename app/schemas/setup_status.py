from pydantic import BaseModel

class SetupStatusBase(BaseModel):
    setup_completed: bool
    current_step: int

class SetupStatusResponse(SetupStatusBase):
    id: int

    class Config:
        from_attributes = True
