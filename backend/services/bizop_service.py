import csv
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.bizop import BizOpportunity

logger = logging.getLogger(__name__)


@dataclass
class BizOpportunityRecord:
    source: str
    source_id: str
    title: str
    description: str
    rationale: str
    potential: str
    risk: str
    quick_return: str
    priority: str
    image_url: Optional[str]
    tags: List[str]
    metadata: Dict[str, Any]
    raw_data: Dict[str, Any]


class BizOpportunityService:
    def __init__(self, data_root: Optional[Path] = None) -> None:
        env_root = os.getenv("BIZOP_DATA_ROOT")
        if env_root:
            self.data_root = Path(env_root)
        else:
            self.data_root = data_root or Path(__file__).resolve().parents[2] / "docs"

    async def list_opportunities(
        self,
        session: AsyncSession,
        source: Optional[str] = None,
        limit: int = 200,
    ) -> List[BizOpportunity]:
        query = select(BizOpportunity)
        if source:
            query = query.where(BizOpportunity.source == source)
        query = query.limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def sync_from_sources(self, session: AsyncSession) -> Dict[str, Any]:
        records = []
        records.extend(self._load_value_propositions())
        records.extend(self._load_ranked_opportunities())

        if not records:
            return {"inserted": 0, "updated": 0, "total": 0}

        existing = await session.execute(select(BizOpportunity))
        existing_map: Dict[Tuple[str, str], BizOpportunity] = {
            (row.source, row.source_id): row for row in existing.scalars().all()
        }

        inserted = 0
        updated = 0
        for record in records:
            key = (record.source, record.source_id)
            existing_row = existing_map.get(key)
            if existing_row:
                self._apply_record(existing_row, record)
                updated += 1
            else:
                row = BizOpportunity(
                    id=str(uuid4()),
                    source=record.source,
                    source_id=record.source_id,
                    title=record.title,
                    description=record.description,
                    rationale=record.rationale,
                    potential=record.potential,
                    risk=record.risk,
                    quick_return=record.quick_return,
                    priority=record.priority,
                    image_url=record.image_url,
                    tags=record.tags,
                    metadata_json=record.metadata,
                    raw_data=record.raw_data,
                )
                session.add(row)
                inserted += 1

        await session.commit()
        return {"inserted": inserted, "updated": updated, "total": len(records)}

    def _apply_record(self, row: BizOpportunity, record: BizOpportunityRecord) -> None:
        row.title = record.title
        row.description = record.description
        row.rationale = record.rationale
        row.potential = record.potential
        row.risk = record.risk
        row.quick_return = record.quick_return
        row.priority = record.priority
        row.image_url = record.image_url
        row.tags = record.tags
        row.metadata_json = record.metadata
        row.raw_data = record.raw_data

    def _load_value_propositions(self) -> List[BizOpportunityRecord]:
        path = self.data_root / "alexandria_protocol" / "value_propositions.json"
        logger.info(f"Loading value propositions from: {path} (exists: {path.exists()})")
        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        records: List[BizOpportunityRecord] = []
        records.extend(
            self._records_from_collection(
                payload.get("consultancy_proposals", []),
                source="alexandria_consultancy",
                tag="consultancy",
            )
        )
        records.extend(
            self._records_from_collection(
                payload.get("freelance_services", []),
                source="alexandria_freelance",
                tag="freelance",
            )
        )
        records.extend(
            self._records_from_collection(
                payload.get("digital_products", []),
                source="alexandria_products",
                tag="digital_product",
            )
        )
        return records

    def _records_from_collection(
        self,
        items: List[Dict[str, Any]],
        source: str,
        tag: str,
    ) -> List[BizOpportunityRecord]:
        records: List[BizOpportunityRecord] = []
        for item in items:
            title = item.get("title", "Untitled Opportunity")
            description = item.get("description") or item.get("service_description") or item.get("problem_statement", "")
            rationale = item.get("value_proposition") or item.get("proposed_solution", "")
            potential = item.get("revenue_potential") or item.get("pricing_model", "")
            risk = item.get("risk", "Not specified")
            quick_return = item.get("timeline") or item.get("estimated_effort", "")
            priority = item.get("priority") or item.get("pricing_strategy", {}).get("single_purchase", "")
            records.append(
                BizOpportunityRecord(
                    source=source,
                    source_id=item.get("id", title),
                    title=title,
                    description=description,
                    rationale=rationale,
                    potential=potential,
                    risk=risk,
                    quick_return=quick_return,
                    priority=str(priority),
                    image_url=item.get("image_url"),
                    tags=[tag],
                    metadata={
                        "target_clients": item.get("target_clients"),
                        "target_audience": item.get("target_audience"),
                        "distribution_channels": item.get("distribution_channels"),
                    },
                    raw_data=item,
                )
            )
        return records

    def _load_ranked_opportunities(self) -> List[BizOpportunityRecord]:
        path = self.data_root / "rankedopportunities.csv"
        logger.info(f"Loading ranked opportunities from: {path} (exists: {path.exists()})")
        if not path.exists():
            return []

        records: List[BizOpportunityRecord] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            rows = list(reader)

        for row_index, row in enumerate(rows):
            if not row or len(row) < 5:
                continue
            if row_index == 0 and row[0].lower().startswith("object-cover"):
                continue

            image_url = row[0] if row[0] else None
            rank = row[1].strip() if len(row) > 1 else ""
            title = row[2].strip() if len(row) > 2 else "Untitled Opportunity"
            description = row[3].strip() if len(row) > 3 else ""
            rationale = row[4].strip() if len(row) > 4 else ""
            potential = row[5].strip() if len(row) > 5 else ""
            risk = row[6].strip() if len(row) > 6 else ""
            quick_return = row[7].strip() if len(row) > 7 else ""
            priority_raw = row[8].strip() if len(row) > 8 else ""

            priority = self._parse_priority(priority_raw)
            source_id = rank or title
            records.append(
                BizOpportunityRecord(
                    source="ranked_opportunities",
                    source_id=source_id,
                    title=title,
                    description=description,
                    rationale=rationale,
                    potential=potential,
                    risk=risk,
                    quick_return=quick_return,
                    priority=priority,
                    image_url=image_url,
                    tags=["ranked"],
                    metadata={"rank": rank, "priority_raw": priority_raw},
                    raw_data={"row": row},
                )
            )

        return records

    def _parse_priority(self, value: str) -> str:
        if not value:
            return ""
        digits = "".join(ch for ch in value if ch.isdigit())
        return digits or value
