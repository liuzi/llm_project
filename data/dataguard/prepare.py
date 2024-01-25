import os
import json
import re
import pandas as pd
from docx2python import docx2python
import uuid
from data.dataguard.prompt_templates import prompts


## preprocess raw data file into json format, give each question a uuid
def preprocess_datafile(input_folder,datafile):
  json_objects=[]

  with docx2python(f'{workdir}/{datafile}.docx','r') as docx_content:
    questions = [s.strip() for s in re.split(r'\n\d+\)\t', docx_content.text)]
    docx_content.close()

  with open(f'{input_folder}/{datafile}_context.txt','w+') as text_file:
    text_file.write(questions[0])
    text_file.close()

  ## transform into json file
  for question in questions[1:]:
    qjson={}
    q,oa=question.split('\n',maxsplit=1)
    qjson["question"]=q.strip()
    o,a=oa.split(r'答案：')
    qjson['cop']=ord(a.strip().lower())-ord('a')+1
    options=[re.sub(r'\n|\t',' ',option).strip() for option in
            re.split(r'\s*([A-D])[\),.]',o) if len(option)][1::2]

    qjson={**qjson,\
           **{f'op{chr(ord("a")+i)}':options[i] for i in range(len(options))}}
    qjson_suffix={
      "subject_name":"Database",
      "topic_name":"Construction related to Oracle database's Data Guard Physical Standby (physical standby database) and its fault handling",
      "id":str(uuid.uuid4()),
      "choice_type":"single"
    }
    qjson={**qjson,**qjson_suffix}
    json_objects.append(qjson)

    with open(f"{input_folder}/{datafile}.json", "w+",encoding="utf-8") as jsonfile:
      json.dump(json_objects, jsonfile, ensure_ascii=False, indent=4)
      jsonfile.close()


## format dataframe into question prompt, with or without answer
def generate_prompt(x,prompt_template,user_inst='',include_answer=2):
    alpha_nums=['A','B','C','D']
    answer = f'{alpha_nums[x["cop"]-1]}'
    # answer = f"""{alpha_nums[x['cop']-1]}. """+\
        #   x[f"""op{chr(ord('a')+x['cop']-1)}"""]

    options=""
    for alpha_num, option in zip(
        alpha_nums,[x['opa'], x['opb'], x['opc'], x['opd']]
    ):
      if option is not None:
        options += f'{alpha_num}. {option}\n'

    # values=[x['question'], options] 
    question_prompt = prompt_template.format(x['question'], options)+user_inst

    if not include_answer:
      return question_prompt
    elif include_answer==1:
      return answer
    else:
      return pd.Series([question_prompt, answer])

## global variables
datafile='Dataguard61'
workdir=os.path.dirname(__file__)
## note: file '标准答案' has been renamed as 'Dataguard61'
input_folder=os.path.join(workdir,'input')
output_folder=os.path.join(workdir,'output')


## !!! Very important step
### move Dataguard61.docx to the same folder of this script file
if not os.path.exists(input_folder):
    os.makedirs(input_folder)
if not os.path.exists(output_folder):
    os.makedirs(output_folder)  
## call function for processing data for the first time
datapath = f"{input_folder}/{datafile}.json"
if not os.path.exists(datapath):
   preprocess_datafile(input_folder,datafile)

## creating prompt files
def format_prompts(company='mistral',version='0'):
    with open(datapath, "r", encoding="utf-8") as f:
        all_df = pd.read_json(f)
        f.close()

    prompt_template, user_inst= "", ""

    for prompt_record in prompts:
       if prompt_record["company"]==company and \
        prompt_record["version"]==version:
          prompt_template = prompt_record["user_prompt"]
          user_inst = prompt_record["user_inst"]

    # context = open(f'{input_folder}/{datafile}_context.txt','r',encoding='utf-8').readline().rstrip()
    prompt_df = all_df[['id']].copy()
    prompt_df[['question_prompt','answer']]=all_df.apply(
        generate_prompt,args=(prompt_template,user_inst,2,),axis=1)

    with open(f'{input_folder}/{company}{version}_prompt.json', 'w+', encoding='utf-8') as prompt_file:
        json.dump(prompt_df.to_dict('records'), prompt_file, ensure_ascii=False, indent=4)
        prompt_file.close()

    return prompt_df

def get_prompts(company='mistral',version='0'):
   prompt_file_path = f'{input_folder}/{company}{version}_prompt.json'

   if os.path.exists(prompt_file_path):
      prompt_df = pd.read_json(prompt_file_path,encoding="utf-8")
   else:
      prompt_df = format_prompts(company,version)

   return prompt_df
          
def get_context(context_id=0):
    context=""
    with open(f'{input_folder}/{datafile}_context.txt', \
            'r',encoding='utf-8') as context_file:
        for i, line in enumerate(context_file):
            if i == context_id:
                context = line
                break
        context_file.close()
    return context
    
