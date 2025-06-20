#!/usr/bin/env python3
"""
Wildfire Pet Rescue Agent using Amazon Bedrock

This agent uses Amazon Bedrock to process wildfire rescue pet data
and automatically adds rescued pets to the petstore using the MCP client.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import boto3
from botocore.exceptions import ClientError

from agent_interface import PetstoreAgent
from client_config import ClientConfig
from prompt_manager import PromptManager
from sampling import SamplingManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wildfire-rescue-agent")


class WildfireRescueAgent:
    """AI Agent for processing wildfire rescued pets using Amazon Bedrock"""
    
    def __init__(self, region_name: str = "us-east-1"):
        """Initialize the Wildfire Rescue Agent
        
        Args:
            region_name: AWS region for Bedrock service
        """
        self.region_name = region_name
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=region_name)
        
        # Initialize MCP client components
        self.petstore_agent = PetstoreAgent(ClientConfig.default())
        self.prompt_manager = PromptManager()
        self.sampling_manager = SamplingManager()
        
        # Add custom prompts for wildfire rescue scenarios
        self._setup_rescue_prompts()
        
        # Rescue operation metadata
        self.rescue_operation_id = f"wildfire_rescue_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
    def _setup_rescue_prompts(self):
        """Setup custom prompts for wildfire rescue operations"""
        from prompt_manager import PromptTemplate
        
        # Pet assessment prompt
        pet_assessment_prompt = PromptTemplate(
            system="""You are a veterinary AI assistant specializing in wildfire rescue operations. 
            Your role is to assess rescued pets and determine their condition, needs, and readiness for adoption.
            
            Consider factors like:
            - Physical condition and injuries
            - Stress levels and behavioral changes
            - Medical needs and treatment requirements
            - Estimated recovery time
            - Adoption readiness status""",
            
            user_template="""Assess the following rescued pet from wildfire incident:
            
            Pet Information:
            - Name: {name}
            - Species: {species}
            - Breed: {breed}
            - Age: {age}
            - Rescue Location: {rescue_location}
            - Rescue Date: {rescue_date}
            - Initial Condition: {condition}
            - Notes: {notes}
            
            Provide assessment including:
            1. Current status (available/pending/medical_care)
            2. Recommended tags for the pet
            3. Special care instructions
            4. Photo description for documentation""",
            
            examples={
                "dog_rescue": "Assess a rescued Golden Retriever with minor smoke inhalation",
                "cat_rescue": "Assess a rescued domestic cat with stress-related behavior"
            }
        )
        
        # Batch processing prompt
        batch_processing_prompt = PromptTemplate(
            system="""You are a rescue coordination AI assistant. Process multiple rescued pets efficiently
            and prepare them for entry into the pet adoption system.
            
            Ensure each pet has:
            - Proper categorization
            - Appropriate status assignment
            - Relevant rescue tags
            - Complete documentation""",
            
            user_template="""Process the following batch of {count} rescued pets from wildfire incident {incident_id}:
            
            Rescue Details:
            - Incident: {incident_name}
            - Location: {location}
            - Date: {date}
            - Rescue Team: {team}
            
            Pets to process:
            {pets_data}
            
            For each pet, provide:
            1. Standardized name format
            2. Category assignment
            3. Status determination
            4. Rescue tags
            5. Priority level""",
            
            examples={
                "small_batch": "Process 3-5 rescued pets",
                "large_batch": "Process 10+ rescued pets"
            }
        )
        
        # Add to prompt manager
        self.prompt_manager.add_template("pet_assessment", pet_assessment_prompt)
        self.prompt_manager.add_template("batch_processing", batch_processing_prompt)
    
    async def invoke_bedrock_model(self, prompt: str, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0") -> str:
        """Invoke Amazon Bedrock model for AI processing
        
        Args:
            prompt: The prompt to send to the model
            model_id: Bedrock model identifier
            
        Returns:
            Model response text
        """
        try:
            # Get sampling configuration
            sampling_config = self.sampling_manager.get_config_dict("balanced")
            
            # Prepare request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": sampling_config["max_tokens"],
                "temperature": sampling_config["temperature"],
                "top_p": sampling_config["top_p"],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error invoking Bedrock model: {e}")
            raise
    
    async def assess_rescued_pet(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to assess a rescued pet's condition and needs
        
        Args:
            pet_data: Raw pet rescue data
            
        Returns:
            AI assessment with recommendations
        """
        logger.info(f"Assessing rescued pet: {pet_data.get('name', 'Unknown')}")
        
        # Generate assessment prompt
        prompt_data = self.prompt_manager.get_prompt("pet_assessment", **pet_data)
        full_prompt = f"{prompt_data['system']}\n\n{prompt_data['user']}"
        
        # Get AI assessment
        assessment_text = await self.invoke_bedrock_model(full_prompt)
        
        # Parse assessment (simplified - in production, use structured output)
        assessment = {
            "pet_id": pet_data.get("rescue_id"),
            "name": pet_data.get("name"),
            "ai_assessment": assessment_text,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "rescue_operation": self.rescue_operation_id
        }
        
        return assessment
    
    async def process_rescue_batch(self, rescue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a batch of rescued pets using AI
        
        Args:
            rescue_data: Batch rescue operation data
            
        Returns:
            Processing results and recommendations
        """
        logger.info(f"Processing rescue batch: {rescue_data.get('incident_name')}")
        
        # Generate batch processing prompt
        prompt_data = self.prompt_manager.get_prompt("batch_processing", **rescue_data)
        full_prompt = f"{prompt_data['system']}\n\n{prompt_data['user']}"
        
        # Get AI processing recommendations
        processing_text = await self.invoke_bedrock_model(full_prompt)
        
        return {
            "batch_id": rescue_data.get("incident_id"),
            "processing_recommendations": processing_text,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "pet_count": rescue_data.get("count", 0)
        }
    
    def _extract_pet_details_from_ai_response(self, ai_response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured pet details from AI response
        
        This is a simplified implementation. In production, you'd use
        structured output or more sophisticated parsing.
        """
        # Default pet structure
        pet_details = {
            "name": original_data.get("name", "Rescued Pet"),
            "photoUrls": [
                f"https://rescue-photos.example.com/{self.rescue_operation_id}/{original_data.get('rescue_id', 'unknown')}.jpg"
            ],
            "status": "pending",  # Default for rescued pets
            "category": {
                "id": 1,
                "name": original_data.get("species", "Unknown").title()
            },
            "tags": [
                {"id": 1, "name": "wildfire_rescue"},
                {"id": 2, "name": self.rescue_operation_id},
                {"id": 3, "name": "needs_assessment"}
            ]
        }
        
        # Parse AI response for status and additional tags
        ai_lower = ai_response.lower()
        
        # Determine status from AI assessment
        if "medical care" in ai_lower or "treatment" in ai_lower:
            pet_details["status"] = "pending"
            pet_details["tags"].append({"id": 4, "name": "medical_care_needed"})
        elif "ready for adoption" in ai_lower or "available" in ai_lower:
            pet_details["status"] = "available"
            pet_details["tags"].append({"id": 4, "name": "adoption_ready"})
        
        # Add condition-based tags
        if "injured" in ai_lower:
            pet_details["tags"].append({"id": 5, "name": "injured"})
        if "stressed" in ai_lower or "trauma" in ai_lower:
            pet_details["tags"].append({"id": 6, "name": "trauma_care"})
        if "friendly" in ai_lower:
            pet_details["tags"].append({"id": 7, "name": "friendly"})
        
        return pet_details
    
    async def add_rescued_pet_to_store(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a rescued pet to the petstore using MCP client
        
        Args:
            pet_data: Rescued pet data
            
        Returns:
            Result of adding pet to store
        """
        try:
            # First, get AI assessment
            assessment = await self.assess_rescued_pet(pet_data)
            
            # Extract structured pet details from AI response
            pet_details = self._extract_pet_details_from_ai_response(
                assessment["ai_assessment"], 
                pet_data
            )
            
            # Add pet using MCP client
            result = await self.petstore_agent.execute_task(
                "manage_pet",
                action="add",
                **pet_details
            )
            
            logger.info(f"Successfully added rescued pet: {pet_details['name']}")
            
            return {
                "success": True,
                "pet_details": pet_details,
                "ai_assessment": assessment,
                "mcp_result": result,
                "rescue_operation": self.rescue_operation_id
            }
            
        except Exception as e:
            logger.error(f"Error adding rescued pet: {e}")
            return {
                "success": False,
                "error": str(e),
                "pet_data": pet_data
            }
    
    async def process_wildfire_rescue_operation(self, rescue_operation: Dict[str, Any]) -> Dict[str, Any]:
        """Process a complete wildfire rescue operation
        
        Args:
            rescue_operation: Complete rescue operation data
            
        Returns:
            Operation results and summary
        """
        logger.info(f"Starting wildfire rescue operation: {rescue_operation.get('incident_name')}")
        
        results = {
            "operation_id": self.rescue_operation_id,
            "incident_name": rescue_operation.get("incident_name"),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "pets_processed": [],
            "successful_additions": 0,
            "failed_additions": 0,
            "ai_batch_analysis": None
        }
        
        try:
            # First, get AI batch analysis
            batch_analysis = await self.process_rescue_batch(rescue_operation)
            results["ai_batch_analysis"] = batch_analysis
            
            # Process each rescued pet
            pets = rescue_operation.get("rescued_pets", [])
            
            for pet_data in pets:
                logger.info(f"Processing pet: {pet_data.get('name', 'Unknown')}")
                
                # Add pet to store with AI assessment
                pet_result = await self.add_rescued_pet_to_store(pet_data)
                results["pets_processed"].append(pet_result)
                
                if pet_result["success"]:
                    results["successful_additions"] += 1
                else:
                    results["failed_additions"] += 1
                
                # Small delay to avoid overwhelming the API
                await asyncio.sleep(0.5)
            
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
            results["total_pets"] = len(pets)
            
            logger.info(f"Rescue operation completed: {results['successful_additions']}/{results['total_pets']} pets added successfully")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in rescue operation: {e}")
            results["error"] = str(e)
            results["completed_at"] = datetime.now(timezone.utc).isoformat()
            return results
    
    async def generate_rescue_report(self, operation_results: Dict[str, Any]) -> str:
        """Generate a comprehensive rescue operation report using AI
        
        Args:
            operation_results: Results from rescue operation
            
        Returns:
            Formatted rescue report
        """
        report_prompt = f"""Generate a comprehensive wildfire pet rescue operation report based on the following data:

Operation Details:
- Operation ID: {operation_results.get('operation_id')}
- Incident: {operation_results.get('incident_name')}
- Duration: {operation_results.get('started_at')} to {operation_results.get('completed_at')}
- Total Pets: {operation_results.get('total_pets', 0)}
- Successfully Added: {operation_results.get('successful_additions', 0)}
- Failed Additions: {operation_results.get('failed_additions', 0)}

AI Batch Analysis:
{json.dumps(operation_results.get('ai_batch_analysis', {}), indent=2)}

Individual Pet Results:
{json.dumps(operation_results.get('pets_processed', []), indent=2)}

Please provide:
1. Executive Summary
2. Operation Statistics
3. Pet Status Breakdown
4. Recommendations for Follow-up Care
5. Lessons Learned
6. Next Steps

Format as a professional rescue operation report."""
        
        report_text = await self.invoke_bedrock_model(report_prompt)
        return report_text


# Sample rescue operation data
SAMPLE_WILDFIRE_RESCUE_DATA = {
    "incident_id": "CA_WILDFIRE_2024_001",
    "incident_name": "Northern California Wildfire Rescue",
    "location": "Sonoma County, CA",
    "date": "2024-06-20",
    "team": "Emergency Animal Rescue Team Alpha",
    "count": 5,
    "pets_data": "5 rescued animals including dogs and cats",
    "rescued_pets": [
        {
            "rescue_id": "WF001",
            "name": "Smokey",
            "species": "dog",
            "breed": "Golden Retriever",
            "age": "3 years",
            "rescue_location": "Evacuated home on Pine Street",
            "rescue_date": "2024-06-20",
            "condition": "Minor smoke inhalation, otherwise healthy",
            "notes": "Very friendly, responds well to commands, slightly stressed but eating normally"
        },
        {
            "rescue_id": "WF002", 
            "name": "Ash",
            "species": "cat",
            "breed": "Domestic Shorthair",
            "age": "2 years",
            "rescue_location": "Found hiding under porch",
            "rescue_date": "2024-06-20",
            "condition": "Dehydrated, minor burns on paws",
            "notes": "Scared but not aggressive, needs medical attention for paw burns"
        },
        {
            "rescue_id": "WF003",
            "name": "Blaze",
            "species": "dog",
            "breed": "Border Collie Mix",
            "age": "5 years",
            "rescue_location": "Abandoned at evacuation center",
            "rescue_date": "2024-06-20",
            "condition": "Good physical condition, separation anxiety",
            "notes": "High energy, needs mental stimulation, good with other dogs"
        },
        {
            "rescue_id": "WF004",
            "name": "Ember",
            "species": "cat",
            "breed": "Maine Coon",
            "age": "4 years",
            "rescue_location": "Rescued from tree near fire line",
            "rescue_date": "2024-06-20",
            "condition": "Exhausted, minor respiratory irritation",
            "notes": "Large cat, very gentle, needs quiet environment for recovery"
        },
        {
            "rescue_id": "WF005",
            "name": "Phoenix",
            "species": "dog",
            "breed": "German Shepherd",
            "age": "6 years",
            "rescue_location": "Found protecting property",
            "rescue_date": "2024-06-20",
            "condition": "Minor cuts, protective behavior",
            "notes": "Loyal and protective, needs experienced handler, good health overall"
        }
    ]
}


async def main():
    """Main function to demonstrate the Wildfire Rescue Agent"""
    
    print("=== Wildfire Pet Rescue Agent Demo ===\n")
    
    try:
        # Initialize the rescue agent
        agent = WildfireRescueAgent(region_name="us-east-1")
        
        print("🔥 Starting wildfire rescue operation...")
        print(f"Operation ID: {agent.rescue_operation_id}")
        print(f"Incident: {SAMPLE_WILDFIRE_RESCUE_DATA['incident_name']}\n")
        
        # Process the rescue operation
        results = await agent.process_wildfire_rescue_operation(SAMPLE_WILDFIRE_RESCUE_DATA)
        
        # Display results
        print("📊 Operation Results:")
        print(f"- Total Pets: {results.get('total_pets', 0)}")
        print(f"- Successfully Added: {results.get('successful_additions', 0)}")
        print(f"- Failed Additions: {results.get('failed_additions', 0)}")
        print(f"- Success Rate: {(results.get('successful_additions', 0) / max(results.get('total_pets', 1), 1)) * 100:.1f}%\n")
        
        # Generate and display report
        print("📋 Generating comprehensive rescue report...\n")
        report = await agent.generate_rescue_report(results)
        
        print("=== RESCUE OPERATION REPORT ===")
        print(report)
        
        # Save results to file
        with open(f"rescue_operation_{agent.rescue_operation_id}.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: rescue_operation_{agent.rescue_operation_id}.json")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
