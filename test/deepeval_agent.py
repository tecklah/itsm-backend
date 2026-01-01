from deepeval.metrics import TaskCompletionMetric
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.tracing import observe
from dotenv import load_dotenv
import os
import sys

# Load environment variables first
load_dotenv(dotenv_path='../.env')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import langchain_deepagent as agent

task_completion_metric = TaskCompletionMetric(model="gpt-4.1-mini")

dataset = EvaluationDataset(
    goldens=[
        Golden(
            input=(
                "A new ITSM service request has been created with the following details:\n"
                "ID: 34\n"
                "Title: Reset password\n"
                "Username: user99\n"
                "Description: Reset password for user99 in Facility Application\n"
                "Application: Facility Application\n"
            )
        )
    ]
)

@observe(metrics=[task_completion_metric])
def test_ai_agent(input: str):
    return agent.run(input, is_test=True)

# Loop through dataset
for golden in dataset.evals_iterator():
    test_ai_agent(golden.input)