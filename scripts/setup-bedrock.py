#!/usr/bin/env python3
"""
Setup script for Bedrock Knowledge Base
Creates IAM roles, OpenSearch Serverless collection, and S3 bucket
"""

import boto3
import json
import sys
from botocore.exceptions import ClientError

# Initialize clients
iam_client = boto3.client('iam')
aoss_client = boto3.client('opensearchserverless')
s3_client = boto3.client('s3')
sts_client = boto3.client('sts')

def get_account_id():
    """Get AWS Account ID"""
    try:
        account_id = sts_client.get_caller_identity()['Account']
        print(f"✅ AWS Account ID: {account_id}")
        return account_id
    except Exception as e:
        print(f"❌ Error getting account ID: {e}")
        sys.exit(1)

def create_iam_role(role_name="bedrock-kb-role"):
    """Create IAM role for Bedrock Knowledge Base"""
    print(f"\n📋 Creating IAM Role: {role_name}")
    
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy),
            Description='Role for Bedrock Knowledge Base'
        )
        role_arn = response['Role']['Arn']
        print(f"✅ Role created: {role_arn}")
        return role_arn
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityAlreadyExists':
            print(f"⚠️  Role already exists")
            response = iam_client.get_role(RoleName=role_name)
            return response['Role']['Arn']
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

def attach_policies(role_name):
    """Attach policies to IAM role"""
    print(f"\n📋 Attaching policies to {role_name}")
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:*",
                    "aoss:*",
                    "s3:GetObject",
                    "s3:ListBucket",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": "*"
            }
        ]
    }
    
    try:
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName='bedrock-kb-policy',
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"✅ Policies attached")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def create_aoss_collection(collection_name="bedrock-kb-collection"):
    """Create OpenSearch Serverless collection"""
    print(f"\n📋 Creating AOSS Collection: {collection_name}")
    
    try:
        response = aoss_client.create_collection(
            name=collection_name,
            type='VECTORSEARCH',
            description='Vector store for Bedrock Knowledge Base'
        )
        collection_arn = response['createCollectionDetail']['arn']
        print(f"✅ Collection created: {collection_arn}")
        return collection_arn
    except ClientError as e:
        if 'already exists' in str(e):
            print(f"⚠️  Collection already exists")
            response = aoss_client.list_collections()
            for collection in response['collectionSummaries']:
                if collection['name'] == collection_name:
                    return collection['arn']
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

def create_s3_bucket(bucket_name):
    """Create S3 bucket for documents"""
    print(f"\n📋 Creating S3 Bucket: {bucket_name}")
    
    try:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        print(f"✅ Bucket created: {bucket_name}")
        return bucket_name
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"⚠️  Bucket already exists: {bucket_name}")
            return bucket_name
        else:
            print(f"❌ Error: {e}")
            sys.exit(1)

def main():
    """Main setup function"""
    print("="*60)
    print("🚀 Bedrock Knowledge Base Setup")
    print("="*60)
    
    # Get account ID
    account_id = get_account_id()
    
    # Create IAM role
    role_arn = create_iam_role()
    role_name = role_arn.split('/')[-1]
    
    # Attach policies
    attach_policies(role_name)
    
    # Create AOSS collection
    aoss_arn = create_aoss_collection()
    
    # Create S3 bucket
    bucket_name = f"bedrock-kb-documents-{account_id}"
    s3_bucket = create_s3_bucket(bucket_name)
    
    # Print summary
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print(f"\nSave these values for later use:")
    print(f"  Role ARN: {role_arn}")
    print(f"  AOSS ARN: {aoss_arn}")
    print(f"  S3 Bucket: {s3_bucket}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
