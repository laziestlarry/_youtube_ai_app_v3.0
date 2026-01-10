from sqlalchemy.orm import Session
from .models import GrowthSku
import random

class CatalogService:
    CATEGORIES = ["Tee", "Mug", "Poster", "PhoneCase"]
    THEMES = ["Cyberpunk", "Zen", "Hustle", "Retro", "Minimal", "Nature", "Space", "Crypto", "Gamer", "Abstract"]

    def __init__(self, db: Session):
        self.db = db

    def generate_sku_code(self, category: str, theme: str, variant: int) -> str:
        return f"{category.upper()}-{theme.upper()}-{variant:03d}"

    def seed_initial_catalog(self, count: int = 60):
        """Generates 'count' SKUs distributed across categories."""
        generated = 0
        
        # Calculate distribution
        per_cat = count // len(self.CATEGORIES)
        
        for category in self.CATEGORIES:
            for i in range(per_cat):
                theme = random.choice(self.THEMES)
                sku_code = self.generate_sku_code(category, theme, i+1)
                
                # Check exist
                if self.db.query(GrowthSku).filter_by(sku_code=sku_code).first():
                    continue

                # Pricing Logic
                base_cost = {
                    "Tee": 800, "Mug": 400, "Poster": 500, "PhoneCase": 600
                }[category]
                
                margin_mult = random.uniform(1.6, 2.2) # 60% - 120% markup
                price = int(base_cost * margin_mult)

                sku = GrowthSku(
                    sku_code=sku_code,
                    name=f"{theme} {category} Design #{i+1}",
                    category=category,
                    tags=f"{theme}, {category.lower()}, trending",
                    cost_basis_cents=base_cost,
                    price_cents=price,
                    status="active",
                    provenance_meta={"origin_name": "Autonomax Generator", "quality_score": 1.0}
                )
                self.db.add(sku)
                generated += 1
        
        self.db.commit()
        return {"generated": generated, "total": self.db.query(GrowthSku).count()}

    def get_catalog(self):
        return self.db.query(GrowthSku).all()
