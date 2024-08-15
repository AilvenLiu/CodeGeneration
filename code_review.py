import os
import platform
import shutil
from openai import OpenAI
import argparse

# 获取系统和处理器信息
def get_system_info():
    return {
        "system": platform.system(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0]
    }

# 获取项目的详细信息，包括结构树、CMakeLists.txt 和代码内容
def get_project_data(root_dir):
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

    return project_structure, cmake_files, code_files

# 生成详细的 prompt，帮助 GPT-4 理解项目结构和代码之间的关系
def generate_prompts(system_info, project_structure, cmake_files, code_files):
    prompts = []

    # 项目描述
    project_description = "This project is a C++ based system designed for [insert purpose]. The project contains multiple modules that interact with each other. Your goal is to analyze and optimize the project structure, build configuration, and source code files."

    # 项目结构分析 prompt
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

    # 代码分析 prompt
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

    return prompts

# 与 GPT-4 交互，获取优化建议
def analyze_with_chatgpt(client, prompts, model="deepseek-coder", max_tokens=2048, stream=True):
    results = []

    for prompt in prompts:
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

        # 如果启用流式输出，逐步收集结果
        if stream:
            collected_result = ""
            for chunk in response:
                collected_result += chunk.choices[0].delta.get("content", "")
            results.append(collected_result.strip())
        else:
            results.append(response.choices[0].message.content.strip())
    
    return results

# 创建新项目路径，保留原项目结构，并将优化后的文件保存到新路径
def create_new_project(root_dir, new_root_dir, code_files, optimized_code_files):
    if not os.path.exists(new_root_dir):
        os.makedirs(new_root_dir)

    for rel_path, filenames in code_files.items():
        new_dir = os.path.join(new_root_dir, rel_path)
        os.makedirs(new_dir, exist_ok=True)

        for filename in filenames:
            original_path = os.path.join(root_dir, rel_path, filename)
            new_path = os.path.join(new_dir, filename)

            if original_path in optimized_code_files:
                with open(new_path, 'w') as f:
                    f.write(optimized_code_files[original_path])
            else:
                shutil.copy2(original_path, new_path)

# 主程序入口
def main(root_dir, new_root_dir):
    system_info = get_system_info()
    project_structure, cmake_files, code_files = get_project_data(root_dir)

    client = OpenAI(api_key="sk-37dd1918001f439a914090d190194753", base_url="https://api.deepseek.com")
    prompts = generate_prompts(system_info, project_structure, cmake_files, code_files)
    results = analyze_with_chatgpt(client, prompts)

    # 解析优化后的代码
    optimized_code_files = {}
    for filepath, result in zip(code_files.keys(), results[1:]):  # 跳过第一个结果（CMakeLists.txt 的结果）
        optimized_code_files[filepath] = result

    # 创建新项目路径并保存优化后的文件
    create_new_project(root_dir, new_root_dir, project_structure, optimized_code_files)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="基于大模型的 C++ 代码审查和优化程序")
    parser.add_argument('--project_dir', type=str, required=True, help='C++ 项目的根目录')
    parser.add_argument('--new_project_dir', type=str, required=True, help='保存优化后的新项目路径')
    args = parser.parse_args()
    
    main(args.project_dir, args.new_project_dir)