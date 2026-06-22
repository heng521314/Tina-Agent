from backend.tina.skills import load_skills


def get_skills_prompt_section() -> str:
    """Generate the skills prompt section with available skills list.

    Returns the <skill_system>...</skill_system> block listing all enabled skills,
    suitable for injection into any agent's system prompt.
    """
    skills = load_skills(enabled_only=True)

    if not skills:
        return ""

    skill_items = "\n".join(
        f"    <skill>\n        <name>{skill.name}</name>\n        <description>{skill.description}</description>\n        <location>{skill.skill_file}</location>\n    </skill>"
        for skill in skills
    )
    skills_list = f"<available_skills>\n{skill_items}\n</available_skills>"

    return f"""<skill_system>
        You have access to skills that provide optimized workflows for specific tasks. Each skill contains best practices, frameworks, and references to additional resources.
        
        **Progressive Loading Pattern:**
        1. When a user query matches a skill's use case, immediately call `read_file` on the skill's main file using the path attribute provided in the skill tag below
        2. Read and understand the skill's workflow and instructions
        3. The skill file contains references to external resources under the same folder
        4. Load referenced resources only when needed during execution
        5. Follow the skill's instructions precisely
        6. If you want to know more about a skill, you need to use the `load_skill` tool and provide the name of the skill.
        7. Even if the user task has a 1% relevance to the skill, the skill will be invoked immediately.
        
        **Skills are located at:** 
        
        {skills_list}
        
        </skill_system>"""
