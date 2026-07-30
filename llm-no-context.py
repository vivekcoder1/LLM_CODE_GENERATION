import os
import anthropic 
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


DRY_RUN = False

class BaselineCodeGeneration:
    def __init__(self):
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2') 
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        

    
    def generate_code(self, task_file_path: str) -> str:
        with open(task_file_path, "r", encoding="utf-8") as f:
            task_description = f.read()

        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=10000,
            system=(
                "You are an expert programmer specializing in physics simulations "
                "and differentiable programming frameworks, specifically PhiFlow.\n"
                "Generate a complete working Python script."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Task description:\n{task_description}",
                }
            ],
        )

        return "".join(
            block.text
            for block in response.content
            if hasattr(block, "text")
        )

if __name__ == "__main__":
    all_dirs = [
            "burgers2d", "heat_flow", "julia_set", "lid_driven_cavity", 
            "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"
        ]
    load_dotenv()
    generator = BaselineCodeGeneration()
    for dir in all_dirs:
        task_file_path = os.getcwd()+f"/test/{dir}.md"
        if DRY_RUN:
            print(f"Would generate code for {task_file_path}")
            print(f"Would write generated code to {os.getcwd()+f'/test_{dir}/generated_code.py'}")
        else:
            code = generator.generate_code(task_file_path)
            with open(os.getcwd() + f"/test_{dir}/generated_code.py", "w", encoding="utf-8") as f:
                f.write(code)
                print(f"Generated code for {task_file_path}")