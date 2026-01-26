"""
AutonomaX Agency Layer
======================

The Agency is the creative and innovative execution arm of AutonomaX.
It contains specialized departments that work autonomously to generate
revenue through hunting, selling, marketing, and creating.

Departments:
- Hunters: Lead discovery, opportunity identification, outreach
- Sales: Deal closing, objection handling, conversion optimization
- Marketing: Content creation, campaigns, brand amplification
- Creative: Innovation, product development, asset generation

Each department operates with KPI accountability under the Command Center.
"""

from .hunter_department import HunterDepartment, LeadHunter, OpportunityScout
from .sales_department import SalesDepartment, DealCloser, ConversionOptimizer
from .marketing_department import MarketingDepartment, ContentCreator, CampaignManager
from .creative_department import CreativeDepartment, ProductInnovator, AssetGenerator

__all__ = [
    # Departments
    "HunterDepartment",
    "SalesDepartment",
    "MarketingDepartment",
    "CreativeDepartment",
    
    # Hunter Agents
    "LeadHunter",
    "OpportunityScout",
    
    # Sales Agents
    "DealCloser",
    "ConversionOptimizer",
    
    # Marketing Agents
    "ContentCreator",
    "CampaignManager",
    
    # Creative Agents
    "ProductInnovator",
    "AssetGenerator",
]
