
class CodeCreator(object):

    code_type = ""

    def __init__(self, template_dir):
        self._template_dir = template_dir

    def parse_code(self, code: str):
        """
        According to the code, parse the class name, is_func_problem and functions
        :param code: code
        :return: class_name, is_func_problem, functions
        """

    def create_main_code(self, dir_loc, code):
        """
        Generate main code
        :param dir_loc: dir location
        :param code: code
        :return: None
        """

    def create_test_code(self, dir_loc, p):
        """
        Generate test code
        :param dir_loc: dir location
        :param p: problem
        :return: None
        """