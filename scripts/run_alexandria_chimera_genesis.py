#!/usr/bin/env python3
"""
Alexandria Chimera Genesis Runner

This script orchestrates the full Alexandria Protocol execution:
1. Genesis Log - Index all project assets
2. Knowledge Graph - Build relationships between assets
3. Value Propositions - Extract monetization opportunities
4. Revenue Mapping - Connect assets to revenue streams

Usage:
    python scripts/run_alexandria_chimera_genesis.py
    python scripts/run_alexandria_chimera_genesis.py --full
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Output directories
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
ALEXANDRIA_DIR = DATA_DIR / "alexandria"
DOCS_PROTOCOL_DIR = ROOT / "docs" / "alexandria_protocol"


def ensure_dirs():
    """Ensure output directories exist."""
    ALEXANDRIA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_PROTOCOL_DIR.mkdir(parents=True, exist_ok=True)


def load_product_catalog() -> List[Dict[str, Any]]:
    """Load product catalog for value mapping."""
    catalog_path = ROOT / "docs" / "commerce" / "product_catalog.json"
    if not catalog_path.exists():
        return []
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return data.get("products", [])


def load_shopier_map() -> Dict[str, Dict[str, str]]:
    """Load Shopier product mapping."""
    map_path = ROOT / "docs" / "commerce" / "shopier_product_map.json"
    if not map_path.exists():
        return {}
    return json.loads(map_path.read_text(encoding="utf-8"))


def load_delivery_map() -> Dict[str, Dict[str, str]]:
    """Load digital delivery mapping."""
    map_path = ROOT / "docs" / "commerce" / "digital_delivery_map.json"
    if not map_path.exists():
        return {}
    return json.loads(map_path.read_text(encoding="utf-8"))


def run_genesis_log() -> Dict[str, Any]:
    """Run Genesis Log generation."""
    print("\n" + "=" * 60)
    print("PHASE 1: GENESIS LOG - Indexing Project Assets")
    print("=" * 60)
    
    from backend.services.alexandria_genesis import (
        GenesisConfig,
        build_genesis_log,
        write_genesis_log,
    )
    
    config = GenesisConfig(
        root=ROOT,
        max_files=5000,
        exclude_dirs=["legacy", "split", ".git", "node_modules", "venv", "__pycache__", "dist", "build"],
    )
    
    payload = build_genesis_log(config)
    
    # Write to data directory
    output_path = ALEXANDRIA_DIR / "genesis_log.json"
    write_genesis_log(payload, output_path)
    
    # Also copy to docs for version control
    docs_output = DOCS_PROTOCOL_DIR / "genesis_log.json"
    write_genesis_log(payload, docs_output)
    
    entries = payload.get("genesis_log", [])
    print(f"  Indexed {len(entries)} files")
    print(f"  Output: {output_path}")
    
    return payload


def build_knowledge_graph(genesis_log: Dict[str, Any]) -> Dict[str, Any]:
    """Build knowledge graph from genesis log."""
    print("\n" + "=" * 60)
    print("PHASE 2: KNOWLEDGE GRAPH - Building Relationships")
    print("=" * 60)
    
    entries = genesis_log.get("genesis_log", [])
    products = load_product_catalog()
    shopier_map = load_shopier_map()
    delivery_map = load_delivery_map()
    
    # Build nodes
    nodes = []
    edges = []
    
    # File nodes
    file_nodes = {}
    for entry in entries:
        node_id = entry["id"]
        file_nodes[entry["file_path"]] = node_id
        nodes.append({
            "id": node_id,
            "type": "file",
            "path": entry["file_path"],
            "content_type": entry.get("content_type", "file"),
            "labels": entry.get("labels", {}),
            "value_signals": entry.get("value_signals", {}),
        })
    
    # Collection nodes (group by top-level directory)
    collections = defaultdict(list)
    for entry in entries:
        collection = entry.get("collection", "root")
        collections[collection].append(entry["id"])
    
    for collection, members in collections.items():
        coll_id = f"COLL-{collection.upper().replace('/', '-')}"
        nodes.append({
            "id": coll_id,
            "type": "collection",
            "name": collection,
            "member_count": len(members),
        })
        for member_id in members:
            edges.append({
                "source": member_id,
                "target": coll_id,
                "relation": "belongs-to-collection",
            })
    
    # Product nodes
    for product in products:
        sku = product.get("sku", "")
        if not sku:
            continue
        prod_id = f"PROD-{sku}"
        nodes.append({
            "id": prod_id,
            "type": "product",
            "sku": sku,
            "title": product.get("title", ""),
            "product_type": product.get("type", "digital"),
            "price_range": product.get("price", {}),
            "channels": product.get("channels", []),
        })
        
        # Link to delivery assets
        if sku in delivery_map:
            delivery = delivery_map[sku]
            asset_path = delivery.get("file", "")
            if asset_path in file_nodes:
                edges.append({
                    "source": prod_id,
                    "target": file_nodes[asset_path],
                    "relation": "delivers",
                })
        
        # Link to Shopier listing
        if sku in shopier_map:
            listing = shopier_map[sku]
            listing_id = f"LISTING-SHOPIER-{listing.get('id', sku)}"
            nodes.append({
                "id": listing_id,
                "type": "listing",
                "platform": "shopier",
                "url": listing.get("url", ""),
                "title": listing.get("title", ""),
            })
            edges.append({
                "source": prod_id,
                "target": listing_id,
                "relation": "listed-on",
            })
    
    # Capability nodes (derived from content types)
    capabilities = {
        "backend-service": "Backend Development",
        "frontend-next": "Frontend Development",
        "automation-script": "Automation Services",
        "commerce-doc": "Commerce Operations",
        "documentation": "Documentation Services",
    }
    
    for content_type, capability_name in capabilities.items():
        cap_id = f"CAP-{content_type.upper()}"
        nodes.append({
            "id": cap_id,
            "type": "capability",
            "name": capability_name,
            "content_type": content_type,
        })
        
        # Link files to capabilities
        for entry in entries:
            if entry.get("content_type") == content_type:
                edges.append({
                    "source": entry["id"],
                    "target": cap_id,
                    "relation": "enables-capability",
                })
    
    knowledge_graph = {
        "version": "1.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "system": "Alexandria Knowledge Graph",
        "statistics": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "file_nodes": len(file_nodes),
            "collection_nodes": len(collections),
            "product_nodes": len(products),
            "capability_nodes": len(capabilities),
        },
        "nodes": nodes,
        "edges": edges,
    }
    
    # Write output
    output_path = ALEXANDRIA_DIR / "knowledge_graph.json"
    output_path.write_text(json.dumps(knowledge_graph, indent=2, ensure_ascii=False), encoding="utf-8")
    
    docs_output = DOCS_PROTOCOL_DIR / "knowledge_graph.json"
    docs_output.write_text(json.dumps(knowledge_graph, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"  Total Nodes: {len(nodes)}")
    print(f"  Total Edges: {len(edges)}")
    print(f"  Output: {output_path}")
    
    return knowledge_graph


def extract_value_propositions(
    genesis_log: Dict[str, Any],
    knowledge_graph: Dict[str, Any]
) -> Dict[str, Any]:
    """Extract monetization value propositions."""
    print("\n" + "=" * 60)
    print("PHASE 3: VALUE PROPOSITIONS - Monetization Opportunities")
    print("=" * 60)
    
    entries = genesis_log.get("genesis_log", [])
    products = load_product_catalog()
    
    propositions = []
    
    # Proposition 1: Direct Digital Products
    sellable = [e for e in entries if e.get("value_signals", {}).get("sellable")]
    propositions.append({
        "id": "VP-DIGITAL-PRODUCTS",
        "name": "Digital Product Sales",
        "type": "product",
        "description": "Directly sellable digital assets including templates, kits, and guides",
        "asset_count": len(sellable),
        "revenue_model": "one-time purchase",
        "price_range": {"min": 9, "max": 299, "currency": "USD"},
        "channels": ["shopier", "shopify", "etsy", "gumroad"],
        "automation_level": "high",
        "sample_assets": [e["file_path"] for e in sellable[:5]],
    })
    
    # Proposition 2: Service-Ready Capabilities
    service_ready = [e for e in entries if e.get("value_signals", {}).get("service_ready")]
    propositions.append({
        "id": "VP-SERVICE-OFFERINGS",
        "name": "Freelance & Consulting Services",
        "type": "service",
        "description": "Backend, frontend, and automation capabilities packaged as services",
        "asset_count": len(service_ready),
        "revenue_model": "project-based or hourly",
        "price_range": {"min": 100, "max": 50000, "currency": "USD"},
        "channels": ["fiverr", "upwork", "direct"],
        "automation_level": "medium",
        "capabilities": ["backend development", "ai integration", "automation", "youtube content"],
    })
    
    # Proposition 3: SaaS Subscriptions
    propositions.append({
        "id": "VP-SAAS-SUBSCRIPTIONS",
        "name": "SaaS Platform Subscriptions",
        "type": "subscription",
        "description": "Recurring revenue from AutonomaX and Bopper platform subscriptions",
        "products": [p["sku"] for p in products if p.get("type") == "subscription"],
        "revenue_model": "monthly recurring",
        "price_range": {"min": 29, "max": 499, "currency": "USD"},
        "channels": ["shopier", "direct"],
        "automation_level": "high",
    })
    
    # Proposition 4: Training & Education
    propositions.append({
        "id": "VP-TRAINING",
        "name": "Training & Educational Programs",
        "type": "training",
        "description": "Courses, workshops, and coaching programs",
        "products": [p["sku"] for p in products if p.get("type") == "training"],
        "revenue_model": "cohort or self-paced",
        "price_range": {"min": 99, "max": 4999, "currency": "USD"},
        "channels": ["youtube", "teachable", "direct"],
        "automation_level": "medium",
    })
    
    # Proposition 5: High-Ticket Consulting
    propositions.append({
        "id": "VP-CONSULTING",
        "name": "Enterprise Consulting & Advisory",
        "type": "consulting",
        "description": "High-touch AI transformation and revenue operations consulting",
        "products": [p["sku"] for p in products if p.get("type") == "consulting"],
        "revenue_model": "project-based or retainer",
        "price_range": {"min": 5000, "max": 50000, "currency": "USD"},
        "channels": ["linkedin", "direct", "referral"],
        "automation_level": "low",
    })
    
    # Proposition 6: Automation Scripts & Tools
    automation_ready = [e for e in entries if e.get("value_signals", {}).get("automation_ready")]
    propositions.append({
        "id": "VP-AUTOMATION-TOOLS",
        "name": "Automation Scripts & API Access",
        "type": "tool",
        "description": "Productized automation scripts and API access",
        "asset_count": len(automation_ready),
        "revenue_model": "license or subscription",
        "price_range": {"min": 49, "max": 999, "currency": "USD"},
        "channels": ["gumroad", "github sponsors", "direct"],
        "automation_level": "high",
    })
    
    # Calculate total revenue potential
    total_min = sum(p.get("price_range", {}).get("min", 0) for p in propositions)
    total_max = sum(p.get("price_range", {}).get("max", 0) for p in propositions)
    
    value_props = {
        "version": "1.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "system": "Alexandria Value Extraction",
        "summary": {
            "total_propositions": len(propositions),
            "total_sellable_assets": len(sellable),
            "total_service_assets": len(service_ready),
            "total_automation_assets": len(automation_ready),
            "revenue_potential": {
                "min_per_proposition": total_min,
                "max_per_proposition": total_max,
                "currency": "USD",
            },
        },
        "propositions": propositions,
    }
    
    # Write output
    output_path = ALEXANDRIA_DIR / "value_propositions.json"
    output_path.write_text(json.dumps(value_props, indent=2, ensure_ascii=False), encoding="utf-8")
    
    docs_output = DOCS_PROTOCOL_DIR / "value_propositions.json"
    docs_output.write_text(json.dumps(value_props, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"  Total Propositions: {len(propositions)}")
    print(f"  Sellable Assets: {len(sellable)}")
    print(f"  Service-Ready Assets: {len(service_ready)}")
    print(f"  Automation-Ready Assets: {len(automation_ready)}")
    print(f"  Output: {output_path}")
    
    return value_props


def build_revenue_map(value_props: Dict[str, Any]) -> Dict[str, Any]:
    """Build revenue stream mapping."""
    print("\n" + "=" * 60)
    print("PHASE 4: REVENUE MAPPING - Stream Configuration")
    print("=" * 60)
    
    products = load_product_catalog()
    propositions = value_props.get("propositions", [])
    
    # Revenue streams
    streams = []
    
    # Stream 1: Digital Products
    digital_products = [p for p in products if p.get("type") == "digital"]
    streams.append({
        "id": "STREAM-DIGITAL",
        "name": "Digital Product Sales",
        "type": "transactional",
        "products": [p["sku"] for p in digital_products],
        "channels": ["shopier", "shopify", "etsy", "gumroad"],
        "automation": {
            "fulfillment": "automatic",
            "payment": "automatic",
            "support": "semi-automatic",
        },
        "metrics": {
            "target_monthly_revenue": 5000,
            "target_orders": 100,
            "avg_order_value": 50,
        },
    })
    
    # Stream 2: Subscriptions
    subscriptions = [p for p in products if p.get("type") == "subscription"]
    streams.append({
        "id": "STREAM-SUBSCRIPTION",
        "name": "SaaS Subscriptions",
        "type": "recurring",
        "products": [p["sku"] for p in subscriptions],
        "channels": ["shopier", "direct"],
        "automation": {
            "fulfillment": "automatic",
            "payment": "automatic",
            "onboarding": "semi-automatic",
        },
        "metrics": {
            "target_mrr": 10000,
            "target_subscribers": 100,
            "target_churn": 0.05,
        },
    })
    
    # Stream 3: Services
    services = [p for p in products if p.get("type") == "service"]
    streams.append({
        "id": "STREAM-SERVICES",
        "name": "Freelance Services",
        "type": "project",
        "products": [p["sku"] for p in services],
        "channels": ["fiverr", "upwork", "direct"],
        "automation": {
            "lead_capture": "automatic",
            "fulfillment": "manual",
            "invoicing": "semi-automatic",
        },
        "metrics": {
            "target_monthly_revenue": 8000,
            "target_projects": 5,
            "avg_project_value": 1600,
        },
    })
    
    # Stream 4: Consulting
    consulting = [p for p in products if p.get("type") == "consulting"]
    streams.append({
        "id": "STREAM-CONSULTING",
        "name": "Enterprise Consulting",
        "type": "high-ticket",
        "products": [p["sku"] for p in consulting],
        "channels": ["linkedin", "direct", "referral"],
        "automation": {
            "lead_capture": "semi-automatic",
            "fulfillment": "manual",
            "relationship": "manual",
        },
        "metrics": {
            "target_monthly_revenue": 15000,
            "target_clients": 1,
            "avg_engagement_value": 15000,
        },
    })
    
    # Stream 5: Training
    training = [p for p in products if p.get("type") == "training"]
    streams.append({
        "id": "STREAM-TRAINING",
        "name": "Training Programs",
        "type": "cohort",
        "products": [p["sku"] for p in training],
        "channels": ["youtube", "teachable", "direct"],
        "automation": {
            "enrollment": "automatic",
            "content_delivery": "automatic",
            "support": "semi-automatic",
        },
        "metrics": {
            "target_monthly_revenue": 5000,
            "target_enrollments": 10,
            "avg_enrollment_value": 500,
        },
    })
    
    # Calculate totals
    total_target = sum(s["metrics"].get("target_monthly_revenue", 0) for s in streams)
    
    revenue_map = {
        "version": "1.0",
        "created": datetime.now(timezone.utc).isoformat(),
        "system": "Alexandria Revenue Mapping",
        "summary": {
            "total_streams": len(streams),
            "total_products": len(products),
            "target_monthly_revenue": total_target,
            "primary_channels": ["shopier", "fiverr", "linkedin", "youtube"],
        },
        "streams": streams,
        "execution_priority": [
            {"stream": "STREAM-DIGITAL", "reason": "Fastest time-to-revenue, fully automated"},
            {"stream": "STREAM-SUBSCRIPTION", "reason": "Recurring revenue, high LTV"},
            {"stream": "STREAM-SERVICES", "reason": "Established channel (Fiverr), proven demand"},
            {"stream": "STREAM-CONSULTING", "reason": "Highest per-engagement value"},
            {"stream": "STREAM-TRAINING", "reason": "Scalable, builds authority"},
        ],
    }
    
    # Write output
    output_path = ALEXANDRIA_DIR / "revenue_map.json"
    output_path.write_text(json.dumps(revenue_map, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"  Total Streams: {len(streams)}")
    print(f"  Target Monthly Revenue: ${total_target:,}")
    print(f"  Output: {output_path}")
    
    return revenue_map


def print_summary(
    genesis_log: Dict[str, Any],
    knowledge_graph: Dict[str, Any],
    value_props: Dict[str, Any],
    revenue_map: Dict[str, Any],
):
    """Print execution summary."""
    print("\n" + "=" * 60)
    print("ALEXANDRIA CHIMERA GENESIS - EXECUTION COMPLETE")
    print("=" * 60)
    
    entries = genesis_log.get("genesis_log", [])
    nodes = knowledge_graph.get("nodes", [])
    edges = knowledge_graph.get("edges", [])
    props = value_props.get("propositions", [])
    streams = revenue_map.get("streams", [])
    
    print(f"""
SUMMARY:
  Genesis Log:
    - Files Indexed: {len(entries)}
    - Created: {genesis_log.get('created')}
  
  Knowledge Graph:
    - Nodes: {len(nodes)}
    - Edges: {len(edges)}
  
  Value Propositions:
    - Propositions: {len(props)}
    - Sellable Assets: {value_props.get('summary', {}).get('total_sellable_assets', 0)}
    - Service-Ready: {value_props.get('summary', {}).get('total_service_assets', 0)}
  
  Revenue Streams:
    - Streams: {len(streams)}
    - Target MRR: ${revenue_map.get('summary', {}).get('target_monthly_revenue', 0):,}

OUTPUT FILES:
  - {ALEXANDRIA_DIR / 'genesis_log.json'}
  - {ALEXANDRIA_DIR / 'knowledge_graph.json'}
  - {ALEXANDRIA_DIR / 'value_propositions.json'}
  - {ALEXANDRIA_DIR / 'revenue_map.json'}

NEXT STEPS:
  1. Review value propositions for prioritization
  2. Configure revenue stream automation
  3. Deploy Cloud Scheduler jobs for ongoing sync
  4. Monitor KPI dashboard for revenue tracking
""")


def main():
    parser = argparse.ArgumentParser(description="Alexandria Chimera Genesis Runner")
    parser.add_argument("--full", action="store_true", help="Run full genesis with all phases")
    parser.add_argument("--genesis-only", action="store_true", help="Run only genesis log")
    args = parser.parse_args()
    
    print("=" * 60)
    print("ALEXANDRIA CHIMERA GENESIS")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)
    
    ensure_dirs()
    
    # Phase 1: Genesis Log
    genesis_log = run_genesis_log()
    
    if args.genesis_only:
        print("\nGenesis log complete (--genesis-only mode)")
        return
    
    # Phase 2: Knowledge Graph
    knowledge_graph = build_knowledge_graph(genesis_log)
    
    # Phase 3: Value Propositions
    value_props = extract_value_propositions(genesis_log, knowledge_graph)
    
    # Phase 4: Revenue Mapping
    revenue_map = build_revenue_map(value_props)
    
    # Summary
    print_summary(genesis_log, knowledge_graph, value_props, revenue_map)


if __name__ == "__main__":
    main()
