# AI B2B Sales Automation - Deployment Guide

## Architecture Overview

This system implements an autonomous AI agent for B2B sales using:
- **Claude Sonnet 4.5**: Core reasoning and decision-making
- **Anthropic Agents SDK**: Agentic workflow orchestration
- **MCP (Model Context Protocol)**: Tool integration for CRM, email, and data enrichment

## System Components

### 1. Main Orchestrator (`sales_agent_main.py`)
- Coordinates the entire sales workflow
- Manages multi-stage pipeline: Research → Qualification → Outreach → CRM Update
- Handles error recovery and retry logic

### 2. MCP Servers
- **CRM Server** (`mcp_crm_server.py`): Lead management, opportunity tracking
- **Email Server** (`mcp_email_server.py`): Email sending, template management, engagement tracking
- **Data Enrichment** (optional): Company data, contact discovery

### 3. Integrated Agent (`integrated_agent.py`)
- Demonstrates full agentic behavior
- Claude autonomously decides which tools to use and when
- Implements feedback loops and adaptive reasoning

## Installation

### Prerequisites
```bash
# Python 3.11+
python --version

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
Create a `.env` file:
```bash
# Anthropic
ANTHROPIC_API_KEY=your_api_key_here

# CRM Integration (Salesforce example)
CRM_API_KEY=your_salesforce_key
CRM_INSTANCE_URL=https://your-instance.salesforce.com

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Data Enrichment (optional)
CLEARBIT_API_KEY=your_clearbit_key
ZOOMINFO_API_KEY=your_zoominfo_key
```

## Running the System

### Option 1: Basic Workflow
```bash
python sales_agent_main.py
```
This runs the structured pipeline with predefined stages.

### Option 2: Agentic Workflow (Recommended)
```bash
python integrated_agent.py
```
This allows Claude to autonomously decide tool usage and workflow steps.

### Option 3: Start MCP Servers Independently
```bash
# Terminal 1: CRM Server
python mcp_crm_server.py

# Terminal 2: Email Server
python mcp_email_server.py

# Terminal 3: Main Agent
python integrated_agent.py
```

## Configuration

### MCP Server Configuration
The `claude_desktop_config.json` file defines available MCP servers:

```json
{
  "mcpServers": {
    "crm-server": {
      "command": "python",
      "args": ["mcp_crm_server.py"]
    },
    "email-server": {
      "command": "python",
      "args": ["mcp_email_server.py"]
    }
  }
}
```

### Customizing the Agent

#### Modify System Prompt
Edit the system prompt in `integrated_agent.py`:
```python
system_prompt = """Your custom instructions here..."""
```

#### Adjust Qualification Criteria
Update BANT scoring thresholds:
```python
# In qualify_lead method
qualification_threshold = 60  # Score needed for qualified status
```

#### Add Custom Tools
Extend MCP servers with new capabilities:
```python
@self.server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    return [
        # ... existing tools
        types.Tool(
            name="your_custom_tool",
            description="What it does",
            inputSchema={...}
        )
    ]
```

## Workflow Details

### Stage 1: Lead Research
- Uses web search to gather company intelligence
- Extracts: size, revenue, decision makers, tech stack, pain points
- Identifies buying signals and competitive landscape

### Stage 2: Lead Qualification (BANT)
- **Budget** (0-25): Financial capacity assessment
- **Authority** (0-25): Access to decision makers
- **Need** (0-25): Problem-solution fit
- **Timeline** (0-25): Buying urgency
- **Threshold**: Score ≥ 60 = Qualified

### Stage 3: Personalized Outreach
- Generates custom email with specific company references
- Creates LinkedIn message (300 char max)
- Schedules follow-up email (+3 days)
- Includes talking points for sales team

### Stage 4: CRM Update
- Records all research and qualification data
- Sets next actions and reminders
- Updates lead status and score

## Production Considerations

### 1. Rate Limiting
```python
# Implement rate limiting for API calls
from anthropic import RateLimitError
import time

try:
    response = client.messages.create(...)
except RateLimitError:
    time.sleep(60)  # Wait before retry
```

### 2. Error Handling
```python
# Robust error handling
try:
    result = await workflow_step()
except Exception as e:
    logger.error(f"Step failed: {e}")
    # Implement retry logic or fallback
```

### 3. Monitoring & Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("lead_qualified", 
    lead_id=lead_id, 
    score=qualification_score,
    company=company_name
)
```

### 4. Database Integration
Replace in-memory storage with persistent database:
```python
import asyncpg

async def save_lead(lead_data):
    conn = await asyncpg.connect('postgresql://...')
    await conn.execute(
        "INSERT INTO leads (...) VALUES (...)",
        *lead_data.values()
    )
```

### 5. Queue-Based Processing
For high-volume lead processing:
```python
import asyncio
from asyncio import Queue

async def lead_processor(queue: Queue):
    while True:
        lead = await queue.get()
        await process_lead(lead)
        queue.task_done()
```

## Security Best Practices

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files (add to `.gitignore`)
3. **Input Validation**: Validate all lead data before processing
4. **Rate Limiting**: Implement exponential backoff for API calls
5. **Access Control**: Restrict MCP server access to authorized agents only

## Monitoring & Analytics

### Key Metrics to Track
- Lead processing rate (leads/hour)
- Qualification rate (% of leads qualified)
- Email open/click rates
- Response rate to outreach
- Time to first response
- Conversion rate (lead → opportunity)

### Example Logging
```python
metrics = {
    "leads_processed": len(results),
    "qualified": sum(r["qualified"] for r in results),
    "emails_sent": len(email_log),
    "avg_qualification_score": avg_score
}

logger.info("daily_metrics", **metrics)
```

## Troubleshooting

### Issue: MCP Server Not Responding
**Solution**: Check if server process is running
```bash
ps aux | grep mcp_crm_server
```

### Issue: Rate Limit Errors
**Solution**: Implement exponential backoff
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
async def api_call_with_retry():
    return await client.messages.create(...)
```

### Issue: Tool Calls Failing
**Solution**: Validate tool schemas match MCP server definitions
```python
# Ensure input_schema matches server expectations
assert tool_input_schema == server_tool_schema
```

## Scaling Strategies

### Horizontal Scaling
- Deploy multiple agent instances
- Use message queue (RabbitMQ, Redis) for load distribution
- Implement leader election for coordination

### Vertical Scaling
- Increase concurrent lead processing
- Batch API calls where possible
- Optimize tool response times

### Async Processing
```python
async def process_leads_concurrent(leads: List[Dict]):
    tasks = [process_lead(lead) for lead in leads]
    return await asyncio.gather(*tasks)
```

## Next Steps

1. **Connect Real CRM**: Replace simulated CRM with Salesforce/HubSpot API
2. **Email Integration**: Connect SMTP or SendGrid for actual email sending
3. **Data Enrichment**: Add Clearbit, ZoomInfo for company data
4. **A/B Testing**: Test different outreach templates
5. **ML Scoring**: Train models on historical conversion data
6. **Multi-Channel**: Add LinkedIn, phone, direct mail channels

## Support & Resources

- Anthropic Documentation: https://docs.anthropic.com
- MCP Specification: https://spec.modelcontextprotocol.io
- Claude API Reference: https://docs.anthropic.com/api
- Example MCP Servers: https://github.com/anthropics/mcp-servers

## License

This is example code for demonstration purposes. Adapt for your production needs with appropriate security, monitoring, and error handling.
