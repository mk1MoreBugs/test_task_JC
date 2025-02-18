from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Wallet(SQLModel, table=True):
    __tablename__ = "wallets"
    uuid: UUID = Field(primary_key=True, default_factory=uuid4)
    amount: int


class OperationType(Enum):
    DEPOSIT: str = "DEPOSIT"
    WITHDRAW: str = "WITHDRAW"


class WalletOperationData(BaseModel):
    operationType: OperationType
    amount: int
