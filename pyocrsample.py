from PIL import Image
import sys
import re

import pyocr
import pyocr.builders

tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
print("Will use tool '%s'" % (tool.get_name()))

#langs = tool.get_available_languages()
#print("Available languages: %s" % ", ".join(langs))
lang = "jpn"#日本語でOCR
print("Will use lang '%s'" % (lang))

assets = input() + ".png"
liabilities = input() + ".png"

def totext(imagefilename):
    #認識するpngのファイル名
    txt = tool.image_to_string(
        Image.open(imagefilename),
        lang="jpn",
        builder=pyocr.builders.TextBuilder()
        )

    txt = re.sub(", |,","",txt)#,除去
    txt = txt + "\n"
    #print(txt)

    results = re.findall(r'.+合計.+\n', txt) #(patter,target)
    if results == []:
        print("OCR has failed!")
        return []

    finaldata = {}
    for row in results:
        item = re.sub(" ","",re.match("[^0-9０-９]+", row).group())
        item = re.sub("央定","固定",item)
        cost = re.findall("[0-9０-９]+", row)
        if len(cost) != 2:
            str1 = "".join(cost[:int(len(cost)/2)])
            str2 = "".join(cost[int(len(cost)/2):])
            cost = [str1,str2]
        finaldata[item] = [cost[0],cost[1]]
    return finaldata

assets_extracted = totext(assets)#辞書型
liabilities_extracted = totext(liabilities)
total = int(assets_extracted["資産合計"][0])#liabilities[-1][1]と同じ値のはず

print(assets_extracted)
print(liabilities_extracted)
print(total)

year = 1 #前事業年度なら0, 今事業年度なら1

####グラフ描画
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(font='IPAexGothic')
assets_index = []
assets_rawdata = []
liabilities_index = []
liabilities_rawdata = []

for element in ["固定資産合計","流動資産合計"]:
    #name = assets_extracted[element][0]
    amount = assets_extracted[element][year]
    assets_index.append(element)
    assets_rawdata.append([int(amount),0])

for element in ["純資産合計","固定負債合計", "流動負債合計"]:
    #name = element[0]
    amount = liabilities_extracted[element][year]
    liabilities_index.append(element)
    liabilities_rawdata.append([0,int(amount)])

rawindex = assets_index + liabilities_index
rawdata = assets_rawdata + liabilities_rawdata

#プロット用データに加工
dataset = pd.DataFrame(rawdata,
                       columns=['借方', '貸方'],
                       index=rawindex)

print(dataset)#データセット確認


#プロット！
fig, ax = plt.subplots(figsize=(10, 8))
for i in range(len(dataset)):
    ax.bar(dataset.columns, dataset.iloc[i], bottom=dataset.iloc[:i].sum())
    for j in range(len(dataset.columns)):
        itemlabelnum = dataset.iloc[i, j]
        itemlabeltext = dataset.index[i]
        if itemlabelnum/total >= 0.05:#小さすぎる文字を表示しないように
            #ラベル文字のオプション設定
            plt.text(x=j,
                     y=dataset.iloc[:i, j].sum() + (dataset.iloc[i, j] / 2),
                     s= itemlabeltext + " " + str(itemlabelnum),
                     ha='center',
                     va='bottom',
                     color = "white"
                    )
ax.set(xlabel='バランスシート', ylabel='額（円）')
#ax.legend(dataset.index)#凡例は不要
plt.show()
