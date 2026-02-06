import re
from datetime import datetime

class ReceiptParser:
    def parse(self, text):
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        result = {
            "vendor": "Unknown Vendor",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_price": 0.0,
            "currency": "USD", # Default
            "items": []
        }
        
        # 1. Extract Date
        date_pattern = r'(\d{4}-\d{2}-\d{2})|(\d{1,2}/\d{1,2}/\d{2,4})'
        for line in lines:
            match = re.search(date_pattern, line)
            if match:
                date_str = match.group(0)
                # Try to normalize date format to YYYY-MM-DD
                try:
                    if '-' in date_str and len(date_str.split('-')[0]) == 4:
                         result["date"] = date_str
                    elif '/' in date_str:
                        parts = date_str.split('/')
                        if len(parts[2]) == 2: parts[2] = '20' + parts[2]
                        # Assume MM/DD/YYYY
                        dt = datetime.strptime(f"{parts[0]}/{parts[1]}/{parts[2]}", "%m/%d/%Y")
                        result["date"] = dt.strftime("%Y-%m-%d")
                except:
                    pass # Keep default or raw found
                break

        # 2. Extract Vendor (First line that doesn't look like a date or total)
        for line in lines:
            if "total" in line.lower(): continue
            if re.search(date_pattern, line): continue
            result["vendor"] = line
            break
            
        # 3. Extract Items
        # Pattern: [Qty] [Name] [Price] or [Name] [Price]
        # We look for a price at the end of the line
        price_pattern = r'(\$)?\s?(\d+\.\d{2})'
        
        calculated_total = 0.0
        
        for line in lines:
            # Skip lines that look like totals or sub-totals
            if "total" in line.lower() or "subtotal" in line.lower() or "tax" in line.lower():
                # Try to grab the actual total price from the Total line
                if "total" in line.lower():
                    price_match = re.search(price_pattern, line)
                    if price_match:
                        result["total_price"] = float(price_match.group(2))
                continue
                
            # Find all price-like patterns
            price_matches = list(re.finditer(price_pattern, line))
            if price_matches:
                # Take the last match as the item price
                price_match = price_matches[-1]
                price = float(price_match.group(2))
                
                # Remove price from line to process name/qty
                remaining = line[:price_match.start()].strip()
                
                # Check for quantity at start (e.g. "2 x Burger" or "2.5 kg Beef")
                qty = 1.0
                # Match: (number or decimal) [xX] (rest)
                qty_match = re.match(r'^(\d+(?:\.\d+)?)\s*[xX]\s+(.*)', remaining)
                if qty_match:
                    qty = float(qty_match.group(1))
                    name = qty_match.group(2).strip()
                else:
                    # Check for quantity as just a number at start
                    # Match: (number or decimal) (rest)
                    qty_match_simple = re.match(r'^(\d+(?:\.\d+)?)\s+(.*)', remaining)
                    if qty_match_simple:
                        # Heuristic: is the first number a quantity? 
                        # If it's 1-100, likely. If it's a barcode, unlikely.
                        # For now, assume it is qty if < 100
                        val = float(qty_match_simple.group(1))
                        if val < 100:
                            qty = val
                            name = qty_match_simple.group(2).strip()
                        else:
                            name = remaining
                    else:
                        name = remaining
                
                if not name: continue # Empty name
                
                result["items"].append({
                    "name": name,
                    "quantity": qty,
                    "price": price
                })
                calculated_total += price

        # If total wasn't found, use calculated
        if result["total_price"] == 0.0:
            result["total_price"] = round(calculated_total, 2)
            
        return result
