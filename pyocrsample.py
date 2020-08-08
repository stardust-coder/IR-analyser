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

    finaldata = []
    for row in results:
        item = re.sub(" ","",re.match("[^0-9０-９]+", row).group())
        item = re.sub("央定","固定",item)
        cost = re.findall("[0-9０-９]+", row)
        if len(cost) != 2:
            str1 = "".join(cost[:int(len(cost)/2)])
            str2 = "".join(cost[int(len(cost)/2):])
            cost = [str1,str2]
        finaldata.append([item,cost[0],cost[1]])
    return finaldata

assets_extracted = totext(assets)
liabilities_extracted = totext(liabilities)#トヨタでバグるなぁ


print(assets_extracted)
print(liabilities_extracted)
