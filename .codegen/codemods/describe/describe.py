import codegen
from codegen import Codebase
import os
from codegen.sdk.codebase.config import CodebaseConfig, Secrets

@codegen.function('describe')
def run(codebase: Codebase):
    explanation_parts = []
    
    print('Total files: ', len(codebase.files()))
    print('Total functions: ', len(codebase.functions))
    print('Total classes: ', len(codebase.classes))

    explanation_parts.append('FUNCTION EXPLANATIONS')
    # Include explanations for each function
    for function in codebase.functions:
        #print('ONE FUNCTION')
        explanation = codebase.ai(
            prompt="Provide a detailed explanation of this function.",
            target=function,
            context={"usages": function.usages, "dependencies": function.dependencies}
        )
        print(explanation)
        explanation_parts.append(explanation)
    explanation_parts.append('CLASS EXPLANATIONS')
    # Include explanations for each class
    for cls in codebase.classes:
        #print('ONE CLASS')
        explanation = codebase.ai(
            prompt="Provide a detailed explanation of this class.",
            target=cls,
            context={"usages": cls.usages, "dependencies": cls.dependencies}
        )
        print(explanation)
        explanation_parts.append(explanation)

    #Include explanations for each file's imports
    explanation_parts.append('FILE EXPLANATIONS')
    for file in codebase.files():
        #print('ONE FILE')
        explanation = codebase.ai(
            prompt="Explain in detail this file and what it does (its features)",
            target=file
        )
        print(explanation,)
        explanation_parts.append(explanation)

    # Write all explanations to output.txt
    with open("output.txt", "w") as f:
        f.write('\n\n'.join(explanation_parts))

    # Commit changes to the codebase
    codebase.commit()


if __name__ == "__main__":
    print('Parsing codebase...')
    repo = 'KevinZWong/ConGen'
    codebase = Codebase.from_repo(repo,config=CodebaseConfig(
        secrets=Secrets(
            openai_key=os.environ.get('OPENAI_API_KEY'))))
    run(codebase)
