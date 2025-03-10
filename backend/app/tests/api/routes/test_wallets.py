from uuid import UUID, uuid4

from sqlmodel import Session
from starlette.testclient import TestClient

from app.core.config import settings
from app.crud.wallets import update_wallet_amount_by_uuid, read_wallet_by_uuid
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
        url=f"{settings.API_V1_STR}/wallets/{uuid4()}/operation",
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

    assert response.status_code == 422
    assert response_body.get("detail") == "Невалидный json"


def test_get_balance__get_balance_of_existing_wallet__return_amount(client: TestClient, wallet: Wallet):
    response = client.get(
        url=f"{settings.API_V1_STR}/wallets/{wallet.uuid}/",
    )
    response_body: dict[str, int] = response.json()

    assert response.status_code == 200
    assert response_body.get("amount") == wallet.amount


def test_get_balance__get_balance_of_non_existent_wallet__return_error(client: TestClient, wallet: Wallet):
    response = client.get(
        url=f"{settings.API_V1_STR}/wallets/{uuid4()}/",
    )
    response_body: dict[str, str] = response.json()

    assert response.status_code == 400
    assert response_body.get("detail") == "Кошелек не существует"


def test_create_wallet__create_new_wallet_and_check_in_db__get_status_code_200(client: TestClient, db: Session):
    response = client.post(
        url=f"{settings.API_V1_STR}/wallets/create",
    )

    response_body: dict[str, UUID] = response.json()
    wallet_uuid: UUID = response_body["wallet_uuid"]
    wallet_in_db = read_wallet_by_uuid(session=db, wallet_uuid=wallet_uuid)

    assert  response.status_code == 200
    assert wallet_in_db is not None
