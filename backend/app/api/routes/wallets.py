from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    status,
)

from app.api.deps import WalletUuid, SessionDep
from app.crud.wallets import read_wallet_by_uuid, update_wallet_amount_by_uuid
from app.models.wallets import WalletOperationIn, OperationType, WalletOperationOut
from app.utils.calculate_new_amount import calculate_new_amount


router = APIRouter(
    prefix="/wallets",
    tags=["wallets"],
)


@router.post("/create")
async def create_wallet() -> WalletUuid:
    pass


@router.post("/{wallet_uuid}/operation")
async def apply_operation(
        wallet_uuid: WalletUuid,
        operation_data: Annotated[WalletOperationIn, Body()],
        session: SessionDep,
) -> WalletOperationOut:

    # check that the wallet exists
    wallet = read_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)

    if wallet is not None:
        if operation_data.operationType == OperationType.WITHDRAW.value:
            # check that there are enough funds
            withdrawal_amount = -1 * operation_data.amount  # write-off amount
            new_amount = calculate_new_amount(old_value=wallet.amount, amount=withdrawal_amount)

            if new_amount >= 0:
                # success
                update_wallet_amount_by_uuid(session=session, wallet_uuid=wallet_uuid, amount=new_amount)
                return WalletOperationOut(uuid=wallet_uuid, message="success")

            else:
                # error: insufficient funds
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно средств"
                )

        elif operation_data.operationType == OperationType.DEPOSIT.value:
            new_amount = calculate_new_amount(old_value=wallet.amount, amount=operation_data.amount)
            update_wallet_amount_by_uuid(session=session, wallet_uuid=wallet_uuid, amount=new_amount)
            return WalletOperationOut(uuid=wallet_uuid, message="success")

        else:
            # error: Incorrect operation type
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный тип операции"
            )
    else:
        # error: The wallet does not exist
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Кошелек не существует"
        )


@router.get("/operation/{wallet_uuid}")
async def get_balance(wallet_uuid: WalletUuid) -> dict[str, int]:
    # check that the wallet exists
    pass
