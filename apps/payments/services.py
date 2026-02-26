from apps.orders.models import PaymentStatus

from .models import PaymentTransaction


def mark_payment_success(transaction: PaymentTransaction):
    transaction.is_success = True
    transaction.save(update_fields=["is_success", "updated_at"])
    order = transaction.order
    order.payment_status = PaymentStatus.PAID
    if order.status == "pending":
        order.status = "confirmed"
    order.save(update_fields=["payment_status", "status", "updated_at"])
