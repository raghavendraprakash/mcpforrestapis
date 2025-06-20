#!/bin/bash

# Setup script for Wildfire Rescue Agent with Amazon Bedrock

echo "Setting up Wildfire Rescue Agent with Amazon Bedrock..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r bedrock_agent_requirements.txt

# Make the agent executable
chmod +x wildfire_rescue_agent.py

# Check AWS credentials
echo "Checking AWS credentials..."
if aws sts get-caller-identity > /dev/null 2>&1; then
    echo "✅ AWS credentials configured"
else
    echo "❌ AWS credentials not configured"
    echo "Please run: aws configure"
    echo "Or set environment variables:"
    echo "  export AWS_ACCESS_KEY_ID=your_access_key"
    echo "  export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "  export AWS_DEFAULT_REGION=us-east-1"
fi

# Check Bedrock model access
echo "Checking Bedrock model access..."
if aws bedrock list-foundation-models --region us-east-1 > /dev/null 2>&1; then
    echo "✅ Bedrock access configured"
else
    echo "⚠️  Bedrock access may need to be enabled"
    echo "Please ensure you have access to Amazon Bedrock in your AWS account"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the Wildfire Rescue Agent:"
echo "  python3 wildfire_rescue_agent.py"
echo ""
echo "Required AWS permissions:"
echo "  - bedrock:InvokeModel"
echo "  - bedrock:ListFoundationModels"
echo ""
echo "Supported Bedrock models:"
echo "  - anthropic.claude-3-sonnet-20240229-v1:0 (default)"
echo "  - anthropic.claude-3-haiku-20240307-v1:0 (fallback)"
