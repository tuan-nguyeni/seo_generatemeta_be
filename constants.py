# API
API_KEY_NAME = "openai_key"
MODEL_NAME = "gpt-3.5-turbo-16k"

# SERVER
DEFAULT_PORT = 5002

# PROMPT SETTINGS
PROMPT_FORMAT_TITLE = "I want to generate a title for a website. It should be optimized for SEO and has " \
                      "less than 580 px. The title should be written in {language}" \
                      " This is the keyword {keyword}  \n\n this is the content: {content} \n\n"
PROMPT_FORMAT_METADESCRIPTION = "generate a meta description. It should be optimized for SEO and " \
                                "has less than 960 px. The generated meta description" \
                                " should be written in {language}"
SYSTEM_MESSAGE = "You are an intelligent assistant."
