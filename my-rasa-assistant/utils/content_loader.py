import yaml
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'i18n')

def load_questions(lang: str, question_id: str, variant_index: int) -> str:
    """Load a specific question variant."""
    file_path = os.path.join(CONTENT_DIR, f'{lang}.yml')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['questions'][question_id]['variants'][variant_index]


def load_summary(lang: str) -> str:
    """Load the summary template."""
    file_path = os.path.join(CONTENT_DIR, f'{lang}.yml')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data['summaries']['final']


def load_question_config():
    """Load question configuration."""
    file_path = os.path.join(CONTENT_DIR, 'config.yml')
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)