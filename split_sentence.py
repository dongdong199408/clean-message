import re
#自定义断句
def split_sentence(line):
    cutLineFlag = ["，", ",", "？", "！", "。", ".", "；", "?", "!", "...", "\n", "\r", "\t"]
    stop_words = []
    sentenceList = []
    #删除空个字符
    words = re.sub(" ", "", line)
    #删除前后文空格
    words = words.strip()
    oneSentence = ""
    if not words == '':
        for word in words:
            if word not in cutLineFlag:
                oneSentence = oneSentence + word
            else:
                oneSentence = oneSentence + word
                # 删除作业相关
                stop = True
                for w in stop_words:
                    if w in oneSentence:
                        stop = False
                        break
                if oneSentence.__len__() > 2 and stop == True:
                    # 删除：开头
                    oneSentence=re.sub("^.*[:：]", "", oneSentence)
                    sentenceList.append(oneSentence.strip())
                oneSentence = ""
        if len(sentenceList)==0:
            sentenceList.append(oneSentence.strip())
    return sentenceList

if __name__=='__main__':
    text='''?'''
    sentencelist=split_sentence(text)
    for s in sentencelist:
        print(len(s))
