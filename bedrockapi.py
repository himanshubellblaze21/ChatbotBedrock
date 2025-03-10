# import boto3
# import json

# aws_region = "us-east-1"
# bedrock_client = boto3.client("bedrock-runtime", region_name=aws_region)

# def query_bedrock(document_text, user_query):
#     model_id = "anthropic.claude-v2"
    
#     # Combine document text and user query
#     full_prompt = f"Context: {document_text}\n\nQuestion: {user_query}\n\nAnswer:"

#     payload = {
#         "prompt": full_prompt,
#         "max_tokens_to_sample": 500
#     }

#     response = bedrock_client.invoke_model(
#         modelId=model_id,
#         contentType="application/json",
#         accept="application/json",
#         body=json.dumps(payload)
#     )

#     result = json.loads(response["body"].read())
#     return result.get("completion", "Error: No response from model.")


import boto3
import json

aws_region = "us-east-1"
bedrock_client = boto3.client("bedrock-runtime", region_name=aws_region)

def query_bedrock(document_text, user_query):
    model_id = "anthropic.claude-v2"
    
    # Format the prompt correctly
    full_prompt = f"""Human: Here is some context for you:
{document_text}

Now, answer this question:
{user_query}

Assistant:"""

    payload = {
        "prompt": full_prompt,
        "max_tokens_to_sample": 500
    }

    response = bedrock_client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    result = json.loads(response["body"].read())
    return result.get("completion", "Error: No response from model.")
