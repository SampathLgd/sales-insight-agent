from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any

def process_orders(orders: List[Dict[str, Any]], start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Filters and processes a list of orders based on a date range.
    
    All monetary values are converted from cents to formatted dollar strings.
    """
    print(f"[Processor] Processing data from {start_date} to {end_date}...")
    
    start_dt = datetime.fromisoformat(start_date + "T00:00:00").date()
    end_dt = datetime.fromisoformat(end_date + "T23:59:59").date()
    
    total_revenue_cents = 0
    total_orders = 0
    item_sales = defaultdict(lambda: {'count': 0, 'revenue_cents': 0})
    customer_sales = defaultdict(lambda: {'count': 0, 'revenue_cents': 0})

    filtered_orders = []
    for order in orders:
        created_time_str = order.get("createdTime")
        if not created_time_str or not isinstance(created_time_str, str):
            continue 

        try:
            order_time = datetime.fromisoformat(created_time_str).date()
        except ValueError:
            print(f"[Processor] Skipping order {order.get('orderId')} with malformed date: {created_time_str}")
            continue

        if start_dt <= order_time <= end_dt and order.get("state") == "locked":
            filtered_orders.append(order)

    # Return zeroed-out data if no orders are found
    if not filtered_orders:
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_revenue": "$0.00",
            "total_orders": 0,
            "top_selling_items": [],
            "top_customers": []
        }

    # Process all filtered orders
    for order in filtered_orders:
        total_revenue_cents += order.get("total", 0)
        total_orders += 1
        
        customer_id = order.get("loyaltyNumber")
        if customer_id:
            customer_sales[customer_id]['count'] += 1
            customer_sales[customer_id]['revenue_cents'] += order.get("total", 0)
            
        for item in order.get("lineItems", []):
            item_name = item.get("name", "Unknown Item")
            item_price_cents = item.get("price", 0) or 0 
            item_sales[item_name]['count'] += 1
            item_sales[item_name]['revenue_cents'] += item_price_cents

    # --- FORMATTING IS NOW DONE IN PYTHON ---

    # Sort and format top items
    sorted_items = sorted(item_sales.items(), key=lambda x: x[1]['count'], reverse=True)
    top_items = [
        {
            "name": name,
            "count": data['count'],
            "revenue": f"${data['revenue_cents'] / 100.0:.2f}" # Format as dollar string
        } 
        for name, data in sorted_items[:5]
    ]
    
    # Sort and format top customers
    sorted_customers = sorted(customer_sales.items(), key=lambda x: x[1]['revenue_cents'], reverse=True)
    top_customers = [
        {
            "id": id,
            "order_count": data['count'],
            "total_revenue": f"${data['revenue_cents'] / 100.0:.2f}" # Format as dollar string
        }
        for id, data in sorted_customers[:5]
    ]

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": f"${total_revenue_cents / 100.0:.2f}", # Format as dollar string
        "total_orders": total_orders,
        "top_selling_items": top_items,
        "top_customers": top_customers
    }