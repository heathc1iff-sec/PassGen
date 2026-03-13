# PassGen - 高级密码字典生成器

[![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

**PassGen**是一款专为红队人员和安全测试工程师设计的高频密码字典生成器


---

## 功能特点

* 个人信息组合：姓名、昵称、生日、伴侣、孩子、宠物、公司/关键词等
* 时间模式组合：季节、月份、星期 + 年份 + 特殊字符
* 键盘行走模式：如 `qwerty`, `1qaz2wsx` 等
* Leet Speak 变体：如 `a -> @`, `e -> 3`, `s -> $` 等
* 常见弱密码库覆盖：国际高频密码集合
* 支持大小写变体、特殊字符后缀、数字组合
* 词语两两组合生成
* 支持自定义密码长度范围
* 可交互或命令行参数模式生成密码字典

---

## 安装

确保系统已安装 Python 3.x：

```bash
git clone https://github.com/yourusername/PassGen.git
cd PassGen
chmod +x passgen.py
```
---

## 使用说明

### 查看帮助

```bash
python passgen.py -h
```

输出示例：

```
usage: passgen.py [-h] [-i] [-n NAME] [--surname SURNAME] [--nickname NICKNAME] ...
PassGen - 密码字典生成器
...
```

---

### 交互式模式

```bash
python passgen.py -i
```

根据提示输入目标信息（姓名、生日、公司、关键词等），选择是否启用季节/月份组合、特殊字符、Leet Speak、键盘模式和常见弱密码。
输出默认文件：`passwords.txt`。

---

### 命令行模式

示例 1：生成季节 + 年份组合

```bash
python passgen.py --season --year 2023
```

示例 2：生成月份组合并限制密码长度

```bash
python passgen.py --month --year 2023-2024 --min 8 --max 16
```

示例 3：基于目标信息生成组合

```bash
python passgen.py -n john+doe -c apple --season --leet
```

---

### 参数说明

| 参数                    | 说明                        |
| --------------------- | ------------------------- |
| `-i, --interactive`   | 交互式模式                     |
| `-n NAME`             | 姓名/用户名 (如 john+doe)       |
| `--surname SURNAME`   | 姓氏                        |
| `--nickname NICKNAME` | 昵称                        |
| `-b BIRTHDAY`         | 生日 (YYYYMMDD)             |
| `--partner-name`      | 伴侣姓名                      |
| `--partner-birthday`  | 伴侣生日                      |
| `--child-name`        | 孩子姓名                      |
| `--child-birthday`    | 孩子生日                      |
| `-p, --pet`           | 宠物名                       |
| `-c, --company`       | 公司/单位名                    |
| `-k, --keywords`      | 关键词 (逗号分隔)                |
| `--season`            | 生成季节组合 (Winter2023!)      |
| `--month`             | 生成月份组合 (January2024!)     |
| `--weekday`           | 生成星期组合 (Monday123!)       |
| `--year YEAR`         | 指定年份 (如 2023 或 2020-2025) |
| `--leet`              | 启用 Leet Speak 模式          |
| `--no-special`        | 禁用特殊字符尾部                  |
| `--no-keyboard`       | 禁用键盘密码模式                  |
| `--no-common`         | 禁用常见弱密码                   |
| `--word-combo`        | 词语两两组合                    |
| `--min`               | 密码最小长度 (默认6)              |
| `--max`               | 密码最大长度 (默认24)             |
| `-o OUTPUT`           | 输出文件名                     |
| `-q, --quiet`         | 静默模式，不显示 Banner           |

---

### 输出

生成的密码字典按长度排序，文件默认保存为 `passwords.txt`。

示例：

```
[*] 正在生成密码字典...
[+] 生成完成!
    密码总数 : 12,345
    文件大小 : 1.24 MB
    耗时     : 0.35s
    输出文件 : /home/kali/Desktop/tools/PassGen/passwords.txt
```

---

## 高级用法

* 支持拼音/英文姓名组合：`-n john+doe` -> `john.doe`, `jdoe` 等
* 可以限制年份范围：`--year 2020-2023`
* 支持词语组合生成更复杂的密码列表

---

## 版本信息
*PassGen v3.0.0*

---

## 免责声明

此工具仅用于安全测试和教育研究，禁止用于非法用途。使用者需自行承担法律责任。
