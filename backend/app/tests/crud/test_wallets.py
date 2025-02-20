from uuid import uuid4

from sqlmodel import Session

from app.crud.wallets import create_wallet, read_wallet_by_uuid, update_wallet_amount_by_uuid


def test__read_wallet_by_uuid__create_and_read_wallet__return_wallet_in_db(db: Session) -> None:
    wallet = create_wallet(session=db)

    wallet_in_db = read_wallet_by_uuid(session=db, wallet_uuid=wallet.uuid)

    assert wallet_in_db.uuid == wallet.uuid
    assert wallet_in_db.amount ==wallet.amount
    assert wallet_in_db.amount == 0


def test__read_wallet_by_uuid__read_wallet_with_incorrect_uuid__return_none(db: Session):
    create_wallet(session=db)
    wallet_in_db = read_wallet_by_uuid(session=db, wallet_uuid=uuid4())
    assert wallet_in_db is None


def test__update_wallet_amount_by_uuid__create_wallet_and_update_amount__in_db_new_value(db: Session):
    wallet = create_wallet(session=db)
    new_amount = 100

    update_wallet_amount_by_uuid(session=db, wallet_uuid=wallet.uuid, amount=new_amount)

    wallet_in_db = read_wallet_by_uuid(session=db, wallet_uuid=wallet.uuid)
    assert wallet_in_db.amount == new_amount


def test__update_wallet_amount_by_uuid__create_wallet_and_update_amount_with_incorrect_uuid__in_db_old_value(db: Session):
    wallet = create_wallet(session=db)
    new_amount = 100

    update_wallet_amount_by_uuid(session=db, wallet_uuid=uuid4(), amount=new_amount)

    wallet_in_db = read_wallet_by_uuid(session=db, wallet_uuid=wallet.uuid)
    assert wallet_in_db.amount == wallet.amount
