import requests
import json
import time
from typing import List, Dict, Any, Optional

# In-memory cache to store API response
CACHE: Dict[str, Any] = {"data": None, "last_fetched": 0}
CACHE_DURATION_SECONDS: int = 60 * 10  # 10 minutes
API_URL: str = "https://sandbox.mkonnekt.net/ch-portal/api/v1/orders/recent"

def fetch_orders() -> Optional[List[Dict[str, Any]]]:
    """
    Fetches recent orders from the Sales API.
    
    Uses a simple in-memory cache to avoid repeated API calls
    within a 10-minute window.
    
    Returns:
        A list of order dictionaries if successful, None otherwise.
    """
    now = time.time()
    
    # Check cache first
    if CACHE["data"] and (now - CACHE["last_fetched"] < CACHE_DURATION_SECONDS):
        print("[ApiClient] Using cached data.")
        return CACHE["data"]

    print("[ApiClient] Fetching new data from API...")
    try:
        response = requests.get(API_URL)
        # Raise an exception for bad HTTP status codes (4xx or 5xx)
        response.raise_for_status() 
        
        data = response.json()
        
        # The live API returns a dictionary: {"orders": [...] }
        # We must handle this format to extract the list.
        if isinstance(data, dict):
            orders_list = data.get("orders")
            
            if isinstance(orders_list, list):
                print("[ApiClient] Successfully extracted 'orders' list from API dictionary.")
                # Update cache
                CACHE["data"] = orders_list
                CACHE["last_fetched"] = now
                return orders_list
            else:
                # This handles the case where the API returns a dict but no "orders" key
                print(f"[ApiClient] Error: API returned a dict, but 'orders' key is missing or not a list.")
                return None
        
        # Fallback in case the API documentation was correct and it returns a list
        if isinstance(data, list):
            print("[ApiClient] API returned a list (as documented in PDF).")
            CACHE["data"] = data
            CACHE["last_fetched"] = now
            return data
        
        print(f"[ApiClient] Error: API returned unexpected data type: {type(data)}")
        return None
        
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"[ApiClient] Error: Failed to fetch or parse data from API. {e}")
        return None