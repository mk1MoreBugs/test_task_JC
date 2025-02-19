from enum import Enum
from uuid import UUID, uuid4
from typing import Annotated

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Wallet(SQLModel, table=True):
    __tablename__ = "wallets"
    uuid: UUID = Field(primary_key=True, default_factory=uuid4)
    amount: Annotated[int, Field(ge=0)]


class OperationType(str, Enum):
    DEPOSIT: str = "DEPOSIT"
    WITHDRAW: str = "WITHDRAW"


class WalletOperationIn(BaseModel):
    amount: Annotated[int, Field(gt=0)]
    operationType: OperationType


class WalletOperationOut(BaseModel):
    uuid: UUID
    message: str
