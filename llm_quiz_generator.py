import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from models import QuizResponse


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Please set GEMINI_API_KEY in your .env file")


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  
    google_api_key=api_key,
    temperature=0.7
)


parser = JsonOutputParser(pydantic_object=QuizResponse)


prompt_template = PromptTemplate(
    input_variables=["title", "content", "url"],
    template=(
        "You are an expert educational content creator.\n\n"
        "Analyze the given Wikipedia article and produce a detailed quiz dataset "
        "in **strict JSON format** matching the following schema:\n"
        "{format_instructions}\n\n"
        "Guidelines:\n"
        "- Provide a concise 2–3 sentence 'summary' of the article.\n"
        "- Under 'key_entities', extract 2–5 key people, organizations, and locations.\n"
        "- List 3–6 key 'sections' from the article (like headings).\n"
        "- Generate 5–10 multiple-choice questions under 'quiz'. Each should include:\n"
        "  • question\n  • 4 options\n  • answer (one correct option)\n  • difficulty (easy/medium/hard)\n  • explanation (why it's correct)\n"
        "- Provide 3–6 'related_topics' — concise keywords related to the article.\n\n"
        "Do not include any text outside the JSON.\n\n"
        "Title: {title}\n"
        "URL: {url}\n\n"
        "Article:\n{content}\n"
    ),
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def generate_quiz_from_content(title: str, content: str, url: str) -> dict:
    """Generate the rich quiz JSON (summary, key entities, sections, quiz, topics)."""
    chain = prompt_template | llm | parser
    result = chain.invoke({"title": title, "content": content, "url": url})
    return result
