# -*- coding:utf-8 -*-

import time
time1=time.time()

# AC自动机算法
class node(object):
    def __init__(self):
        self.next = {}
        self.fail = None
        self.isWord = False
        self.word = ""

class ac_automation(object):

    def __init__(self):
        self.root = node()

    # 添加敏感词函数
    def addword(self, word):
        temp_root = self.root
        for char in word:
            if char not in temp_root.next:
                temp_root.next[char] = node()
            temp_root = temp_root.next[char]
        temp_root.isWord = True
        temp_root.word = word

    # 失败指针函数
    def make_fail(self):
        temp_que = []
        temp_que.append(self.root)
        while len(temp_que) != 0:
            temp = temp_que.pop(0)
            p = None
            for key,value in temp.next.item():
                if temp == self.root:
                    temp.next[key].fail = self.root
                else:
                    p = temp.fail
                    while p is not None:
                        if key in p.next:
                            temp.next[key].fail = p.fail
                            break
                        p = p.fail
                    if p is None:
                        temp.next[key].fail = self.root
                temp_que.append(temp.next[key])

    # 查找敏感词函数
    def search(self, content):
        p = self.root
        result = []
        currentposition = 0

        while currentposition < len(content):
            word = content[currentposition]
            while word in p.next == False and p != self.root:
                p = p.fail

            if word in p.next:
                p = p.next[word]
            else:
                p = self.root

            if p.isWord:
                result.append(p.word)
                p = self.root
            currentposition += 1
        return result

    # 加载敏感词库函数
    def parse(self, path):
        with open(path,encoding='utf-8') as f:
            for keyword in f:
                self.addword(str(keyword).strip())

    # 敏感词替换函数
    def words_replace(self, text):
        """
        :param ah: AC自动机
        :param text: 文本
        :return: 过滤敏感词之后的文本
        """
        result = list(set(self.search(text)))
        for x in result:
            m = text.replace(x, '*' * len(x))
            text = m
        return text