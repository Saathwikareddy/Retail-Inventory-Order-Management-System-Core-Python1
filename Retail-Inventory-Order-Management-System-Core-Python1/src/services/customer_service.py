from typing import List, Dict
import src.dao.customer_dao as customer_dao
import src.dao.order_dao as order_dao  # to check existing orders

class CustomerError(Exception):
    pass

def add_customer(name: str, email: str, phone: str, city: str | None = None) -> Dict:
    if customer_dao.get_customer_by_email(email):
        raise CustomerError(f"Email already exists: {email}")
    return customer_dao.create_customer(name, email, phone, city)

def update_customer(cust_id: int, phone: str | None = None, city: str | None = None) -> Dict:
    fields = {}
    if phone:
        fields["phone"] = phone
    if city:
        fields["city"] = city
    if not fields:
        raise CustomerError("No fields to update")
    return customer_dao.update_customer(cust_id, fields)

def delete_customer(cust_id: int) -> Dict:
    orders = order_dao.get_orders_by_customer(cust_id)
    if orders:
        raise CustomerError("Cannot delete customer with existing orders")
    return customer_dao.delete_customer(cust_id)

def list_customers(limit: int = 100) -> List[Dict]:
    return customer_dao.list_customers(limit)

def search_customers(email: str | None = None, city: str | None = None) -> List[Dict]:
    return customer_dao.search_customers(email, city)

