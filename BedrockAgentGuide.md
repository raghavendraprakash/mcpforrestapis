# Wildfire Pet Rescue Agent with Amazon Bedrock

This guide explains how to use the Wildfire Pet Rescue Agent that combines Amazon Bedrock AI capabilities with the Petstore MCP Client to automatically process and add rescued pets from wildfire incidents.

## Overview

The Wildfire Rescue Agent demonstrates advanced AI integration by:
- Using Amazon Bedrock for intelligent pet assessment
- Leveraging the MCP Client for seamless pet store integration
- Processing rescue operations with AI-driven decision making
- Generating comprehensive rescue reports

## Architecture

```
┌─────────────────────────────────────┐
│        Wildfire Rescue Agent       │
├─────────────────────────────────────┤
│         Amazon Bedrock AI           │  ← AI Assessment & Processing
├─────────────────────────────────────┤
│       Petstore MCP Client           │  ← Pet Store Integration
├─────────────────────────────────────┤
│      Petstore MCP Server            │  ← API Operations
└─────────────────────────────────────┘
```

## Key Features

### 🤖 AI-Powered Pet Assessment
- Veterinary AI assessment of rescued pets
- Condition evaluation and status determination
- Automated tag generation based on pet needs
- Medical care recommendations

### 🔥 Wildfire-Specific Processing
- Specialized prompts for wildfire rescue scenarios
- Batch processing of multiple rescued pets
- Rescue operation tracking and documentation
- Emergency response workflow optimization

### 📊 Comprehensive Reporting
- AI-generated rescue operation reports
- Statistical analysis of rescue outcomes
- Recommendations for follow-up care
- Lessons learned documentation

### 🔄 Seamless Integration
- Direct integration with Petstore MCP Client
- Automated pet addition to adoption system
- Real-time status updates and tracking
- Error handling and retry mechanisms

## Installation and Setup

### Prerequisites

1. **AWS Account with Bedrock Access**
   - Amazon Bedrock service enabled
   - Access to Claude 3 models
   - Appropriate IAM permissions

2. **Python Environment**
   - Python 3.8 or higher
   - Required dependencies

3. **MCP Server**
   - Petstore MCP Server running
   - MCP Client components available

### Installation Steps

1. **Install Dependencies**:
   ```bash
   pip3 install -r bedrock_agent_requirements.txt
   ```

2. **Configure AWS Credentials**:
   ```bash
   aws configure
   # Or set environment variables:
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Run Setup Script**:
   ```bash
   bash setup_bedrock_agent.sh
   ```

### Required AWS Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage Examples

### Basic Usage

```python
from wildfire_rescue_agent import WildfireRescueAgent

# Initialize the agent
agent = WildfireRescueAgent(region_name="us-east-1")

# Process a rescue operation
rescue_data = {
    "incident_name": "Northern California Wildfire",
    "rescued_pets": [
        {
            "name": "Smokey",
            "species": "dog",
            "breed": "Golden Retriever",
            "condition": "Minor smoke inhalation"
        }
    ]
}

# Execute the rescue operation
results = await agent.process_wildfire_rescue_operation(rescue_data)
```

### Individual Pet Assessment

```python
# Assess a single rescued pet
pet_data = {
    "name": "Ash",
    "species": "cat",
    "breed": "Domestic Shorthair",
    "age": "2 years",
    "condition": "Dehydrated, minor burns on paws",
    "rescue_location": "Found hiding under porch"
}

assessment = await agent.assess_rescued_pet(pet_data)
print(f"AI Assessment: {assessment['ai_assessment']}")
```

### Batch Processing

```python
# Process multiple pets at once
batch_data = {
    "incident_id": "CA_WILDFIRE_2024_001",
    "incident_name": "Northern California Wildfire",
    "count": 5,
    "rescued_pets": [...]  # List of rescued pets
}

batch_results = await agent.process_rescue_batch(batch_data)
```

### Report Generation

```python
# Generate comprehensive rescue report
operation_results = await agent.process_wildfire_rescue_operation(rescue_data)
report = await agent.generate_rescue_report(operation_results)

print("=== RESCUE OPERATION REPORT ===")
print(report)
```

## Configuration Options

### Bedrock Configuration

```json
{
  "bedrock_config": {
    "region_name": "us-east-1",
    "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
    "fallback_model_id": "anthropic.claude-3-haiku-20240307-v1:0",
    "max_retries": 3,
    "timeout": 60
  }
}
```

### MCP Client Configuration

```json
{
  "mcp_config": {
    "server_path": "./petstore-mcp-server.py",
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "log_level": "INFO"
  }
}
```

### Rescue Operation Configuration

```json
{
  "rescue_operation_config": {
    "batch_size": 10,
    "processing_delay": 0.5,
    "default_status": "pending",
    "auto_generate_tags": true
  }
}
```

## AI Prompt Templates

### Pet Assessment Prompt

The agent uses specialized prompts for veterinary assessment:

```python
system_prompt = """You are a veterinary AI assistant specializing in wildfire rescue operations. 
Your role is to assess rescued pets and determine their condition, needs, and readiness for adoption.

Consider factors like:
- Physical condition and injuries
- Stress levels and behavioral changes
- Medical needs and treatment requirements
- Estimated recovery time
- Adoption readiness status"""
```

### Batch Processing Prompt

For processing multiple pets efficiently:

```python
system_prompt = """You are a rescue coordination AI assistant. Process multiple rescued pets efficiently
and prepare them for entry into the pet adoption system.

Ensure each pet has:
- Proper categorization
- Appropriate status assignment
- Relevant rescue tags
- Complete documentation"""
```

## Sample Rescue Operation

The agent includes a complete sample rescue operation:

```python
SAMPLE_WILDFIRE_RESCUE_DATA = {
    "incident_id": "CA_WILDFIRE_2024_001",
    "incident_name": "Northern California Wildfire Rescue",
    "location": "Sonoma County, CA",
    "rescued_pets": [
        {
            "rescue_id": "WF001",
            "name": "Smokey",
            "species": "dog",
            "breed": "Golden Retriever",
            "condition": "Minor smoke inhalation, otherwise healthy"
        },
        {
            "rescue_id": "WF002", 
            "name": "Ash",
            "species": "cat",
            "breed": "Domestic Shorthair",
            "condition": "Dehydrated, minor burns on paws"
        }
        # ... more pets
    ]
}
```

## Workflow Process

### 1. Rescue Operation Initialization
- Generate unique operation ID
- Setup custom rescue prompts
- Initialize AI and MCP clients

### 2. AI Batch Analysis
- Process all rescued pets through AI
- Generate batch recommendations
- Determine processing priorities

### 3. Individual Pet Processing
- AI assessment for each pet
- Extract structured pet details
- Add to petstore via MCP client

### 4. Results Compilation
- Track success/failure rates
- Compile operation statistics
- Generate comprehensive reports

## Error Handling

### Bedrock API Errors
```python
try:
    response = await agent.invoke_bedrock_model(prompt)
except ClientError as e:
    logger.error(f"Bedrock API error: {e}")
    # Implement fallback or retry logic
```

### MCP Client Errors
```python
try:
    result = await agent.petstore_agent.execute_task("manage_pet", **pet_data)
except Exception as e:
    logger.error(f"MCP client error: {e}")
    # Handle pet addition failure
```

### Rescue Operation Errors
```python
# Comprehensive error tracking in operation results
results = {
    "successful_additions": 0,
    "failed_additions": 0,
    "errors": []
}
```

## Monitoring and Logging

### Operation Tracking
- Unique operation IDs for each rescue
- Timestamp tracking for all operations
- Success/failure rate monitoring

### Detailed Logging
```python
logger.info(f"Starting rescue operation: {incident_name}")
logger.info(f"Processing pet: {pet_name}")
logger.info(f"Operation completed: {success_rate}% success")
```

### Results Persistence
- JSON output files for each operation
- Comprehensive rescue reports
- AI assessment documentation

## Best Practices

### 1. Resource Management
```python
# Use proper async context management
async with agent.petstore_agent.transport.connect():
    # Perform operations
    pass
```

### 2. Error Resilience
```python
# Implement retry logic for critical operations
for attempt in range(max_retries):
    try:
        result = await operation()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            raise
        await asyncio.sleep(retry_delay)
```

### 3. Batch Processing
```python
# Process pets in batches to avoid overwhelming APIs
for batch in chunks(rescued_pets, batch_size):
    await process_batch(batch)
    await asyncio.sleep(processing_delay)
```

### 4. AI Prompt Optimization
```python
# Use specific, context-aware prompts
prompt = f"""Assess this {species} rescued from wildfire:
Condition: {condition}
Location: {rescue_location}
Provide specific medical and behavioral recommendations."""
```

## Extending the Agent

### Adding New Assessment Types
```python
# Add custom prompt templates
custom_prompt = PromptTemplate(
    system="You are a specialist in {specialty}",
    user_template="Assess {pet_type} for {assessment_type}",
    examples={"example": "Sample assessment"}
)
agent.prompt_manager.add_template("custom_assessment", custom_prompt)
```

### Custom Processing Workflows
```python
async def custom_rescue_workflow(self, rescue_data):
    # Implement custom processing logic
    # Use existing AI and MCP capabilities
    pass
```

### Integration with Other Services
```python
# Add additional AWS services
self.s3_client = boto3.client('s3')
self.sns_client = boto3.client('sns')

# Implement photo storage, notifications, etc.
```

## Troubleshooting

### Common Issues

1. **Bedrock Access Denied**
   - Verify AWS credentials
   - Check IAM permissions
   - Ensure Bedrock is enabled in your region

2. **MCP Server Connection Failed**
   - Verify MCP server is running
   - Check server path configuration
   - Review network connectivity

3. **AI Assessment Errors**
   - Check prompt formatting
   - Verify model availability
   - Review input data structure

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run agent with debug logging
agent = WildfireRescueAgent()
```

## Performance Considerations

### Optimization Tips
- Use batch processing for multiple pets
- Implement caching for repeated assessments
- Use appropriate Bedrock model for task complexity
- Monitor API rate limits and costs

### Cost Management
- Choose cost-effective Bedrock models
- Implement request batching
- Use caching to reduce API calls
- Monitor usage and set budgets

This comprehensive guide provides everything needed to understand, deploy, and extend the Wildfire Pet Rescue Agent with Amazon Bedrock integration.
