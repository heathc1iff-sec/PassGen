#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PassGen - 密码字典生成器 (精简纯净版)
=====================================
基于目标画像信息生成高质量、全覆盖的密码字典。
去除了多余的拼音及地域化策略，专注于纯粹的高频逻辑组合。

核心功能:
  - 季节 / 月份 / 星期 + 年份 + 特殊字符 (如 Winter2023!, January2024#)
  - 个人信息组合 (姓名/生日/公司等)
  - 键盘行走模式 (qwerty, 1qaz2wsx)
  - Leet speak 变体 (a->@, e->3, s->$)
  - 常见弱密码 + 泄露库高频密码
"""

import argparse
import itertools
import os
import time
from datetime import datetime

__version__ = "3.0.0"

BANNER = r"""
  ____                 ____            
 |  _ \ __ _ ___ ___  / ___| ___ _ __  
 | |_) / _` / __/ __|| |  _ / _ \ '_ \ 
 |  __/ (_| \__ \__ \| |_| |  __/ | | |
 |_|   \__,_|___/___/ \____|\___|_| |_|
                                       
  [密码字典生成器 v%s - 精简纯净版]

  示例命令:
  --season --year 2023       -> Winter2023!, winter23#, ...
  --month  --year 2024       -> January2024!, jan2024#, ...
  --season --year 2023 -n admin -> admin_Winter2023!, ...
""" % __version__

# ==============================================================================
# 全局数据集
# ==============================================================================

# --- 连接符 ---
CONNECTORS = ['', '_', '-', '.', '@', '#']

# --- 尾部特殊字符 ---
SPECIAL_TAILS = [
    '!', '@', '#', '$', '~', '.', '*', 
    '!!', '!@', '!#', '@@', '##', '!@#'
]

# --- 数字后缀 (国际高频排序) ---
NUM_SUFFIXES = [
    '1', '12', '123', '1234', '12345', '123456', '12345678', '123456789',
    '0', '00', '01', '11', '111', '222', '333', '666', '777', '888', '999',
    '0000', '1111', '6666', '8888', '9999',
    '110', '911', '123123', '112233', '123321', '007', '404'
]

# --- 时间关键词 ---
SEASONS = ['spring', 'summer', 'autumn', 'fall', 'winter']
MONTHS_FULL = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
MONTHS_SHORT = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
WEEKDAYS_SHORT = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

# --- 键盘行走模式 ---
KEYBOARD_PATTERNS = [
    'qwerty', 'qwertyuiop', 'asdfgh', 'asdfghjkl', 'zxcvbn', 'zxcvbnm',
    '1qaz2wsx', 'qazwsx', 'qazwsxedc', '1234qwer', 'qwer1234',
    '!@#$%', '!@#$%^&*', 'passwd', 'password', 'passw0rd', 'p@ssw0rd'
]

# --- 常见弱密码 (国际高频) ---
COMMON_PASSWORDS = [
    'password', 'password123', 'admin', 'admin123', 'admin888', 'admin!@#',
    'administrator', 'root', 'root123', 'test', 'test123', 'guest',
    'default', 'changeme', 'welcome', 'login', 'master',
    '123456', '12345678', '111111', '000000', '888888',
    'iloveyou', 'monkey', 'dragon', 'shadow', 'superman', 'batman',
    'Aa123456', 'Aa123456!', 'P@ssw0rd', 'P@ssw0rd!', 'Qwer1234!'
]

# --- Leet speak 映射 ---
LEET_MAP = {'a': ['@', '4'], 'e': ['3'], 'i': ['1', '!'], 'o': ['0'], 's': ['$', '5'], 't': ['7']}

# ==============================================================================
# 工具函数
# ==============================================================================

def case_variants(word):
    """生成精准的大小写变体: 全部小写, 首字母大写, 全部大写"""
    if not word or not word.strip():
        return set()
    w = word.strip().lower()
    return {w, w.capitalize(), w.upper()}

def make_leet_variants(word):
    """生成 leet speak 变体"""
    if not word: return set()
    results = set()
    lower = word.lower()
    # 单字符逐个替换
    for ch, reps in LEET_MAP.items():
        if ch in lower:
            for r in reps:
                results.add(lower.replace(ch, r))
                results.add(word.capitalize().replace(ch, r).replace(ch.upper(), r))
    # 全部替换
    full = lower
    for ch, reps in LEET_MAP.items():
        full = full.replace(ch, reps[0])
    results.add(full)
    return results

def parse_birthday(bd_str):
    """解析生日字符串 -> 各种日期片段"""
    bd_str = bd_str.strip()
    if not bd_str or len(bd_str) != 8 or not bd_str.isdigit():
        return set()
    year, month, day = bd_str[:4], bd_str[4:6], bd_str[6:8]
    frags = {year, year[-2:], month, day, str(int(month)), str(int(day)),
             year+month+day, year[-2:]+month+day, month+day, year+month}
    return frags

def get_year_variants():
    """获取年份列表: 默认近几年"""
    now = datetime.now().year
    years = set()
    for y in range(now - 3, now + 2):
        years.update([str(y), str(y)[-2:]])
    return sorted(years)

# ==============================================================================
# 核心生成器
# ==============================================================================

class PassGen:
    def __init__(self, cfg):
        self.cfg = cfg
        self.pool = set()

    def run(self):
        cfg = self.cfg
        base_words = self._gather_base_words()
        date_frags = self._gather_date_fragments()
        
        target_years = cfg.get('target_years', [])
        years = target_years if target_years else get_year_variants()

        word_variants = set()
        for w in base_words:
            word_variants.update(case_variants(w))

        # 1) 基础个人信息组合
        self.pool.update(word_variants)
        if word_variants:
            self._cross(word_variants, CONNECTORS, NUM_SUFFIXES[:10])
            self._cross(word_variants, CONNECTORS, years)
            if date_frags:
                self._cross(word_variants, CONNECTORS, date_frags)
            
            # 基础词 + 年份 + 特殊尾部 (admin2023!)
            if cfg.get('special_chars', True):
                for w in word_variants:
                    for y in years:
                        for s in SPECIAL_TAILS[:5]:
                            self.pool.add(f"{w}{y}{s}")
                            self.pool.add(f"{w}_{y}{s}")

        # 2) 季节模式 (如 Winter2023!)
        if cfg.get('season', False):
            self._gen_temporal(SEASONS, years)

        # 3) 月份模式 (如 January2024!)
        if cfg.get('month_mode', False):
            self._gen_temporal(MONTHS_FULL + MONTHS_SHORT, years)

        # 4) 星期模式 (如 Monday2023!)
        if cfg.get('weekday', False):
            self._gen_temporal(WEEKDAYS + WEEKDAYS_SHORT, years)

        # 5) 键盘行走模式
        if cfg.get('keyboard', True):
            for kp in KEYBOARD_PATTERNS:
                self.pool.update(case_variants(kp))
                self.pool.add(kp + '123')
                self.pool.add(kp + '!')

        # 6) 常见弱密码
        if cfg.get('common_passwords', True):
            self.pool.update(COMMON_PASSWORDS)

        # 7) 词语两两组合
        if cfg.get('word_combo', False) and len(word_variants) <= 50:
            for a, b in itertools.permutations(list(word_variants), 2):
                self.pool.update([a+b, a+'_'+b, a+'.'+b])

        # 8) Leet Speak
        if cfg.get('leet', False):
            leet_extra = set()
            for pw in list(self.pool):
                if len(pw) <= 16:
                    leet_extra.update(make_leet_variants(pw))
            self.pool.update(leet_extra)

        # 过滤长度
        min_l, max_l = cfg.get('min_length', 1), cfg.get('max_length', 32)
        return {p for p in self.pool if p and min_l <= len(p) <= max_l}

    def _cross(self, lefts, connectors, rights):
        for l in lefts:
            for c in connectors:
                for r in rights:
                    self.pool.add(f"{l}{c}{r}")

    def _gen_temporal(self, base_list, years):
        """处理时间组合 (季节/月份/星期) -> Winter2023!"""
        words = set()
        for w in base_list:
            words.update(case_variants(w))
        
        self.pool.update(words)
        tails = SPECIAL_TAILS if self.cfg.get('special_chars', True) else ['']

        for w in words:
            for y in years:
                # 核心逻辑：季节+年份+可选特殊字符 (如 Winter2023!)
                for tail in tails:
                    self.pool.add(f"{w}{y}{tail}")       # Winter2023!
                    self.pool.add(f"{w}_{y}{tail}")      # Winter_2023!
            
            # 添加少部分数字后缀组合 (如 Winter123!)
            for n in NUM_SUFFIXES[:5]:
                for tail in tails[:3]:
                    self.pool.add(f"{w}{n}{tail}")

    def _gather_base_words(self):
        words = set()
        keys = ['name', 'surname', 'nickname', 'partner_name', 'child_name', 'pet_name', 'company']
        for key in keys:
            val = self.cfg.get(key, '').strip()
            if val:
                for v in val.split(','):
                    if v.strip(): words.add(v.strip())

        for kw in self.cfg.get('keywords', []):
            if kw.strip(): words.add(kw.strip())

        # 处理名与姓 (如 john+doe)
        expanded = set()
        for w in list(words):
            if '+' in w:
                parts = [p for p in w.split('+') if p]
                expanded.add(''.join(parts))
                expanded.add('_'.join(parts))
                expanded.add('.'.join(parts))
                if len(parts) >= 2:
                    expanded.add(parts[0][0] + parts[1]) # jdoe
            else:
                expanded.add(w)
        return expanded

    def _gather_date_fragments(self):
        frags = set()
        for key in ['birthday', 'partner_birthday', 'child_birthday']:
            val = self.cfg.get(key, '').strip()
            if val:
                frags.update(parse_birthday(val))
        return frags

# ==============================================================================
# 输出与文件操作
# ==============================================================================

def write_output(passwords, path):
    pw_list = sorted(list(passwords), key=lambda x: (len(x), x))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(pw_list) + '\n')
    return len(pw_list)

def size_str(n):
    if n < 1024: return f"{n} B"
    if n < 1024 * 1024: return f"{n / 1024:.1f} KB"
    return f"{n / (1024 * 1024):.2f} MB"

# ==============================================================================
# 交互式 & 参数解析
# ==============================================================================

def interactive_mode():
    print("\n[*] 请输入目标信息 (不知道的直接回车跳过)\n")
    cfg = {}
    cfg['name'] = input("  姓名/用户名 (拼音或英文用+连接, 如 john+doe): ").strip()
    cfg['birthday'] = input("  生日 (YYYYMMDD, 如 19900315): ").strip()
    cfg['company'] = input("  公司/单位名: ").strip()
    kw = input("  其他关键词 (逗号分隔): ").strip()
    cfg['keywords'] = [k.strip() for k in kw.split(',')] if kw else []
    
    print()
    cfg['season'] = input("  生成季节组合 (Winter2023!, ...)? (Y/n): ").strip().lower() != 'n'
    cfg['month_mode'] = input("  生成月份组合 (January2024!, ...)? (y/N): ").strip().lower() == 'y'
    ty = input("  指定目标年份 (如 2023 或 2020-2025, 默认近几年): ").strip()
    cfg['target_years'] = parse_year_arg(ty) if ty else []
    
    print()
    cfg['special_chars'] = input("  添加特殊字符后缀 (!,@,# 等)? (Y/n): ").strip().lower() != 'n'
    cfg['leet'] = input("  Leet模式 (a->@, e->3)? (y/N): ").strip().lower() == 'y'
    cfg['keyboard'] = input("  包含键盘密码模式? (Y/n): ").strip().lower() != 'n'
    cfg['common_passwords'] = input("  包含常见弱密码? (Y/n): ").strip().lower() != 'n'

    out = input("  输出文件名 (默认 passwords.txt): ").strip() or 'passwords.txt'
    return cfg, out

def build_parser():
    p = argparse.ArgumentParser(
        description='PassGen - 密码字典生成器 (精简纯净版)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i                                   进入交互式模式
  %(prog)s --season --year 2023                 生成季节+年份组合 (Winter2023! 等)
  %(prog)s --month --year 2023-2024             生成月份组合 (January2024 等)
  %(prog)s -n john+doe -c apple --season        生成目标组合 + 默认年份季节
  %(prog)s -n admin --min 8 --max 16            限制密码长度
        """)

    p.add_argument('-i', '--interactive', action='store_true', help='交互式模式')
    p.add_argument('-n', '--name', default='', help='姓名/用户名 (如 john+doe)')
    p.add_argument('--surname', default='', help='姓氏')
    p.add_argument('--nickname', default='', help='昵称')
    p.add_argument('-b', '--birthday', default='', help='生日 (YYYYMMDD)')
    p.add_argument('--partner-name', default='', help='伴侣姓名')
    p.add_argument('--partner-birthday', default='', help='伴侣生日')
    p.add_argument('--child-name', default='', help='孩子姓名')
    p.add_argument('--child-birthday', default='', help='孩子生日')
    p.add_argument('-p', '--pet', default='', help='宠物名')
    p.add_argument('-c', '--company', default='', help='公司/单位名')
    p.add_argument('-k', '--keywords', default='', help='关键词 (逗号分隔)')

    p.add_argument('--season', action='store_true', help='启用季节组合 (Winter2023!)')
    p.add_argument('--month', action='store_true', help='启用月份组合 (January2024!)')
    p.add_argument('--weekday', action='store_true', help='启用星期组合 (Monday123!)')
    p.add_argument('--year', default='', help='指定年份 (如 2023 或 2020-2025)')

    p.add_argument('--leet', action='store_true', help='启用 Leet speak 模式')
    p.add_argument('--no-special', action='store_true', help='禁用特殊字符尾部')
    p.add_argument('--no-keyboard', action='store_true', help='禁用键盘密码模式')
    p.add_argument('--no-common', action='store_true', help='禁用常见弱密码')
    p.add_argument('--word-combo', action='store_true', help='词语两两组合')

    p.add_argument('--min', type=int, default=6, dest='min_length', help='最小长度 (默认6)')
    p.add_argument('--max', type=int, default=24, dest='max_length', help='最大长度 (默认24)')
    p.add_argument('-o', '--output', default='passwords.txt', help='输出文件名')
    p.add_argument('-q', '--quiet', action='store_true', help='静默模式')
    return p

def parse_year_arg(year_str):
    if not year_str: return []
    years = set()
    for part in year_str.split(','):
        part = part.strip()
        if '-' in part and not part.startswith('-'):
            try:
                start, end = part.split('-', 1)
                for y in range(int(start), int(end) + 1):
                    years.update([str(y), str(y)[-2:]])
            except ValueError:
                years.add(part)
        elif part.isdigit():
            years.update([part, part[-2:]])
        elif part:
            years.add(part)
    return sorted(years)

def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.quiet:
        print(BANNER)

    if args.interactive:
        cfg, out = interactive_mode()
    elif any([args.name, args.keywords, args.company, args.season, args.month, args.weekday]):
        cfg = vars(args).copy()
        cfg['target_years'] = parse_year_arg(args.year)
        cfg['special_chars'] = not args.no_special
        cfg['keyboard'] = not args.no_keyboard
        cfg['common_passwords'] = not args.no_common
        cfg['keywords'] = [k.strip() for k in args.keywords.split(',')] if args.keywords else []
        cfg['month_mode'] = args.month
        out = args.output
    else:
        parser.print_help()
        return

    print("\n[*] 正在生成密码字典...")
    t0 = time.time()
    
    gen = PassGen(cfg)
    passwords = gen.run()
    count = write_output(passwords, out)
    fs = os.path.getsize(out)

    print(f"[+] 生成完成!")
    print(f"    密码总数 : {count:,}")
    print(f"    文件大小 : {size_str(fs)}")
    print(f"    耗时     : {time.time()-t0:.2f}s")
    print(f"    输出文件 : {os.path.abspath(out)}\n")

if __name__ == '__main__':
    main()