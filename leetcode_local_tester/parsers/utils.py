from leetcode_local_tester.helper.utils import find_non_ASCII
from typing import List

from leetcode_local_tester.helper.utils import get_first_children
from bs4.element import Tag


def parse_sample_text(text: str, parse_args: bool, is_func_problem: bool):
    text = text.strip()
    if text == "":
        return []
    lines = text.split("\n")
    for i, s in enumerate(lines):
        lines[i] = s.strip()

    if not is_func_problem:
        return lines

    text = "".join(lines)
    idx = find_non_ASCII(text)
    if idx != -1:
        print("[warn] Case contains non-ASCII characters, truncated, original text is", text)
        text = text[:idx]

    # Does not contain equal sign, indicating that there is only one parameter
    if not parse_args or "=" not in text:
        return [text]

    # https://leetcode.cn/problems/remove-comments/
    # splits = text.split("=")
    splits = []
    now = 0
    sz = len(text)
    in_quote = False
    while now < sz:
        go = now
        while go < sz:
            in_quote = in_quote ^ (text[go] == "\"")
            if text[go] == '=' and not in_quote:
                break
            go += 1
        splits.append(text[now: go])
        now = go + 1

    sample = []
    for s in splits[1: len(splits) - 1]:
        end = s.rfind(",")
        sample.append(s[:end].strip())
    sample.append(splits[len(splits) - 1].strip())
    return sample


def parse_sample(node: Tag, is_func_problem: bool) -> (List[List[str]], List[List[str]]):
    # Need to determine whether the next child element of <pre> is tag
    #     https://leetcode-cn.com/contest/weekly-contest-190/problems/max-dot-product-of-two-subsequences/
    #     https://leetcode-cn.com/contest/weekly-contest-212/problems/arithmetic-subarrays/
    # If there is a tag, it may not be <strong>
    #     <img> https://leetcode-cn.com/contest/weekly-contest-103/problems/snakes-and-ladders/
    #     <b> https://leetcode-cn.com/contest/weekly-contest-210/problems/split-two-strings-to-make-palindrome/
    # Extract the text, remove the text after "Explanation" and "Hint", and then parse the data after "Input" and "Output"

    sample_ins = []
    sample_outs = []

    input_token = "Input"
    output_token = "Output"
    explanation_token = "Explanation"
    explanation_token2 = "Explaination"

    def tidy(data: str):
        data = data.strip()
        if data != "" and data[-1] == ":":
            data = data[:-1]
        return data

    def is_input(data: str):
        if data is None:
            return False
        data = tidy(data)
        return data == input_token

    def is_output(data: str):
        if data is None:
            return False
        data = tidy(data)
        return data == output_token

    def is_explanation(data: str):
        if data is None:
            return False
        data = tidy(data)
        return data == explanation_token or data == explanation_token2

    def parse_node(o):
        first_child = get_first_children(o)
        if o.name == "strong" and first_child and (is_input(first_child.string) or is_output(first_child.string)):
            cur_node = first_child
            raw_data = []

            def parse_text_after_strong(o: Tag) -> bool:
                if o != cur_node and o.name is None:
                    if is_output(o.string) or is_explanation(o.string):
                        return True
                    raw_data.append(str(o.string))

                c = get_first_children(o)
                while c is not None:
                    if parse_text_after_strong(c):
                        return True
                    c = c.next_sibling
                return False

            c = o
            while c is not None:
                if parse_text_after_strong(c):
                    break
                c = c.next_sibling

            raw_data = "".join(raw_data)

            if is_input(first_child.string):
                sample_ins.append(parse_sample_text(raw_data, True, is_func_problem))
            elif is_output(first_child.string):
                sample_outs.append(parse_sample_text(raw_data, True, is_func_problem))
            else:
                raise Exception("unknown strong node")

        c = get_first_children(o)
        while c is not None:
            parse_node(c)
            c = c.next_sibling

    parse_node(node)
    if len(sample_ins) != len(sample_outs):
        raise Exception("len(sampleIns) != len(sampleOuts) : %d != %d" % (len(sample_ins), len(sample_outs)))
    if len(sample_ins) == 0:
        raise Exception("Parse failed, sample input and output not found!")
    return sample_ins, sample_outs


def parse_season_sample(node: Tag, is_func_problem: bool) -> (List[List[str]], List[List[str]]):
    """
    Parse the sample input and output of the season problem, Only leetcode.cn supports this function
    :param node: <div class
    :param is_func_problem: weather is a function problem
    :return: (sampleIns, sampleOuts)
    """
    sample_ins = []
    sample_outs = []

    def parse_node(o):
        first_child = get_first_children(o)
        if o.name == "div" and first_child and "示例" in first_child.string:
            # print(o)
            raw = first_child.string
            sp = raw.split("`")
            for i, s in enumerate(sp):
                if ">输入" in s or "> 输入" in s:
                    text = sp[i + 1]
                    if not is_func_problem:
                        # https://leetcode-cn.com/contest/season/2020-fall/problems/IQvJ9i/
                        text += "\n" + sp[i + 3]
                    sample_ins.append(parse_sample_text(text, True, is_func_problem))
                elif ">输出" in s or "> 输出" in s:
                    text = sp[i + 1]
                    sample_outs.append(parse_sample_text(text, True, is_func_problem))

        c = first_child
        while c is not None:
            parse_node(c)
            c = c.next_sibling

    parse_node(node)
    if len(sample_ins) != len(sample_outs):
        raise Exception("len(sampleIns) != len(sampleOuts) : %d != %d" % (len(sample_ins), len(sample_outs)))
    if len(sample_ins) == 0:
        raise Exception("Parse failed, sample input and output not found!")
    return sample_ins, sample_outs
