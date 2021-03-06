import requests
import hashlib
import uuid
import json
import time
import random
import math
import urllib.parse


class MyBot:

    def answer(self, msg):
        if '|' in msg:
            ss = msg.split("|")
            nextStr = ss[1] + " " + self.answer(ss[0])
            if len(ss) > 2:
                nextStr += " | " + '|'.join(ss[2:])
            return self.answer(nextStr)
        msg = str.strip(msg)
        splt = list(filter(None, msg.split(" ")))
        splt[0] = str.strip(splt[0])
        if len(splt) == 1:
            if splt[0] == 'talk':
                return self.randWord()
            if splt[0] == 'random':
                return str(random.random())
            if splt[0] == 'welcome':
                return "欢迎欢迎 热烈欢迎"
            if splt[0] == 'shutdown':
                return "你很坏哦"
            if splt[0] == 'reboot':
                return "重启中——重启失败——再次重启——重启成功！"
        if len(splt) == 2:
            if splt[0] == 'split':
                return ' '.join(list(splt[1]))
            if splt[0] == 'sort':
                return ''.join(sorted(list(splt[1].replace('\n', ''))))
            if splt[0] == 'list':
                return '\n'.join(list(splt[1]))
            if splt[0] == 'concat':
                return splt[1].replace('\n', '')
        if len(splt) == 3:
            if splt[0] == 'split':
                return ' '.join(splt[1].split(splt[2]))
            if splt[0] == 'append':
                return splt[2] + splt[1]
        if splt[0] == 'loop' and len(splt) >= 3:
            try:
                loopNum = int(splt[1])
                if loopNum > 10:
                    return "循环次数超过10了……我拒绝"
                result = []
                for i in range(loopNum):
                    result.append(self.answer(' '.join(splt[2:])))
                return '\n'.join(result)
            except Exception:
                return "我觉得你这语法有问题哦"
        if splt[0] == 'each' and len(splt) >= 2:
            result = []
            children = splt[-1].split('\n')
            for i in range(len(children)):
                splt[-1] = children[i]
                result.append(self.answer(' '.join(splt[1:])))
            return '\n'.join(result)
        if (splt[0] == 'translate' or splt[0] == 'trans') and len(splt) > 1:
            return self.translate(' '.join(splt[1:]))
        if (splt[0] == 'echo') and len(splt) > 1:
            return ''.join(splt[1:])
        if (splt[0] == 'reverse') and len(splt) > 1:
            return ''.join(splt[1:])[::-1]
        if (splt[0] == 'shuffle') and len(splt) > 1:
            return self.shuffle(''.join(splt[1:]))
        if (splt[0] == 'calc') and len(splt) > 1:
            return self.calc(''.join(splt[1:]))
        if splt[0] == 'import':
            return 'import! import! 天天import!'
        if splt[0] == 'sudo':
            return '你没有sudo的权限啦!!!'
        if splt[0] == 'baidu' and len(splt) > 1:
            return 'https://www.baidu.com/s?wd=' + urllib.parse.quote('+'.join(splt[1:]))
        return "……"

    def shuffle(self, msg):
        def swap(someStr, i, j):
            someStr[i], someStr[j] = someStr[j], someStr[i]

        msg = list(msg)
        for i in range(len(msg)):
            rand = random.randint(0, i)
            swap(msg, rand, i)
        return ''.join(msg)

    def translate(self, msg):
        r = Helper.connect(msg)
        return r

    def calc(self, expr):
        vstack = []
        ostack = []
        ops = ['+', '-', '*', '/']
        sops = ['sin', 'cos', 'sqrt']

        def subCalc(ost, vst):
            op = ost.pop()
            if op in ops:
                rvalue = float(vst.pop())
                lvalue = float(vst.pop())
                if op == '+':
                    vst.append(str(lvalue + rvalue))
                elif op == '-':
                    vst.append(str(lvalue - rvalue))
                elif op == '*':
                    vst.append(str(lvalue * rvalue))
                elif op == '/':
                    vst.append(str(lvalue / rvalue))
            elif op in sops:
                value = float(vst.pop())
                if op == 'sin':
                    vst.append(str(math.sin(value)))
                elif op == 'cos':
                    vst.append(str(math.cos(value)))
                elif op == 'sqrt':
                    vst.append(str(math.sqrt(value)))

        def getTokens(expr):
            tks = []
            bop = ['+', '-', '*', '/']
            ssop = ['sin', 'cos', 'sqrt', 'PI']
            mach = [
                {
                    's': 1,
                    'c': 2,
                    'P': 7,
                },
                {
                    'i': 4,
                    'q': 5,
                },
                {
                    'o': 3,
                },
                {
                    's': 'cos',
                },
                {
                    'n': 'sin',
                },
                {
                    'r': 6,
                },
                {
                    't': 'sqrt',
                },
                {
                    'I': 'PI',
                }
            ]
            lastDigit = False
            hasDot = False
            machineState = 0
            for i in range(len(expr)):
                if machineState > 0:
                    if expr[i] in mach[machineState].keys():
                        tState = mach[machineState][expr[i]]
                        if tState in ssop:
                            tks.append(tState)
                            machineState = 0
                        else:
                            machineState = tState
                    else:
                        return "error"
                elif expr[i].isdigit():
                    if lastDigit:
                        tks.append(tks.pop() + expr[i])
                    else:
                        tks.append(expr[i])
                        lastDigit = True
                elif expr[i] == ')':
                    lastDigit = False
                    hasDot = False
                    tks.append(')')
                elif expr[i] == '(':
                    lastDigit = False
                    hasDot = False
                    tks.append('(')
                elif expr[i] == '.' and not hasDot:
                    tks.append(tks.pop() + expr[i])
                    hasDot = True
                elif expr[i] in bop:
                    lastDigit = False
                    hasDot = False
                    tks.append(expr[i])
                elif expr[i] in mach[0].keys():
                    machineState = mach[0][expr[i]]
                    lastDigit = False
                    hasDot = False
                else:
                    return "error"
            return tks

        print(getTokens(expr))
        expr = getTokens(expr)
        if expr == 'error':
            return "我不会算这个，我只能算点简单的"
        for i in range(len(expr)):
            if expr[i][0].isdigit():
                vstack.append(expr[i])
            elif expr[i] == 'PI':
                vstack.append(str(math.pi))
            elif expr[i] == ')':
                try:
                    subCalc(ostack, vstack)
                except ZeroDivisionError:
                    return "我不能算这个！除以0你自己除！"
                except IndexError:
                    return "我不会了，对不起（卑微）"
            elif expr[i] in ops or expr[i] in sops:
                ostack.append(expr[i])
        while len(ostack) > 0:
            try:
                subCalc(ostack, vstack)
            except ZeroDivisionError:
                return "我不能算这个！除以0你自己除！"
            except IndexError:
                return "我不会了，对不起（卑微）"
        result = vstack.pop()
        if result.endswith(".0"):
            return result[:-2]
        return result

    def randWord(self):
        words = [
            '五十六个星座，五十六枝花',
            '相信科学',
            'Internal server eeeeeeerror',
            '岩烧店的烟味弥漫隔壁是国术馆',
            '安静的巷口，单车和人交错经过',
            '还记得昨天，那个夏天，微风吹过的一瞬间',
            '手中握着格桑花呀，美得让我忘了摘下',
            '风吹落最后一片叶，我的心也飘着雪',
            'System.gc()',
            '黄色烟硝还在飘,头顶风帆在鼓噪',
            '因为我，仍有梦，依然将你放在我心中',
            'PHP是世界上最好的语言',
            'We are the world, we are the children',
            '我啥也不会说',
            '听说我这个talk功能就只是随机的',
        ]
        index = random.randint(0, len(words) - 1)
        return words[index]


class Helper:
    YOUDAO_URL = 'http://openapi.youdao.com/api'
    APP_KEY = ''
    APP_SECRET = ''

    @staticmethod
    def encrypt(signStr):
        hash_algorithm = hashlib.sha256()
        hash_algorithm.update(signStr.encode('utf-8'))
        return hash_algorithm.hexdigest()

    @staticmethod
    def truncate(q):
        if q is None:
            return None
        size = len(q)
        return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]

    @staticmethod
    def do_request(data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(Helper.YOUDAO_URL, data=data, headers=headers)

    @staticmethod
    def connect(q):
        # q = "test"

        data = {}
        data['from'] = 'auto'
        data['to'] = 'zh-CHS'
        data['signType'] = 'v3'
        curtime = str(int(time.time()))
        data['curtime'] = curtime
        salt = str(uuid.uuid1())
        signStr = Helper.APP_KEY + Helper.truncate(q) + salt + curtime + Helper.APP_SECRET
        sign = Helper.encrypt(signStr)
        data['appKey'] = Helper.APP_KEY
        data['q'] = q
        data['salt'] = salt
        data['sign'] = sign

        response = Helper.do_request(data)
        return json.loads(response.content.decode('utf-8'))["translation"][0]

