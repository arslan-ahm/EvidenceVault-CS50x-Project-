from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "category"

    id: str = Field(primary_key=True, index=True)
    value: str = Field(unique=True, index=True)
    label: str
