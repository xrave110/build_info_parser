import re
import os
import json

INPUT_JSON_PATH = os.getcwd() + os.sep + "json"

def create_directory(path):
    """
    Creates a directory and any necessary parent directories.

    Args:
        path (str): The path of the directory to create.
    """
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{path}' created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")

def write_dict_to_json(dictionary, file_path):
    """
    Writes a dictionary to a JSON file.

    Args:
        dictionary (dict): The dictionary to write to the JSON file.
        file_path (str): The path of the JSON file to write to.
    """
    try:
        with open(file_path, 'w') as json_file:
            json.dump(dictionary, json_file, indent=4)
        print(f"Dictionary successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def load_json_to_dict(file_path):
    """Loads a JSON file into a Python dictionary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file at {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

def find_imports(file_path):
    """Extracts all imported file names from a Solidity file."""
    import_pattern = re.compile(r'import\s+(?:\{.*?\}\s+from\s+)?["\'](.+?)["\'];')
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    imports = import_pattern.findall(content)
    return imports

def parse_solidity_files(directory):
    """Parses all Solidity files in the given directory to find import statements."""
    imports_dict = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.sol'):
                file_path = os.path.join(root, file)
                imports = find_imports(file_path)
                imports_dict[file_path] = imports

    return imports_dict

def remove_part_from_path(path, part_to_remove):
    """Removes a specified part from the given path."""
    # Split the path into parts
    path_parts = path.split(os.sep)
    tmp_path_parts = path.split(os.sep)
    
    # Remove the specified part if it exists in the path
    # print("Parthparts: ",path_parts)
    for part in tmp_path_parts:
        # print("PART", part)
        if part_to_remove == part:
            path_parts.remove(part_to_remove)
    
    # Reconstruct the path without the specified part
    new_path = os.sep.join(path_parts)
    
    return new_path

def parse_solidity_outs(directory, imports_dict):
    """Parses all Solidity files in the given directory to find import statements."""
    build_info_path = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                # print("Root:", root)
                # print("File:", file)
                file_path = os.path.join(root, file)
                try:
                    build_info_path = load_json_to_dict(file_path)["buildInfo"]
                except:
                    continue
                # print(build_info)
                root_path = remove_part_from_path(directory, "src")
                build_info_path = remove_part_from_path(build_info_path, "..")
                # print("root_path", root_path)
                # print("build_info", build_info)
                path_to_open = os.sep.join([root_path,build_info_path])
                print("CONTRACT", root)
                build_info_inputs = load_json_to_dict(path_to_open)["input"]
                getInputsForContract(build_info_inputs, imports_dict, root)

def getInputsForContract(build_info_inputs, imports_dict, contract):
    inputJson = {}
    inputSources = {}
    contents_list = []
    inputJson["language"] = (build_info_inputs["language"])

    for element in imports_dict.keys():
        
        if(element.split("/")[-1] in contract):
            print("Element {} is in {}".format(element.split("/")[-1], contract))
            for fileImported in imports_dict[element]:
                print("\tFile imported ", fileImported.split("/")[-1])
                contents_list.append(fileImported.split("/")[-1])
            contents_list.append(element.split("/")[-1])
    print("CONTENT DICT: ", contents_list)
    for content_info in build_info_inputs["sources"].keys():
        for content in contents_list:
            if content in content_info:
                inputSources[content_info] = (build_info_inputs["sources"][content_info])
                print("Updating source: ", content_info)
    inputJson["sources"] = inputSources
    inputJson["settings"] = (build_info_inputs["settings"])
    # print("INPUUT JSON: ", inputJson)
    path_to_save = INPUT_JSON_PATH + os.sep + contract.split(os.sep)[-1].split(".")[0] + ".json"
    print("PATH_TO_SAVE:", path_to_save)
    
    write_dict_to_json(inputJson, path_to_save)


def main():
    # Directory containing Solidity files
    cwd = os.getcwd()
    contracts_dir = '{}/src'.format(cwd)
    out_dir = '{}/artifacts/src'.format(cwd)
    
    print(contracts_dir)
    print(out_dir)

    # Parse the directory and get imports
    imports_dict = parse_solidity_files(contracts_dir)
    print("Imported". format(imports_dict))
    
    # Print the results
    print("ITEMS IMPO ", imports_dict)
    for file_path, imports in imports_dict.items():
        print(f'File: {file_path}')
        for imp in imports:
            print(f'  Import: {imp}')

    create_directory(INPUT_JSON_PATH)

    parse_solidity_outs(out_dir, imports_dict)

if __name__ == '__main__':
    main()
