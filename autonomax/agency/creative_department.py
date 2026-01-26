"""
Creative Department
===================

The Creative Department is the innovation engine of AutonomaX.
Responsible for product development, asset generation, and
creative solutions.

Philosophy: "Automate the mundane, create the remarkable"
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger("autonomax.agency.creative")


class AssetType(Enum):
    DIGITAL_PRODUCT = "digital_product"
    TEMPLATE = "template"
    COURSE = "course"
    EBOOK = "ebook"
    SOFTWARE = "software"
    ART = "art"
    COPY = "copy"
    VIDEO_SCRIPT = "video_script"
    MOCKUP = "mockup"


class ProductionStage(Enum):
    IDEATION = "ideation"
    DESIGN = "design"
    DEVELOPMENT = "development"
    TESTING = "testing"
    LAUNCH_READY = "launch_ready"
    LIVE = "live"


@dataclass
class Product:
    """A product being developed"""
    id: str
    name: str
    asset_type: AssetType
    description: str
    target_audience: str
    price_range: Dict[str, float]
    stage: ProductionStage = ProductionStage.IDEATION
    created_at: datetime = field(default_factory=datetime.utcnow)
    components: List[str] = field(default_factory=list)
    monetization: List[str] = field(default_factory=list)


@dataclass
class Asset:
    """A generated creative asset"""
    id: str
    asset_type: AssetType
    name: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ProductInnovator:
    """
    Autonomous product innovation agent.
    
    Identifies market opportunities, designs new products,
    and guides them through development.
    """
    
    def __init__(self, name: str = "Innovator-Alpha"):
        self.name = name
        self.products: List[Product] = []
        
        # Product frameworks from Profit OS
        self.product_frameworks = {
            "digital_download": {
                "components": ["main_content", "bonus_materials", "quick_start_guide"],
                "price_range": {"min": 9, "max": 97},
                "time_to_create": "1-3 days",
                "platforms": ["gumroad", "shopier", "etsy"],
            },
            "template_pack": {
                "components": ["templates", "instructions", "examples", "video_walkthrough"],
                "price_range": {"min": 19, "max": 149},
                "time_to_create": "3-7 days",
                "platforms": ["gumroad", "notion", "shopier"],
            },
            "mini_course": {
                "components": ["video_modules", "worksheets", "community_access"],
                "price_range": {"min": 47, "max": 297},
                "time_to_create": "7-14 days",
                "platforms": ["teachable", "gumroad", "youtube"],
            },
            "automation_kit": {
                "components": ["scripts", "documentation", "setup_guide", "support"],
                "price_range": {"min": 49, "max": 499},
                "time_to_create": "7-21 days",
                "platforms": ["gumroad", "github", "shopier"],
            },
            "consulting_package": {
                "components": ["strategy_session", "implementation_guide", "follow_up"],
                "price_range": {"min": 500, "max": 5000},
                "time_to_create": "1 day (template)",
                "platforms": ["calendly", "direct", "fiverr"],
            },
        }
        
        # Innovation sources
        self.innovation_sources = [
            "customer_pain_points",
            "competitor_gaps",
            "market_trends",
            "internal_capabilities",
            "technology_advances",
        ]
    
    def ideate_product(
        self,
        pain_point: str,
        target_audience: str,
        framework: str = "digital_download"
    ) -> Product:
        """Generate product idea from pain point"""
        fw = self.product_frameworks.get(framework, self.product_frameworks["digital_download"])
        
        product_id = f"PROD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        product = Product(
            id=product_id,
            name=f"{pain_point.title()} Solution Kit",
            asset_type=AssetType.DIGITAL_PRODUCT,
            description=f"Complete solution for {target_audience} struggling with {pain_point}",
            target_audience=target_audience,
            price_range=fw["price_range"],
            components=fw["components"],
            monetization=fw["platforms"],
        )
        
        self.products.append(product)
        logger.info(f"[{self.name}] Ideated product: {product.name}")
        
        return product
    
    def generate_product_spec(self, product: Product) -> Dict[str, Any]:
        """Generate detailed product specification"""
        return {
            "product_id": product.id,
            "name": product.name,
            "spec_version": "1.0",
            "created": datetime.utcnow().isoformat(),
            "overview": {
                "description": product.description,
                "target_audience": product.target_audience,
                "unique_value_proposition": f"The only solution that {product.description.lower()}",
            },
            "components": [
                {
                    "name": comp,
                    "description": f"Core {comp.replace('_', ' ')} module",
                    "priority": "high" if i == 0 else "medium",
                    "estimated_hours": 4 * (i + 1),
                }
                for i, comp in enumerate(product.components)
            ],
            "pricing": {
                "strategy": "value_based",
                "base_price": product.price_range["min"],
                "premium_price": product.price_range["max"],
                "launch_discount": 20,
            },
            "launch_plan": {
                "pre_launch": ["Build email list", "Create teaser content", "Set up landing page"],
                "launch": ["Email sequence", "Social push", "Community posts"],
                "post_launch": ["Collect testimonials", "Iterate based on feedback", "Create upsells"],
            },
            "success_metrics": {
                "units_sold_week1": 10,
                "revenue_week1": product.price_range["min"] * 10,
                "customer_rating": 4.5,
            },
        }
    
    def identify_bundle_opportunity(self, products: List[Product]) -> Dict[str, Any]:
        """Identify bundling opportunity from existing products"""
        if len(products) < 2:
            return {"status": "insufficient_products", "minimum_required": 2}
        
        # Calculate bundle value
        total_value = sum(p.price_range["max"] for p in products)
        bundle_price = total_value * 0.6  # 40% discount
        
        return {
            "bundle_name": f"Ultimate {products[0].target_audience} Bundle",
            "included_products": [p.name for p in products],
            "individual_value": total_value,
            "bundle_price": bundle_price,
            "savings": total_value - bundle_price,
            "savings_percentage": f"{((total_value - bundle_price) / total_value) * 100:.0f}%",
            "recommended_platforms": ["shopier", "gumroad"],
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get innovator status"""
        by_stage = {}
        for product in self.products:
            stage = product.stage.value
            by_stage[stage] = by_stage.get(stage, 0) + 1
        
        return {
            "name": self.name,
            "products_total": len(self.products),
            "products_by_stage": by_stage,
            "frameworks_available": list(self.product_frameworks.keys()),
        }


class AssetGenerator:
    """
    Generates creative assets on demand.
    
    Creates copy, mockups, scripts, and other creative
    assets for products and marketing.
    """
    
    def __init__(self, name: str = "Generator-Alpha"):
        self.name = name
        self.assets_generated: List[Asset] = []
        self.daily_quota = 20
        self.generated_today = 0
        
        # Copy templates
        self.copy_templates = {
            "product_title": {
                "pattern": "{benefit} {solution} for {audience}",
                "examples": [
                    "Complete Automation Kit for Solopreneurs",
                    "Time-Saving Templates for Content Creators",
                    "Revenue Dashboard for Etsy Sellers",
                ],
                "max_chars": 80,
            },
            "product_description": {
                "pattern": """Stop {pain_point}.

{product_name} gives you everything you need to {benefit}.

What's Inside:
{bullet_points}

Perfect for {audience} who want to {outcome}.

{cta}""",
                "max_chars": 2000,
            },
            "email_subject": {
                "pattern": "{curiosity_hook}",
                "examples": [
                    "I almost deleted this...",
                    "The lazy way to {outcome}",
                    "Why most {audience} fail at {topic}",
                ],
                "max_chars": 50,
            },
        }
        
        # Mockup configurations
        self.mockup_configs = {
            "digital_product": {
                "sizes": ["1200x630", "1080x1080", "1920x1080"],
                "styles": ["modern", "minimal", "bold"],
            },
            "social_post": {
                "sizes": ["1080x1080", "1200x628", "1080x1920"],
                "styles": ["branded", "clean", "engaging"],
            },
        }
    
    def generate_copy(
        self,
        copy_type: str,
        context: Dict[str, Any]
    ) -> Asset:
        """Generate marketing copy"""
        template = self.copy_templates.get(
            copy_type,
            self.copy_templates["product_title"]
        )
        
        # Generate based on template
        if copy_type == "product_title":
            content = template["pattern"].format(
                benefit=context.get("benefit", "Complete"),
                solution=context.get("solution", "Solution"),
                audience=context.get("audience", "Creators"),
            )
        elif copy_type == "product_description":
            bullets = "\n".join([f"• {b}" for b in context.get("bullets", ["Feature 1", "Feature 2"])])
            content = template["pattern"].format(
                pain_point=context.get("pain_point", "struggling"),
                product_name=context.get("product_name", "This Kit"),
                benefit=context.get("benefit", "succeed"),
                bullet_points=bullets,
                audience=context.get("audience", "creators"),
                outcome=context.get("outcome", "grow faster"),
                cta=context.get("cta", "Get instant access below."),
            )
        elif copy_type == "email_subject":
            content = context.get("hook", template["examples"][0])
        else:
            content = f"Generated {copy_type} for {context.get('product_name', 'product')}"
        
        # Truncate if needed
        max_chars = template.get("max_chars", 500)
        if len(content) > max_chars:
            content = content[:max_chars-3] + "..."
        
        asset_id = f"COPY-{copy_type.upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        asset = Asset(
            id=asset_id,
            asset_type=AssetType.COPY,
            name=f"{copy_type} for {context.get('product_name', 'product')}",
            content=content,
            metadata={"type": copy_type, "context": context},
        )
        
        self.assets_generated.append(asset)
        self.generated_today += 1
        
        return asset
    
    def generate_video_script(
        self,
        topic: str,
        duration_minutes: int = 5,
        style: str = "educational"
    ) -> Asset:
        """Generate video script"""
        script = f"""# {topic} - Video Script ({duration_minutes} min)

## Hook (0:00 - 0:30)
"If you've been struggling with {topic.lower()}, this video is going to change everything..."

[Show problem visualization]

## Problem (0:30 - 1:30)
Most people approach {topic.lower()} completely wrong.

They think they need to [common misconception].

But here's what actually works...

## Solution (1:30 - 3:30)
The key to {topic.lower()} comes down to 3 things:

1. [First key point]
   - Explanation
   - Example

2. [Second key point]
   - Explanation
   - Example

3. [Third key point]
   - Explanation
   - Example

## Proof/Demo (3:30 - 4:30)
Let me show you exactly how this works...

[Screen share or demonstration]

## CTA (4:30 - 5:00)
If you want to go deeper on this, I've put together [lead magnet].

Link in the description.

And if you found this helpful, smash that like button.

See you in the next one!

---
B-roll suggestions:
- [Visual 1]
- [Visual 2]
- [Visual 3]

Music: Upbeat, energetic
"""
        
        asset_id = f"SCRIPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        asset = Asset(
            id=asset_id,
            asset_type=AssetType.VIDEO_SCRIPT,
            name=f"Video Script: {topic}",
            content=script,
            metadata={
                "topic": topic,
                "duration_minutes": duration_minutes,
                "style": style,
            },
        )
        
        self.assets_generated.append(asset)
        self.generated_today += 1
        
        return asset
    
    def generate_product_batch(
        self,
        product_name: str,
        product_type: str = "digital_product"
    ) -> List[Asset]:
        """Generate all assets needed for a product"""
        assets = []
        
        # Title
        title = self.generate_copy("product_title", {
            "benefit": "Complete",
            "solution": product_name,
            "audience": "Creators",
        })
        assets.append(title)
        
        # Description
        desc = self.generate_copy("product_description", {
            "pain_point": "wasting time on manual work",
            "product_name": product_name,
            "benefit": "automate and scale",
            "bullets": [
                "Ready-to-use templates",
                "Step-by-step video guides",
                "Lifetime updates",
                "Community access",
            ],
            "audience": "busy entrepreneurs",
            "outcome": "save 10+ hours per week",
            "cta": "Get instant access now.",
        })
        assets.append(desc)
        
        # Email subjects
        for hook in ["The lazy way to automate", "I saved 10 hours this week", "Stop doing this manually"]:
            subject = self.generate_copy("email_subject", {"hook": hook})
            assets.append(subject)
        
        return assets
    
    def get_status(self) -> Dict[str, Any]:
        """Get generator status"""
        by_type = {}
        for asset in self.assets_generated:
            t = asset.asset_type.value
            by_type[t] = by_type.get(t, 0) + 1
        
        return {
            "name": self.name,
            "assets_generated_total": len(self.assets_generated),
            "generated_today": self.generated_today,
            "daily_quota": self.daily_quota,
            "quota_progress": f"{(self.generated_today / self.daily_quota) * 100:.0f}%",
            "assets_by_type": by_type,
        }


class CreativeDepartment:
    """
    Creative Department orchestrates all creative operations.
    
    Manages innovators and generators to produce new products
    and creative assets.
    """
    
    def __init__(self):
        self.name = "Creative Department"
        self.innovators = [
            ProductInnovator("Innovator-Alpha"),
        ]
        self.generators = [
            AssetGenerator("Generator-Alpha"),
            AssetGenerator("Generator-Beta"),
        ]
        
        # KPIs
        self.kpis = {
            "products_ideated": {"target": 5, "current": 0},
            "products_launched": {"target": 2, "current": 0},
            "assets_generated": {"target": 100, "current": 0},
            "product_revenue": {"target": 2000, "current": 0},
            "innovation_score": {"target": 80, "current": 0},
        }
    
    def innovation_sprint(self, pain_points: List[str]) -> Dict[str, Any]:
        """Run innovation sprint to generate product ideas"""
        results = {
            "sprint_date": datetime.utcnow().isoformat(),
            "products_created": [],
        }
        
        innovator = self.innovators[0]
        
        for pain_point in pain_points:
            product = innovator.ideate_product(
                pain_point=pain_point,
                target_audience="solopreneurs",
                framework="digital_download"
            )
            spec = innovator.generate_product_spec(product)
            results["products_created"].append({
                "product": product.name,
                "spec": spec,
            })
        
        return results
    
    def generate_launch_assets(self, product_name: str) -> Dict[str, Any]:
        """Generate all assets needed for product launch"""
        generator = self.generators[0]
        assets = generator.generate_product_batch(product_name)
        
        return {
            "product": product_name,
            "assets_generated": len(assets),
            "asset_ids": [a.id for a in assets],
        }
    
    def get_department_status(self) -> Dict[str, Any]:
        """Get full department status"""
        return {
            "department": self.name,
            "innovators": [i.get_status() for i in self.innovators],
            "generators": [g.get_status() for g in self.generators],
            "kpis": self.kpis,
            "health": self._calculate_health(),
        }
    
    def _calculate_health(self) -> float:
        """Calculate department health score"""
        scores = []
        for kpi, data in self.kpis.items():
            if data["target"] > 0:
                progress = min(100, (data["current"] / data["target"]) * 100)
                scores.append(progress)
        return sum(scores) / len(scores) if scores else 0.0
