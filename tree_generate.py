import os
import re
from openai import OpenAI
import argparse

def parse_proto_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    messages = re.findall(r'message (\w+)\s*{([^}]*)}', content)
    parsed_messages = {}
    for message in messages:
        message_name = message[0]
        fields = re.findall(r'\s*(\w+)\s+(\w+)\s*=\s*\d+;', message[1])
        parsed_messages[message_name] = fields
    return parsed_messages

def generate_prompt(parsed_messages):
    prompts = []
    for message, fields in parsed_messages.items():
        prompt = f"Generate a hierarchical tree structure for the protobuf message '{message}' where each node represents a field. Include basic types as leaf nodes. The fields are:\n"
        for field_type, field_name in fields:
            prompt += f"- {field_type} {field_name}\n"
        prompt += "The tree should clearly show the hierarchy and structure of the message."
        prompts.append(prompt)
    return prompts

def get_tree_from_openai(prompt, client):
    response = client.chat.completions.create(
        model="deepseek-coder",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

def main(folder_path, client):
    parsed_messages = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.proto'):
                file_path = os.path.join(root, file)
                parsed_messages.update(parse_proto_file(file_path))
    prompts = generate_prompt(parsed_messages)

    for prompt in prompts:
        tree = get_tree_from_openai(prompt, client)
        print(tree)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--key', type=str, default='sk-37dd1918001f439a914090d190194753')
    parser.add_argument('--base_url', type=str, default='https://api.deepseek.com')
    parser.add_argument('--message_folder', type=str, default='./mazu_messages/common/dlb')
    args = parser.parse_args()

    api_key = args.key
    base_url = args.base_url
    folder = args.message_folder

    client = OpenAI(api_key=api_key, base_url=base_url)
    main(folder, client)
