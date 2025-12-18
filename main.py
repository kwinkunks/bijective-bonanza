import subprocess
import random

import pandas as pd
from jinja2 import Environment, FileSystemLoader


random.seed(42)

def prepare_questions(df):
    questions = []
    solutions = []
    
    for index, row in df.iterrows():
        domain = row['domain']
        domain_members = row['domain_members'].split(',')
        codomain = row['codomain']
        codomain_members = row['codomain_members'].split(',')
        
        shuffled_codomain = codomain_members[:]
        random.shuffle(shuffled_codomain)
        
        # Store the solution as the order of indices in the shuffled codomain
        solution = ''.join(chr(65 + shuffled_codomain.index(member)) for member in codomain_members)
        solutions.append(f"{index + 1}. {solution}")
        
        # Zip domain_members with shuffled_codomain 
        domain_zipped = list(zip("VWXYZ", domain_members))
        codomain_zipped = list(zip("ABCDE", shuffled_codomain))
        
        questions.append({
            'number': index + 1,
            'domain': domain,
            'domain_members': domain_zipped,  # pass zipped list
            'codomain': codomain,
            'shuffled_codomain': codomain_zipped,  # pass zipped list
            'original_codomain': codomain_members,
            'domain_and_codomain': list(zip("VWXYZ", domain_members, "ABCDE", shuffled_codomain))
        })
        
    return questions, solutions

def render_html(questions, solutions, output_html, template_file):
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template(template_file)
    
    # Render quiz page
    with open(output_html, 'w') as f:
        f.write(template.render(questions=questions))
        
    # Render solution page (simple text format)
    with open('solutions.txt', 'w') as f:

        for s, q in zip(solutions, questions):
            f.write(s + '\n')
            for (_, d), c in zip(q['domain_members'], q['original_codomain']):
                f.write(f" {d} -> {c}\n")
            f.write('\n')



# Convert HTML to PDF using Pandoc
def convert_to_pdf(input_html, output_pdf):
    # Call Pandoc as a subprocess
    subprocess.run(['pandoc', input_html, '-o', output_pdf], check=True)

if __name__ == '__main__':

    import sys
    sheet = 'Sheet1' if len(sys.argv) == 1 else sys.argv[1]

    key = '1c2qJaO8kpTyOc49NXZJ1G3L3KXABWvfPQ6Brh5cxsYA'
    url = f'https://docs.google.com/spreadsheets/d/{key}/gviz/tq?tqx=out:csv&sheet={sheet}'

    df = pd.read_csv(url)
    questions, solutions = prepare_questions(df)
    
    render_html(questions, solutions, 'quiz.html', 'quiz_template.html')
    
    # convert_to_pdf('quiz.html', 'quiz.pdf')
    # print("Quiz PDF generated: quiz.pdf")
    # print("Solution file generated: solutions.txt")
