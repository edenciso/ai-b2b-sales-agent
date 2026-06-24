"""
Quick Start Example - Minimal B2B Sales Agent
Get started in 5 minutes with this simplified version
"""

import asyncio
from anthropic import Anthropic
import os

# Initialize Claude
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


async def process_lead_simple(company_name: str, contact_email: str):
    """
    Simplified lead processing with Claude + web search
    """
    
    prompt = f"""You are a B2B sales research and outreach specialist.

TASK: Research and create outreach for this lead:
- Company: {company_name}
- Contact: {contact_email}

STEPS:
1. Search the web for information about {company_name}
2. Identify their key challenges and needs
3. Create a personalized 100-word cold email
4. Provide a qualification score (0-100)

FORMAT YOUR RESPONSE AS:
---RESEARCH---
[Your research findings]

---QUALIFICATION---
Score: [0-100]
Reasoning: [Why this score?]

---EMAIL---
Subject: [Email subject]

[Email body - max 100 words]
"""

    # Call Claude with web search enabled
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        tools=[
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ],
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Extract response
    result = ""
    for block in response.content:
        if hasattr(block, 'text'):
            result += block.text
    
    return result


async def main():
    """
    Quick demo with sample leads
    """
    
    print("🚀 Quick Start: AI B2B Sales Agent\n")
    print("="*60)
    
    # Sample leads
    leads = [
        ("Stripe", "sales@stripe.com"),
        ("Snowflake", "sales@snowflake.com"),
        ("Databricks", "contact@databricks.com")
    ]
    
    for company, email in leads:
        print(f"\n📊 Processing: {company}")
        print("-"*60)
        
        try:
            result = await process_lead_simple(company, email)
            print(result)
            
            print("\n✅ Done!")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
        await asyncio.sleep(2)  # Rate limiting


if __name__ == "__main__":
    # Quick setup check
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Please set ANTHROPIC_API_KEY environment variable")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        exit(1)
    
    print("""
╔══════════════════════════════════════════════════════════╗
║         AI B2B Sales Agent - Quick Start                 ║
║                                                          ║
║  This demo shows Claude autonomously:                    ║
║  • Researching companies via web search                  ║
║  • Qualifying leads based on research                    ║
║  • Creating personalized outreach emails                 ║
║                                                          ║
║  For full MCP integration, see sales_agent_main.py      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
