# lambda_function.py - Simplified for Lightweight Deployment
import json
import boto3
import os
import traceback # For detailed error logging

# --- Configuration ---
# These are loaded from Lambda Environment Variables
# Key: S3_BUCKET_NAME, Value: sentinel-ops-data-lake-satya (still needed for context, though not for model loading)
# Key: MODEL_S3_KEY, Value: models/disk_usage_predictor.joblib (not used for loading, but can be left for future)
# Key: SNS_TOPIC_ARN, Value: arn:aws:sns:us-east-2:YOUR_ACCOUNT_ID:sentinel-ops-alerts-topic (REPLACE YOUR_ACCOUNT_ID)
# Key: AWS_REGION, Value: us-east-2

s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
model_s3_key = os.environ.get('MODEL_S3_KEY') # Not actively used for loading now
sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
aws_region = os.environ.get('AWS_REGION', 'us-east-2')

sns_client = boto3.client('sns', region_name=aws_region)

# --- SIMPLIFIED PREDICTION LOGIC ---
# For MVP, we'll use a hardcoded threshold. In a full system, this would be learned from a model.
HIGH_DISK_USAGE_THRESHOLD = 90 # If disk_usage_percent > 90, predict 1 (high)

def predict_disk_usage(disk_usage_percent):
    """
    Performs a simplified prediction based on a hardcoded threshold.
    """
    if disk_usage_percent > HIGH_DISK_USAGE_THRESHOLD:
        return 1 # Predicted high usage
    else:
        return 0 # Predicted normal usage

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    server_id = None
    hour = None
    dayofweek = None
    disk_usage_percent = None

    # --- 1. Extract/Simulate Input Data ---
    try:
        if 'server_id' in event and 'disk_usage_percent' in event:
            server_id = event['server_id']
            # Extract hour/dayofweek if present, otherwise default (not used by simplified model)
            hour = event.get('hour')
            dayofweek = event.get('dayofweek')
            disk_usage_percent = event.get('disk_usage_percent')
            print("Parsed from direct Lambda event.")
        elif event.get('sessionState', {}).get('intent', {}).get('name') == 'CheckServerHealth': # Lex v2 input format
            server_id = event['sessionState']['intent']['slots']['serverName']['value']['interpretedValue']
            # For simplified model, we only need disk_usage_percent
            disk_usage_percent = 91 # Defaulting to high for Lex demo
            hour = 10 # Default
            dayofweek = 4 # Default
            print(f"Parsed from Lex event for server: {server_id}. Using mock disk_usage_percent for prediction.")
        else:
            # Fallback to mock data if no event data or unexpected format
            server_id = 'server-mock-001'
            disk_usage_percent = 92 # Default to high for easy testing
            hour = 12
            dayofweek = 1
            print("Using fallback mock data for testing.")

        if hour is None or dayofweek is None:
            hour = 12
            dayofweek = 1 # Not used by simplified model, but kept for consistent logging

    except Exception as e:
        print(f"ERROR during input parsing: {e}")
        server_id = 'UNKNOWN_SERVER'
        disk_usage_percent = 80 # Default to normal to avoid false alerts on error
        print("Input parsing failed, using generic mock data.")

    # --- 2. Make Prediction (using simplified logic) ---
    try:
        prediction_result = predict_disk_usage(disk_usage_percent)
        print(f"Prediction result for {server_id}: {prediction_result}")

        # --- 3. Formulate Message ---
        message_subject = f"Sentinel AI Ops Status: {server_id}"
        message_body = f"Sentinel AI Ops Report for {server_id} (Disk Usage: {disk_usage_percent}%):\n"
        lex_fulfillment_state = 'Fulfilled'

        if prediction_result == 1: # High disk usage predicted
            message_body += "ALERT: Predicted High Disk Usage! Immediate attention recommended to prevent issues."
            message_subject = f"🚨 ALERT: {server_id} - Predicted High Disk Usage"
        else:
            message_body += "STATUS: Disk usage is currently normal."

        # --- 4. Send Notification (using SNS, if predicted issue) ---
        if prediction_result == 1:
            if sns_topic_arn:
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=message_body,
                    Subject=message_subject
                )
                print(f"SNS publish response (alert): {message_body}")
            else:
                print("SNS_TOPIC_ARN not configured. Skipping SNS notification.")
        else:
            print("No high disk usage predicted. No SNS notification sent.")

        # --- 5. Format Response for Lambda Test/API Gateway/Lex ---
        if event.get('sessionState', {}).get('intent', {}).get('name') == 'CheckServerHealth':
             return {
                'sessionState': {
                    'dialogAction': {
                        'type': 'Close'
                    },
                    'intent': {
                        'name': event['sessionState']['intent']['name'],
                        'slots': event['sessionState']['intent']['slots'],
                        'state': lex_fulfillment_state
                    }
                },
                'messages': [
                    {
                        'contentType': 'PlainText',
                        'content': message_body
                    }
                ]
            }
        else: # For direct Lambda test or other API
            return {
                'statusCode': 200,
                'body': json.dumps({'message': message_body, 'prediction': prediction_result})
            }

    except Exception as e:
        print(f"ERROR during prediction or message formulation: {str(e)}")
        if event.get('sessionState', {}).get('intent', {}).get('name') == 'CheckServerHealth':
             return {
                'sessionState': {
                    'dialogAction': {'type': 'Close'},
                    'intent': {'name': event['sessionState']['intent']['name'], 'state': 'Failed'}
                },
                'messages': [{'contentType': 'PlainText', 'content': f"Copilot: An error occurred: {str(e)}"}]
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e), 'trace': traceback.format_exc()})
            }