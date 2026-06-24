"""
Integrated B2B Sales Agent using Claude with MCP Tools
Demonstrates full workflow with CRM and Email MCP server integration
"""

import asyncio
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
from anthropic import Anthropic

client = Anthropic()


class IntegratedSalesAgent:
    """Sales agent with full MCP integration"""
    
    def __init__(self):
        self.model = "claude-sonnet-4-20250514"
        
        # Define MCP tools that will be available
        self.mcp_tools = [
            # Web search (built-in)
            {
                "type": "web_search_20250305",
                "name": "web_search"
            },
            # CRM tools
            {
                "type": "function",
                "name": "crm_create_lead",
                "description": "Create a new lead in the CRM system",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "company": {"type": "string"},
                        "contact_name": {"type": "string"},
                        "contact_email": {"type": "string"},
                        "contact_title": {"type": "string"},
                        "industry": {"type": "string"},
                        "website": {"type": "string"}
                    },
                    "required": ["company", "contact_email"]
                }
            },
            {
                "type": "function",
                "name": "crm_update_lead",
                "description": "Update lead with qualification score and status",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"},
                        "status": {"type": "string"},
                        "qualification_score": {"type": "number"},
                        "notes": {"type": "string"},
                        "next_action": {"type": "string"}
                    },
                    "required": ["lead_id"]
                }
            },
            # Email tools
            {
                "type": "function",
                "name": "email_send",
                "description": "Send a personalized email",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "lead_id": {"type": "string"}
                    },
                    "required": ["to", "subject", "body"]
                }
            },
            {
                "type": "function",
                "name": "email_schedule",
                "description": "Schedule a follow-up email",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "send_at": {"type": "string"},
                        "lead_id": {"type": "string"}
                    },
                    "required": ["to", "subject", "body", "send_at"]
                }
            }
        ]
    
    async def execute_sales_workflow(
        self, 
        lead_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complete sales workflow with agentic behavior
        """
        print(f"\n{'='*70}")
        print(f"🚀 Starting Agentic Sales Workflow for {lead_info['company']}")
        print(f"{'='*70}\n")
        
        # Build the agentic prompt
        system_prompt = """You are an expert B2B sales agent with access to CRM and email tools.

Your mission: Execute a complete sales workflow for the provided lead.

WORKFLOW STEPS:
1. Research the company using web search
2. Create lead in CRM with crm_create_lead
3. Analyze research and qualify the lead (BANT criteria)
4. Update CRM with qualification using crm_update_lead
5. If qualified (score >= 60), create personalized outreach email
6. Send immediate email using email_send
7. Schedule follow-up email for 3 days later using email_schedule
8. Provide final summary

QUALIFICATION CRITERIA (BANT):
- Budget: Financial capacity (0-25 points)
- Authority: Can reach decision makers (0-25 points)
- Need: Clear pain points we solve (0-25 points)
- Timeline: Buying signals (0-25 points)
Total: 60+ = qualified, 40-59 = nurture, <40 = unqualified

OUTREACH GUIDELINES:
- Reference specific company news or initiatives
- Address pain points directly
- Keep emails under 150 words
- Include clear, low-friction CTA
- Use conversational tone, avoid sales jargon

Execute the workflow step by step, using tools as needed."""

        user_prompt = f"""Execute the sales workflow for this lead:

Company: {lead_info['company']}
Industry: {lead_info.get('industry', 'Unknown')}
Contact: {lead_info['contact_name']} ({lead_info['contact_title']})
Email: {lead_info['contact_email']}
Website: {lead_info.get('website', 'Unknown')}

Begin the workflow now. Use tools to complete each step."""

        # Track the conversation
        messages = [{"role": "user", "content": user_prompt}]
        workflow_log = []
        max_turns = 15
        turn = 0
        
        while turn < max_turns:
            turn += 1
            print(f"\n--- Turn {turn} ---")
            
            # Make API call with tools
            response = client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=system_prompt,
                tools=self.mcp_tools,
                messages=messages
            )
            
            # Log the response
            workflow_log.append({
                "turn": turn,
                "stop_reason": response.stop_reason,
                "content": response.content
            })
            
            # Check stop reason
            if response.stop_reason == "end_turn":
                # Extract final response
                final_text = self._extract_text(response.content)
                print(f"\n✅ Workflow Complete!\n")
                print(final_text)
                break
            
            # Process tool uses
            if response.stop_reason == "tool_use":
                tool_results = []
                
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"\n🔧 Using tool: {block.name}")
                        print(f"   Input: {json.dumps(block.input, indent=2)}")
                        
                        # Execute the tool
                        result = await self._execute_tool(block.name, block.input)
                        
                        print(f"   Result: {result[:200]}...")
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result
                        })
                
                # Add assistant message and tool results
                messages.append({"role": "assistant", "content": response.content})
                messages.append({"role": "user", "content": tool_results})
            
            # Safety check
            if turn >= max_turns:
                print("\n⚠️ Max turns reached")
                break
        
        return {
            "company": lead_info["company"],
            "workflow_log": workflow_log,
            "completed_at": datetime.now().isoformat()
        }
    
    async def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute MCP tool (simulated for demo)
        In production, this would call actual MCP servers
        """
        
        if tool_name == "crm_create_lead":
            lead_id = f"lead_{hash(tool_input['company']) % 10000:04d}"
            return json.dumps({
                "success": True,
                "lead_id": lead_id,
                "message": f"Lead created for {tool_input['company']}"
            })
        
        elif tool_name == "crm_update_lead":
            return json.dumps({
                "success": True,
                "lead_id": tool_input["lead_id"],
                "updated_fields": list(tool_input.keys())
            })
        
        elif tool_name == "email_send":
            email_id = f"email_{hash(tool_input['to']) % 10000:04d}"
            return json.dumps({
                "success": True,
                "email_id": email_id,
                "message": f"Email sent to {tool_input['to']}",
                "subject": tool_input["subject"]
            })
        
        elif tool_name == "email_schedule":
            scheduled_id = f"sched_{hash(tool_input['to']) % 10000:04d}"
            return json.dumps({
                "success": True,
                "scheduled_id": scheduled_id,
                "send_at": tool_input["send_at"],
                "message": f"Email scheduled for {tool_input['send_at']}"
            })
        
        return json.dumps({"success": False, "error": "Unknown tool"})
    
    def _extract_text(self, content: List) -> str:
        """Extract text from response content"""
        text_parts = []
        for block in content:
            if hasattr(block, 'text'):
                text_parts.append(block.text)
        return "\n".join(text_parts)


async def demo_integrated_workflow():
    """
    Demonstration of the integrated agentic sales workflow
    """
    
    # Sample leads
    leads = [
        {
            "company": "DataFlow Technologies",
            "industry": "Data Analytics SaaS",
            "contact_name": "Jennifer Martinez",
            "contact_title": "VP of Engineering",
            "contact_email": "j.martinez@dataflow.example.com",
            "website": "dataflow.example.com"
        },
        {
            "company": "CloudScale Systems",
            "industry": "Cloud Infrastructure",
            "contact_name": "David Park",
            "contact_title": "CTO",
            "contact_email": "dpark@cloudscale.example.com",
            "website": "cloudscale.example.com"
        }
    ]
    
    agent = IntegratedSalesAgent()
    
    print("\n" + "="*70)
    print("🤖 AI B2B SALES AGENT - AGENTIC WORKFLOW DEMO")
    print("="*70)
    print("\nThis agent will autonomously:")
    print("  1. Research companies using web search")
    print("  2. Create and update CRM records")
    print("  3. Qualify leads using BANT criteria")
    print("  4. Generate personalized outreach")
    print("  5. Send and schedule emails")
    print("\n" + "="*70)
    
    results = []
    
    for i, lead in enumerate(leads, 1):
        print(f"\n\n{'#'*70}")
        print(f"# LEAD {i}/{len(leads)}: {lead['company']}")
        print(f"{'#'*70}")
        
        try:
            result = await agent.execute_sales_workflow(lead)
            results.append(result)
            
            # Brief pause between leads
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"\n❌ Error processing {lead['company']}: {str(e)}")
            continue
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("📊 WORKFLOW SUMMARY")
    print(f"{'='*70}")
    print(f"Total leads processed: {len(results)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Save results
    output_file = "integrated_sales_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo_integrated_workflow())
