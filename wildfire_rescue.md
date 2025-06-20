# Wildfire Rescue Agent - Functional Flow Documentation

This document explains the complete functional flow of the Wildfire Pet Rescue Agent, including all data structures, API calls, and integration patterns with Amazon Bedrock and the MCP Petstore system.

## System Architecture Overview

```
Rescue Data → Wildfire Agent → Amazon Bedrock AI → Pet Assessment → MCP Client → Petstore API
     ↓              ↓                ↓                  ↓             ↓            ↓
Sample Data → AI Processing → Model Response → Structured Data → Tool Calls → Pet Records
```

## Core Components Flow

### 1. Agent Initialization Flow

#### WildfireRescueAgent Constructor
```python
agent = WildfireRescueAgent(region_name="us-east-1")
```

**Initialization Data:**
```json
{
  "region_name": "us-east-1",
  "bedrock_client": "boto3.client('bedrock-runtime')",
  "petstore_agent": "PetstoreAgent(ClientConfig.default())",
  "prompt_manager": "PromptManager()",
  "sampling_manager": "SamplingManager()",
  "rescue_operation_id": "wildfire_rescue_20240620_080000"
}
```

#### Custom Prompt Setup
```python
self._setup_rescue_prompts()
```

**Pet Assessment Prompt Template:**
```json
{
  "system": "You are a veterinary AI assistant specializing in wildfire rescue operations...",
  "user_template": "Assess the following rescued pet from wildfire incident:\n\nPet Information:\n- Name: {name}\n- Species: {species}\n- Breed: {breed}\n- Age: {age}\n- Rescue Location: {rescue_location}\n- Rescue Date: {rescue_date}\n- Initial Condition: {condition}\n- Notes: {notes}",
  "examples": {
    "dog_rescue": "Assess a rescued Golden Retriever with minor smoke inhalation",
    "cat_rescue": "Assess a rescued domestic cat with stress-related behavior"
  }
}
```

**Batch Processing Prompt Template:**
```json
{
  "system": "You are a rescue coordination AI assistant. Process multiple rescued pets efficiently...",
  "user_template": "Process the following batch of {count} rescued pets from wildfire incident {incident_id}:\n\nRescue Details:\n- Incident: {incident_name}\n- Location: {location}\n- Date: {date}\n- Rescue Team: {team}\n\nPets to process:\n{pets_data}",
  "examples": {
    "small_batch": "Process 3-5 rescued pets",
    "large_batch": "Process 10+ rescued pets"
  }
}
```

## Main Execution Flow

### 2. Process Wildfire Rescue Operation

#### Main Function Entry Point
```python
results = await agent.process_wildfire_rescue_operation(SAMPLE_WILDFIRE_RESCUE_DATA)
```

**Input Rescue Operation Data:**
```json
{
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
    }
  ]
}
```

#### Results Initialization
```json
{
  "operation_id": "wildfire_rescue_20240620_080000",
  "incident_name": "Northern California Wildfire Rescue",
  "started_at": "2024-06-20T08:00:00Z",
  "pets_processed": [],
  "successful_additions": 0,
  "failed_additions": 0,
  "ai_batch_analysis": null
}
```

### 3. AI Batch Analysis Flow

#### Process Rescue Batch
```python
batch_analysis = await self.process_rescue_batch(rescue_operation)
```

**Batch Processing Prompt Generation:**
```python
prompt_data = self.prompt_manager.get_prompt("batch_processing", **rescue_data)
full_prompt = f"{prompt_data['system']}\n\n{prompt_data['user']}"
```

**Generated Prompt Example:**
```text
You are a rescue coordination AI assistant. Process multiple rescued pets efficiently
and prepare them for entry into the pet adoption system.

Process the following batch of 5 rescued pets from wildfire incident CA_WILDFIRE_2024_001:

Rescue Details:
- Incident: Northern California Wildfire Rescue
- Location: Sonoma County, CA
- Date: 2024-06-20
- Rescue Team: Emergency Animal Rescue Team Alpha

Pets to process:
5 rescued animals including dogs and cats

For each pet, provide:
1. Standardized name format
2. Category assignment
3. Status determination
4. Rescue tags
5. Priority level
```

#### Bedrock Model Invocation
```python
processing_text = await self.invoke_bedrock_model(full_prompt)
```

**Bedrock API Request:**
```json
{
  "modelId": "anthropic.claude-3-sonnet-20240229-v1:0",
  "body": {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "temperature": 0.7,
    "top_p": 0.9,
    "messages": [
      {
        "role": "user",
        "content": "You are a rescue coordination AI assistant..."
      }
    ]
  },
  "contentType": "application/json"
}
```

**Batch Analysis Response:**
```json
{
  "batch_id": "CA_WILDFIRE_2024_001",
  "processing_recommendations": "Based on the rescue data, I recommend the following processing approach:\n\n1. Priority Assessment:\n   - High Priority: Pets with medical needs (Ash - paw burns)\n   - Medium Priority: Pets with behavioral concerns (Blaze - separation anxiety)\n   - Standard Priority: Healthy pets ready for assessment\n\n2. Category Assignments:\n   - Dogs: Smokey (Golden Retriever), Blaze (Border Collie Mix), Phoenix (German Shepherd)\n   - Cats: Ash (Domestic Shorthair), Ember (Maine Coon)\n\n3. Status Recommendations:\n   - Medical Care Needed: Ash, Ember\n   - Behavioral Assessment: Blaze, Phoenix\n   - Ready for Adoption: Smokey\n\n4. Rescue Tags:\n   - All pets: wildfire_rescue, trauma_care\n   - Medical needs: medical_care_needed\n   - Behavioral: needs_assessment",
  "processed_at": "2024-06-20T08:00:15Z",
  "pet_count": 5
}
```

### 4. Individual Pet Processing Flow

#### Pet Processing Loop
```python
for pet_data in pets:
    pet_result = await self.add_rescued_pet_to_store(pet_data)
```

#### Individual Pet Assessment
```python
assessment = await self.assess_rescued_pet(pet_data)
```

**Pet Assessment Prompt for Smokey:**
```text
You are a veterinary AI assistant specializing in wildfire rescue operations.

Assess the following rescued pet from wildfire incident:

Pet Information:
- Name: Smokey
- Species: dog
- Breed: Golden Retriever
- Age: 3 years
- Rescue Location: Evacuated home on Pine Street
- Rescue Date: 2024-06-20
- Initial Condition: Minor smoke inhalation, otherwise healthy
- Notes: Very friendly, responds well to commands, slightly stressed but eating normally

Provide assessment including:
1. Current status (available/pending/medical_care)
2. Recommended tags for the pet
3. Special care instructions
4. Photo description for documentation
```

**Bedrock Assessment Response:**
```text
Based on my assessment of Smokey, the rescued Golden Retriever:

1. Current Status: AVAILABLE
   - Minor smoke inhalation has resolved
   - Eating normally and responding well to commands
   - Stress levels are manageable and decreasing

2. Recommended Tags:
   - wildfire_rescue
   - friendly
   - well_trained
   - family_friendly
   - good_with_commands

3. Special Care Instructions:
   - Monitor for any delayed respiratory symptoms
   - Provide calm, structured environment for first few days
   - Regular exercise to help with stress management
   - Continue current feeding schedule

4. Photo Description:
   - Beautiful Golden Retriever with alert, friendly expression
   - Clean, well-groomed coat despite rescue circumstances
   - Bright eyes showing good health and responsiveness
   - Sitting position demonstrates good training and calm demeanor
```

#### Pet Details Extraction
```python
pet_details = self._extract_pet_details_from_ai_response(assessment["ai_assessment"], pet_data)
```

**Extracted Pet Details for Smokey:**
```json
{
  "name": "Smokey",
  "photoUrls": [
    "https://rescue-photos.example.com/wildfire_rescue_20240620_080000/WF001.jpg"
  ],
  "status": "available",
  "category": {
    "id": 1,
    "name": "Dog"
  },
  "tags": [
    {"id": 1, "name": "wildfire_rescue"},
    {"id": 2, "name": "wildfire_rescue_20240620_080000"},
    {"id": 3, "name": "needs_assessment"},
    {"id": 4, "name": "adoption_ready"},
    {"id": 7, "name": "friendly"}
  ]
}
```

### 5. MCP Client Integration Flow

#### Add Pet to Store via MCP
```python
result = await self.petstore_agent.execute_task(
    "manage_pet",
    action="add",
    **pet_details
)
```

**MCP Tool Call Data:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_pet",
    "arguments": {
      "pet": {
        "name": "Smokey",
        "photoUrls": ["https://rescue-photos.example.com/wildfire_rescue_20240620_080000/WF001.jpg"],
        "category": {
          "id": 1,
          "name": "Dog"
        },
        "tags": [
          {"id": 1, "name": "wildfire_rescue"},
          {"id": 2, "name": "wildfire_rescue_20240620_080000"},
          {"id": 3, "name": "needs_assessment"},
          {"id": 4, "name": "adoption_ready"},
          {"id": 7, "name": "friendly"}
        ],
        "status": "available"
      }
    }
  }
}
```

**Petstore API Call:**
```http
POST https://petstore3.swagger.io/api/v3/pet
Content-Type: application/json

{
  "name": "Smokey",
  "photoUrls": ["https://rescue-photos.example.com/wildfire_rescue_20240620_080000/WF001.jpg"],
  "category": {
    "id": 1,
    "name": "Dog"
  },
  "tags": [
    {"id": 1, "name": "wildfire_rescue"},
    {"id": 2, "name": "wildfire_rescue_20240620_080000"},
    {"id": 3, "name": "needs_assessment"},
    {"id": 4, "name": "adoption_ready"},
    {"id": 7, "name": "friendly"}
  ],
  "status": "available"
}
```

#### Pet Addition Result
```json
{
  "success": true,
  "pet_details": {
    "name": "Smokey",
    "photoUrls": ["https://rescue-photos.example.com/wildfire_rescue_20240620_080000/WF001.jpg"],
    "status": "available",
    "category": {"id": 1, "name": "Dog"},
    "tags": [
      {"id": 1, "name": "wildfire_rescue"},
      {"id": 2, "name": "wildfire_rescue_20240620_080000"},
      {"id": 3, "name": "needs_assessment"},
      {"id": 4, "name": "adoption_ready"},
      {"id": 7, "name": "friendly"}
    ]
  },
  "ai_assessment": {
    "pet_id": "WF001",
    "name": "Smokey",
    "ai_assessment": "Based on my assessment of Smokey, the rescued Golden Retriever...",
    "processed_at": "2024-06-20T08:00:30Z",
    "rescue_operation": "wildfire_rescue_20240620_080000"
  },
  "mcp_result": {
    "content": [
      {
        "type": "text",
        "text": "Pet added successfully with ID: 12345"
      }
    ],
    "isError": false
  },
  "rescue_operation": "wildfire_rescue_20240620_080000"
}
```

### 6. Complete Operation Results

#### Final Operation Results
```json
{
  "operation_id": "wildfire_rescue_20240620_080000",
  "incident_name": "Northern California Wildfire Rescue",
  "started_at": "2024-06-20T08:00:00Z",
  "completed_at": "2024-06-20T08:05:30Z",
  "total_pets": 5,
  "successful_additions": 5,
  "failed_additions": 0,
  "ai_batch_analysis": {
    "batch_id": "CA_WILDFIRE_2024_001",
    "processing_recommendations": "Based on the rescue data, I recommend...",
    "processed_at": "2024-06-20T08:00:15Z",
    "pet_count": 5
  },
  "pets_processed": [
    {
      "success": true,
      "pet_details": {...},
      "ai_assessment": {...},
      "mcp_result": {...},
      "rescue_operation": "wildfire_rescue_20240620_080000"
    }
  ]
}
```

## Report Generation Flow

### 7. AI-Generated Rescue Report

#### Report Generation Call
```python
report = await agent.generate_rescue_report(results)
```

**Report Generation Prompt:**
```text
Generate a comprehensive wildfire pet rescue operation report based on the following data:

Operation Details:
- Operation ID: wildfire_rescue_20240620_080000
- Incident: Northern California Wildfire Rescue
- Duration: 2024-06-20T08:00:00Z to 2024-06-20T08:05:30Z
- Total Pets: 5
- Successfully Added: 5
- Failed Additions: 0

AI Batch Analysis:
{
  "batch_id": "CA_WILDFIRE_2024_001",
  "processing_recommendations": "Based on the rescue data...",
  "processed_at": "2024-06-20T08:00:15Z",
  "pet_count": 5
}

Individual Pet Results:
[
  {
    "success": true,
    "pet_details": {...},
    "ai_assessment": {...}
  }
]

Please provide:
1. Executive Summary
2. Operation Statistics
3. Pet Status Breakdown
4. Recommendations for Follow-up Care
5. Lessons Learned
6. Next Steps

Format as a professional rescue operation report.
```

**Generated Report Example:**
```text
# WILDFIRE PET RESCUE OPERATION REPORT

## Executive Summary
Operation wildfire_rescue_20240620_080000 successfully processed 5 rescued animals from the Northern California Wildfire incident in Sonoma County. All 5 pets were successfully assessed using AI-powered veterinary analysis and added to the adoption system with appropriate care recommendations.

## Operation Statistics
- **Operation Duration**: 5 minutes 30 seconds
- **Success Rate**: 100% (5/5 pets processed)
- **AI Processing Time**: Average 15 seconds per pet
- **Total Processing Time**: 5 minutes 30 seconds

## Pet Status Breakdown
- **Available for Adoption**: 2 pets (Smokey, Blaze)
- **Pending Medical Care**: 2 pets (Ash, Ember)
- **Behavioral Assessment Needed**: 1 pet (Phoenix)

## Recommendations for Follow-up Care
1. **Immediate Medical Attention**: Ash requires paw burn treatment
2. **Behavioral Support**: Blaze needs separation anxiety management
3. **Monitoring**: All pets should be monitored for delayed stress symptoms
4. **Adoption Readiness**: Smokey is ready for immediate adoption placement

## Lessons Learned
- AI assessment significantly improved processing efficiency
- Structured data capture enabled better care coordination
- Integration with adoption system streamlined placement process

## Next Steps
1. Schedule veterinary follow-ups for pets requiring medical care
2. Implement behavioral assessment protocols
3. Begin adoption matching for ready pets
4. Continue monitoring all rescued animals
```

## Error Handling Flow

### 8. Error Processing

#### Pet Addition Failure
```json
{
  "success": false,
  "error": "Connection timeout to MCP server",
  "pet_data": {
    "rescue_id": "WF002",
    "name": "Ash",
    "species": "cat"
  }
}
```

#### Bedrock API Error
```json
{
  "error": "ClientError",
  "message": "The security token included in the request is invalid",
  "operation": "invoke_bedrock_model",
  "model_id": "anthropic.claude-3-sonnet-20240229-v1:0"
}
```

## Data Persistence Flow

### 9. Results Storage

#### JSON File Output
```python
with open(f"rescue_operation_{agent.rescue_operation_id}.json", "w") as f:
    json.dump(results, f, indent=2)
```

**Saved File Structure:**
```json
{
  "operation_id": "wildfire_rescue_20240620_080000",
  "incident_name": "Northern California Wildfire Rescue",
  "started_at": "2024-06-20T08:00:00Z",
  "completed_at": "2024-06-20T08:05:30Z",
  "total_pets": 5,
  "successful_additions": 5,
  "failed_additions": 0,
  "ai_batch_analysis": {...},
  "pets_processed": [...]
}
```

## Integration Points Summary

### 10. System Integration Flow

```
1. Rescue Data Input
   ↓
2. Agent Initialization (Bedrock + MCP clients)
   ↓
3. AI Batch Analysis (Bedrock Claude model)
   ↓
4. Individual Pet Processing Loop:
   a. AI Assessment (Bedrock)
   b. Data Extraction & Structuring
   c. MCP Tool Call (add_pet)
   d. Petstore API Integration
   ↓
5. Results Aggregation
   ↓
6. AI Report Generation (Bedrock)
   ↓
7. Data Persistence (JSON file)
```

### Key Data Transformations:

1. **Raw Rescue Data** → **AI Prompt** → **Assessment Text**
2. **Assessment Text** → **Structured Pet Data** → **MCP Tool Call**
3. **MCP Tool Call** → **HTTP Request** → **Petstore Record**
4. **Operation Results** → **Report Prompt** → **Formatted Report**

This comprehensive flow demonstrates how the Wildfire Rescue Agent seamlessly integrates AI-powered assessment with automated pet store management through the MCP protocol, providing an end-to-end solution for emergency pet rescue operations.
