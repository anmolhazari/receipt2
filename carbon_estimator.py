import json
import os

class CarbonEstimator:
    def __init__(self, factors_file='emission_factors.json'):
        self.factors = self._load_factors(factors_file)

    def _load_factors(self, filepath):
        if not os.path.exists(filepath):
            # Fallback if file doesn't exist
            return {}
        with open(filepath, 'r') as f:
            return json.load(f)

    def estimate_item(self, name, quantity, price, category=None):
        """
        Estimate carbon footprint for a single item.
        """
        name_lower = name.lower()
        
        # 1. Determine Category if missing
        if not category:
            category = self._guess_category(name_lower)
        
        # 2. Find best matching factor
        factor, match_name, source_category = self._find_factor(name_lower, category)
        
        # 3. Calculate footprint
        # Assumption: quantity is in the unit matching the factor (e.g. kg or item)
        # If quantity is missing (e.g. None), assume 1
        qty = quantity if quantity is not None else 1.0
        footprint = factor * qty
        
        # 4. Generate Assumptions
        assumptions = []
        if match_name:
            assumptions.append(f"Matched '{name}' to emission factor for '{match_name}' ({factor} kg CO2e/unit).")
        else:
            assumptions.append(f"No specific match for '{name}'. Used default factor for category '{category}' ({factor} kg CO2e/unit).")
        
        if quantity is None:
            assumptions.append("Quantity not specified, assumed 1 unit.")
            
        # 5. Suggest Alternatives
        alternatives = self._get_alternatives(name_lower, category, footprint, qty)
        
        return {
            "name": name,
            "quantity": qty,
            "price": price,
            "category": category,
            "carbon_footprint_kg_co2e": round(footprint, 2),
            "assumptions": assumptions,
            "alternatives": alternatives
        }

    def _guess_category(self, name):
        # Simple keyword matching
        for cat, items in self.factors.items():
            if cat == 'defaults': continue
            for item in items:
                if item in name:
                    return cat
        return "other"

    def _find_factor(self, name, category):
        # Try to find exact or partial match in the specific category
        if category in self.factors:
            for item, factor in self.factors[category].items():
                if item in name:
                    return factor, item, category
        
        # Try to find match in any category
        for cat, items in self.factors.items():
            if cat == 'defaults': continue
            for item, factor in items.items():
                if item in name:
                    return factor, item, cat
                    
        # Fallback to default
        default_factor = self.factors.get('defaults', {}).get(category, 1.0)
        return default_factor, None, category

    def _get_alternatives(self, name, category, current_footprint, quantity):
        alts = []
        
        # Hardcoded logic for common high-impact items
        if 'beef' in name or 'steak' in name:
            chicken_factor = self.factors['food'].get('chicken', 6.0)
            saving = current_footprint - (chicken_factor * quantity)
            if saving > 0:
                alts.append({
                    "name": "Chicken",
                    "carbon_saving_kg_co2e": round(saving, 2),
                    "reason": "Lower emission meat alternative."
                })
            
            veg_factor = self.factors['food'].get('vegetables', 0.5)
            saving_veg = current_footprint - (veg_factor * quantity)
            if saving_veg > 0:
                alts.append({
                    "name": "Plant-based alternative",
                    "carbon_saving_kg_co2e": round(saving_veg, 2),
                    "reason": "Significantly lower carbon footprint."
                })
                
        elif 'milk' in name and 'almond' not in name and 'oat' not in name and 'soy' not in name:
             # Assume dairy milk
             # Oat milk approx 0.9 kg CO2e/kg vs Dairy 3.0
             oat_factor = 0.9
             dairy_factor = 3.0 # Approx
             # If we used the factor from DB
             used_factor = self.factors['food'].get('milk', 3.0)
             
             if used_factor > oat_factor:
                 saving = (used_factor - oat_factor) * quantity
                 alts.append({
                     "name": "Oat Milk",
                     "carbon_saving_kg_co2e": round(saving, 2),
                     "reason": "Plant-based milks have lower emissions than dairy."
                 })

        return alts
