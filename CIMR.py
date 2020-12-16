import cv2
import os
import PIL
from PIL import ImageDraw, ImageFont, Image

#--------Param--------
#
# drawing_path = '' #
sizeForCrop = 2000
sizeForStride = 1000
#
# result_path = ''
originWidth = 9933
originHeight = 7016

#---------------------

def resizeBigImg(src):
    resizedImg = src.Image.resize((6622, 4677))
    return resizedImg


def getXposYpos(width, height):
    xPosList = []
    yPosList = []
    xPosList.append(0)
    yPosList.append(0)

    startX = 0
    while 1:
        startX = startX + sizeForStride
        if startX + sizeForCrop > width:
            startX = width - sizeForCrop
            xPosList.append(startX)
            break
        else:
            xPosList.append(startX)

    startY = 0
    while 1:
        startY = startY + sizeForStride
        if startY + sizeForCrop > height:
            startY = height - sizeForCrop
            yPosList.append(startY)
            break
        else:
            yPosList.append(startY)

    return xPosList, yPosList


def cropBigImage(result_root, dirname, resizedWidth = originWidth, resizedHeight = originHeight): # drawing_path
    imgNames_withExt = os.listdir(dirname)
    for imgName_withExt in imgNames_withExt:
        imgName = os.path.splitext(imgName_withExt)[0]
        full_img_path = os.path.join(dirname, imgName_withExt)

        crop_result_dir = os.path.join(dirname, imgName)  # 해당 도면이름의 dir생성  (crop result 폴더)
        if not os.path.isdir(crop_result_dir):
            os.mkdir(crop_result_dir)

            drawing = cv2.imread(full_img_path)

            resizedImg = cv2.resize(drawing, dsize=(resizedWidth, resizedHeight))
            cv2.imwrite(os.path.join(result_root, imgName + ".jpg"), resizedImg)


            xPosList, yPosList = getXposYpos(resizedWidth, resizedHeight)

            y_num = 0
            for y in yPosList:
                x_num = 0
                for x in xPosList:
                    croppedImg = resizedImg[y:y + sizeForCrop, x:x + sizeForCrop]
                    save_name = str(imgName) + '_' + str(x_num) + '_' + str(y_num) + '.jpg'
                    cv2.imwrite(os.path.join(crop_result_dir, save_name), croppedImg)
                    x_num += 1
                y_num += 1


def mergeResult(dir, resultRoot): #per Drawing

    txtNames_withExt = os.listdir(dir)

    img_name = os.path.basename(dir)
    img_name = str(img_name.split('_')[0])
    finalTxtResultPath = os.path.join(resultRoot, img_name + ".txt")
    f_write = open(finalTxtResultPath, 'w')


    xPosList, yPosList = getXposYpos(originWidth, originHeight)



    for txtName_withExt in txtNames_withExt: # per subDrawing
        recognition_txt_path = os.path.join(dir, txtName_withExt)
        txtName = str(txtName_withExt.split('.')[0])

        relativeXpos = int(txtName.split('_')[1])
        # print("relativeXPos" + str(relativeXpos))
        relativeYpos = int(txtName.split('_')[2])
        # print("relativeYPos" + str(relativeYpos))

        subDrawingL = xPosList[relativeXpos]
        subDrawingT = yPosList[relativeYpos]
        subDrawingR = subDrawingL + sizeForCrop
        subDrawingB = subDrawingT + sizeForCrop

        xPosList_LastIndex = len(xPosList) - 1
        yPosList_LastIndex = len(yPosList) - 1

        case = 0
        rightSideInCommonL = 0
        downSideInCommonT = 0
        if relativeXpos != xPosList_LastIndex and relativeYpos != yPosList_LastIndex:  # 둘다 마지막 아님
            case = 1
            rightSideInCommonL = xPosList[relativeXpos + 1]
            downSideInCommonT = yPosList[relativeYpos + 1]

        elif relativeYpos != yPosList_LastIndex:  # x만 마지막
            case = 2
            downSideInCommonT = yPosList[int(relativeYpos) + 1]

        elif relativeXpos != xPosList_LastIndex:  # y만 마지막
            case = 3
            rightSideInCommonL = xPosList[int(relativeXpos) + 1]

        else:  # 둘 다 마지막
            case = 4

        # print("case: " + str(case))
        craftTessFile = open(recognition_txt_path, 'r')
        lines = craftTessFile.readlines()
        craftTessFile.close()

        for line in lines: #per detection Box
            # draw = ImageDraw.Draw(newImageForMerge)
            parsedBox = line.split('ㅣ')
            relB_xmin = int(parsedBox[0])
            relB_ymin = int(parsedBox[1])
            relB_xmax = int(parsedBox[2])
            relB_ymax = int(parsedBox[3])
            # Tstring = parsedBox[4]

            absB_xmin = subDrawingL + relB_xmin
            absB_ymin = subDrawingT + relB_ymin
            absB_xmax = subDrawingL + relB_xmax
            absB_ymax = subDrawingT + relB_ymax

            if case == 1:  # 둘다 마지막 아님
                # if absB_xmin != subDrawingL and absB_ymin != subDrawingT and absB_xmin < rightSideInCommonL and absB_ymin < downSideInCommonT:
                if subDrawingL + 2 < absB_xmin < rightSideInCommonL and subDrawingT + 2 < absB_ymin < downSideInCommonT:
                    resultData = str(absB_xmin) + "ㅣ" + str(absB_ymin) + "ㅣ" + str(absB_xmax) + "ㅣ" + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 2:  # x만 마지막
                # if absB_xmin != subDrawingL and absB_ymin != subDrawingT and absB_ymin < downSideInCommonT:
                if subDrawingL + 2 < absB_xmin and subDrawingT + 2 < absB_ymin < downSideInCommonT:
                    resultData = str(absB_xmin) + "ㅣ" + str(absB_ymin) + "ㅣ" + str(absB_xmax) + "ㅣ" + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 3:  # y만 마지막
                # if absB_xmin != subDrawingL and absB_ymin != subDrawingT and absB_xmin < rightSideInCommonL:
                if subDrawingL + 2 < absB_xmin < rightSideInCommonL and subDrawingT + 2 < absB_ymin:
                    resultData = str(absB_xmin) + "ㅣ" + str(absB_ymin) + "ㅣ" + str(absB_xmax) + "ㅣ" + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 4:  # 둘다 마지막
                # if absB_xmin != subDrawingL and absB_ymin != subDrawingT:
                if subDrawingL + 2 < absB_xmin and subDrawingT + 2 < absB_ymin:
                    resultData = str(absB_xmin) + "ㅣ" + str(absB_ymin) + "ㅣ" + str(absB_xmax) + "ㅣ" + str(absB_ymax) + "\n"
                    f_write.write(resultData)


    f_write.close()


def return_to_original_size(exceptXpos, exceptYpos, txt_dir, outpath):
    basename = os.path.basename(txt_dir)
    txt_name = str(basename.split('_')[0])
    filename_to_save = os.path.join(outpath, txt_name + "_origin_result.txt")

    f_to_read = open(txt_dir, 'r', encoding='UTF8')
    lines = f_to_read.readlines()
    f_to_read.close()

    f_to_write = open(filename_to_save, 'w', encoding='UTF8')
    for line in lines:
        parsed_box = line.split('ㅣ')
        resized_xmin = int(parsed_box[0])
        resized_ymin = int(parsed_box[1])
        resized_xmax = int(parsed_box[2])
        resized_ymax = int(parsed_box[3])
        Tstring = parsed_box[4]
        orientation = parsed_box[5]
        confidence = parsed_box[6]

        #
        # origin_xmin = int(resized_xmin*3/2)
        # origin_ymin = int(resized_ymin*3/2)
        # origin_xmax = int(resized_xmax*3/2)
        # origin_ymax = int(resized_ymax*3/2)
        #
        origin_xmin = int(resized_xmin)
        origin_ymin = int(resized_ymin)
        origin_xmax = int(resized_xmax)
        origin_ymax = int(resized_ymax)

        if not(origin_xmax > exceptXpos and origin_ymax > exceptYpos):
            data = str(origin_xmin) + "ㅣ" + str(origin_ymin) + "ㅣ" + str(origin_xmax) + "ㅣ" + str(origin_ymax) + "ㅣ" + Tstring + "ㅣ" + orientation + 'ㅣ' + confidence
            f_to_write.write(data)
        # data = str(origin_xmin) + "ㅣ" + str(origin_ymin) + "ㅣ" + str(origin_xmax) + "ㅣ" + str(
        #     origin_ymax) + "ㅣ" + Tstring + "ㅣ" + orientation + 'ㅣ' + confidence
        # f_to_write.write(data)

    f_to_write.close()












