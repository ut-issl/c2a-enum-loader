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

        files_tmp = [p.replace("\\", "/") for p in glob.glob(search_path, recursive=True)]

        files = [
            p
            for p in files_tmp
            if re.fullmatch(r".*\.(c|cc|cpp|h|hh|hpp)$", p)
            and "Examples" not in p.replace(self.path, "")
            and ("src_core" in p.replace(self.path, "") or "src_user" in p.replace(self.path, ""))
        ]

        for file in files:
            self._load_enum_from_file(file)

    def _load_enum_from_file(self, path):
        with open(path, encoding=self.encoding) as f:
            last_enum_id = -1
            mode = 0
            for line in f.readlines():
                line = line.rstrip()
                if mode == 0 and line == "typedef enum":
                    mode += 1
                elif mode == 1 and line == "{":
                    mode += 1
                elif mode == 2 and len(line) >= 1 and line[0] == "}":
                    mode = 0
                    last_enum_id = -1
                elif mode == 2:
                    # コメント削除 & 削除した後に末尾の空白削除
                    line = re.sub("//.*", "", line).rstrip()
                    p_with_id = re.compile(r"^  (\w+) += +([-\w]+)")
                    p_without_id = re.compile(r"^  (\w+)")
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
