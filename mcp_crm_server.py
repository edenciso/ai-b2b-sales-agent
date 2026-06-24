"""
MCP Server for CRM Integration (Salesforce/HubSpot compatible)
Provides tools for lead management, contact updates, and opportunity tracking
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

# Simulated CRM database (in production, connect to real CRM API)
CRM_DATABASE = {
    "leads": {},
    "contacts": {},
    "opportunities": {},
    "activities": []
}


class CRMServer:
    """MCP Server for CRM operations"""
    
    def __init__(self):
        self.server = Server("crm-server")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP tool handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available CRM tools"""
            return [
                types.Tool(
                    name="create_lead",
                    description="Create a new lead in the CRM",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "contact_name": {"type": "string"},
                            "contact_email": {"type": "string"},
                            "contact_title": {"type": "string"},
                            "industry": {"type": "string"},
                            "phone": {"type": "string"},
                            "website": {"type": "string"},
                            "lead_source": {"type": "string"}
                        },
                        "required": ["company", "contact_email"]
                    }
                ),
                types.Tool(
                    name="update_lead",
                    description="Update an existing lead with new information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"},
                            "status": {"type": "string"},
                            "qualification_score": {"type": "number"},
                            "notes": {"type": "string"},
                            "next_action": {"type": "string"},
                            "custom_fields": {"type": "object"}
                        },
                        "required": ["lead_id"]
                    }
                ),
                types.Tool(
                    name="get_lead",
                    description="Retrieve lead information by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"}
                        },
                        "required": ["lead_id"]
                    }
                ),
                types.Tool(
                    name="search_leads",
                    description="Search leads by company name, email, or other criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "status": {"type": "string"},
                            "industry": {"type": "string"},
                            "min_score": {"type": "number"}
                        }
                    }
                ),
                types.Tool(
                    name="create_activity",
                    description="Log an activity (email, call, meeting) for a lead",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"},
                            "activity_type": {
                                "type": "string",
                                "enum": ["email", "call", "meeting", "note"]
                            },
                            "subject": {"type": "string"},
                            "description": {"type": "string"},
                            "scheduled_date": {"type": "string"}
                        },
                        "required": ["lead_id", "activity_type", "subject"]
                    }
                ),
                types.Tool(
                    name="convert_to_opportunity",
                    description="Convert a qualified lead to an opportunity",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"},
                            "opportunity_name": {"type": "string"},
                            "expected_revenue": {"type": "number"},
                            "close_date": {"type": "string"},
                            "probability": {"type": "number"}
                        },
                        "required": ["lead_id", "opportunity_name"]
                    }
                ),
                types.Tool(
                    name="get_lead_activities",
                    description="Get all activities for a specific lead",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lead_id": {"type": "string"},
                            "activity_type": {"type": "string"}
                        },
                        "required": ["lead_id"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: Dict[str, Any] | None
        ) -> List[types.TextContent]:
            """Handle tool execution"""
            
            if name == "create_lead":
                return await self._create_lead(arguments)
            elif name == "update_lead":
                return await self._update_lead(arguments)
            elif name == "get_lead":
                return await self._get_lead(arguments)
            elif name == "search_leads":
                return await self._search_leads(arguments)
            elif name == "create_activity":
                return await self._create_activity(arguments)
            elif name == "convert_to_opportunity":
                return await self._convert_to_opportunity(arguments)
            elif name == "get_lead_activities":
                return await self._get_lead_activities(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _create_lead(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Create a new lead"""
        lead_id = f"lead_{len(CRM_DATABASE['leads']) + 1:04d}"
        
        lead_data = {
            "id": lead_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "new",
            "qualification_score": 0,
            **args
        }
        
        CRM_DATABASE["leads"][lead_id] = lead_data
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "lead_id": lead_id,
                "message": f"Lead created successfully for {args.get('company')}"
            }, indent=2)
        )]
    
    async def _update_lead(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Update an existing lead"""
        lead_id = args.pop("lead_id")
        
        if lead_id not in CRM_DATABASE["leads"]:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Lead not found"})
            )]
        
        lead = CRM_DATABASE["leads"][lead_id]
        lead.update(args)
        lead["updated_at"] = datetime.now().isoformat()
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "lead_id": lead_id,
                "updated_fields": list(args.keys())
            }, indent=2)
        )]
    
    async def _get_lead(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Get lead by ID"""
        lead_id = args["lead_id"]
        lead = CRM_DATABASE["leads"].get(lead_id)
        
        if not lead:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Lead not found"})
            )]
        
        return [types.TextContent(
            type="text",
            text=json.dumps(lead, indent=2)
        )]
    
    async def _search_leads(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Search leads"""
        results = []
        query = args.get("query", "").lower()
        status = args.get("status")
        min_score = args.get("min_score", 0)
        
        for lead in CRM_DATABASE["leads"].values():
            # Apply filters
            if status and lead.get("status") != status:
                continue
            if lead.get("qualification_score", 0) < min_score:
                continue
            if query:
                searchable = f"{lead.get('company', '')} {lead.get('contact_email', '')}".lower()
                if query not in searchable:
                    continue
            
            results.append(lead)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "count": len(results),
                "leads": results
            }, indent=2)
        )]
    
    async def _create_activity(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Log an activity"""
        activity_id = f"activity_{len(CRM_DATABASE['activities']) + 1:04d}"
        
        activity = {
            "id": activity_id,
            "created_at": datetime.now().isoformat(),
            **args
        }
        
        CRM_DATABASE["activities"].append(activity)
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "activity_id": activity_id
            }, indent=2)
        )]
    
    async def _convert_to_opportunity(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Convert lead to opportunity"""
        lead_id = args["lead_id"]
        
        if lead_id not in CRM_DATABASE["leads"]:
            return [types.TextContent(
                type="text",
                text=json.dumps({"success": False, "error": "Lead not found"})
            )]
        
        opp_id = f"opp_{len(CRM_DATABASE['opportunities']) + 1:04d}"
        lead = CRM_DATABASE["leads"][lead_id]
        
        opportunity = {
            "id": opp_id,
            "lead_id": lead_id,
            "company": lead["company"],
            "created_at": datetime.now().isoformat(),
            "stage": "prospecting",
            **args
        }
        
        CRM_DATABASE["opportunities"][opp_id] = opportunity
        lead["status"] = "converted"
        lead["opportunity_id"] = opp_id
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "opportunity_id": opp_id,
                "message": "Lead converted to opportunity"
            }, indent=2)
        )]
    
    async def _get_lead_activities(
        self, 
        args: Dict[str, Any]
    ) -> List[types.TextContent]:
        """Get activities for a lead"""
        lead_id = args["lead_id"]
        activity_type = args.get("activity_type")
        
        activities = [
            a for a in CRM_DATABASE["activities"]
            if a["lead_id"] == lead_id and 
            (not activity_type or a["activity_type"] == activity_type)
        ]
        
        return [types.TextContent(
            type="text",
            text=json.dumps({
                "lead_id": lead_id,
                "count": len(activities),
                "activities": activities
            }, indent=2)
        )]
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="crm-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Entry point for the CRM MCP server"""
    server = CRMServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
