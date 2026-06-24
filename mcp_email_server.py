"""
MCP Server for Email Operations
Provides tools for sending emails, managing templates, and tracking engagement
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

# Simulated email database
EMAIL_DATABASE = {
    "sent_emails": [],
    "templates": {},
    "engagement_tracking": {}
}


class EmailServer:
    """MCP Server for email operations"""
    
    def __init__(self):
        self.server = Server("email-server")
        self._setup_handlers()
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default email templates"""
        EMAIL_DATABASE["templates"]["cold_outreach"] = {
            "name": "Cold Outreach",
            "subject": "Quick question about {company_name}",
            "body": """Hi {contact_name},

I noticed {personalization_hook} and thought you might be interested in {value_proposition}.

{specific_benefit}

Would you be open to a quick 15-minute call this week to discuss?

Best regards,
{sender_name}"""
        }
        
        EMAIL_DATABASE["templates"]["follow_up"] = {
            "name": "Follow Up",
            "subject": "Re: {original_subject}",
            "body": """Hi {contact_name},

I wanted to follow up on my previous email about {topic}.

{additional_context}

Let me know if you'd like to schedule a brief call.

Best,
{sender_name}"""
        }
    
    def _setup_handlers(self):
        """Setup MCP tool handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available email tools"""
            return [
                types.Tool(
                    name="send_email",
                    description="Send a personalized email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "to": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"},
                            "cc": {"type": "string"},
                            "bcc": {"type": "string"},
                            "track_opens": {"type": "boolean"},
                            "track_clicks": {"type": "boolean"},
                            "lead_id": {"type": "string"}
                        },
                        "required": ["to", "subject", "body"]
                    }
                ),
                types.Tool(
                    name="send_from_template",
                    description="Send email using a template with variable substitution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {"type": "string"},
                            "to": {"type": "string"},
                            "variables": {"type": "object"},
                            "lead_id": {"type": "string"}
                        },
                        "required": ["template_name", "to", "variables"]
                    }
                ),
                types.Tool(
                    name="create_template",
                    description="Create a new email template",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "template_name": {"type": "string"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"},
                            "variables": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["template_name", "subject", "body"]
                    }
                ),
                types.Tool(
                    name="get_email_status",
                    description="Get the delivery and engagement status of an email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email_id": {"type": "string"}
                        },
                        "required": ["email_id"]
                    }
                ),
                types.Tool(
                    name="get_engagement_metrics",
                    description="Get engagement metrics for a lead's emails",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"}
                        },
                        "required": ["lead_id"]
                    }
                ),
                types.Tool(
                    name="schedule_email",
                    description="Schedule an email to be sent at a specific time",
                    inputSchema={
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
                ),
                types.Tool(
                    name="list_templates",
                    description="List all available email templates",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool execution"""
            
            if name == "send_email":
                return await self._send_email(arguments)
            elif name == "send_from_template":
                return await self._send_from_template(arguments)
            elif name == "create_template":
                return await self._create_template(arguments)
            elif name == "get_email_status":
                return await self._get_email_status(arguments)
            elif name == "get_engagement_metrics":
                return await self._get_engagement_metrics(arguments)
            elif name == "schedule_email":
                return await self._schedule_email(arguments)
            elif name == "list_templates":
                return await self._list_templates(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _send_email(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Send an email"""
        email_id = f"email_{len(EMAIL_DATABASE['sent_emails']) + 1:04d}"
        
        email_record = {
            "id": email_id,
            "to": args["to"],
            "subject": args["subject"],
            "body": args["body"],
            "cc": args.get("cc"),
            "bcc": args.get("bcc"),
            "sent_at": datetime.now().isoformat(),
            "status": "sent",
            "lead_id": args.get("lead_id"),
            "track_opens": args.get("track_opens", True),
            "track_clicks": args.get("track_clicks", True)
        }
        
        EMAIL_DATABASE["sent_emails"].append(email_record)
        
        # Initialize tracking
        if email_record["lead_id"]:
            lead_id = email_record["lead_id"]
            if lead_id not in EMAIL_DATABASE["engagement_tracking"]:
                EMAIL_DATABASE["engagement_tracking"][lead_id] = {
                    "emails_sent": 0,
                    "opens": 0,
                    "clicks": 0,
                    "replies": 0
                }
            EMAIL_DATABASE["engagement_tracking"][lead_id]["emails_sent"] += 1
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "email_id": email_id,
                "message": f"Email sent to {args['to']}"
            }, indent=2)
        )]
    
    async def _send_from_template(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Send email from template"""
        template_name = args["template_name"]
        
        if template_name not in EMAIL_DATABASE["templates"]:
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": f"Template '{template_name}' not found"
                })
            )]
        
        template = EMAIL_DATABASE["templates"][template_name]
        variables = args["variables"]
        
        # Substitute variables
        subject = template["subject"].format(**variables)
        body = template["body"].format(**variables)
        
        # Send the email
        email_args = {
            "to": args["to"],
            "subject": subject,
            "body": body,
            "lead_id": args.get("lead_id")
        }
        
        return await self._send_email(email_args)
    
    async def _create_template(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Create email template"""
        template_name = args["template_name"]
        
        EMAIL_DATABASE["templates"][template_name] = {
            "name": template_name,
            "subject": args["subject"],
            "body": args["body"],
            "variables": args.get("variables", []),
            "created_at": datetime.now().isoformat()
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "template_name": template_name,
                "message": "Template created successfully"
            }, indent=2)
        )]
    
    async def _get_email_status(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Get email status"""
        email_id = args["email_id"]
        
        email = next(
            (e for e in EMAIL_DATABASE["sent_emails"] if e["id"] == email_id),
            None
        )
        
        if not email:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Email not found"})
            )]
        
        # Simulate engagement tracking
        status = {
            "email_id": email_id,
            "status": email["status"],
            "sent_at": email["sent_at"],
            "delivered": True,
            "opened": False,  # Would be tracked via pixel
            "clicked": False,  # Would be tracked via link tracking
            "replied": False
        }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(status, indent=2)
        )]
    
    async def _get_engagement_metrics(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Get engagement metrics for a lead"""
        lead_id = args["lead_id"]
        
        metrics = EMAIL_DATABASE["engagement_tracking"].get(lead_id, {
            "emails_sent": 0,
            "opens": 0,
            "clicks": 0,
            "replies": 0
        })
        
        metrics["open_rate"] = (
            metrics["opens"] / metrics["emails_sent"] * 100
            if metrics["emails_sent"] > 0 else 0
        )
        metrics["click_rate"] = (
            metrics["clicks"] / metrics["emails_sent"] * 100
            if metrics["emails_sent"] > 0 else 0
        )
        metrics["reply_rate"] = (
            metrics["replies"] / metrics["emails_sent"] * 100
            if metrics["emails_sent"] > 0 else 0
        )
        
        return [types.TextContent(
            type="text",
            text=json.dumps(metrics, indent=2)
        )]
    
    async def _schedule_email(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Schedule an email"""
        scheduled_id = f"scheduled_{len(EMAIL_DATABASE['sent_emails']) + 1:04d}"
        
        scheduled_email = {
            "id": scheduled_id,
            "to": args["to"],
            "subject": args["subject"],
            "body": args["body"],
            "send_at": args["send_at"],
            "status": "scheduled",
            "lead_id": args.get("lead_id"),
            "created_at": datetime.now().isoformat()
        }
        
        EMAIL_DATABASE["sent_emails"].append(scheduled_email)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "scheduled_id": scheduled_id,
                "send_at": args["send_at"]
            }, indent=2)
        )]
    
    async def _list_templates(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """List all templates"""
        templates = [
            {
                "name": name,
                "subject": template["subject"],
                "variables": template.get("variables", [])
            }
            for name, template in EMAIL_DATABASE["templates"].items()
        ]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(templates),
                "templates": templates
            }, indent=2)
        )]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="email-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Entry point for the Email MCP server"""
    server = EmailServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
