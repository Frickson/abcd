import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('codepipeline')
    try:
        sns_message = json.loads(event['Records'][0]['Sns']['Message'])
        token = sns_message['approval']['token']
        pipeline = sns_message['approval']['pipelineName']
        stage = sns_message['approval']['stageName']
        approval_action = sns_message['approval']['actionName']
        response = client.put_approval_result(
            pipelineName=pipeline,
            stageName=stage,
            actionName=approval_action,
            result={
                'status': 'Approved',
                'summary': 'Auto-approved by Lambda function.'
            },
            token=token
        )
        print("Approval result:", response)
        return {
            'statusCode': 200,
            'body': json.dumps('Approval successful!')
        }
    except Exception as e:
        print("Error:", e)
        return {
            'statusCode': 500,
            'body': json.dumps('Error auto-approving the action.')
        }