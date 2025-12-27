import os
from typing import Type, TypeVar
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

T = TypeVar("T", bound=BaseModel)


def get_llm_client(model_name: str, temperature: float = 0.0):
    
    hf_token = os.getenv("HF_TOKEN")
    
    llm = HuggingFaceEndpoint(
        repo_id=model_name,
        task="text-generation",
        temperature=temperature,
        huggingfacehub_api_token=hf_token,
        max_new_tokens=2048,
    )
    
    return ChatHuggingFace(llm=llm)


def invoke_with_structured_output(
    model_name: str,
    messages: list[dict],
    response_model: Type[T],
    temperature: float = 0.0
) -> T:
    llm = get_llm_client(model_name, temperature)
    
    lc_messages = []
    for msg in messages:
        if msg["role"] == "system":
            lc_messages.append(SystemMessage(content=msg["content"]))
        elif msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
    
    structured_llm = llm.with_structured_output(response_model)
    
    return structured_llm.invoke(lc_messages)
