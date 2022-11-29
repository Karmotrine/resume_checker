from email.policy import default
import dearpygui.dearpygui as dpg
import ctypes
from tika import parser
from functions import *

dpg.create_context()
dpg.create_viewport(title='Resume Checker', width=560, height=740, x_pos=620, y_pos=84, resizable=False)
dpg.setup_dearpygui()
dpg.set_global_font_scale(1.22)
#ctypes.windll.shcore.SetProcessDpiAwareness(3)
file_path=""
constraints = []
bias = "Strong (>95%)"


def clear():
    global constraints, ratio_data
    constraints =  []
    ratio_data = {}
    dpg.set_value("constraint_gui", ", ".join(constraints))
    dpg.delete_item("console", children_only=True)
    dpg.delete_item("result-window", children_only=True)
    dpg.delete_item("accuracy-window", children_only=True)
    dpg.add_text("Resume Checker v.0.1", parent="console")
    dpg.add_text("BSCS 2-3 | DAA Group 1", parent="console")
    print("Console and panels cleared")

def add_constraint():
    global constraints
    str = dpg.get_value("keyword_stream")
    if (len(str) > 1 and len(str.split()) == 1):
        constraints.append(str)
        print("Added {} to constraints".format(str) )
        dpg.set_value("keyword_stream","")
        dpg.set_value("constraint_gui", ", ".join(constraints))
    elif (len(str.split()) > 1):
        dpg.add_text("[ERROR] | Keyword must be a single word.", parent="console", color=(255,0,0))
        return
    else:
        dpg.add_text("[ERROR] | Keyword must be greater than 1 character.", parent="console", color=(255,0,0))
        return

def parse_file(path):
    # Biases: "Strong (>95%)", "Medium (>90%)", "Weak (>80%)"
    # Default is Strong (>95%)
    bias_values = {"excellent": 95, "good": 85,"fair": 80} 
    if (bias == "Strong (>80%)"):
        bias_values = {"excellent": 90, "good": 80,"fair": 70}
    elif (bias == "Weak (>70%)"):
        bias_values = {"excellent": 50, "good": 65,"fair": 50}

    # Check if there is a path selected (GUI), none = terminate function
    if(path == ""):
        dpg.add_text("[ERROR] | No File selected", parent="console", color=(255,0,0))
        return
    # Check if there is a constraint entered (GUI), none = terminate function
    if(len(constraints) < 1):
        dpg.add_text("[ERROR] | No constraints defined", parent="console", color=(255,0,0))
        return
    dpg.add_text("=================PARSING=================", parent="console")
    dpg.configure_item("loader", show=True)
    parsed_pdf = parser.from_file(path)
    dpg.configure_item("loader", show=False)
    data = parsed_pdf['content']
    data = data.split("\n\n")
    dpg.add_text("================ANALYZING================", parent="console")
    for keyword in constraints:
        dpg.add_text(f"<--Constraint: {keyword}", parent="console")
        ratio_data = {}
        for sentence in data:
            array_words = sentence.split()
            for word in array_words:
                if len(word) < 3:
                    continue
                isFound = False
                if (word.isspace()):
                    continue
                ratio = partial_ratio(keyword, word)
                ratio_data[word] = ratio
                isFound = bf_string_match(keyword.lower(), word.lower())
                dpg.add_text("Word: {}, Acc: {}%".format(word, (round(ratio*100, 2))), parent="console")
        best_ratio_key = max(ratio_data, key=ratio_data.get)
        best_ratio_value = ratio_data[best_ratio_key]
        if (isFound or best_ratio_value*100 >= bias_values["excellent"]):
            dpg.add_text(f'- Criterion "{keyword}" \nis highly present:', parent="result-window", color=(0, 255, 0))
            dpg.add_text("- Accuracy: {}% | Word: {}".format(round(best_ratio_value*100, 2), best_ratio_key), parent="accuracy-window")
        elif (not isFound and best_ratio_value*100 >= bias_values["good"]):
            dpg.add_text(f'- Exact match not found but criterion \n"{keyword}"is most likely present', parent="result-window", color=(144,238,144))
            dpg.add_text("- Accuracy: {}% | Word: {}".format(round(best_ratio_value*100, 2), best_ratio_key), parent="accuracy-window")
        elif (not isFound and best_ratio_value*100 >= bias_values["fair"]):
            dpg.add_text(f'Exact match not found and criterion \n"{keyword}" is most likely missing', parent="result-window", color=(255,165,0))
            dpg.add_text("- Accuracy: {}% | Word: {}".format(round(best_ratio_value*100, 2), best_ratio_key), parent="accuracy-window")
        else:
            dpg.add_text(f'Criterion {keyword} not found.', parent="result-window", color=(255, 0, 0))
            dpg.add_text("- Highest Accuracy match: {}% | \n Word: {}".format(round(best_ratio_value*100, 2), best_ratio_key), parent="accuracy-window")


def open_file(sender, app_data, user_data):
    global file_path
    file_path = app_data['file_path_name']
    dpg.set_value("file_path_gui", file_path)

with dpg.file_dialog(directory_selector=False, show=False, modal=True, callback=open_file, id="file_dialog_pdf", min_size=[460,300], max_size=[460,300]):
    dpg.add_file_extension(".pdf")

def set_bias(sender, app_data, user_data):
    global bias
    bias = app_data

with dpg.window(label="Resume Checker", width=560, height=450, no_title_bar=True, no_move=True, no_collapse=True, no_resize=True, tag="resume-checker", pos=[0,0], indent=20):
    
    dpg.add_text(default_value="File path selected:")
    dpg.add_text(tag="file_path_gui", default_value="No file selected.")
    dpg.add_button(label="Open File", callback=lambda: dpg.show_item("file_dialog_pdf"))
    dpg.add_separator()
    dpg.add_text(default_value="Constraints:")
    dpg.add_text(tag="constraint_gui", default_value="None")
    with dpg.group(horizontal=True, show=True, tag="input-group",):
        dpg.add_input_text(tag="keyword_stream", parent="input-group", hint="Enter single-word keyword...", width=392, height=28, tracked=True)
        dpg.add_button(label="Add Constraint", callback=lambda: add_constraint())
    dpg.add_separator()
    with dpg.group(horizontal=True):
        dpg.add_text("Tolerance:")
        dpg.add_combo(("Strong (>95%)", "Medium (>90%)", "Weak (>80%)"), tag="bias_select", default_value=bias, callback=set_bias)
    dpg.add_separator()
    with dpg.group(horizontal=True):
        with dpg.group():
            dpg.add_button(label="Verify", callback=lambda: parse_file(file_path), width=174, height=119)
            dpg.add_button(label="Clear", callback=lambda: clear(), width=174, height=119)
        with dpg.group():
            with dpg.group(horizontal=True):
                dpg.add_text("Result:")
                dpg.add_loading_indicator(show=False, tag="loader")
            dpg.add_child_window(height=90, width=345, horizontal_scrollbar=True, tag="result-window")
            dpg.add_text("Accuracy:")
            dpg.add_child_window(height=90, width=345, horizontal_scrollbar=True, tag="accuracy-window")
            

with dpg.window(label="Console", width=548, height=250, no_move=True, no_collapse=True, no_resize=True, no_close=True, tag="console", pos=[0,450]):
    dpg.add_text("Resume Checker v.0.1")
    dpg.add_text("BSCS 2-3 | DAA Group 1")
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
