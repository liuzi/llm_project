import os
import configparser
import re
import json

class Rest_API():

    def __init__(self, prompt_df, context, \
                 promptcol="question_prompt",answercol="answer") :
        self.config = configparser.ConfigParser()
        self.config.read(f'{os.path.basename(__file__)[:-3]}.ini')
        self.promptcol, self.answercol = promptcol, answercol
        self.prompt_df = prompt_df[["id",promptcol,answercol]]
        self.context = context
        self.clients = {"mistral": self.mistral_client,
                        "openai": self.openai_client} 


    # def mistral_api(self, company="mistral"):
    #     from mistralai.client import MistralClient
    #     from mistralai.models.chat_completion import ChatMessage

    #     # company='mistral'
    #     section_data=dict(self.config.items(company))

    #     sys_msg = ChatMessage(role="system", content=self.context)
    #         #  for prompt in self.prompt_df[self.promptcol]]
    #     client = MistralClient(api_key=section_data["api_key"], timeout=int(section_data["timeout"]))
    #     # client = MistralClient(api_key=section_data["api_key"]),timeout=int(section_data["timeout"]))
    #     params={"model":f'{company}-{section_data["model"]}',
    #         "temperature":float(section_data["temperature"]),
    #         "top_p":float(section_data["top_p"]),
    #         "max_tokens":int(section_data["max_tokens"])}
 
    #     def call_client(row, jsonlist):
    #         nonlocal correct_count, response_count, total_count
    #         print(f'Solved question {row["id"]}, already solved {response_count} questions, {correct_count} are correct')
    #         params["messages"]=[sys_msg, \
    #                             ChatMessage(role="user", content=row[self.promptcol])]
    #         chat_response = self.format_response(client.chat(**params))
    #         jsonlist.append({**{'id':row['id'],'answer':row['answer']},\
    #                          **chat_response})
            
    #         if chat_response['pred_answer']:
    #             response_count+=1
    #             if chat_response['pred_answer']==row['answer']:
    #                 correct_count+=1
    #         total_count+=1
        
    #     jsonlist=[]
    #     correct_count, response_count, total_count = 0,0,0   
    #     self.prompt_df.apply(call_client, args=(jsonlist,), axis=1)
    #     section_data.pop('api_key')
    #     section_data = {**section_data,
    #         **{'correct_count':correct_count,
    #          'response_count':response_count,
    #          'total_count':total_count,
    #          'accuracy':correct_count*100.0/response_count}}
    #     return jsonlist, section_data


    ## mistral-tiny, mistral-small, mistral-medium
    def mistral_client(self,api_key,timeout,questions):
        from mistralai.client import MistralClient
        from mistralai.models.chat_completion import ChatMessage
        client = MistralClient(api_key=api_key, timeout=timeout)
        sys_msg = ChatMessage(role="system", content=self.context)
        return client.chat, sys_msg, [
            ChatMessage(role="user", content=question) for question in questions
        ]


    # //TODO: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_format_inputs_to_ChatGPT_models.ipynb
    ## gpt-4, gpt-3.5-turbo, 
    def openai_client(self,api_key,timeout,questions):
        from openai import OpenAI
        client = OpenAI(api_key=api_key, timeout=timeout)
        sys_msg = {"role": "system", "content": self.context}
        return client.chat.completions.create, sys_msg, [
            {'role':'user', "content":question} for question in questions
        ]


    def call_api(self, company="mistral"):

        section_data=dict(self.config.items(company))
        client_chat, sys_msg, user_msgs = self.clients[company](
            section_data['api_key'], int(section_data['timeout']),
            self.prompt_df[self.promptcol]
        )
        self.prompt_df['user_msg']=user_msgs
       
        params={"model":section_data["model"],
            "temperature":float(section_data["temperature"]),
            "top_p":float(section_data["top_p"]),
            "max_tokens":int(section_data["max_tokens"])}
 
        def call_client(row, jsonlist):
            nonlocal correct_count, response_count, total_count
            print(f'Solved question {row["id"]}, already solved {response_count} questions, {correct_count} are correct')
            params["messages"]=[sys_msg, row['user_msg']]
            chat_response = self.format_response(client_chat(**params))
            jsonlist.append({**{'id':row['id'],'answer':row['answer']},\
                             **chat_response})
            
            if chat_response['pred_answer']:
                response_count+=1
                if chat_response['pred_answer']==row['answer']:
                    correct_count+=1
            total_count+=1
        
        jsonlist=[]
        correct_count, response_count, total_count = 0,0,0   

        self.prompt_df.apply(call_client, args=(jsonlist,), axis=1)
        section_data.pop('api_key')
        section_data = {**section_data,
            **{'correct_count':correct_count,
             'response_count':response_count,
             'total_count':total_count,
             'accuracy':correct_count*100.0/response_count}}
        return jsonlist, section_data
    

        
    def format_response(self, response):
        response_str = response.choices[0].message.content
        res_dict = {"pred_answer":"","exp":"","response":response_str}
        try:
            response_json = json.loads(response_str)
            if "答题结果" in response_json:
                response_json = response_json["答题结果"]
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            return res_dict

        pred_answer=re.match(\
            r'^([ABCD])',response_json.get("答案","").strip())
        res_dict["pred_answer"]=pred_answer[0] if pred_answer else ""
        res_dict["exp"]=response_json.get("解释","")

        return res_dict


