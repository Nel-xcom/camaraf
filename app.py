def calculate_total_revenue(transactions): 
    total = 0 
    for transaction in transactions: 
       if transaction['status'] == 'completed': 
           total += transaction['itemPrice'] * transaction['quantity'] 
       elif transaction['quantity'] <= 0: 
        raise ValueError("Quantity cannot be 0 or negative")
    if total > 10000: 
       total -= total * 0.1 
    return total