import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from api.models import DependencyInfo, UpgradePlanItem

# Initialize the Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY", "dummy_key_for_now"),
    convert_system_message_to_human=True
)

def generate_upgrade_plan(dependencies: list[DependencyInfo]) -> list[UpgradePlanItem]:
    if not dependencies:
        return []
        
    deps_text = ""
    for dep in dependencies:
        status = "OUTDATED" if dep.is_outdated else "UP-TO-DATE"
        latest = dep.latest_version or dep.current_version
        deps_text += f"- {dep.name}: {dep.current_version} -> {latest} ({status}, in {dep.file_path})\n"
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI software architect. Analyze the provided dependencies (some are outdated, some are up-to-date) and generate an evaluation and upgrade plan for EACH dependency.
Respond ONLY with a JSON array of objects, containing these exact keys for EVERY dependency:
- "dependency": string (name of the package)
- "from_version": string (current version)
- "to_version": string (latest version)
- "breaking_changes": string (description of potential breaking changes, or 'None' if up-to-date)
- "risk_level": string ("None", "Low", "Medium", "High")
- "recommended": boolean (whether it's safe to upgrade automatically. false if up-to-date or high risk)
- "reasoning": string (a detailed explanation for the risk level assigned and why it is or isn't recommended)

Example:
[
  {{
    "dependency": "fastapi",
    "from_version": "0.75.0",
    "to_version": "0.110.0",
    "breaking_changes": "Major Pydantic v2 changes, router path evaluation differences.",
    "risk_level": "High",
    "recommended": false,
    "reasoning": "Upgrading from 0.7x to 0.11x crosses a major semantic jump in FastAPI, requiring manual refactors for Pydantic V2 migrations. Automated upgrade is highly discouraged."
  }}
]"""),
        ("human", "Here are the dependencies:\n{deps_text}")
    ])
    
    chain = prompt | llm
    
    try:
        response = chain.invoke({"deps_text": deps_text})
        
        content = response.content
        clean_content = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_content)
        
        plan_items = []
        for item in data:
            plan_items.append(UpgradePlanItem(**item))
        return plan_items
    except Exception as e:
        print(f"Error generating plan: {e}")
        plan_items = []
        for dep in dependencies:
            plan_items.append(UpgradePlanItem(
                dependency=dep.name,
                from_version=dep.current_version,
                to_version=dep.latest_version or dep.current_version,
                breaking_changes="AI failed to generate details",
                risk_level="Unknown",
                recommended=False,
                reasoning="Failed to contact AI model"
            ))
        return plan_items
