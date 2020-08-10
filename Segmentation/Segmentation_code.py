# -*- coding: utf-8 -*-
"""

Created on Thu Apr 26 18:50:39 2018

@author: GUPTA50
"""

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pdfminer
import pandas as pd
import json
import os
import math
import re


def parseFiles(file, locationofjson):
    rejected_text = re.compile(r'^([0-9]{1,3}(\)|\.|\s+))$')
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    list5 = []
    list6 = []
    Index_key_List = []
    Line_JSON = []
    paragraph = []
    Line_JSON_1 = []
    my_list = []
    # for i in list1:
    with open(file, "rb") as fp:
                jsonfilename = file.split("\\")[-1]
                parser = PDFParser(fp)
                document = PDFDocument(parser)
                    # Check if the document allows text extraction. If not, abort.
                '''if not document.is_extractable:
                   raise "Not extractable"'''
                rsrcmgr = PDFResourceManager()
                laparams = LAParams()
                device = PDFPageAggregator(rsrcmgr, laparams=laparams)
                interpreter = PDFPageInterpreter(rsrcmgr, device)

                class Point(object):
                    def __init__(self, x, y):
                        self.x = x
                        self.y = y

                    def read_point(self, x, y):
                        self.x = x
                        self.y = y

                class Location(object):
                    def __init__(self, x1, y1, x2, y2):
                        self.leftpoint = Point(x1, y1)
                        self.rightpoint = Point(x2, y2)

                    def read_location(self, leftpoint, rightpoint):
                        self.leftpoint = leftpoint
                        self.rightpoint = rightpoint

                class Font(object):
                    def __init__(self, myFontName, myFontSize):
                        self.FontName = myFontName
                        self.FontSize = myFontSize

                class Character(object):
                    def __init__(self, location, font, value):
                        self.location = location
                        self.font = font
                        self.value = value

                    def read_character(location, font, value):
                        self.location = location
                        self.font = font
                        self.value = value

                class Word(object):
                    def __init__(self, listofCharacters, location, value):
                        self.listofCharacters = listofCharacters
                        self.location = location
                        self.value = value

                    def read_word(self, listofCharacters, location, value):
                        self.listofCharacters = listofCharacters
                        self.location = location
                        self.value = value

                class Line(object):
                    def __init__(self, listofWords, location, value):
                        self.listofWords = listofWords
                        self.location = location
                        self.value = value

                    def read_line(self, listofWords, location, value):
                        self.listofWords = listofWords
                        self.location = location
                        self.value = value

                class Page(object):
                    listofLines = []
                    page_number = 0

                    def __init__(self, listofLines, page_number):
                        self.listofLines = listofLines
                        self.page_number = page_number

                    def read_page(self, listoflines, page_number):
                        self.listoflines = listoflines
                        self.page_number = page_number

                class Document(object):
                    listofPages = []

                    def __init__(self, listofPages):
                        self.listofPages = listofPages

                    def read_document(self, listofPages):
                        self.listofPages = listofPages

                page_num = 0
                docobj = Document([])
                for page in PDFPage.create_pages(document):
                        # read the page into a layout object
                        interpreter.process_page(page)
                        layout = device.get_result()
                        page_num = page_num + 1
                        Index_key = 0
                        pageobj = Page([], page_num)
                        docobj.listofPages.append(pageobj)
                        # print (pageobj.page_number,pageobj.listofLines)
                        # docobj.listofPages.append(pageobj)
                        for obj in layout._objs:
                            if isinstance(obj, pdfminer.layout.LTTextBox):
                                text = obj.get_text()
                                paragraph.append(text)
                                # lineobj = Line([],Location(0,0,0,0))
                                for o in obj:
                                    if isinstance(o, pdfminer.layout.LTTextLine):
                                        text = o.get_text()
                                        lineobj = Line(
                                            [],
                                            Location(
                                                o.bbox[0],
                                                o.bbox[1],
                                                o.bbox[2],
                                                o.bbox[3],
                                            ),
                                            text,
                                        )
                                        pageobj.listofLines.append(lineobj)
                                        if text.strip():
                                            str1 = ""
                                            wordobj = Word([], Location(0, 0, 0, 0), "")
                                            Count = 0
                                            for c in o._objs:
                                                if isinstance(
                                                    c, pdfminer.layout.LTChar
                                                ):
                                                    if c._text != " ":
                                                        Count+=1
                                                        if (Count == 1):
                                                            Leftpoint_X = c.bbox[0]
                                                            Leftpoint_Y = c.bbox[1]
                                                        str1 = str1 + c._text
                                                        charobj = Character(
                                                            Location(
                                                                c.bbox[0],
                                                                c.bbox[1],
                                                                "",
                                                                "",
                                                            ),
                                                            Font(c.fontname, c.size),
                                                            c._text,
                                                        )
                                                        wordobj.listofCharacters.append(
                                                            charobj
                                                        )
                                                    else:
                                                        if len(str1) != 0:
                                                            wordobjtemp = wordobj.listofCharacters[
                                                                0
                                                            ]
                                                            wordobj.location.leftpoint = (
                                                                wordobjtemp.location.leftpoint
                                                            )
                                                            wordobjtemp = wordobj.listofCharacters[
                                                                len(
                                                                    wordobj.listofCharacters
                                                                )
                                                                - 1
                                                            ]
                                                            wordobj.value = str1
                                                            wordobj.location.rightpoint.x = c.bbox[
                                                                0
                                                            ]
                                                            wordobj.location.rightpoint.y = c.bbox[
                                                                1
                                                            ]
                                                            # print(wordobj.value,wordobj.location.leftpoint.x,wordobj.location.leftpoint.y,wordobj.location.rightpoint.x,wordobj.location.rightpoint.y)
                                                            lineobj.listofWords.append(
                                                                wordobj
                                                            )
                                                            # print (lineobj)
                                                            # wordobj = Word([],Location(0,0,0,0),"")
                                                            str1 = ""
                                                            continue
                                                else:
                                                    if len(str1) != 0:
                                                        wordobjtemp = wordobj.listofCharacters[
                                                            0
                                                        ]
                                                        wordobj.location.leftpoint = (
                                                            wordobjtemp.location.leftpoint
                                                        )
                                                        wordobjtemp = wordobj.listofCharacters[
                                                            len(
                                                                wordobj.listofCharacters
                                                            )
                                                            - 1
                                                        ]
                                                        wordobj.value = str1
                                                        wordobj.location.rightpoint.x = obj.bbox[
                                                            2
                                                        ]
                                                        wordobj.location.rightpoint.y = obj.bbox[
                                                            1
                                                        ]
                                                        # print(wordobj.value,wordobj.location.leftpoint.x,wordobj.location.leftpoint.y,wordobj.location.rightpoint.x,wordobj.location.rightpoint.y)
                                                        lineobj.listofWords.append(
                                                            wordobj
                                                        )
                                                        # wordobj = Word([],Location(0,0,0,0),"")
                                                        str1 = ""
                                                        continue
                                        if lineobj.value.strip() == "":
                                            # Line_data = {"Value": lineobj.value,"leftpoint_x": lineobj.location.leftpoint.x,"leftpoint_y": lineobj.location.leftpoint.y,"rightpoint_x": lineobj.location.rightpoint.x,"rightpoint_y": lineobj.location.rightpoint.y, "page_number": page_num,"Specification": ""}
                                            continue
                                        else:
                                            Line_data = {
                                                "Value": lineobj.value,
                                                "leftpoint_x": Leftpoint_X,
                                                "leftpoint_y": Leftpoint_Y,
                                                "rightpoint_x": lineobj.location.rightpoint.x,
                                                "rightpoint_y": lineobj.location.rightpoint.y,
                                                "font_name": charobj.font.FontName,
                                                "font_size": charobj.font.FontSize,
                                                "page_number": page_num,
                                                "Specification": "",
                                            }
                                        Line_JSON.append({"Line_Data": Line_data})
                                        # json_object = json.dumps(Line_data)
                            else:
                                pass
                        df = pd.DataFrame({"value": list1})
                        df1 = pd.DataFrame({"LeftPoint_X": list2})
                        df2 = pd.DataFrame({"LeftPoint_Y": list3})
                        df3 = pd.DataFrame({"RightPoint_X": list4})
                        df4 = pd.DataFrame({"RightPoint_Y": list5})
                        df5 = pd.DataFrame({"Font": list6})
                        writer = pd.ExcelWriter(
                            "pandas_simple_demo.xlsx", engine="xlsxwriter"
                        )
                        df.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=0
                        )
                        df1.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=1
                        )
                        df2.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=2
                        )
                        df3.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=3
                        )
                        df4.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=4
                        )
                        df5.to_excel(
                            writer, sheet_name="Sheet1", index=False, startcol=5
                        )
                        writer.save()
                        # print (type(Line_JSON))
                        # print (Line_JSON)
                        Line_JSON_1 = sorted(
                            Line_JSON,
                            key=lambda x: (
                                x["Line_Data"]["page_number"],
                                -(roundnumber(x["Line_Data"]["leftpoint_y"])),
                                roundnumber(round(x["Line_Data"]["leftpoint_x"], 0)),
                            ),
                        )
                return Line_JSON_1
                        # Line_JSON_1 = Line_JSON_1.decode('unicode_escape').encode('ascii','ignore')
                        # with open(
                        #     locationofjson + "\\" + jsonfilename + ".json", "w"
                        # ) as outfile:
                        #     json.dump(Line_JSON_1, outfile)
                        # with open(
                        #     locationofjson + "\\" + jsonfilename + ".txt",
                        #     "w",
                        #     encoding="utf-8",
                        # ) as outfile:
                        #     outfile.write(str(paragraph) + "\n")
                        # print (list_gap)
                        # print (pageobj.listofLines,pageobj.page_number)
                # for page in PDFPage.create_pages(document):
                #         # read the page into a layout object
                #         interpreter.process_page(page)
                #         layout = device.get_result()
                #         page_num = page_num + 1
                #         main_function(layout._objs)

# list1 = []


def roundnumber(n): 
    return int(math.ceil(n / 10.0)) * 10
    # # Smaller multiple 
    # a = (n // 10) * 10
      
    # # Larger multiple 
    # b = a + 10
      
    # # Return of closest of two 
    # return (b if n - a > b - n else a)


# def PDFLocation(pathofPDF):
#     for dirpath, dirname, filenames in os.walk(pathofPDF):
#         for file in filenames:
#             try:
#                 if file.lower().endswith(".pdf"):
#                     path = os.path.abspath(os.path.join(dirpath, file))
#                     list1.append(path)
#                 else:
#                     continue
#             except (FileNotFoundError, IOError):
#                 print("runtime exception")


# locationofpdf = input("Please enter the location of input pdf :\n")
# locationofjson = input("Please enter the location of output JSON :\n")
# PDFLocation(locationofpdf)
# parseFiles(list1)
