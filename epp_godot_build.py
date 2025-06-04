"""
Evil Pear Productions Godot Build Tool
@author Connor McCloskey

Built in Python 3.12

See ReadMe for full information.
"""

#region --- Imports ---

import os
import subprocess
import sys
import json
from datetime import datetime
import configparser

#endregion

#region --- Vars ---

engine_path:                    str = "path to godot editor"
project_path:                   str = "path to project.godot to build"
version_path:                   str = "path to version number config file"
build_path:                     str = "path to where builds are stored"
export_preset:                  str = "MyPreset"
should_update_build_version:    bool = False

project_name:                   str = "MyGame"

build_extension:                str = "exe"

generated_build_path:           str = ""

settings_file_name:             str = "settings.json"

build_config:                   str = "export-debug"

build_types:                    dict = {
    "release":                  "export-release",
    "debug":                    "export-debug"
}

valid_args:                     list = [
                                    "projectname",
                                    "buildextension",
                                    "onlyupdate",
                                    "enginepath",
                                    "projectpath",
                                    "buildpath",
                                    "versionconfig",
                                    "updateversion",
                                    "makebuild",
                                    "savesettings"
                                ]

#endregion

#region --- Functions ---

def exit_tool(code: int):
    print("")
    print(">>>>>>>>>> EXITING EPP GODOT BUILD TOOL <<<<<<<<<<")
    print("")
    sys.exit(code)

def read_settings_json():

    print("")
    print(">>>>> Reading settings from JSON")

    if not os.path.exists(settings_file_name):
        print(">>>>> No settings file found, using script defaults")
        return

    file = open(settings_file_name, "r")
    settings = json.load(file)
    file.close()

    set_project_name(settings["projectname"])
    set_build_extension(settings["buildextension"])
    set_engine_path(settings["enginepath"])
    set_project_path(settings["projectpath"])
    set_version_config(settings["versionpath"])
    set_build_path(settings["buildpath"])
    set_export_preset(settings["exportpreset"])
    set_do_version_update(settings["do_update"])

def display_settings():
    print("")
    print("---- Run Settings ---")
    print(">> Project name:        ", project_name)
    print(">> Extension:           ", build_extension)
    print(">> Engine path:         ", engine_path)
    print(">> Project path:        ", project_path)
    print(">> Version config path: ", version_path)
    print(">> Build path:          ", build_path)
    print(">> Export preset:       ", export_preset)
    print(">> Update config file?  ", should_update_build_version)

def write_settings_json():

    print("")
    print(">>>>> Writing settings to JSON")

    new_settings = {
        "projectname": project_name,
        "buildextension": build_extension,
        "enginepath": engine_path,
        "projectpath": project_path,
        "versionpath": version_path,
        "buildpath": build_path,
        "exportpreset": export_preset,
        "do_update": should_update_build_version
    }

    json_data = json.dumps(new_settings,indent=4)

    file = open(settings_file_name, "w")
    file.write(json_data)
    file.close()

def generate_build_path():
    global generated_build_path
    build = project_name + "." + build_extension
    generated_build_path = os.path.join(build_path, build)

def helpme():
    pass

def set_engine_path(path: str):
    global engine_path
    engine_path = path

def set_project_path(path: str):
    global project_path
    project_path = path

def set_build_path(path: str):
    global build_path
    build_path = path

def set_build_config(t: str):
    global build_config
    global build_types

    if t not in build_types.keys():
        return

    build_config = build_types[t]

def set_version_config(path: str):
    global version_path
    version_path = path

def set_do_version_update(value: bool):
    global should_update_build_version
    should_update_build_version = value

def set_export_preset(preset: str):
    global export_preset
    export_preset = preset

def set_project_name(name: str):
    global project_name
    project_name = name

def set_build_extension(ext: str):
    global build_extension
    build_extension = ext

def update_version():

    print("")
    print(">>>>> Updating version config file...")

    build_date = "\"" + datetime.today().strftime('%m.%d.%y') + "\""

    if not os.path.exists(version_path):
        print("!! WARNING !! Could not find config file! Path: " + version_path)
        exit_tool(1)

    parser = configparser.ConfigParser()
    parser.read(version_path)
    parser.set("version", "build_date", build_date)
    with open(version_path, "w") as configfile:
        parser.write(configfile)

def test_update():
    global version_path
    version_path = "version.cfg"
    update_version()

def make_build():

    print("")
    print(">>>>> Starting build process")

    if should_update_build_version:
        update_version()

    # build_command = engine_path + " " + "--headless" + " " + f"--path {project_path}" + " " + f"--{build_config} \"{export_preset}\"" + " " + generated_build_path
    build_command = engine_path + " " + f"--path {project_path}" + " " + f"--{build_config} \"{export_preset}\"" + " " + generated_build_path

    print("")
    print(">>>>> Packaging...")
    print(">> Build command: ", build_command)
    print("")

    try:
        result = subprocess.run(build_command, shell=True, check=True)
        print("")
        print(">>>>> PACKAGING DONE! Return code: ", result.returncode)
        exit_tool(0)
    except subprocess.CalledProcessError as e:
        print("")
        print(">>>>> PACKAGING FAILED: ", e)
        exit_tool(1)

def process_args() -> bool:

    do_build = True
    save_settings = False
    update_settings_only = False

    num_args = len(sys.argv)
    if num_args == 0:
        return do_build

    sorted_args: dict = {}
    index = 1
    while index < num_args - 1:
        key = sys.argv[index].lower()
        if key not in valid_args:
            print("!!! WARNING !!! Invalid argument! Use 'helpme' for a list of all valid commands! Invalid command: ", key)
            exit_tool(1)
        if key == "helpme":
            helpme()
            exit_tool(0)
        if key == "onlyupdate":
            do_build = False
            save_settings = True
            update_settings_only = True
            index += 1
            continue
        value = sys.argv[index + 1]
        sorted_args[key] = value
        index += 2

    print("")
    print(">>>>> Processing command line arguments")

    if "projectname" in sorted_args:
        set_project_name(sorted_args["projectname"])

    if "buildextension" in sorted_args:
        set_build_extension(sorted_args["buildextension"])

    if "enginepath" in sorted_args:
        set_engine_path(sorted_args["enginepath"])

    if "projectpath" in sorted_args:
        set_project_path(sorted_args["projectpath"])

    if "buildpath" in sorted_args:
        set_build_path(sorted_args["buildpath"])

    if "buildconfig" in sorted_args:
        set_build_config(sorted_args["builconfig"])

    if "versionconfig" in sorted_args:
        set_version_config(sorted_args["versionconfig"])

    if "updateversion" in sorted_args:
        v = bool(sorted_args["updateversion"])
        set_do_version_update(v)

    if "makebuild" in sorted_args:
        if not update_settings_only:
            do_build = bool(sorted_args["makebuild"])

    if "savesettings" in sorted_args:
        if not update_settings_only:
            save_settings = bool(sorted_args["savesettings"])

    if "exportpreset" in sorted_args:
        set_export_preset(sorted_args["exportpreset"])

    if save_settings:
        write_settings_json()

    display_settings()

    return do_build

def start_tool():

    print("")
    print(">>>>>>>>>> RUNNING EPP GODOT BUILD TOOL <<<<<<<<<<")
    print("")

    read_settings_json()
    do_build = process_args()
    if do_build:
        generate_build_path()
        make_build()
    else:
        exit_tool(0)
#endregion

#region --- Main ---

def main():
    start_tool()

#endregion

if __name__ == "__main__":
    main()