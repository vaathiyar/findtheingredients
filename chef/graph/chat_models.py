from langchain.chat_models import init_chat_model

from chef.constants import CHEF_MODEL, SUMMARIZATION_MODEL

chef_model = init_chat_model(CHEF_MODEL, temperature=0)
summarization_model = init_chat_model(SUMMARIZATION_MODEL, temperature=0)
