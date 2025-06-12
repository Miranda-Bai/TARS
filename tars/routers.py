from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import config

def prompt_route(model_name, prompt_template_params, user_input):
    try:
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=config.openrouter_api_key,  # Fixed typo
            openai_api_base=config.openrouter_api_base
        )
        
        # Build classification instructions
        classification_instructions = "Given the user question below, classify it as either being about "
        options_descriptions = ""
        options_data = prompt_template_params["options"]
        
        # Build the classification options list
        option_names = list(options_data.keys())
        for i, option in enumerate(option_names):
            classification_instructions += f"'{option}'"
            if i < len(option_names) - 1:
                classification_instructions += ", "
            else:
                classification_instructions += "."
        
        # Build the descriptions for each option
        for option, keywords in options_data.items():
            if len(keywords) > 1:
                formatted_descriptions = ", ".join(keywords[:-1]) + ", or " + keywords[-1]
            else:
                formatted_descriptions = keywords[0]
            
            options_descriptions += f"<If the question is about {formatted_descriptions}, classify it as '{option}'>\n"
        
        options_descriptions += f"<If the question does not fit any of the classifications, classify it as '{prompt_template_params['default_none']}'>"
        
        # Create prompt template
        prompt_template = (
            PromptTemplate.from_template(
                """You are good at classifying a question.
{classification_instructions}

{options_descriptions}

<question>
{user_input}
</question>

NOTE: The question could have more than one classification; in those cases, return your answer with commas separating each classification.

Classification:"""
            )
            | llm
        )
        
        classification_result = prompt_template.invoke({
            "user_input": user_input,
            "classification_instructions": classification_instructions,
            "options_descriptions": options_descriptions,
        })
        
        return classification_result.content
        
    except Exception as e:
        print(f"Error in prompt_route: {str(e)}")
        return prompt_template_params['default_none']