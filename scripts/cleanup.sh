#!/bin/bash

# Cleanup script for Bedrock Knowledge Base resources
# Deletes: KB, AOSS collections, IAM roles, S3 buckets

set -e

echo "=============================================="
echo "🧹 Bedrock Knowledge Base Cleanup"
echo "=============================================="

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ Account ID: $ACCOUNT_ID"

# Variables
ROLE_NAME="bedrock-kb-role"
AOSS_COLLECTION="bedrock-kb-collection"
S3_BUCKET="bedrock-kb-documents-${ACCOUNT_ID}"

echo ""
echo "📋 Resources to delete:"
echo "  - IAM Role: $ROLE_NAME"
echo "  - AOSS Collection: $AOSS_COLLECTION"
echo "  - S3 Bucket: $S3_BUCKET"
echo ""

read -p "Continue with cleanup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

# Delete IAM role and policies
echo ""
echo "🔄 Deleting IAM role..."
if aws iam get-role --role-name $ROLE_NAME 2>/dev/null; then
    # Delete inline policies
    aws iam delete-role-policy --role-name $ROLE_NAME --policy-name bedrock-kb-policy 2>/dev/null || true
    # Delete role
    aws iam delete-role --role-name $ROLE_NAME
    echo "✅ IAM role deleted: $ROLE_NAME"
else
    echo "⚠️  IAM role not found: $ROLE_NAME"
fi

# Delete AOSS collection
echo ""
echo "🔄 Deleting AOSS collection..."
if aws opensearchserverless list-collections --query "collectionSummaries[?name=='$AOSS_COLLECTION']" --output text 2>/dev/null | grep -q $AOSS_COLLECTION; then
    # Get collection ID
    COLLECTION_ID=$(aws opensearchserverless list-collections --query "collectionSummaries[?name=='$AOSS_COLLECTION'].id" --output text)
    aws opensearchserverless delete-collection --id $COLLECTION_ID
    echo "✅ AOSS collection deleted: $AOSS_COLLECTION"
else
    echo "⚠️  AOSS collection not found: $AOSS_COLLECTION"
fi

# Delete S3 bucket
echo ""
echo "🔄 Deleting S3 bucket..."
if aws s3 ls "s3://$S3_BUCKET" 2>/dev/null; then
    # Empty bucket first
    aws s3 rm "s3://$S3_BUCKET" --recursive
    # Delete bucket
    aws s3 rb "s3://$S3_BUCKET"
    echo "✅ S3 bucket deleted: $S3_BUCKET"
else
    echo "⚠️  S3 bucket not found: $S3_BUCKET"
fi

echo ""
echo "=============================================="
echo "✅ Cleanup Complete!"
echo "=============================================="
