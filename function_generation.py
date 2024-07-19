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

def generate_tree_prompt(parsed_messages):
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

def generate_cpp_prompt(parsed_messages):
    prompts = []
    for message, fields in parsed_messages.items():
        prompt = f"Generate a C++ function to prepare an instance of the protobuf message '{message}' with the following fields:\n"
        for field_type, field_name in fields:
            prompt += f"- {field_type} {field_name}\n"
        prompt += """
The function should:
- Create a shared pointer for the message.
- Set values for each field with appropriate placeholder values.
- Return true if the preparation is successful.

The C++ function should follow this structure:
```cpp
inline bool Prepare{message}(std::shared_ptr<nio::ad::messages::{message}>& message_ptr) {
    // Initialize message fields
    // Example:
    // message_ptr->set_field_name(value);
    return true;
}
```
"""
        prompts.append(prompt)
    return prompts

def get_cpp_function_from_openai(prompt, client):
    response = client.chat.completions.create(
        model="deepseek-coder",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048
    )
    return response.choices[0].message.content.strip()

def main(folder_path, client, output_trees_path, output_functions_path):
    parsed_messages = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.proto'):
                file_path = os.path.join(root, file)
                parsed_messages.update(parse_proto_file(file_path))
    
    # Step 1: Generate and save message trees
    tree_prompts = generate_tree_prompt(parsed_messages)
    with open(output_trees_path, 'w') as trees_file:
        for prompt in tree_prompts:
            tree = get_tree_from_openai(prompt, client)
            trees_file.write(tree + "\n\n")

    # Step 2: Generate and save C++ preparation functions
    cpp_prompts = generate_cpp_prompt(parsed_messages)
    with open(output_functions_path, 'w') as functions_file:
        for prompt in cpp_prompts:
            cpp_function = get_cpp_function_from_openai(prompt, client)
            functions_file.write(cpp_function + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate message trees and C++ functions for protobuf message preparation.")
    parser.add_argument('--key', type=str, default='sk-37dd1918001f439a914090d190194753', help='Your OpenAI API key.')
    parser.add_argument('--base_url', type=str, default='https://api.deepseek.com', help='Base URL for the OpenAI API.')
    parser.add_argument('--message_folder', type=str, default='./mazu_messages/common/dlb', help='Path to the folder containing protobuf files.')
    parser.add_argument('--output_trees_path', type=str, default='./message_tree.txt', help='Path to save the generated message trees.')
    parser.add_argument('--output_functions_path', type=str, default='./data_prepare.hpp', help='Path to save the generated C++ functions.')
    args = parser.parse_args()

    api_key = args.key
    base_url = args.base_url
    folder = args.message_folder
    output_trees_path = args.output_trees_path
    output_functions_path = args.output_functions_path

    client = OpenAI(api_key=api_key, base_url=base_url)
    main(folder, client, output_trees_path, output_functions_path)