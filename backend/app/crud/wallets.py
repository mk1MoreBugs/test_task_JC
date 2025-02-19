from uuid import UUID

from sqlalchemy import update
from sqlmodel import Session, select

from app.models.wallets import Wallet


def create_wallet(session: Session) -> Wallet:
    wallet = Wallet(amount=0)
    session.add(wallet)
    session.commit()
    return wallet


def read_wallet_by_uuid(session: Session, wallet_uuid: UUID) -> Wallet | None:
    statement = select(Wallet).where(Wallet.uuid == wallet_uuid)
    wallet: Wallet | None = session.exec(statement).first()
    return wallet


def update_wallet_amount_by_uuid(session: Session, wallet_uuid: UUID, amount: int) -> None:
    statement = update(Wallet).where(Wallet.uuid == wallet_uuid).values(amount=amount)
    session.exec(statement)
    session.commit()
