import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

endpoint    = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment  = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_key     = os.getenv("AZURE_OPENAI_API_KEY")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([endpoint, deployment, api_key, api_version]):
    raise EnvironmentError("環境変数が正しく設定されていません")

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version,
)

def call_chat(messages, **kwargs):
    return client.chat.completions.create(
        model=deployment,
        messages=messages,
        **kwargs
    )