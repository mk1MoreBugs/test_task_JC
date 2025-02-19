from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    HTTPException,
    status,
)

from app.api.deps import WalletUuid, SessionDep
from app.crud import wallets as crud_wallets
from app.models.responses import DetailMessage
from app.models.wallets import WalletOperationIn, OperationType, WalletOperationOut
from app.utils.calculate_new_amount import calculate_new_amount


router = APIRouter(
    prefix="/wallets",
    tags=["wallets"],
)

wallet_not_exist_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Кошелек не существует",
)


@router.post("/create")
async def create_wallet(session: SessionDep) -> dict[str, WalletUuid]:
    wallet = crud_wallets.create_wallet(session=session)
    return {"wallet_uuid": wallet.uuid}


@router.post(
    path="/{wallet_uuid}/operation",
    responses={
        400: {"model": DetailMessage},
        422: {"model": DetailMessage},
    }
)
async def apply_operation(
        wallet_uuid: WalletUuid,
        operation_data: Annotated[WalletOperationIn, Body()],
        session: SessionDep,
) -> WalletOperationOut:

    # check that the wallet exists
    wallet = crud_wallets.read_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)

    if wallet is not None:
        if operation_data.operationType == OperationType.WITHDRAW.value:
            # check that there are enough funds
            withdrawal_amount = -1 * operation_data.amount  # write-off amount
            new_amount = calculate_new_amount(old_value=wallet.amount, amount=withdrawal_amount)

            if new_amount >= 0:
                # success
                crud_wallets.update_wallet_amount_by_uuid(session=session, wallet_uuid=wallet_uuid, amount=new_amount)
                return WalletOperationOut(uuid=wallet_uuid, message="success")

            else:
                # error: insufficient funds
                raise HTTPException (
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недостаточно средств"
                )

        elif operation_data.operationType == OperationType.DEPOSIT.value:
            new_amount = calculate_new_amount(old_value=wallet.amount, amount=operation_data.amount)
            crud_wallets.update_wallet_amount_by_uuid(session=session, wallet_uuid=wallet_uuid, amount=new_amount)
            return WalletOperationOut(uuid=wallet_uuid, message="success")

    else:
        # error: The wallet does not exist
        raise wallet_not_exist_exception


@router.get(
    path="/{wallet_uuid}",
    responses={
        400: {"model": DetailMessage},
        422: {"model": DetailMessage},
    }
)
async def get_balance(wallet_uuid: WalletUuid, session: SessionDep) -> dict[str, int]:
    # check that the wallet exists
    wallet = crud_wallets.read_wallet_by_uuid(session=session, wallet_uuid=wallet_uuid)

    if wallet is not None:
        # return amount
        return {"amount": wallet.amount}
    else:
        # error: The wallet does not exist
        raise wallet_not_exist_exception
