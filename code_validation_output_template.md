# **{{SCRIPT_NAME}} Code Validation Output**
## **Entire File Criteria**
- [{{FILE_HEADER_EXISTS}}] Has file header
- [{{EXCEPTABLE_FILE_SIZE}}] File is less than {{MAX_FILE_LINES}} lines long
- [{{VALID_IMPORTS}}] Imports don't use 'import *' for other modules
- [{{VALID_LINE_LENGTHS}}] All lines in the file are less than {{MAX_LINE_CHARACTERS}} characters long (excluding comments)
- [{{CLASSES_HAVE_HEADERS}}] All classes have headers
- [{{FUNCTIONS_HAVE_HEADERS}}] All functions have headers
- [{{VALID_FUNCTION_LENGTHS}}] All functions are less than {{MAX_LINES_PER_METHOD}} lines long (excluding comments)
- [{{VALID_VARIABLE_LENGTHS}}] All non-capitalized variable names are less than {{MAX_VARIABLE_NAME_LENGTH}} characters long

## **Specific Information**
### **Invalid Import Modules**
{{INVALID_IMPORT_CHECKBOXES}}
### **Lines with more than {{MAX_LINE_CHARACTERS}} characters:**
{{INVALID_LINE_LENGTH_CHECKBOXES}}
### **Classes without headers**
{{CLASSES_WITHOUT_HEADERS_CHECKBOXES}}
### **Functions without headers**
{{FUNCTIONS_WITHOUT_HEADERS_CHECKBOXES}}
### **Functions that have more than {{MAX_LINES_PER_METHOD}} lines**
{{INVALID_FUNCTION_LENGTH_CHECKBOXES}}
### **Lines with variables that have more than {{MAX_VARIABLE_NAME_LENGTH}} characters**
{{INVALID_VARIABLE_LENGTH_CHECKBOXES}}