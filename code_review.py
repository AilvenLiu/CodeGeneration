import os
import platform
import shutil
from openai import OpenAI
import argparse

# 获取系统和处理器信息
def get_system_info():
    system_info = {
        "system": platform.system(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0]
    }
    print(f"System Info: {system_info}")
    return system_info

# 获取项目的详细信息，包括结构树、CMakeLists.txt 和代码内容
def get_project_data(root_dir):
    print("Collecting project data...")
    project_structure = {}
    cmake_files = []
    code_files = {}

    for dirpath, _, filenames in os.walk(root_dir):
        rel_path = os.path.relpath(dirpath, root_dir)
        project_structure[rel_path] = []

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            project_structure[rel_path].append(filename)

            if filename == "CMakeLists.txt":
                with open(filepath, 'r') as f:
                    cmake_files.append((rel_path, f.read()))
            elif filename.endswith(('.cpp', '.h')):
                with open(filepath, 'r') as f:
                    code_files[filepath] = f.read()

    print(f"Collected {len(cmake_files)} CMakeLists.txt files and {len(code_files)} code files.")
    return project_structure, cmake_files, code_files

# 生成详细的 prompt，帮助 GPT-4 理解项目结构和代码之间的关系
def generate_prompts(system_info, project_structure, cmake_files, code_files):
    print("Generating prompts for project analysis...")
    prompts = []

    project_description = "This project is a C++ based system designed for [insert purpose]. The project contains multiple modules that interact with each other. Your goal is to analyze and optimize the project structure, build configuration, and source code files."

    project_structure_prompt = f"""
System Info: {system_info}
You are a C++ project structure and build expert.
{project_description}
The following is the project structure and the associated CMakeLists.txt files.
Analyze the structure, identify potential issues, and suggest improvements for better organization, performance, and maintainability.
"""
    for rel_path, cmake_content in cmake_files:
        project_structure_prompt += f"\nDirectory: {rel_path}\nCMakeLists.txt:\n{cmake_content}\n"
    
    prompts.append(project_structure_prompt)

    for filepath, content in code_files.items():
        module_description = f"File: {filepath}\n"
        dependencies = "\n".join([
            f"- {dep}" for dep in code_files if dep != filepath and os.path.basename(dep) in content
        ])
        
        code_analysis_prompt = f"""
System Info: {system_info}
You are a C++ code quality and performance expert.
The following is a C++ source file from a project designed for {project_description}. Analyze its structure, dependencies, and implementation.
Focus on issues related to performance, memory management, coding style, and modularity. Suggest improvements following C++ best practices.
{module_description}
Dependencies:
{dependencies}
Code:
{content}
"""
        prompts.append(code_analysis_prompt)

    print(f"Generated {len(prompts)} prompts.")
    return prompts

# 与 GPT-4 交互，获取优化建议
def analyze_with_chatgpt(client, prompts, model="deepseek-coder", max_tokens=2048, stream=True, new_root_dir=None):
    for idx, prompt in enumerate(prompts):
        print(f"Sending prompt {idx + 1}/{len(prompts)} to the model...")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert C++ reviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.3,
            stream=stream
        )

        # 逐步收集并写入响应结果
        collected_result = ""
        for chunk in response:
            if "content" in chunk.choices[0].delta:
                collected_result += chunk.choices[0].delta["content"]
                if stream:
                    # 生成对应的文件路径
                    if idx == 0:  # CMakeLists.txt 分析结果
                        output_file = os.path.join(new_root_dir, "optimized_CMakeLists.txt")
                    else:  # 代码文件分析结果
                        output_file = os.path.join(new_root_dir, f"optimized_{os.path.basename(prompts[idx].split('File: ')[-1].splitlines()[0])}")

                    # 将增量内容写入文件
                    with open(output_file, 'a') as f:
                        f.write(collected_result)
                    collected_result = ""

        print(f"Received and saved response for prompt {idx + 1}/{len(prompts)}.")

# 创建新项目路径，保留原项目结构，并将优化后的文件保存到新路径
def create_new_project(root_dir, new_root_dir, code_files):
    print(f"Creating new project directory at: {new_root_dir}")
    if not os.path.exists(new_root_dir):
        os.makedirs(new_root_dir)

    for rel_path, filenames in code_files.items():
        new_dir = os.path.join(new_root_dir, rel_path)
        os.makedirs(new_dir, exist_ok=True)

        for filename in filenames:
            original_path = os.path.join(root_dir, rel_path, filename)
            new_path = os.path.join(new_dir, filename)

            shutil.copy2(original_path, new_path)

    print("New project structure created successfully.")

# 主程序入口
def main(root_dir, new_root_dir):
    system_info = get_system_info()
    project_structure, cmake_files, code_files = get_project_data(root_dir)

    client = OpenAI(api_key="sk-37dd1918001f439a914090d190194753", base_url="https://api.deepseek.com")
    create_new_project(root_dir, new_root_dir, project_structure)
    prompts = generate_prompts(system_info, project_structure, cmake_files, code_files)
    analyze_with_chatgpt(client, prompts, new_root_dir=new_root_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="基于大模型的 C++ 代码审查和优化程序")
    parser.add_argument('--project_dir', type=str, required=True, help='C++ 项目的根目录')
    parser.add_argument('--new_project_dir', type=str, required=True, help='保存优化后的新项目路径')
    args = parser.parse_args()
    
    main(args.project_dir, args.new_project_dir)