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
        prompt = f"Generate a hierarchical tree structure for the protobuf message '{message}' where each node represents a field. Include basic types as leaf nodes. Only generate the tree structure, without explanations. The fields are:\n"
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
        max_tokens=2048,
        stream=True
    )
    full_response = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content'):
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)  # Print in real-time
    print("\n")  # New line after full response
    return full_response

def generate_cpp_prompt(parsed_messages):
    prompts = []
    for message, fields in parsed_messages.items():
        prompt = f"Generate a C++ function to prepare an instance of the protobuf message '{message}' with the following fields. Only generate the function code without explanations:\n"
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
        max_tokens=2048,
        stream=True
    )
    full_response = ""
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content'):
            content = chunk.choices[0].delta.content
            full_response += content
            print(content, end="", flush=True)  # Print in real-time
    print("\n")  # New line after full response
    return full_response

def main(client, folder_path, output_dir):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.proto'):
                file_path = os.path.join(root, file)
                parsed_messages = parse_proto_file(file_path)
                
                tree_prompts = generate_tree_prompt(parsed_messages)
                cpp_prompts = generate_cpp_prompt(parsed_messages)

                # Create individual output files
                tree_file_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_tree.txt")
                cpp_file_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}_functions.cpp")

                with open(tree_file_path, 'w') as tree_file:
                    for prompt in tree_prompts:
                        tree = get_tree_from_openai(prompt, client)
                        tree_file.write(tree + "\n\n")

                with open(cpp_file_path, 'w') as cpp_file:
                    for prompt in cpp_prompts:
                        cpp_function = get_cpp_function_from_openai(prompt, client)
                        cpp_file.write(cpp_function + "\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate message trees and C++ functions for protobuf message preparation.")
    parser.add_argument('--key', type=str, required=True, help='Your OpenAI API key.')
    parser.add_argument('--base_url', type=str, default='https://api.deepseek.com', help='Base URL for the OpenAI API.')
    parser.add_argument('--message_folder', type=str, default='./mazu_messages/common/dlb', help='Path to the folder containing protobuf files.')
    parser.add_argument('--output_folder', type=str, default='./data_prepare_for_dlb', help='Path to save the generated message trees.')
    args = parser.parse_args()

    api_key = args.key
    base_url = args.base_url
    message_folder = args.message_folder
    output_folder = args.output_folder

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    client = OpenAI(api_key=api_key, base_url=base_url)
    main(client, message_folder, output_folder)