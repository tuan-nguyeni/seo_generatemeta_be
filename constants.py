# API
API_KEY_NAME = "openai_key"
MODEL_NAME = "gpt-3.5-turbo-16k"

# SERVER
DEFAULT_PORT = 5002

# PROMPT SETTINGS
PROMPT_FORMAT_TITLE = "I want to generate a title for a website. It should be optimized for SEO and has " \
                      "less than 45 characters. The title should be written in {language}" \
                      " This is the keyword {keyword}  \n\n this is the content, which might be empty: {content} \n\n"
PROMPT_FORMAT_METADESCRIPTION = "Generate a meta description. Only meta description and nothing more. It should be optimized for SEO and " \
                                "has less than 120 characters. The generated meta description" \
                                " should be written in {language}. The generated meta description is based on the above title, keywords, and content." \
                                "if the content or keywords are empty, create some suggestions anyway" \
                                " The format: 'meta description' "
SYSTEM_MESSAGE = "You are an intelligent SEO Consultant."
