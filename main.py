# import sys
import os
import json
import pandas as pd
import datetime
import argparse

from data.dataguard.prepare import get_prompts, get_context, output_folder
from rest_api import Rest_API


def main(args):
    # Your code goes here
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    company, version, context_id = args.company, args.version, args.context_id
    prompt_df = get_prompts(company=company,version=version)
    context = get_context(context_id=context_id)

    res_api = Rest_API(prompt_df=prompt_df,context=context)
    res_jsonlist, params_data = res_api.call_api(company=company)

    result_file_path=f'{output_folder}/{company}_v{version}_c{context_id}_{params_data["response_count"]}_{params_data["accuracy"]:.2f}_{now}.json'
    with open(result_file_path,'w+', encoding='utf-8') as f:
        json.dump(res_jsonlist, f, ensure_ascii=False, indent=4)
        f.close()
    
    params_data={**{"company":company,"version":version,
                    "context_id":context_id,
                    "datetime":now, "output_file":result_file_path},**params_data}
    pd.json_normalize([params_data]).to_csv(\
        f'{output_folder}/params_results.csv', mode='a', 
        header=not os.path.exists(f'{output_folder}/params_results.csv'), 
        index=False)


if __name__ == "__main__":
    # Create an instance of ArgumentParser
    parser = argparse.ArgumentParser(description="Parse arguments for GPT tests")
    parser.add_argument('--company', '-c', \
                        help='company name of GPT, e.g., mistral, openai, huggingface')
    parser.add_argument('--version', '-v', help='version of prompt templates')
    parser.add_argument('--context_id', '-ci', \
                        help='ID (line number) for system prompts, should be 0 for the first time',default='0')
    
    args = parser.parse_args()
    main(args)
# tt = Rest_API(get_prompts(company='mistral',version='2').head(2),get_context(1))
# tt.mistral_api()