#%%
v = 0
#%%
#%%
v += 1
print(v)
#%%
#%%
import subprocess
import sys
import os
import random

class Run_Entry():
    def __init__(self, id_:str, code:str):
        self.__id = id_
        self.__code = code
        self.__stdout = ""
        self.__stderr = ""

    def get_code(self):
        return self.__code

    def set_code(self, code:str):
        self.__code = code

    def len_stdout(self):
        return len(self.__stdout)

    def len_stderr(self):
        return len(self.__stderr)

    def get_stdout(self):
        return self.__stdout

    def get_stderr(self):
        return self.__stderr

    def get_id(self):
        return self.__id

    def update_std(self, std:tuple):
        self.__stdout = std[0]
        #self.__stderr = std[1]

class Code_Executer():
    def __init__(self):
        self.__entries = []
        self.__code = ""

    def add_entry(self, id_:int, code:str):
        # delte old entry, if it exist
        #index = None
        #for i, entry in enumerate(self.__entries):
        #    if entry.get_id() == id_:
        #        index = i

        #if index != None:
        #    self.del_entry(index)

        # create + add Entry
        new_entry = Run_Entry(id_, code)
        self.__entries += [new_entry]

    # Variant 1 of running code
    def run_entry_(self, id_:int, code:str):
        self.add_entry(id_, code)
        len_out, len_err = self.calc_hide()
        self.update_code()

        # variant 1 without file -> code have to be shorter
        #result = subprocess.run([sys.executable, "-c", self.__code], capture_output=True, text=True)

        # variant 2
        with open("_x_x_x_x_x_x_x_x.py", "w") as f:
            f.write(self.__code)
        file = os.getcwd()+"/_x_x_x_x_x_x_x_x.py"
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run([sys.executable, file], startupinfo=startupinfo, capture_output=True, text=True)
        os.remove(file)

        out = result.stdout[len_out:]
        err = result.stderr
        self.__entries[-1].update_std((out, err))
        # remove dont runnable code
        err_len = len(err.replace(" ", "").replace("\n", ""))
        if err_len >= 1:
            self.__entries[-1].set_code("")
        return out+err

    # Variant 2 of running
    def run_entry(self, id_:int, code:str):
        self.add_entry(id_, code)
        len_out, len_err = self.calc_hide()
        self.update_code()
        file_name = self.get_file_name()
        
        with open(file_name, "w") as f:
            f.write(self.__code)
        file = os.getcwd()+"/"+file_name
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        #result = subprocess.Popen([sys.executable, file], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        result = subprocess.Popen(["python", file], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        out = result.stdout.read().decode('utf-8')[len_out:]
        err = result.stderr.read().decode('utf-8')

        os.remove(file)

        self.__entries[-1].update_std((out, err))
        # remove dont runnable code
        err_len = len(err.replace(" ", "").replace("\n", ""))
        if err_len >= 1:
            self.__entries[-1].set_code("")
        return out+err

    def calc_hide(self) -> tuple:
        len_out = 0
        len_err = 0
        for entry in self.__entries:
            len_out += entry.len_stdout()
            len_err += entry.len_stderr()
        return (len_out, len_err)

    def update_code(self) -> str:
        code = ""
        for entry in self.__entries:
            code += entry.get_code()
        self.__code = code

    def del_entry(self, index):
        new_entries = []
        for i, entry in enumerate(self.__entries):
            if i != index:
                new_entries += [entry]

        self.__entries = new_entries

    def clear(self):
        self.__entries = []

    def get_code(self):
        self.update_code()
        code = self.__code
        code = code.replace("#%%", "")
        code = code.lstrip()
        return code

    def get_file_name(self) -> str:
        file_name = "python_lair_subprocess"
        files = os.listdir()
        while file_name+".py" in files:
            rand = str(random.randint(0, 101))
            file_name += rand
        return file_name+".py"
#%%
