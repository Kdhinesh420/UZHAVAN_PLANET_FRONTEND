
import pydantic
print(f"Pydantic version: {pydantic.VERSION}")
try:
    from pydantic import BaseModel
    class Test(BaseModel):
        class Config:
            from_attributes = True
    print("from_attributes supported")
except Exception as e:
    print(f"from_attributes NOT supported: {e}")
