from typing import Optional, List, Dict
from src.config import get_supabase

_sb = get_supabase()

# ---------- Orders ----------
def create_order(cust_id: int, items: List[Dict], total_amount: float) -> Optional[Dict]:
    order_payload = {"cust_id": cust_id, "total_amount": total_amount, "status": "PLACED"}
    resp = _sb.table("orders").insert(order_payload).execute()
    order = resp.data[0] if resp.data else None
    if not order:
        return None

    order_id = order["order_id"]

    # Insert order items
    for item in items:
        oi_payload = {
            "order_id": order_id,
            "prod_id": item["prod_id"],
            "quantity": item["quantity"],
            "price": item["price"]
        }
        _sb.table("order_items").insert(oi_payload).execute()

    return get_order_by_id(order_id)

def get_order_by_id(order_id: int) -> Optional[Dict]:
    resp = _sb.table("orders").select("*").eq("order_id", order_id).limit(1).execute()
    order = resp.data[0] if resp.data else None
    if not order:
        return None

    # Add items
    items = _sb.table("order_items").select("*").eq("order_id", order_id).execute().data or []
    order["items"] = items

    # Add payment info
    payment = _sb.table("payments").select("*").eq("order_id", order_id).limit(1).execute().data
    order["payment"] = payment[0] if payment else None

    return order

def update_order(order_id: int, fields: Dict) -> Optional[Dict]:
    _sb.table("orders").update(fields).eq("order_id", order_id).execute()
    return get_order_by_id(order_id)

def cancel_order(order_id: int) -> Optional[Dict]:
    _sb.table("orders").update({"status": "CANCELLED"}).eq("order_id", order_id).execute()
    update_payment_status(order_id, "REFUNDED")
    return get_order_by_id(order_id)

# ---------- Payments ----------
def create_payment(order_id: int, amount: float, status: str = "PENDING", method: str | None = None):
    payload = {
        "order_id": order_id,
        "amount": amount,
        "status": status,
        "method": method
    }
    _sb.table("payments").insert(payload).execute()

def update_payment_status(order_id: int, status: str, method: str | None = None):
    fields = {"status": status}
    if method:
        fields["method"] = method
    _sb.table("payments").update(fields).eq("order_id", order_id).execute()
