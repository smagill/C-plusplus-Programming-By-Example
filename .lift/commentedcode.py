#!/usr/bin/env python3
import json
import sys
import subprocess
import os
import re
import json
from pathlib import Path
from dataclasses import dataclass
from json import JSONEncoder

NAME = "CommentedCode"
API_VERSION = 1

class ToolNoteEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

@dataclass
class ToolNote:
    type: str
    message: str
    file: str
    line: int
    column: int
    function: str
    details_url: str
    noteId: str
    codeLine: str

    def to_json(self):
        return json.dumps(self, indent=4, cls=ToolNoteEncoder)


@dataclass
class ToolNotes:
    toolNotes: [ToolNote]

    def to_json(self):
        return json.dumps(self, indent=4, cls=ToolNoteEncoder)


def emitStartInfo():
    info = { "version": API_VERSION, "name": NAME }
    print(json.dumps(info))

def emitVersion():
    print(API_VERSION)

def emitName():
    print(NAME)

def emitApplicable(path):
    pathlist = list(Path(path).glob('**/*.c')) + list(Path(path).glob('**/*.cpp')) + list(Path(path).glob('**/*.cc'))
    print(json.dumps(len(pathlist) > 0))

def createLiftNoteCode(filePath, lineNum):
    return {
        'type'      : "CommentedCode",
        'message'   : "Code should not be commented out.",
        'file'      : filePath,
        'line'      : lineNume,
        'column'    : 0,
    }

def createLiftNoteComment(filePath, lineNum):
    return {
        'type'      : "MultiLineComment",
        'message'   : "Multiline comments are not allowed.",
        'file'      : filePath,
        'line'      : lineNume,
        'column'    : 0,
    }

def addJSHintConfigIfNotExists(path):
    configs_exist = len(list(Path(path).glob('**/.jshintrc'))) > 0
    if configs_exist:
        return []
    else:
        return ["--config=/home/lift/.jshintrc"]

def readfiles(codedir, pattern):
    res = subprocess.run(["git","ls-files","*.c"], capture_output=True)
    files = res.stdout.decode("utf-8").split('\n')
    files = list(filter(lambda x: os.path.exists(x), files))
    return files

def analyze_file(filename):
    linenum = 1
    single_line_re = re.compile('//.*;')
    multi_line_pos_re = re.compile('/*')
    multi_line_neg_re = re.compile('*/')
    results = list()
    with open(filename) as f:
        for line in f:
            if single_line_re.search(line):
                results.append(createLiftNoteCode(filename,line))
            elif multi_line_pos_re.search(line) and (not multi_line_neg_re.search(line)):
                results.append(createLiftNoteComment(filename,line))
            line += 1

def analyze(codedir):
    to_execute = ["jshint"]
    if len(config) > 0:
        to_execute.extend(config)

    c_files = readfiles(codedir,"*.c")
    cpp_files = readfiles(codedir,"*.cpp")
    cc_files = readfiles(codedir,"*.cc")
    filenames = c_files + cpp_files + cc_files

    results = list()
    for file in files:
        results += analyze_file(filenames)
    return results

def run(args):
    codedir = args[1]
    results = analyze(codedir)
    print(json.dumps(results))

def main():
    args = sys.argv
    if (len(args) < 4):
        emitStartInfo()
    else:
        cmd = args[3]
        if cmd == "run":
            run(args)
        elif cmd == "applicable":
            emitApplicable(args[1])
        elif cmd == "name":
            emitName()
        else:
            emitVersion()

if __name__ == "__main__":
    main()
