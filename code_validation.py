"""
This is a script that verifies that each of the following code standards are met:
    1. Each class should have a header (comment above or docstring below definition)
    2. Each function (in a class or not) should have a header (comment above or docstring below definition)
    3. The maximum number of lines in a python file should be at most 2000 lines long if possible
    4. The maximum number of lines in a function should be at most 40 lines long if possible
    5. The maximum variable length should be at most 20 characters long if possible
    6. The maximum number of characters in a file line should be at most 150 characters if possible
    7. Imports should never use the '*' to import all. You should only import what you need
    8. The python file should have a header explaining what it does
:param argv[1]: The first real arg passed in should be a path to a directory containing python files to parse
:return: The output of the script is a markdown file containing information about the results of this run. 
"""
import sys, os, re, ast

MAX_FILE_LINES = 2000
MAX_LINE_CHARACTERS = 150
MAX_VARIABLE_NAME_LENGTH = 25
MAX_LINES_PER_METHOD = 40

CHECKBOX_OUTLINE = " - [{}] {}\n"


def set_data_for_parsing():
    global template_variables, specific_file_information
    template_variables = {
        "SCRIPT_NAME": "",
        "FILE_HEADER_EXISTS": True,
        "EXCEPTABLE_FILE_SIZE": True,
        "VALID_IMPORTS": True,
        "VALID_LINE_LENGTHS": True,
        "CLASSES_HAVE_HEADERS": True,
        "FUNCTIONS_HAVE_HEADERS": True,
        "VALID_FUNCTION_LENGTHS": True,
        "VALID_VARIABLE_LENGTHS": True,
        "INVALID_IMPORT_CHECKBOXES": "",
        "INVALID_LINE_LENGTH_CHECKBOXES": "",
        "CLASSES_WITHOUT_HEADERS_CHECKBOXES": "",
        "FUNCTIONS_WITHOUT_HEADERS_CHECKBOXES": "",
        "INVALID_FUNCTION_LENGTH_CHECKBOXES": "",
        "INVALID_VARIABLE_LENGTH_CHECKBOXES": "",
    }

    specific_file_information = {
        "INVALID_IMPORTS": None,
        "INVALID_LENGTHY_LINES": None,
        "HEADLESS_CLASSES": None,
        "HEADLESS_FUNCTIONS": None,
        "INVALID_LENGTHY_FUNCTIONS": None,
        "INVALID_LENGTHY_VARIABLES": None,
    }

def check_invalid_imports(file_path, implementation):
    invalid_imports = []
    for line in implementation:
        if line.strip().startswith("import"):
            continue
        from_import_match = re.search(r'from\s(.*)\simport\s', line)
        if from_import_match:
            from_module = from_import_match.groups()[0]
            if 'import *' in line:
                invalid_imports.append(from_module)
    return invalid_imports
    # send_warning("Python file: '{}' is using 'import *' for the following modules: {}. Please only import the modules you need.".format(file_path, invalid_imports))


def has_file_docstring(file_path):
    """This function checks if the python file has a docstring header
    :param file_path: This is the path to the python file
    :return: (True or False) if the function has a docstring header
    """
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    if isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
        return True
    return False

def check_for_file_header(file_path, implementation):
    """This function checks if there is a file header (comment or docstring)
    :param file_path: This is the path to the python file
    :param implementation: This is the array of implementation code lines
    """
    if not implementation[0].strip().startswith('#') and not has_file_docstring(file_path):
        return False
    return True
        # send_warning("Python file: '{}' does not have a file header. Please make one.".format(file_path))

def remove_docstring(source_code):
    """This function removes docstrings from the source code
    :param source_code: An array containing each line of the source code
    :return: A string without any of the docstrings
    """
    return re.sub(r'""".*?"""', '', source_code, flags=re.DOTALL)

def check_module_using_comment_header(implementation, start_line):
    """Check if the current module is using a comment header
    :param implementation: An array containing each line of the source code
    :param start_line: The starting line index of the module definition (where 'def <function_name>():' or 'class <class_name' is located)
    :return: (True or False) depending on if the module has a comment header
    """
    has_comment_header = False
    current_line_index = start_line - 1
    current_line = implementation[start_line - 1]
    while current_line.strip().startswith('#'):
        has_comment_header = True
        current_line_index -= 1
        current_line = implementation[current_line_index]
    return has_comment_header

def check_class_headers(file_path):
    """Checks all the classes in the given file and sees if each of them have headers
    :param file_path: The path to the python file
    """
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    no_header_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            start_line = node.lineno - 1
            has_docstring_header = bool(ast.get_docstring(node))
            has_comment_header = check_module_using_comment_header(code.splitlines(), start_line)
            if not has_docstring_header and not has_comment_header:
                no_header_classes.append(node.name)
    return no_header_classes
    # if no_header_classes != []:
    #     send_warning("Python file: '{}' contains classes that do not have headers. Please make them for these methods: {}".format(file_path, no_header_classes))

def check_functions_headers(file_path):
    """Checks all the functions in the given file and sees if each of them have headers
    :param file_path: The path to the python file
    """
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    no_header_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            if 'def __' in code.splitlines()[start_line]:
                continue
            has_docstring_header = bool(ast.get_docstring(node))
            has_comment_header = check_module_using_comment_header(code.splitlines(), start_line)
            if not has_docstring_header and not has_comment_header:
                no_header_functions.append(node.name)
    return no_header_functions
    # if no_header_functions != []:
    #     send_warning("Python file: '{}' contains methods that do not have headers. Please make them for these methods: {}".format(file_path, no_header_functions))

def check_functions_less_than_40_lines(file_path):
    """Checks all the functions to find which ones have more than 40 lines of code.
    :param file_path: The path to the python file
    """
    with open(file_path, 'r') as file:
        code = file.read()
    tree = ast.parse(code)
    long_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
            function_code = code.splitlines()[start_line:end_line]
            for i, line in zip(range(len(function_code) - 1, -1, -1), reversed(function_code)):
                if line.strip().startswith("#"):
                    function_code.pop(i)
            function_code = remove_docstring('\n'.join(function_code))
            if function_code.count('\n') > 40:
                long_functions.append(node.name)
    return long_functions
    # if long_functions != []:
    #     send_warning("Python file: '{}' contains methods that have more than {} lines. Check {} to see if they can be reduced.".format(file_path, MAX_LINES_PER_METHOD, long_functions))

def send_warning(message):
    """Prints a warning message"""
    print("WARNING: {}".format(message))

def check_implementation_variable_length(file_path, implementation_lines):
    """Checks all the variables in the file to see their word length
    :param file_path: The path to the python file
    :param implementation_lines: An array containing each of the python file source code lines
    """
    line_numbers = []
    for i, line in enumerate(implementation_lines):
        match = re.search(r'\b(\w+)\s*=', line)
        if match:
            words = match.groups()
            for word in words:
                if word.upper() == word:
                    continue
                if len(word) > MAX_VARIABLE_NAME_LENGTH:
                    line_numbers.append(i + 1)
    return line_numbers
    # if line_numbers != []:
    #     send_warning("Python file: '{}' contains variables that have more than {} characters. Check line numbers {} too see if they can be reduced.".format(file_path, MAX_VARIABLE_NAME_LENGTH, line_numbers))

def check_implementation_line_length(file_path, implementation_lines):
    """Checks each line in the code and sees if any of the lines are too long
    :param file_path: The path to the python file
    :param implementation_lines: An array containing each of the python file source code lines
    """
    line_numbers = []
    for i, line in enumerate(implementation_lines):
        if line.strip().startswith('#'):
            continue
        line = re.sub(r'#.*', '', line)
        if len(line) > MAX_LINE_CHARACTERS:
            line_numbers.append(i + 1)
    return line_numbers
    # if line_numbers != []:
    #     send_warning("Python file: '{}' contains lines that have more than {} characters. Check line numbers {} too see if they can be reduced.".format(file_path, MAX_LINE_CHARACTERS, line_numbers))

def check_file_too_large(file_path, implementation_lines):
    """Checks if the file is too long (more than a certain number of lines)
    :param file_path: The path to the python file
    :param implementation_lines: An array containing each of the python file source code lines
    """
    return len(implementation_lines) <= MAX_FILE_LINES
        # send_warning("Python file: '{}' has over {} lines. It might be worth splitting this file up into multiple modules.".format(file_path, MAX_FILE_LINES))

def generate_validation_output():
    for line_number in specific_file_information["INVALID_LENGTHY_LINES"]:
        template_variables["VALID_LINE_LENGTHS"] = False
        line_number_string = "Line Number - {}".format(line_number)
        template_variables["INVALID_LINE_LENGTH_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", line_number_string)

    for line_number in specific_file_information["INVALID_LENGTHY_VARIABLES"]:
        template_variables["VALID_VARIABLE_LENGTHS"] = False
        line_number_string = "Line Number - {}".format(line_number)
        template_variables["INVALID_VARIABLE_LENGTH_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", line_number_string)

    for function_name in specific_file_information["INVALID_LENGTHY_FUNCTIONS"]:
        template_variables["VALID_FUNCTION_LENGTHS"] = False
        template_variables["INVALID_FUNCTION_LENGTH_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", function_name)

    for function_name in specific_file_information["HEADLESS_FUNCTIONS"]:
        template_variables["FUNCTIONS_HAVE_HEADERS"] = False
        template_variables["FUNCTIONS_WITHOUT_HEADERS_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", function_name)

    for class_name in specific_file_information["HEADLESS_CLASSES"]:
        template_variables["CLASSES_HAVE_HEADERS"] = False
        template_variables["CLASSES_WITHOUT_HEADERS_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", class_name)
    
    for import_package in specific_file_information["INVALID_IMPORTS"]:
        template_variables["VALID_IMPORTS"] = False
        template_variables["INVALID_IMPORT_CHECKBOXES"] += CHECKBOX_OUTLINE.format(" ", import_package)

def convert_bool_to_checkbox_value(value):
    if value:
        return "X"
    else:
        return " "

def write_validation_output():
    directory = os.path.dirname(__file__)
    path_to_template = directory + "/code_validation_output_template.md"
    with open(path_to_template, 'r') as template:
        template_lines = template.readlines()
    template_lines = "".join(template_lines)
    for variable, replacement in template_variables.items():
        if type(replacement) == bool:
            replacement = convert_bool_to_checkbox_value(replacement)
        if replacement == "":
            replacement = "None :)"
        template_lines = template_lines.replace('{{' + variable + '}}', replacement)

    template_lines = template_lines.replace('{{' + "MAX_FILE_LINES" + '}}', str(MAX_FILE_LINES))
    template_lines = template_lines.replace('{{' + "MAX_LINE_CHARACTERS" + '}}', str(MAX_LINE_CHARACTERS))
    template_lines = template_lines.replace('{{' + "MAX_VARIABLE_NAME_LENGTH" + '}}', str(MAX_VARIABLE_NAME_LENGTH))
    template_lines = template_lines.replace('{{' + "MAX_LINES_PER_METHOD" + '}}', str(MAX_LINES_PER_METHOD))

    path_to_output_storage = directory + "/code_validation_output/"
    if not os.path.exists(path_to_output_storage):
        os.mkdir(path_to_output_storage)
    path_to_output_md_file = path_to_output_storage + "/{}_validation_output.md".format(template_variables["SCRIPT_NAME"])
    with open(path_to_output_md_file, 'w') as output_file:
        output_file.write(template_lines)

def parse_python_file(file_path):
    """Parses a specific python file and gets the errors
    :param file_path: The path to the python file
    """
    set_data_for_parsing()
    with open(file_path, 'r') as python_file:
        lines = python_file.readlines()
        if len(lines) == 0:
            return
        template_variables["SCRIPT_NAME"] = os.path.basename(file_path)
        template_variables["FILE_HEADER_EXISTS"] = check_for_file_header(file_path, lines)
        template_variables["EXCEPTABLE_FILE_SIZE"] = check_file_too_large(file_path, lines)
        specific_file_information["INVALID_LENGTHY_LINES"] = check_implementation_line_length(file_path, lines)
        specific_file_information["INVALID_LENGTHY_VARIABLES"] = check_implementation_variable_length(file_path, lines)
        specific_file_information["INVALID_LENGTHY_FUNCTIONS"] = check_functions_less_than_40_lines(file_path)
        specific_file_information["HEADLESS_FUNCTIONS"] = check_functions_headers(file_path)
        specific_file_information["HEADLESS_CLASSES"] = check_class_headers(file_path)
        specific_file_information["INVALID_IMPORTS"] = check_invalid_imports(file_path, lines)
        generate_validation_output()
        write_validation_output()
        
def get_all_python_files(directory):
    """Gets all the python files in a directory (recursively)
    :param directory: The path to the directory we are searching
    :return: A list of python file paths
    """
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def parse_directory(directory):
    """Parses a directory containing python files and gets all the source code standards issues
    :param directory: The path to the directory we are searching
    """
    python_files = get_all_python_files(directory)
    for python_file in python_files:
        parse_python_file(python_file)
    

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        raise Exception("Please provide a path")
    python_files_path = args[0]
    parse_directory(python_files_path)
    # parse_python_file('Z:\\bug-73799-R4_4_ADC_Verification_Bugs\\Verification\\SATS_Scripts\\API\\utilities\\ADC_API.py')
    # parse_python_file('C:\\Users\\d.gauger\\Code Validation\\PyDocsaurus.py')
    # parse_python_file('C:\\Users\\d.gauger\\Code Validation\\code_validation.py')
