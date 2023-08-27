from leetcode_local_tester.creator.creator import CodeCreator
from leetcode_local_tester.model.problem import Function, Problem
import os
from string import Template
import subprocess


class CppCreator(CodeCreator):
    code_type = "cpp"

    def format_file(self, file_loc):
        subprocess.call(["clang-format", f"-style=file:{self._template_dir}/.clang-format", "-i", file_loc])

    """
    // problem can be divided into 4 types:
    // function - no predefined type, most of the problems are this type
    // function - with predefined type, such as LC174C
    // method - no predefined type, such as LC175C
    // method - with predefined type, such as LC163B
    """

    def parse_code(self, code):
        lines = code.split("\n")
        # get class name
        class_name = ""
        for l in lines:
            i = l.find("class")
            if i != -1:
                class_name = l[6:-2]
                break
        functions = list()
        is_func_problem = True
        for lo, line in enumerate(lines):
            line = line.strip()
            if "{" in line and not line.startswith("struct") and not line.startswith("class") and not line.startswith(
                    "/*") and not line.startswith("//") and not line.startswith("*"):
                f = Function()
                i = line.find("(")
                left = line[:i]
                right = line[i + 1:]
                left_words = left.split(" ")
                f.name = left_words[-1].strip()
                f.is_constructor = (f.name == class_name)
                if f.is_constructor:
                    is_func_problem = False
                f.location = lo
                name_len = len(f.name)
                f.output_params = left[:-name_len - 1].strip()
                i = right.find(")")
                right = right[:i]
                right_words = right.split(",")
                for w in right_words:
                    w = w.strip()
                    f.input_params.append(w)
                functions.append(f)
        return class_name, is_func_problem, functions

    def create_main_code(self, dir_loc, code):
        file_location = f"{dir_loc}/solution.h"
        d = {
            "problem": code,
        }

        with open(f"{self._template_dir}/solve.h", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

        self.format_file(file_location)

    def _create_func_problem_test(self, dir_loc, p: Problem):
        f = p.functions[0]
        sol = f"{p.class_name} sol = {p.class_name}();"

        input_number = len(f.input_params)
        build_params_str_list = []
        input_names = []
        for idx, input_param in enumerate(f.input_params):
            if input_param == "":
                continue
            # tmp maybe long long value
            tmp = input_param.rsplit(" ", 1)

            input_type = tmp[0]
            input_name = tmp[1]

            # remove & symbol
            input_type = input_type.replace("&", "")
            build_params_str_list.append(f"{input_type} {input_name};")
            build_params_str_list.append(f"convert_params(data[i * one_test_number + {idx}], {input_name});")
            input_names.append(input_name)

        build_params_str_list.append(f"{f.output_params} real_res;")
        build_params_str_list.append(f"convert_params(data[i * one_test_number + {input_number}], real_res);")
        build_params = "\n".join(build_params_str_list)
        run_str = f"{f.output_params} my_res = sol.{f.name}({', '.join(input_names)});"
        d = {
            "input_number": input_number,
            "sol": sol,
            "build_params": build_params,
            "run": run_str,
        }

        file_location = f"{dir_loc}/main.cpp"

        with open(f"{self._template_dir}/main.cpp", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

        self.format_file(file_location)

    def _create_method_problem_test(self, dir_loc, p: Problem):
        name_to_function = {}

        for f in p.functions:
            name_to_function[f.name] = f

        def work(func_name):
            res = []
            f = name_to_function[func_name]
            input_params = f.input_params
            output_params = f.output_params

            input_names = []
            for idx, input_param in enumerate(input_params):
                if input_param == '':
                    continue
                tmp = input_param.rsplit(" ", 1)
                input_type = tmp[0]
                input_name = tmp[1]

                # remove & symbol
                input_type = input_type.replace("&", "")
                res.append(f"{input_type} {input_name};")
                res.append(f"convert_params(input_param[{idx}], {input_name});")
                input_names.append(input_name)
            if output_params == "void":
                res.append(f"sol.{func_name}({', '.join(input_names)});")
            elif output_params == '':
                res.append(f"{p.class_name} sol = {p.class_name}({', '.join(input_names)});")
            else:
                res.append(f"{output_params} real_res;")
                res.append(f"convert_params(output_params[j], real_res);")
                res.append(f"{output_params} my_res = sol.{func_name}({', '.join(input_names)});")
                res.append(
                    f"bool check_result = compare_result(to_string(i + 1) + \"-\" + to_string(j), my_res, real_res);")
                res.append("all_test++;")
                res.append("if (!check_result) fail_test++;")
            res = "\n".join(res)
            return res

        constructor = name_to_function[p.class_name]
        sol = work(constructor.name)
        build_func = []

        for idx, f in enumerate(p.functions):
            if f.name == p.class_name:
                continue
            build_func.append(f"if (function_names[j] == \"{f.name}\") " + "{")
            build_func.append(f"{work(f.name)}")
            build_func.append("}")

        build_func = "\n".join(build_func)

        d = {
            "sol": sol,
            "build_func": build_func
        }

        file_location = f"{dir_loc}/main.cpp"

        with open(f"{self._template_dir}/method_main.cpp", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

        self.format_file(file_location)

    def create_test_code(self, dir_loc, p: Problem):
        if p.is_func_problem:
            self._create_func_problem_test(dir_loc, p)
        else:
            self._create_method_problem_test(dir_loc, p)
