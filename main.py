import sys
import json
import os
from receipt_parser import ReceiptParser
from carbon_estimator import CarbonEstimator

def main():
    # 1. Get Input
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if os.path.exists(input_path):
            with open(input_path, 'r') as f:
                receipt_text = f.read()
        else:
            print(f"Error: File '{input_path}' not found.")
            return
    else:
        # Default to sample if exists
        if os.path.exists('sample_receipt.txt'):
            print("No input file provided. Using 'sample_receipt.txt'...")
            with open('sample_receipt.txt', 'r') as f:
                receipt_text = f.read()
        else:
            print("Usage: python main.py <receipt_file.txt>")
            return

    # 2. Parse Receipt
    parser = ReceiptParser()
    parsed_data = parser.parse(receipt_text)
    
    # 3. Estimate Carbon Footprint
    estimator = CarbonEstimator()
    enriched_items = []
    total_footprint = 0.0
    
    for item in parsed_data['items']:
        analysis = estimator.estimate_item(
            name=item['name'],
            quantity=item['quantity'],
            price=item['price']
        )
        enriched_items.append(analysis)
        total_footprint += analysis['carbon_footprint_kg_co2e']
        
    # 4. Construct Final JSON
    # Identify top contributor
    top_item = max(enriched_items, key=lambda x: x['carbon_footprint_kg_co2e']) if enriched_items else None
    summary = f"Total estimated carbon footprint is {round(total_footprint, 2)} kg CO2e."
    if top_item:
        summary += f" The largest contributor is '{top_item['name']}' with {top_item['carbon_footprint_kg_co2e']} kg CO2e."

    final_result = {
        "receipt_details": {
            "vendor": parsed_data['vendor'],
            "date": parsed_data['date'],
            "total_price": parsed_data['total_price'],
            "currency": parsed_data['currency']
        },
        "items": enriched_items,
        "total_carbon_footprint_kg_co2e": round(total_footprint, 2),
        "analysis_summary": summary
    }
    
    # 5. Output JSON
    print(json.dumps(final_result, indent=2))

if __name__ == "__main__":
    main()
