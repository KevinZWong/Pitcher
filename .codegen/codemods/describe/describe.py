import codegen
from codegen import Codebase
import os
from codegen.sdk.codebase.config import CodebaseConfig, Secrets
#import subprocesses
import concurrent.futures
global explanation_parts 

#explanation_parts = []


def analyze_functions():
    explanations = []
    explanations.append('FUNCTION EXPLANATIONS')
    i = len(codebase.functions)
    # Include explanations for each function
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                codebase.ai,
                prompt="Provide a detailed explanation of this function.",
                target=function,
                context={"usages": function.usages, "dependencies": function.dependencies}
            ) for function in codebase.functions
        ]
        for future in concurrent.futures.as_completed(futures):
            explanations.append(future.result())
    return  '\n'.join(explanations)
def analyze_classes():
    explanations = []
    explanations.append('CLASS EXPLANATIONS')
    i = len(codebase.classes)
    # Include explanations for each class
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                codebase.ai,
                prompt="Provide a detailed explanation of this class.",
                target=cls,
                context={"usages": cls.usages, "dependencies": cls.dependencies}
            ) for cls in codebase.classes
        ]
        for future in concurrent.futures.as_completed(futures):
            explanations.append(future.result())
    return  '\n'.join(explanations)
def analyze_files():
    explanations = []
    explanations.append('FILE EXPLANATIONS')
    i = len(codebase.files)
    # Include files for each class
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                codebase.ai,
                prompt="Explain in detail this file and what it does (its features)",
                target=file,
            ) for file in codebase.files
        ]
        for future in concurrent.futures.as_completed(futures):
            explanations.append(future.result())
    return '\n'.join(explanations)

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
            explanation_parts.append(future.result())

    # Write all explanations to output.txt
    with open("output.txt", "w") as f:
        f.write('\n'.join(explanation_parts))

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