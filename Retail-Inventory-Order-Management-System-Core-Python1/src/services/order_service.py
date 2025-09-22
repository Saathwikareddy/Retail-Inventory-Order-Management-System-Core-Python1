from typing import List, Dict
from src.dao import order_dao, product_dao, customer_dao

class OrderError(Exception):
    pass

def create_order(customer_id: int, items: List[Dict]) -> Dict:
    # Validate customer
    customer = customer_dao.get_customer_by_id(customer_id)
    if not customer:
        raise OrderError(f"Customer not found: {customer_id}")

    # Validate products & calculate total
    total_amount = 0
    for item in items:
        product = product_dao.get_product_by_id(item["prod_id"])
        if not product:
            raise OrderError(f"Product not found: {item['prod_id']}")
        total_amount += product["price"] * item["quantity"]
        item["price"] = product["price"]

    # Create order & insert pending payment
    order = order_dao.create_order(customer_id, items, total_amount)
    order_dao.create_payment(order["order_id"], total_amount, "PENDING")

    return order

def get_order_details(order_id: int) -> Dict:
    order = order_dao.get_order_by_id(order_id)
    if not order:
        raise OrderError(f"Order not found: {order_id}")
    return order

def cancel_order(order_id: int) -> Dict:
    order = order_dao.cancel_order(order_id)
    return order

def process_payment(order_id: int, method: str):
    # Mark payment as PAID and order as COMPLETED
    order_dao.update_payment_status(order_id, "PAID", method)
    order_dao.update_order(order_id, {"status": "COMPLETED"})


