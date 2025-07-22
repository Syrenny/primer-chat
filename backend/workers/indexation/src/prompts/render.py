from pathlib import Path

from jinja2 import Environment, FileSystemLoader

PROMPT_DIR = Path(__file__).parent

env = Environment(loader=FileSystemLoader(PROMPT_DIR), autoescape=False)


def render_prompt(name: str, context: dict) -> str:
    template = env.get_template(name)
    return template.render(**context)
