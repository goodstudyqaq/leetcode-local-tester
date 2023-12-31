# Leetcode-local-tester
[![Maintenance](https://img.shields.io/badge/maintained-yes-brightgreen.svg)](https://github.com/goodstudyqaq/leetcode-local-tester/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/leetcode-local-tester.svg)](https://pypi.python.org/pypi/leetcode-local-tester/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/leetcode-local-tester.svg)](https://pypi.python.org/pypi/leetcode-local-tester/)
[![Downloads](https://static.pepy.tech/personalized-badge/leetcode-local-tester?period=month&units=international_system&left_color=grey&right_color=orange&left_text=downloads/month)](https://pepy.tech/project/leetcode-local-tester)
[![Downloads](https://static.pepy.tech/personalized-badge/leetcode-local-tester?period=total&units=international_system&left_color=grey&right_color=orange&left_text=downloads)](https://pepy.tech/project/leetcode-local-tester)
![GitHub Sponsors](https://img.shields.io/github/sponsors/goodstudyqaq)


Leetcode test utils for local environment

# Background
Because of Leetcode's special design for test cases, if you want to test your code locally, you need to write some boilerplate code to read the test cases from the file and parse them into the format that your code can understand, which is very annoying. Especially in a contest, you may not have enough time to write the boilerplate code. So I wrote this tool to help me generate the boilerplate code automatically. It will improve your efficiency in a contest.

The design is really like TopCoder's test cases, but TopCoder has a very good tool ([TZTester](https://community.topcoder.com/contest/classes/TZTester/TZTester.html)) to generate the boilerplate code for you, which is very convenient.

# Usage

## Install
```bash
pip install leetcode-local-tester
```

## Command
```bash
leetcode-local-tester work --help

Options:
  --kind TEXT          The question kind. Now support: `contest`, `problem`,
                       `season`, and `contest` includes `weekly` and
                       `biweekly`. Default is `problem`.
  --detail TEXT        The detail of the question. If type is `contest` or
                       `problem`, the detail is the url. Such as
                       `https://leetcode.com/contest/weekly-contest-326/`,
                       `https://leetcode.cn/problems/minimum-number-of-
                       operations-to-reinitialize-a-permutation/`. If type is
                       `season`, the detail is the season name. Such as
                       `2020-fall-solo` or `2020-fall-team`.
  --language TEXT      The language of the code. Now support: `cpp`,
                       `python3`. Default is `python3`.
  --location TEXT      The location of the code. Default is `./leetcode/`.
  --help               Show this message and exit.
```
## Before you use
Because the utility needs to login to Leetcode to get some information, there are two ways to login. One is to use username and password. You need to set these value to environment variables: `LEETCODE_USERNAME` and `LEETCODE_PASSWORD`. The other is to use cookie. You need to set the cookie to environment variable: `LEETCODE_COOKIE`. You can read the article [How to get the cookie](https://betterprogramming.pub/work-on-leetcode-problems-in-vs-code-5fedf1a06ca1) to get the cookie.
- Note: If you use `leetcode.com`. You cannot use username and password to login, because `leetcode.com` has recaptcha. So you need to use cookie to login.




## Example
```bash
leetcode-local-tester work --kind contest --detail https://leetcode.com/contest/weekly-contest-326/ --language cpp --location ./leetcode/
```
After running the command, you will get the following files:


![dir.jpg](https://s2.loli.net/2023/07/25/APhmjgsIa9G3BSw.jpg)

`weekly-contest-326`: The folder of the contest. It contains all test cases and the code file.

`utils`: The folder of the utils. It contains code that is used to parse the test cases. 

**Pay attention: `utils` folder is only generated once. After generated the first time, it will not be updated. So you can add your own code in it.**

You can write your code in `solution.h`. We take the first question in `weekly-contest-300` as an example.
The `solution.h` file is like this:

```cpp
/*
Code generated by https://github.com/goodstudyqaq/leetcode-local-tester
*/
#if __has_include("../utils/cpp/help.hpp")
#include "../utils/cpp/help.hpp"
#elif __has_include("../../utils/cpp/help.hpp")
#include "../../utils/cpp/help.hpp"
#else
#define debug(...) 42
#endif

class Solution {
   public:
    string decodeMessage(string key, string message) {
        int res[26];
        memset(res, -1, sizeof(res));
        int cnt = 0;
        for (auto v : key) {
            int cur = v - 'a';
            if (cur >= 0 && cur < 26) {
                if (res[cur] != -1) continue;
                res[cur] = cnt++;
            }
        }
        string fin;
        for (auto v : message) {
            if (v == ' ')
                fin += ' ';
            else {
                char cur = 'a' + res[v - 'a'];
                fin += cur;
            }
        }
        return fin;
    }
};
```

After you finish your own code, you can run `main.cpp` to test your code.
    
```bash
g++ main.cpp -std=c++11 -o main && ./main

Case 1 testing...
[my_ans]: "this is a secret"
[result]: "this is a secret"
Case 1 passed!
Case 2 testing...
[my_ans]: "the five boxing wizards jump quickly"
[result]: "the five boxing wizards jump quickly"
Case 2 passed!
The number of test cases: 2
The number of test cases failed: 0
```

If you get `Wrong answer`, you can snip the test case and paste it into `data` to debug your code.
**Pay attention: `data`'s format is Input + Output.**

In this example, the test case is:

```text
"the quick brown fox jumps over the lazy dog"
"vkbs bs t suepuv"
```

# TODO
- [x] Support `python` (completed)

# License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.

Maintaining the project is hard and time-consuming, and I've put much ❤️ and effort into this.

If you've appreciated my work, you can back me up with a donation! Thank you 😊

If there is any problem, please create an issue. I will reply to you as soon as possible.


[<img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/goodstudyqaq)

