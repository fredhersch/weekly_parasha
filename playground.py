# playground.py
from agno.app.playground import Playground
from agno.app import serve_playground_app
from workflows.parasha_workflow import TorahStudyWorkflow
from agno.storage.sqlite import SqliteStorage

workflow = TorahStudyWorkflow(
    storage=SqliteStorage(table_name="torah_workflows", db_file="torah_agent.db")
)

app = Playground(workflows=[workflow]).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)