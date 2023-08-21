from leetcode_local_tester.creator.cpp_creator import CppCreator
from leetcode_local_tester.creator.python3_creator import PythonCreator

creator_factory = {
    CppCreator.code_type: CppCreator,
    PythonCreator.code_type: PythonCreator
}
