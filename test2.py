import boto3
import json
import re
from time import sleep
import time
from datetime import datetime  


def start_pipeline(list, commit_sha, run_list, branch_name, param_name):
    client = boto3.client('codepipeline')
    for x in list:
        if x in run_list:
            pipeline_name = branch_name + "-" + x
            response = client.start_pipeline_execution(name=pipeline_name)
    return pipeline_name

def lambda_handler(event, context):
    # Read the payload from the event
    payload = json.loads(event['body'])
    # Execute pipeline if folder name inside the list
    run_list = ["webserver", "authapi", "userapi", "livechatapi", "chatbotapi", "fileserver", "videoserver", "sockerserver"]
    # Execute pipeline if filename not inside the list
    exclude_list = ["README.md"]
    param_name = "project_path"
    
    # Extract the repository name and commit details from the payload
    ref = payload["ref"]
    branch_match = re.match(r"refs/heads/(.*)", ref)
    if branch_match:
        # If the ref matches the regex pattern "refs/heads/(.*)", extract the branch name
        branch_name = branch_match.group(1)
        
    repository_name = payload['repository']['name']
    
    # get data from payload
    commit_sha = payload['after']
    commit_data = payload['commits'][0]
    commit_files = commit_data['added'] + commit_data['modified']
    
    #filter commited file with regax
    filtered_list = list(filter(lambda x: '/' in x, commit_files))

    # Split the remaining strings into two parts
    split_list = [s.split('/') for s in filtered_list]
    
    # Extract the first and second parts of each split string
    output_list = [[s[0], s[1]] for s in split_list]

    # check if filename is inside exclude list
    res =[]
    for file in output_list:
        if file[1] not in exclude_list:
            res.append(file[0])
    
    # remove duplicate from list
    res = [*set(res)]
    

    # if list empty mean no folder modified in specific folder
    if not res:
        return {
            'statusCode': 200,
            'body': json.dumps('No files modified in the specific folder')
        }
    ssm = boto3.client('ssm')
    response = ssm.put_parameter(
        Name="commit_id",
        Value=commit_sha,
        Type='String',
        Overwrite=True
    )
    # Trigger the CodePipeline if any of the modified or added files are in the specific folder
    pname = start_pipeline(res, commit_sha, run_list, branch_name, param_name)

    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline execution triggered successfully ' + pname)
    }
