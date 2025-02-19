import uuid

from sqlmodel import Session
from starlette.testclient import TestClient

from app.core.config import settings
from app.crud.wallets import update_wallet_amount_by_uuid
from app.models.wallets import Wallet


def test_apply_operation__apply_withdraw_operation__return_new_amount(client: TestClient, db: Session, wallet: Wallet):
    data = {
        "operationType": "WITHDRAW",
        "amount": 1000,
    }
    # top up the test wallet with the withdrawal amount
    update_wallet_amount_by_uuid(session=db, wallet_uuid=wallet.uuid, amount=data["amount"])
    initial_amount = wallet.amount

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()
    db.refresh(wallet)

    assert response.status_code == 200
    assert wallet.amount == initial_amount - data["amount"]
    assert response_body.get("uuid") == str(wallet.uuid)


def test_apply_operation__apply_withdraw_operation_with_insufficient_funds__return_error(
        client: TestClient,
        db: Session,
        wallet: Wallet,
):
    data = {
        "operationType": "WITHDRAW",
        "amount": 1000,
    }

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()

    assert response.status_code == 400
    assert wallet.amount == 0
    assert response_body.get("detail") == "Недостаточно средств"


def test_apply_operation__apply_deposit_operation__return_new_amount(client: TestClient, db: Session, wallet: Wallet):
    data = {
        "operationType": "DEPOSIT",
        "amount": 1000,
    }
    # save initial amount value
    initial_amount = wallet.amount

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()
    db.refresh(wallet)

    assert response.status_code == 200
    assert wallet.amount == initial_amount + data["amount"]
    assert response_body.get("uuid") == str(wallet.uuid)


def test_apply_operation__apply_operation_with_incorrect_type__return_error(
        client: TestClient,
        db: Session,
        wallet: Wallet,
):
    data = {
        "operationType": "withdraw",
        "amount": 1000,
    }

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()

    assert response.status_code == 400
    assert response_body.get("detail") == "Некорректный тип операции"


def test_apply_operation__apply_operation_with_incorrect_uuid__return_error(
        client: TestClient,
        db: Session,
        wallet: Wallet,
):
    data = {
        "operationType": "WITHDRAW",
        "amount": 1000,
    }

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{uuid.uuid4()}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()

    assert response.status_code == 400
    assert response_body.get("detail") == "Кошелек не существует"


def test_apply_operation__apply_operation_with_incorrect_json__return_error(
        client: TestClient,
        db: Session,
        wallet: Wallet,
):
    data = {
        "operationType": "WITHDRAW",
        "amount1": 1000,
    }

    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/operation",
        json=data,
    )
    response_body: dict[str, str] = response.json()
    print(response_body)

    assert response.status_code == 422
    assert response_body.get("detail") == "Невалидный json"
