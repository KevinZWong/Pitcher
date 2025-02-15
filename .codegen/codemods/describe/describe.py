import codegen
from codegen import Codebase
import os
from codegen.sdk.codebase.config import CodebaseConfig, Secrets
#import subprocesses
import concurrent.futures
global explanation_parts 

#explanation_parts = []


def analyze_functions():
    explanation_parts = []
    explanation_parts.append('FUNCTION EXPLANATIONS')
    i = len(codebase.functions)
    # Include explanations for each function
    for function in codebase.functions:
        i -= 1
        #print(i)
        explanation = codebase.ai(
            prompt="Provide a detailed explanation of this function.",
            target=function,
            context={"usages": function.usages, "dependencies": function.dependencies}
        )
        #print(explanation)
        explanation_parts.append(explanation)
    return explanation_parts
def analyze_classes():
    explanation_parts = []
    i = len(codebase.classes)
    explanation_parts.append('CLASS EXPLANATIONS')
    # Include explanations for each class
    for cls in codebase.classes:
        i -= 1
        #print(i)
        explanation = codebase.ai(
            prompt="Provide a detailed explanation of this class.",
            target=cls,
            context={"usages": cls.usages, "dependencies": cls.dependencies}
        )
        #print(explanation)
        explanation_parts.append(explanation)
    return explanation_parts
def analyze_files():
    explanation_parts = []
    i = len(codebase.files())
    #Include explanations for each file's imports
    explanation_parts.append('FILE EXPLANATIONS')
    for file in codebase.files():
        i -= 1
        #print(i)
        explanation = codebase.ai(
            prompt="Explain in detail this file and what it does (its features)",
            target=file
        )
        #print(explanation,)
        explanation_parts.append(explanation)
    return explanation_parts

@codegen.function('describe')
def run(codebase: Codebase):
    explanation_parts = []
    print('Total files: ', len(codebase.files()))
    print('Total functions: ', len(codebase.functions))
    print('Total classes: ', len(codebase.classes))
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(analyze_functions),
            executor.submit(analyze_classes),
            executor.submit(analyze_files)
        ]
        for future in concurrent.futures.as_completed(futures):
            explanation_parts.extend(future.result())

    # Write all explanations to output.txt
    with open("output.txt", "w") as f:
        f.write('\n\n'.join(explanation_parts))

    # Commit changes to the codebase
    codebase.commit()

import time
if __name__ == "__main__":
    print('Parsing codebase...')
    repo = 'cheollie/pengage'
    start_time = time.time()
    codebase = Codebase.from_repo(repo,config=CodebaseConfig(
        secrets=Secrets(
            openai_key=os.environ.get('OPENAI_API_KEY'))))
    run(codebase)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")

