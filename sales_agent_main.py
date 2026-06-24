"""
AI B2B Sales Agent - Main Orchestrator
Uses Claude Sonnet 4.5 with Agents SDK and MCP for end-to-end sales automation
"""

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
from anthropic import Anthropic

# Initialize Anthropic client
client = Anthropic()

class SalesOrchestrator:
    """Main orchestrator for the B2B sales automation workflow"""
    
    def __init__(self):
        self.model = "claude-sonnet-4-20250514"
        self.conversation_history = []
        
    async def process_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single lead through the entire sales workflow
        
        Args:
            lead_data: Initial lead information (company name, industry, contact info)
            
        Returns:
            Complete workflow results including research, qualification, and outreach
        """
        workflow_results = {
            "lead_id": lead_data.get("id", "unknown"),
            "company": lead_data.get("company"),
            "timestamp": datetime.now().isoformat(),
            "stages": {}
        }
        
        # Stage 1: Lead Research
        print(f"\n🔍 Stage 1: Researching {lead_data['company']}...")
        research_results = await self.research_lead(lead_data)
        workflow_results["stages"]["research"] = research_results
        
        # Stage 2: Lead Qualification
        print(f"\n✅ Stage 2: Qualifying {lead_data['company']}...")
        qualification_results = await self.qualify_lead(lead_data, research_results)
        workflow_results["stages"]["qualification"] = qualification_results
        
        # Stage 3: Personalized Outreach (only if qualified)
        if qualification_results.get("qualified", False):
            print(f"\n📧 Stage 3: Creating outreach for {lead_data['company']}...")
            outreach_results = await self.create_outreach(
                lead_data, research_results, qualification_results
            )
            workflow_results["stages"]["outreach"] = outreach_results
        else:
            print(f"\n❌ Lead not qualified. Skipping outreach.")
            workflow_results["stages"]["outreach"] = {
                "status": "skipped",
                "reason": qualification_results.get("reason")
            }
        
        # Stage 4: CRM Update
        print(f"\n💾 Stage 4: Updating CRM...")
        await self.update_crm(workflow_results)
        
        return workflow_results
    
    async def research_lead(self, lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Research lead using web search MCP tool
        """
        research_prompt = f"""
You are a B2B sales research agent. Research the following company thoroughly:

Company: {lead_data.get('company')}
Industry: {lead_data.get('industry', 'Unknown')}
Website: {lead_data.get('website', 'Unknown')}

Use web search to find:
1. Company overview and size
2. Recent news and announcements
3. Key decision makers
4. Technology stack they use
5. Pain points and challenges in their industry
6. Recent funding or growth signals
7. Competitors they might be evaluating

Provide a comprehensive research summary in JSON format with these fields:
- company_size
- revenue_range
- key_decision_makers
- recent_news
- tech_stack
- pain_points
- buying_signals
- competitive_intelligence
"""
        
        response = client.messages.create(
            model=self.model,
            max_tokens=4000,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search"
                }
            ],
            messages=[{"role": "user", "content": research_prompt}]
        )
        
        # Extract research results
        research_text = self._extract_response_text(response)
        
        return {
            "raw_research": research_text,
            "completed_at": datetime.now().isoformat()
        }
    
    async def qualify_lead(
        self, 
        lead_data: Dict[str, Any], 
        research_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Qualify lead based on research using Claude's reasoning
        """
        qualification_prompt = f"""
You are a B2B sales qualification agent. Based on the research below, qualify this lead using BANT criteria:

LEAD INFO:
{json.dumps(lead_data, indent=2)}

RESEARCH:
{research_results['raw_research']}

Evaluate the lead on:
1. BUDGET: Do they have the financial capacity?
2. AUTHORITY: Can we reach decision makers?
3. NEED: Do they have clear pain points we can solve?
4. TIMELINE: Are there buying signals indicating near-term purchase?

Provide your qualification in JSON format:
{{
  "qualified": true/false,
  "score": 0-100,
  "budget_score": 0-25,
  "authority_score": 0-25,
  "need_score": 0-25,
  "timeline_score": 0-25,
  "reasoning": "Detailed explanation",
  "recommended_action": "Next steps",
  "priority": "high/medium/low"
}}
"""
        
        response = client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": qualification_prompt}]
        )
        
        qualification_text = self._extract_response_text(response)
        
        # Parse JSON from response
        try:
            qualification_data = json.loads(
                qualification_text.replace("```json", "").replace("```", "").strip()
            )
        except:
            qualification_data = {
                "qualified": False,
                "score": 0,
                "reasoning": qualification_text
            }
        
        return qualification_data
    
    async def create_outreach(
        self,
        lead_data: Dict[str, Any],
        research_results: Dict[str, Any],
        qualification_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create personalized outreach email and LinkedIn message
        """
        outreach_prompt = f"""
You are a B2B sales outreach specialist. Create highly personalized outreach for this qualified lead:

LEAD: {json.dumps(lead_data, indent=2)}
RESEARCH: {research_results['raw_research']}
QUALIFICATION: {json.dumps(qualification_results, indent=2)}

Create:
1. A personalized cold email (subject + body, max 150 words)
2. A LinkedIn connection request message (max 300 characters)
3. A follow-up email for 3 days later

Guidelines:
- Reference specific company news or initiatives
- Address their pain points directly
- Include a clear, low-friction call to action
- Use conversational, human tone
- No generic sales language
- Create value immediately

Return as JSON:
{{
  "email": {{
    "subject": "...",
    "body": "...",
    "call_to_action": "..."
  }},
  "linkedin_message": "...",
  "follow_up_email": {{
    "subject": "...",
    "body": "..."
  }},
  "talking_points": ["point1", "point2", "point3"]
}}
"""
        
        response = client.messages.create(
            model=self.model,
            max_tokens=3000,
            messages=[{"role": "user", "content": outreach_prompt}]
        )
        
        outreach_text = self._extract_response_text(response)
        
        try:
            outreach_data = json.loads(
                outreach_text.replace("```json", "").replace("```", "").strip()
            )
        except:
            outreach_data = {"raw": outreach_text}
        
        outreach_data["created_at"] = datetime.now().isoformat()
        
        return outreach_data
    
    async def update_crm(self, workflow_results: Dict[str, Any]):
        """
        Update CRM with workflow results (simulated MCP call)
        """
        # In production, this would use an MCP server for CRM integration
        # For now, we'll simulate the update
        crm_payload = {
            "lead_id": workflow_results["lead_id"],
            "company": workflow_results["company"],
            "last_activity": datetime.now().isoformat(),
            "qualification_score": workflow_results["stages"]["qualification"].get("score", 0),
            "status": "qualified" if workflow_results["stages"]["qualification"].get("qualified") else "unqualified",
            "next_action": workflow_results["stages"]["qualification"].get("recommended_action"),
            "research_summary": workflow_results["stages"]["research"]["raw_research"][:500],
        }
        
        print(f"📊 CRM Updated: {json.dumps(crm_payload, indent=2)}")
        
        return {"status": "success", "crm_id": workflow_results["lead_id"]}
    
    def _extract_response_text(self, response) -> str:
        """Extract text from Claude's response"""
        text_content = []
        for block in response.content:
            if hasattr(block, 'text'):
                text_content.append(block.text)
        return "\n".join(text_content)


async def main():
    """
    Example usage of the B2B Sales Orchestrator
    """
    # Sample lead data
    sample_leads = [
        {
            "id": "lead_001",
            "company": "TechCorp Industries",
            "industry": "SaaS",
            "website": "techcorp.example.com",
            "contact_name": "Sarah Johnson",
            "contact_title": "VP of Engineering",
            "contact_email": "sarah.johnson@techcorp.example.com"
        },
        {
            "id": "lead_002", 
            "company": "FinanceFlow Solutions",
            "industry": "FinTech",
            "website": "financeflow.example.com",
            "contact_name": "Michael Chen",
            "contact_title": "CTO",
            "contact_email": "m.chen@financeflow.example.com"
        }
    ]
    
    orchestrator = SalesOrchestrator()
    
    print("🚀 Starting B2B Sales Automation Workflow\n")
    print("=" * 60)
    
    results = []
    for lead in sample_leads:
        try:
            print(f"\n{'='*60}")
            print(f"Processing: {lead['company']}")
            print(f"{'='*60}")
            
            result = await orchestrator.process_lead(lead)
            results.append(result)
            
            print(f"\n✅ Completed processing {lead['company']}")
            
        except Exception as e:
            print(f"\n❌ Error processing {lead['company']}: {str(e)}")
            continue
    
    # Summary report
    print(f"\n\n{'='*60}")
    print("📊 WORKFLOW SUMMARY")
    print(f"{'='*60}")
    print(f"Total leads processed: {len(results)}")
    
    qualified_count = sum(
        1 for r in results 
        if r["stages"]["qualification"].get("qualified", False)
    )
    print(f"Qualified leads: {qualified_count}")
    print(f"Outreach messages created: {qualified_count}")
    
    # Save results
    with open("sales_workflow_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to sales_workflow_results.json")


if __name__ == "__main__":
    asyncio.run(main())
