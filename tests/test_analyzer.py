import ast
from odocxify import analyzer

def test_analyze_simple_function(tmp_path):
    source_code = """
def hello(name):
    '''Says hello.'''
    print(f"Hello {name}")
"""
    f = tmp_path / "simple.py"
    f.write_text(source_code, encoding="utf-8")

    results = analyzer.analyze_file(str(f))
    
    assert len(results["functions"]) == 1
    func = results["functions"][0]
    assert func["name"] == "hello"
    assert func["docstring"] == "Says hello."
    assert "name" in func["args"]

def test_analyze_class(tmp_path):
    source_code = """
class Greeter:
    '''A class that greets.'''
    
    def greet(self):
        pass
"""
    f = tmp_path / "cls.py"
    f.write_text(source_code, encoding="utf-8")

    results = analyzer.analyze_file(str(f))
    
    assert len(results["classes"]) == 1
    cls = results["classes"][0]
    assert cls["name"] == "Greeter"
    assert len(cls["methods"]) == 1
    assert cls["methods"][0]["name"] == "greet"


def test_analyze_richer_api_surface(tmp_path):
    source_code = '''
"""Module docs."""

DEFAULT_LIMIT: int = 10

@decorated
async def fetch_user(user_id: int) -> str:
    """Fetch a user."""
    return str(user_id)

def _internal():
    return None

class Client(BaseClient):
    """API client."""

    TIMEOUT = 30

    def __init__(self, token: str):
        self.token = token

    @property
    def ready(self) -> bool:
        """Whether the client is ready."""
        return True
'''
    f = tmp_path / "richer.py"
    f.write_text(source_code, encoding="utf-8")

    results = analyzer.analyze_file(str(f))

    assert results["module_docstring"] == "Module docs."
    assert results["constants"][0]["name"] == "DEFAULT_LIMIT"
    assert results["functions"][0]["signature"] == "async def fetch_user(user_id: int) -> str"
    assert results["functions"][0]["decorators"] == ["decorated"]
    assert len(results["functions"]) == 1

    cls = results["classes"][0]
    assert cls["bases"] == ["BaseClient"]
    assert cls["attributes"][0]["name"] == "TIMEOUT"
    assert [method["name"] for method in cls["methods"]] == ["__init__", "ready"]


def test_analyze_syntax_error_returns_error(tmp_path):
    f = tmp_path / "broken.py"
    f.write_text("def nope(:\n    pass\n", encoding="utf-8")

    results = analyzer.analyze_file(str(f))

    assert results["errors"]
    assert results["classes"] == []
