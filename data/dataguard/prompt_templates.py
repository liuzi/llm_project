prompts=[
    {
        "company": "general",
        "version": "0",
        "date": "2024-01-19",
        "user_prompt": """
    Question:
    {}
    Options:
    {}
    [INST] Solve this Dataguard Physical Standby MCQ exam and provide the correct option.[/INST]

    Answer: 
""",
        "user_inst":""
    },
    {
        "company": "mistral",
        "version": "0",
        "date": "2024-01-23",
        "user_prompt": """
这里是问题:
{}
这里是备选答案:
{}
    [INST] 这是一道单选题，包含多个备选答案，其中只有一个答案是正确的。请按“答案：X \n 解释：<解释> ”的格式输出你的答案。[/INST]
""",
        "user_inst":""
    },
    {
        "company": "mistral",
        "version": "1",
        "date": "2024-01-24",
        "user_prompt": """
这里是问题:
{}
这里是备选答案:
{}
""",
        "user_inst":"""[INST] 这是一道单选题，包含多个备选答案，其中只有一个答案是正确的。
你只能以JSON object的格式回答，比如{"答案": <[ABCD]>, "解释":<解释>}。[/INST]
"""
    },
    {
        "company": "mistral",
        "version": "2",
        "date": "2024-01-24",
        "user_prompt": """
这里是问题:
{}
这里是备选答案:
{}
""",
        "user_inst":"""[INST] 这是一道单选题，包含多个备选答案，其中只有一个答案是正确的。
你只能以JSON object的格式回答，比如{"答案": "(?P<答案>[ABCD])", "解释":"(?P<解释>.+)"}。[/INST]
"""
    },
    {
        "company": "openai",
        "version": "0",
        "date": "2024-01-23",
        "user_prompt": """
    这里是问题:
    {}
    这里是备选答案:
    {}
    [INST] 这是一道单选题，包含多个备选答案，其中只有一个答案是正确的。请按“答案：X \n 解释：<解释> ”的格式输出你的答案。[/INST]
""",
        "user_inst":""
    },
    {
        "company": "openai",
        "version": "2",
        "date": "2024-01-25",
        "user_prompt": """
这里是问题:
{}
这里是备选答案:
{}
""",
        "user_inst":"""[INST] 这是一道单选题，包含多个备选答案，其中只有一个答案是正确的。
你只能以JSON object的格式回答，比如{"答案": "(?P<答案>[ABCD])", "解释":"(?P<解释>.+)"}。[/INST]
"""
    }
    
]