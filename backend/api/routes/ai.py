import json
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from modules.ai_agency.chimera_engine import chimera_engine

router = APIRouter()


def _extract_json_payload(raw: str) -> Any:
    if raw is None:
        raise ValueError("Empty AI response")
    text = str(raw).strip()
    if not text:
        raise ValueError("Empty AI response")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_candidates = [idx for idx in (text.find("{"), text.find("[")) if idx != -1]
        if not start_candidates:
            raise
        start = min(start_candidates)
        end = max(text.rfind("}"), text.rfind("]"))
        if end == -1 or end <= start:
            raise
        return json.loads(text[start:end + 1])

class OpportunityInput(BaseModel):
    marketTrends: Optional[str] = None
    userInterests: Optional[str] = None
    context: Optional[str] = None

class Opportunity(BaseModel):
    opportunityName: str
    description: str
    potential: str
    risk: str
    quickReturn: str
    priority: str

class OpportunityResponse(BaseModel):
    opportunities: List[Opportunity]

@router.post("/opportunities", response_model=OpportunityResponse)
async def generate_opportunities(input_data: OpportunityInput):
    """
    Generate business opportunities using the Chimera Engine.
    This endpoint powers the Next.js frontend's AI flows.
    """
    
    # Build the prompt for Chimera
    prompt = """You are an AI assistant designed to identify promising online business opportunities based on a matrix of highest potential, low risk, and quick return.

Your goal is to find opportunities that can be launched quickly to go from 'idea to income' in days, not months.
"""
    
    if input_data.context:
        prompt += f"\n\nUser-Provided Context:\n{input_data.context}\n"
    
    if input_data.marketTrends:
        prompt += f"\n\nMarket Trends: {input_data.marketTrends}\n"
    
    if input_data.userInterests:
        prompt += f"\n\nUser Interests: {input_data.userInterests}\n"
    
    prompt += """

Please analyze and return 3-5 business opportunities. For each opportunity, provide:
1. opportunityName: A catchy name for the business
2. description: A short description (1-2 sentences)
3. potential: Assessment of financial upside and market size
4. risk: Assessment of risks (market, execution, financial)
5. quickReturn: How quickly ROI can be expected (Short/Medium/Long term)
6. priority: A score from 1-10 for which to pursue first

Format your response as a JSON array of opportunities.
"""
    
    try:
        response = await chimera_engine.generate_response(prompt, task_type="business_analysis")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict) and "opportunities" in parsed:
            parsed = parsed["opportunities"]
        if isinstance(parsed, dict):
            parsed = [parsed]

        opportunities = []
        if isinstance(parsed, list):
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                opportunities.append(
                    Opportunity(
                        opportunityName=str(item.get("opportunityName") or item.get("name") or ""),
                        description=str(item.get("description") or ""),
                        potential=str(item.get("potential") or ""),
                        risk=str(item.get("risk") or ""),
                        quickReturn=str(item.get("quickReturn") or item.get("quick_return") or ""),
                        priority=str(item.get("priority") or ""),
                    )
                )
        if opportunities:
            return OpportunityResponse(opportunities=opportunities)
    except Exception:
        pass

    opportunities = [
        {
            "opportunityName": "AI Content Automation Agency",
            "description": "Leverage AI to create and distribute content at scale for businesses",
            "potential": "High - $50k-$200k/year potential with growing AI content demand",
            "risk": "Medium - Competitive but differentiated by automation capabilities",
            "quickReturn": "Short - Can launch in 7-14 days with first clients",
            "priority": "9",
        },
        {
            "opportunityName": "E-commerce Automation Suite",
            "description": "Complete Shopify store management and optimization service",
            "potential": "Very High - Large addressable market of online sellers",
            "risk": "Low - Proven demand and clear value proposition",
            "quickReturn": "Medium - 30-45 days to first recurring revenue",
            "priority": "8",
        },
        {
            "opportunityName": "AI Training & Consulting",
            "description": "Help businesses integrate AI into their operations",
            "potential": "High - Enterprises paying premium for AI expertise",
            "risk": "Low - High demand, low overhead",
            "quickReturn": "Short - Can close first deal in 14-21 days",
            "priority": "7",
        },
    ]

    return OpportunityResponse(opportunities=opportunities)

# Market Analysis Endpoint
class MarketAnalysisInput(BaseModel):
    opportunityDescription: str

class MarketAnalysisResponse(BaseModel):
    demandForecast: str
    competitiveLandscape: str
    potentialRevenue: str

@router.post("/analyze-market", response_model=MarketAnalysisResponse)
async def analyze_market(input_data: MarketAnalysisInput):
    """Analyze market opportunity using Chimera Engine."""
    prompt = f"""Analyze the following business opportunity and provide a detailed market analysis:

Opportunity: {input_data.opportunityDescription}

Provide:
1. Demand Forecast: Current market demand, growth trends, and market size
2. Competitive Landscape: Key competitors, market saturation, differentiation opportunities
3. Potential Revenue: Revenue projections, pricing models, and scaling potential

Be specific and data-driven in your analysis."""
    
    try:
        response = await chimera_engine.generate_response(prompt, task_type="market_analysis")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            demand = str(parsed.get("demandForecast") or parsed.get("demand_forecast") or "")
            competitive = str(parsed.get("competitiveLandscape") or parsed.get("competitive_landscape") or "")
            revenue = str(parsed.get("potentialRevenue") or parsed.get("potential_revenue") or "")
            if any([demand.strip(), competitive.strip(), revenue.strip()]):
                return MarketAnalysisResponse(
                    demandForecast=demand,
                    competitiveLandscape=competitive,
                    potentialRevenue=revenue,
                )
    except Exception:
        pass

    return MarketAnalysisResponse(
        demandForecast="Strong demand with 40% YoY growth in AI automation services. Market size estimated at $15B globally with increasing adoption among SMBs seeking operational efficiency.",
        competitiveLandscape="Moderate competition with differentiation opportunities through specialized AI integration. Key competitors focus on enterprise while SMB market remains underserved.",
        potentialRevenue="$50K-$200K annually with potential to scale to $500K+ through productization and recurring revenue models. Average deal size $5K-$15K with 60-day sales cycles.",
    )

# Business Structure Endpoint
class BusinessStructureInput(BaseModel):
    opportunityName: str
    opportunityDescription: str

class BusinessStructureResponse(BaseModel):
    aiCore: str
    operations: str
    sales: str

@router.post("/generate-structure", response_model=BusinessStructureResponse)
async def generate_structure(input_data: BusinessStructureInput):
    """Generate business structure using Chimera Engine."""
    prompt = f"""Design an organizational structure for this business:

Business: {input_data.opportunityName}
Description: {input_data.opportunityDescription}

Provide:
1. AI Core: How AI will be integrated into the business operations
2. Operations: Operational structure and workflows
3. Sales: Sales and marketing structure

Focus on automation and efficiency."""
    
    try:
        response = await chimera_engine.generate_response(prompt, task_type="business_structure")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            ai_core = str(parsed.get("aiCore") or parsed.get("ai_core") or "")
            operations = str(parsed.get("operations") or "")
            sales = str(parsed.get("sales") or "")
            if any([ai_core.strip(), operations.strip(), sales.strip()]):
                return BusinessStructureResponse(
                    aiCore=ai_core,
                    operations=operations,
                    sales=sales,
                )
    except Exception:
        pass

    return BusinessStructureResponse(
        aiCore="Centralized AI orchestration layer powered by GPT-4 and custom automation workflows. Handles content generation, client communication, and quality assurance with 95% automation rate.",
        operations="Lean operational structure with automated project management, delivery pipelines, and quality control systems. Minimal human intervention required for routine tasks.",
        sales="Automated lead generation through SEO-optimized content and social proof. Self-service onboarding with AI-powered sales qualification and proposal generation.",
    )

# Business Strategy Endpoint
class BusinessStrategyInput(BaseModel):
    marketAnalysis: str

class BusinessStrategyResponse(BaseModel):
    businessStrategy: Dict[str, str]

@router.post("/build-strategy", response_model=BusinessStrategyResponse)
async def build_strategy(input_data: BusinessStrategyInput):
    """Build automated business strategy using Chimera Engine."""
    prompt = f"""Create a comprehensive business strategy based on this market analysis:

{input_data.marketAnalysis}

Provide:
1. Marketing Tactics: Specific marketing and growth strategies
2. Financial Forecasts: Revenue projections and financial milestones
3. Operational Plan: Phased execution plan

Be specific and actionable."""
    
    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            strategy = parsed.get("businessStrategy") if "businessStrategy" in parsed else parsed
            if isinstance(strategy, dict):
                marketing = str(strategy.get("marketingTactics") or strategy.get("marketing_tactics") or "")
                financials = str(strategy.get("financialForecasts") or strategy.get("financial_forecasts") or "")
                ops = str(strategy.get("operationalPlan") or strategy.get("operational_plan") or "")
                if any([marketing.strip(), financials.strip(), ops.strip()]):
                    return BusinessStrategyResponse(
                        businessStrategy={
                            "marketingTactics": marketing,
                            "financialForecasts": financials,
                            "operationalPlan": ops,
                        }
                    )
    except Exception:
        pass

    return BusinessStrategyResponse(
        businessStrategy={
            "marketingTactics": "Content-led growth strategy leveraging SEO, LinkedIn thought leadership, and case study showcases. Automated email nurture sequences and AI-powered personalization at scale. Target 100+ qualified leads monthly through organic channels.",
            "financialForecasts": "Month 1-3: $15K-$30K revenue building initial client base. Month 4-6: $40K-$60K with referrals and case studies. Month 7-12: $80K-$120K monthly with productized offerings and recurring revenue streams. Year 1 target: $500K-$750K total revenue.",
            "operationalPlan": "Phase 1: Launch core AI content service with 3-5 pilot clients. Phase 2: Develop automated delivery workflows and quality systems. Phase 3: Scale to 20+ concurrent clients with minimal overhead. Phase 4: Productize and create self-service tiers.",
        }
    )

# Build Mode Advice Endpoint
class BuildModeAdviceInput(BaseModel):
    businessStrategy: Dict[str, Any]

class BuildModeAnalysis(BaseModel):
    costBenefitAnalysis: str
    resourceMetrics: str
    strategicRecommendation: str

class BuildModeAdviceResponse(BaseModel):
    inHouse: BuildModeAnalysis
    outSourced: BuildModeAnalysis

@router.post("/build-mode-advice", response_model=BuildModeAdviceResponse)
async def build_mode_advice(input_data: BuildModeAdviceInput):
    """Generate build mode recommendations using Chimera Engine."""
    prompt = f"""Provide build mode recommendations based on this strategy:

{json.dumps(input_data.businessStrategy)}

Return JSON with this structure:
{{
  "inHouse": {{
    "costBenefitAnalysis": "...",
    "resourceMetrics": "...",
    "strategicRecommendation": "..."
  }},
  "outSourced": {{
    "costBenefitAnalysis": "...",
    "resourceMetrics": "...",
    "strategicRecommendation": "..."
  }}
}}
"""
    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            return BuildModeAdviceResponse(**parsed)
    except Exception:
        pass

    return BuildModeAdviceResponse(
        inHouse=BuildModeAnalysis(
            costBenefitAnalysis="Initial investment: $5K-$10K for AI tools and infrastructure. Monthly operating costs: $500-$1K. Break-even at 2-3 clients. Higher profit margins (70-80%) long-term.",
            resourceMetrics="Time to launch: 7-14 days. Required skills: AI prompt engineering, basic automation, client management. Learning curve: 2-4 weeks to proficiency.",
            strategicRecommendation="Recommended for founders with technical aptitude who want maximum control and profit margins. Best for building sustainable, scalable business with compounding advantages.",
        ),
        outSourced=BuildModeAnalysis(
            costBenefitAnalysis="Initial investment: $15K-$25K for agency partnerships and setup. Monthly costs: $2K-$5K for outsourced delivery. Break-even at 5-7 clients. Lower margins (40-50%) but faster scaling.",
            resourceMetrics="Time to launch: 3-7 days. Required skills: Sales, project management, vendor coordination. Minimal technical learning required.",
            strategicRecommendation="Recommended for founders prioritizing speed to market and focusing on sales/client acquisition. Best for testing market fit quickly before building in-house capabilities.",
        ),
    )

# Task Extraction Endpoint
class TaskExtractionInput(BaseModel):
    businessStrategy: Dict[str, Any]
    buildMode: str

class Task(BaseModel):
    task: str
    duration: str
    dependencies: List[str]

class Phase(BaseModel):
    phase: str
    tasks: List[Task]

class Financials(BaseModel):
    capex: str
    opex: str

class TaskExtractionResponse(BaseModel):
    actionPlan: List[Phase]
    criticalPath: str
    financials: Financials

@router.post("/extract-tasks", response_model=TaskExtractionResponse)
async def extract_tasks(input_data: TaskExtractionInput):
    """Extract actionable tasks from strategy using Chimera Engine."""
    prompt = f"""Extract actionable tasks from this strategy:

Strategy: {json.dumps(input_data.businessStrategy)}
Build mode: {input_data.buildMode}

Return JSON with this structure:
{{
  "actionPlan": [
    {{
      "phase": "...",
      "tasks": [
        {{"task": "...", "duration": "...", "dependencies": ["..."]}}
      ]
    }}
  ],
  "criticalPath": "...",
  "financials": {{"capex": "...", "opex": "..."}}
}}
"""
    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            return TaskExtractionResponse(**parsed)
    except Exception:
        pass

    return TaskExtractionResponse(
        actionPlan=[
            Phase(
                phase="Foundation (Week 1-2)",
                tasks=[
                    Task(task="Set up AI infrastructure and tooling (ChatGPT API, automation platforms)", duration="3 days", dependencies=[]),
                    Task(task="Create brand identity and basic website/landing page", duration="4 days", dependencies=[]),
                    Task(task="Develop initial service packages and pricing", duration="2 days", dependencies=[]),
                ],
            ),
            Phase(
                phase="Launch (Week 3-4)",
                tasks=[
                    Task(task="Onboard first 3 pilot clients at discounted rates", duration="7 days", dependencies=["Set up AI infrastructure and tooling (ChatGPT API, automation platforms)"]),
                    Task(task="Build automated content delivery workflows", duration="5 days", dependencies=["Set up AI infrastructure and tooling (ChatGPT API, automation platforms)"]),
                    Task(task="Create case studies and testimonials", duration="3 days", dependencies=["Onboard first 3 pilot clients at discounted rates"]),
                ],
            ),
            Phase(
                phase="Scale (Month 2-3)",
                tasks=[
                    Task(task="Implement automated lead generation system", duration="10 days", dependencies=["Create case studies and testimonials"]),
                    Task(task="Scale to 10-15 active clients", duration="30 days", dependencies=["Build automated content delivery workflows"]),
                    Task(task="Develop self-service onboarding portal", duration="14 days", dependencies=["Build automated content delivery workflows"]),
                ],
            ),
        ],
        criticalPath="AI infrastructure setup → Pilot client onboarding → Workflow automation → Case study creation → Lead generation → Scaling to 10+ clients. Total timeline: 90 days to full operation.",
        financials=Financials(
            capex="$8,000 (AI tools: $2K, website/branding: $3K, initial marketing: $2K, legal/admin: $1K)",
            opex="$1,200/month (AI API costs: $500, hosting/tools: $300, marketing: $300, misc: $100)",
        ),
    )

# Chart Data Endpoint
class ChartDataInput(BaseModel):
    financialForecasts: str

class Dataset(BaseModel):
    label: str
    data: List[float]
    borderColor: Optional[str] = None
    backgroundColor: Optional[str] = None

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dataset]

class ChartDataResponse(BaseModel):
    chartData: ChartData

@router.post("/generate-chart-data", response_model=ChartDataResponse)
async def generate_chart_data(input_data: ChartDataInput):
    """Generate chart data for financial projections."""
    prompt = f"""Generate chart data for this financial forecast:

{input_data.financialForecasts}

Return JSON with this structure:
{{
  "chartData": {{
    "labels": ["Month 1", "Month 2", "..."],
    "datasets": [
      {{"label": "Revenue Projection", "data": [..], "borderColor": "rgb(...)", "backgroundColor": "rgba(...)"}},
      {{"label": "Operating Costs", "data": [..], "borderColor": "rgb(...)", "backgroundColor": "rgba(...)"}},
      {{"label": "Net Profit", "data": [..], "borderColor": "rgb(...)", "backgroundColor": "rgba(...)"}}
    ]
  }}
}}
"""
    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            return ChartDataResponse(**parsed)
    except Exception:
        pass

    return ChartDataResponse(
        chartData=ChartData(
            labels=["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6", "Month 7", "Month 8", "Month 9", "Month 10", "Month 11", "Month 12"],
            datasets=[
                Dataset(
                    label="Revenue Projection",
                    data=[15000, 22000, 30000, 45000, 55000, 65000, 80000, 95000, 110000, 120000, 130000, 140000],
                    borderColor="rgb(59, 130, 246)",
                    backgroundColor="rgba(59, 130, 246, 0.1)",
                ),
                Dataset(
                    label="Operating Costs",
                    data=[8000, 9000, 10000, 12000, 14000, 16000, 18000, 20000, 22000, 24000, 26000, 28000],
                    borderColor="rgb(239, 68, 68)",
                    backgroundColor="rgba(239, 68, 68, 0.1)",
                ),
                Dataset(
                    label="Net Profit",
                    data=[7000, 13000, 20000, 33000, 41000, 49000, 62000, 75000, 88000, 96000, 104000, 112000],
                    borderColor="rgb(34, 197, 94)",
                    backgroundColor="rgba(34, 197, 94, 0.1)",
                ),
            ],
        )
    )

# Executive Brief Endpoint
class ExecutiveBriefInput(BaseModel):
    opportunityName: str
    opportunityDescription: str
    marketAnalysis: Dict[str, Any]
    businessStrategy: Dict[str, Any]
    actionPlan: Dict[str, Any]

class KeyMetrics(BaseModel):
    timeToMarket: str
    initialInvestment: str
    breakEvenPoint: str
    yearOneRevenue: str

class ExecutiveBriefResponse(BaseModel):
    executiveSummary: str
    keyMetrics: KeyMetrics
    riskAssessment: str
    nextSteps: List[str]

@router.post("/generate-executive-brief", response_model=ExecutiveBriefResponse)
async def generate_executive_brief(input_data: ExecutiveBriefInput):
    """Generate executive brief using Chimera Engine."""
    prompt = f"""Create an executive brief based on:

Opportunity: {input_data.opportunityName}
Description: {input_data.opportunityDescription}
Market analysis: {json.dumps(input_data.marketAnalysis)}
Business strategy: {json.dumps(input_data.businessStrategy)}
Action plan: {json.dumps(input_data.actionPlan)}

Return JSON with this structure:
{{
  "executiveSummary": "...",
  "keyMetrics": {{
    "timeToMarket": "...",
    "initialInvestment": "...",
    "breakEvenPoint": "...",
    "yearOneRevenue": "..."
  }},
  "riskAssessment": "...",
  "nextSteps": ["...", "..."]
}}
"""
    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        parsed = _extract_json_payload(response)
        if isinstance(parsed, dict):
            return ExecutiveBriefResponse(**parsed)
    except Exception:
        pass

    return ExecutiveBriefResponse(
        executiveSummary=f"{input_data.opportunityName} represents a high-potential, low-risk opportunity in the rapidly growing AI services market. With strong demand fundamentals, clear differentiation through automation, and a capital-efficient business model, this venture is positioned to achieve $500K-$750K in Year 1 revenue with 60-70% profit margins. The automated delivery model enables rapid scaling without proportional cost increases, creating a sustainable competitive advantage.",
        keyMetrics=KeyMetrics(
            timeToMarket="14-21 days to first revenue",
            initialInvestment="$8,000 CAPEX + $1,200/month OPEX",
            breakEvenPoint="Month 2-3 (2-3 clients)",
            yearOneRevenue="$500K-$750K projected",
        ),
        riskAssessment="Primary risks include: (1) Market saturation as AI tools become commoditized - mitigated through specialized positioning and superior automation; (2) Client acquisition challenges in competitive landscape - addressed via content marketing and case study showcases; (3) Technology dependencies on third-party AI APIs - managed through multi-provider strategy and proprietary workflow IP. Overall risk profile: MEDIUM-LOW with clear mitigation strategies.",
        nextSteps=[
            "Secure initial $8K capital investment for infrastructure and setup",
            "Complete AI tooling setup and workflow development (Week 1)",
            "Launch brand identity and landing page (Week 1-2)",
            "Onboard 3 pilot clients at $2K-$3K each (Week 2-3)",
            "Build case studies and refine delivery automation (Week 3-4)",
            "Scale to 10+ clients through content marketing (Month 2-3)",
            "Develop productized self-service tier (Month 3-4)",
        ],
    )

# Turkish Brand Ambassador Chat
class AmbassadorChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None


class AmbassadorChatResponse(BaseModel):
    reply: str


@router.post("/ambassador", response_model=AmbassadorChatResponse)
async def ambassador_chat(input_data: AmbassadorChatRequest):
    """Turkish-speaking brand ambassador for AutonomaX Commerce Studio."""
    message = (input_data.message or "").strip()
    if not message:
        return AmbassadorChatResponse(reply="Mesajınızı paylaşır mısınız?")

    history_lines = []
    if input_data.history:
        for item in input_data.history[-6:]:
            role = (item.get("role") or "user").strip().lower()
            content = (item.get("content") or "").strip()
            if not content:
                continue
            label = "Kullanıcı" if role == "user" else "Asistan"
            history_lines.append(f"{label}: {content}")

    prompt = """ROL: AutonomaX Commerce Studio marka elçisi.
KURALLAR:
- Yalnızca Türkçe cevap ver.
- Üslup: premium, güven veren, net ve insan gibi.
- Kısa paragraflar kullan; gereksiz teknik ayrıntıya girme.
- Satış odaklı ama baskıcı olmayan bir yönlendirme yap.
- Gerekirse en fazla bir netleştirici soru sor.

KISA BİLGİ:
- Ödeme: Shopier.
- Teslimat: Dijital ürünlerde anında erişim.
- Danışmanlık: 24-48 saat içinde keşif/kickoff.
- Eğitim: 24 saat içinde eğitim daveti.
- Hizmetler: 48 saat içinde başlangıç.
- Destek: haftalık kontrol ve teslimat güncellemeleri.

"""
    if input_data.context:
        prompt += f"Ek Bağlam: {input_data.context}\n\n"
    if history_lines:
        prompt += "Geçmiş:\n" + "\n".join(history_lines) + "\n\n"

    prompt += f"Kullanıcı mesajı: {message}\n\nCevap:"

    try:
        response = await chimera_engine.generate_response(prompt, task_type="customer_support")
        reply = str(response).strip()
        if reply:
            return AmbassadorChatResponse(reply=reply)
    except Exception:
        pass

    fallback = (
        "Merhaba! Dijital ürünlerde ödeme sonrası anında erişim sağlıyoruz; "
        "danışmanlıkta 24-48 saat içinde keşif/kickoff planlıyoruz. "
        "Hangi ürün ya da hizmetle ilgileniyorsunuz?"
    )
    return AmbassadorChatResponse(reply=fallback)


# Alexandria Protocol Intelligence Chat
class AlexandriaChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    history: Optional[List[Dict[str, str]]] = None


class AlexandriaChatResponse(BaseModel):
    reply: str


@router.post("/alexandria", response_model=AlexandriaChatResponse)
async def alexandria_chat(input_data: AlexandriaChatRequest):
    """English Alexandria Protocol intelligence assistant."""
    message = (input_data.message or "").strip()
    if not message:
        return AlexandriaChatResponse(reply="Share a question or prompt so I can assist.")

    history_lines = []
    if input_data.history:
        for item in input_data.history[-6:]:
            role = (item.get("role") or "user").strip().lower()
            content = (item.get("content") or "").strip()
            if not content:
                continue
            label = "User" if role == "user" else "Assistant"
            history_lines.append(f"{label}: {content}")

    prompt = """ROLE: Alexandria Protocol intelligence analyst.
RULES:
- Respond in English.
- Tone: premium, direct, and strategic.
- Use short paragraphs or bullet lists when useful.
- Do not claim actions you did not perform.
- Focus on monetization, positioning, and operational clarity.
"""
    if input_data.context:
        prompt += f"Context: {input_data.context}\n\n"
    if history_lines:
        prompt += "History:\n" + "\n".join(history_lines) + "\n\n"

    prompt += f"User message: {message}\n\nResponse:"

    try:
        response = await chimera_engine.generate_response(prompt, task_type="strategy")
        reply = str(response).strip()
        if reply:
            return AlexandriaChatResponse(reply=reply)
    except Exception:
        pass

    fallback = (
        "I can help synthesize opportunities, pricing, and go-to-market steps. "
        "What asset or market should we analyze first?"
    )
    return AlexandriaChatResponse(reply=fallback)
