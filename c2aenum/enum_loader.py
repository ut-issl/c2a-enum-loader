#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob


class C2aEnum:
    def __init__(self, c2a_src_path, encoding):
        self.path = c2a_src_path.replace("//", "/")
        search_path = (self.path + "/**").replace("//", "/")
        self.encoding = encoding

        p_file_ext = re.compile(r".*\.(c|cc|cpp|h|hh|hpp)$")
        files_tmp = [
            file_path.replace("\\", "/")
            for file_path in glob.glob(search_path, recursive=True)
            if p_file_ext.fullmatch(file_path)
        ]

        files = [
            file_path
            for file_path in files_tmp
            if "Examples" not in file_path.replace(self.path, "")
            and (
                "src_core" in file_path.replace(self.path, "")
                or "src_user" in file_path.replace(self.path, "")
            )
        ]

        for file in files:
            self._load_enum_from_file(file)

    def _load_enum_from_file(self, path):
        with open(path, encoding=self.encoding) as f:
            last_enum_id = -1
            mode = 0  # enum の中でどれを探している段階にいるか
            p_typedef_enum = re.compile(r"^ *typedef *enum *\s$")
            p_start_brackets = re.compile(r"^ *{.*\s$")
            p_end_brackets = re.compile(r"^ *}.*\s$")
            p_with_id = re.compile(r"^ *(\w+) *= *([-\w]+)")
            p_without_id = re.compile(r"^ *(\w+)")
            for line in f.readlines():
                if mode == 0 and p_typedef_enum.fullmatch(line):
                    mode += 1
                elif mode == 1 and p_start_brackets.fullmatch(line):
                    mode += 1
                elif mode == 2 and p_end_brackets.fullmatch(line):
                    mode = 0
                    last_enum_id = -1
                elif mode == 2:
                    # コメント削除 & 削除した後に末尾の空白削除
                    # FIXME: 複数行の /* */ みたいなコメントは死ぬ
                    line = re.sub("//.*", "", line).rstrip()
                    m_with_id = p_with_id.match(line)
                    m_without_id = p_without_id.match(line)
                    if not m_with_id and not m_without_id:
                        continue
                    if m_with_id:
                        enum_name = m_with_id.group(1)
                        enum_id = m_with_id.group(2)
                    else:
                        enum_name = m_without_id.group(1)
                        enum_id = str(last_enum_id + 1)

                    if enum_id[:2] == "0x":
                        enum_id = int(enum_id, base=16)
                    else:
                        enum_id = int(enum_id, base=10)

                    self.__setattr__(enum_name, enum_id)
                    last_enum_id = enum_id


def load_enum(c2a_src_path, encoding) -> C2aEnum:
    c2a_enum = C2aEnum(c2a_src_path, encoding)
    return c2a_enum


if __name__ == "__main__":
    # 単なる動作確認用
    c2a_enum = load_enum(os.path.dirname(__file__) + "/../../..", "utf-8")
