from leetcode_local_tester.creator.creator import CodeCreator
from leetcode_local_tester.model.problem import Function, Problem
import os
from string import Template


class PythonCreator(CodeCreator):
    code_type = "python3"

    def parse_code(self, code: str):
        lines = code.split("\n")
        # get class name
        class_name = ""
        for l in lines:
            if l.startswith("class"):
                class_name = l[6:-1]
                break
        functions = list()
        is_func_problem = True

        for lo, line in enumerate(lines):
            line = line.strip()
            if ":" in line and not line.startswith("class") and not line.startswith("#"):
                f = Function()
                i = line.find("(")
                left = line[:i]
                right = line[i + 1:]
                left_words = left.split(" ")
                f.name = left_words[-1].strip()
                f.is_constructor = (f.name == "__init__")
                if f.is_constructor:
                    is_func_problem = False
                f.location = lo
                name_len = len(f.name)
                output_params_idx = right.find("->")
                if output_params_idx != -1:
                    f.output_params = right[output_params_idx + 3: -1].strip()
                i = right.find(")")
                right = right[:i]
                right_words = right.split(",")
                for w in right_words:
                    w = w.strip()
                    if w != "self":
                        f.input_params.append(w)
                functions.append(f)
        return class_name, is_func_problem, functions

    def create_main_code(self, dir_loc, code):
        file_location = f"{dir_loc}/solution.py"
        d = {
            "problem": code
        }
        with open(f"{self._template_dir}/solution.py", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

    def _generate_code_with_indent(self, code: str, indent: int):
        return 4 * indent * " " + code

    def _create_func_problem_test(self, dir_loc, p: Problem):
        f = p.functions[0]
        sol = f"sol: {p.class_name} = {p.class_name}()"
        sol = self._generate_code_with_indent(sol, 1)
        input_number = len(f.input_params)
        build_params_str_list = []
        input_names = []

        for idx, input_param in enumerate(f.input_params):
            if input_param == "":
                continue
            tmp = input_param.split(": ")
            input_type = tmp[1]
            # remove Optional
            while "Optional[" in input_type:
                beg_idx = input_type.find("Optional[")
                score = 0
                end_idx = -1
                for i in range(beg_idx, len(input_type)):
                    if input_type[i] == "[":
                        score += 1
                    elif input_type[i] == "]":
                        score -= 1
                        if score == 0:
                            end_idx = i
                            break
                input_type = input_type[:beg_idx] + input_type[beg_idx + 9:end_idx] + input_type[end_idx + 1:]

            if input_type.startswith("Optional["):
                input_type = input_type[9:-1]
            input_name = tmp[0]

            build_params_str_list.append(
                f"{input_name}: {input_type} = convert_params(data[i * one_test_number + {idx}], '{input_type}')")
            input_names.append(input_name)

        while "Optional[" in f.output_params:
            beg_idx = f.output_params.find("Optional[")
            score = 0
            end_idx = -1
            for i in range(beg_idx, len(f.output_params)):
                if f.output_params[i] == "[":
                    score += 1
                elif f.output_params[i] == "]":
                    score -= 1
                    if score == 0:
                        end_idx = i
                        break
            f.output_params = f.output_params[:beg_idx] + f.output_params[beg_idx + 9:end_idx] + f.output_params[
                                                                                                 end_idx + 1:]

        build_params_str_list.append(
            f"real_res: {f.output_params} = convert_params(data[i * one_test_number + {input_number}], '{f.output_params}')")
        build_params_str_list = [self._generate_code_with_indent(s, 2) for s in build_params_str_list]
        build_params = "\n".join(build_params_str_list)
        run_str = f"my_res: {f.output_params} = sol.{f.name}({', '.join(input_names)})"
        run_str = self._generate_code_with_indent(run_str, 2)

        d = {
            "input_number": input_number,
            "sol": sol,
            "build_params": build_params,
            "run": run_str,
            "return_type": f.output_params,
        }

        file_location = f"{dir_loc}/main.py"

        with open(f"{self._template_dir}/main.py", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

    def _create_method_problem_test(self, dir_loc, p: Problem):
        name_to_function = {}

        for f in p.functions:
            name_to_function[f.name] = f

        def work(func_name):
            res = []
            f = name_to_function[func_name]
            input_params = f.input_params
            output_params = f.output_params
            # remove Optional
            if output_params.startswith("Optional["):
                output_params = output_params[9:-1]

            input_names = []
            for idx, input_param in enumerate(input_params):
                if input_param == '':
                    continue
                tmp = input_param.split(": ")
                input_type = tmp[1]
                # remove Optional
                if input_type.startswith("Optional["):
                    input_type = input_type[9:-1]

                input_name = tmp[0]

                res.append(f"{input_name}: {input_type} = convert_params(input_param[{idx}], '{input_type}')")
                input_names.append(input_name)

            if output_params == "None":
                res.append(f"sol.{func_name}({', '.join(input_names)})")
            elif output_params == "":
                res.append(f"sol: {p.class_name} = {p.class_name}({', '.join(input_names)})")
            else:
                res.append(f"real_res: {output_params} = convert_params(output_params[j], '{output_params}')")
                res.append(f"my_res: {output_params} = sol.{func_name}({', '.join(input_names)})")
                res.append(
                    'check_result: bool = compare_result(f"{i + 1}-{j}", my_res, real_res, ' + f"'{output_params}')")
                res.append("all_test += 1")
                res.append("if not check_result:")
                res.append(self._generate_code_with_indent("fail_test += 1", 1))
            return res

        constructor = name_to_function["__init__"]
        sol = work(constructor.name)
        sol = [self._generate_code_with_indent(s, 2) for s in sol]
        sol = "\n".join(sol)

        build_func = []

        for idx, f in enumerate(p.functions):
            if f.name == "__init__":
                continue
            build_func.append(f"if function_names[j] == \"{f.name}\":")
            tmp = work(f.name)
            tmp = [self._generate_code_with_indent(s, 1) for s in tmp]
            build_func.extend(tmp)

        build_func = [self._generate_code_with_indent(s, 3) for s in build_func]
        build_func = "\n".join(build_func)

        d = {
            "sol": sol,
            "build_func": build_func
        }

        file_location = f"{dir_loc}/main.py"

        with open(f"{self._template_dir}/method_main.py", "r", encoding="utf-8") as f:
            src = Template(f.read())
            result = src.substitute(d)

        with open(file_location, "w", encoding="utf-8") as f:
            f.writelines(result)

    def create_test_code(self, dir_loc, p: Problem):
        if p.is_func_problem:
            self._create_func_problem_test(dir_loc, p)
        else:
            self._create_method_problem_test(dir_loc, p)
