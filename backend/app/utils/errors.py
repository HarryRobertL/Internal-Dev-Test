import uuid

from fastapi import HTTPException, status


def customer_not_found(customer_id: uuid.UUID) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "code": "not_found",
            "message": f"Customer {customer_id} not found",
            "details": None,
        },
    )
