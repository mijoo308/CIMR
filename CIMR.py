import cv2
import os
import PIL
from PIL import ImageDraw, ImageFont, Image

#--------Param--------
#
# drawing_path = '' #
crop_size = 2000
stride_size = 1000
#
# result_path = ''
# origin_width = 9933
# origin_height = 7016


margin_to_include = 2  # margin to include in results
symbol_to_split_result = ','  # detection result format would be xmin,ymin,xmax,ymax
#---------------------

# def resizeBigImg(src):
#     resizedImg = src.Image.resize((6622, 4677))
#     return resizedImg


def getXposYpos(width, height):
    x_pos_list = []
    y_pos_list = []
    x_pos_list.append(0)
    y_pos_list.append(0)

    start_x = 0
    while 1:
        start_x = start_x + stride_size
        if start_x + crop_size > width:
            start_x = width - crop_size
            x_pos_list.append(start_x)
            break
        else:
            x_pos_list.append(start_x)

    start_y = 0
    while 1:
        start_y = start_y + stride_size
        if start_y + crop_size > height:
            start_y = height - crop_size
            y_pos_list.append(start_y)
            break
        else:
            y_pos_list.append(start_y)

    return x_pos_list, y_pos_list


def crop_big_image(result_root, dirname): # drawing_path
    imgNames_withExt = os.listdir(dirname)  # [S199.jpg, S211-100.jpg, S211-103.jpg]
    print(imgNames_withExt)

    already_exist = False # is already cropped

    only_img_list = []
    for imgName_withExt in imgNames_withExt:
        full_img_path = os.path.join(dirname, imgName_withExt)
        if os.path.isdir(full_img_path):
            already_exist = True
        else:
            only_img_list.append(full_img_path)


    if not already_exist:
        for imgName_withExt in imgNames_withExt:  # S199.jpg
            print(imgName_withExt)
            imgName = os.path.splitext(imgName_withExt)[0]  # S199
            full_img_path = os.path.join(dirname, imgName_withExt)

            crop_result_dir = os.path.join(dirname, imgName)  # make dir named with img name
            if not os.path.isdir(crop_result_dir):
                os.mkdir(crop_result_dir)

                drawing = cv2.imread(full_img_path)

                cv2.imwrite(os.path.join(result_root, imgName + ".jpg"), drawing)

                drawing_width = drawing.shape[1]
                drawing_height = drawing.shape[0]

                x_pos_list, y_pos_list = getXposYpos(drawing_width, drawing_height)

                y_num = 0
                for y in y_pos_list:
                    x_num = 0
                    for x in x_pos_list:
                        cropped_img = drawing[y:y + crop_size, x:x + crop_size]
                        save_name = str(imgName) + '_' + str(x_num) + '_' + str(y_num) + '.jpg'
                        cv2.imwrite(os.path.join(crop_result_dir, save_name), cropped_img)
                        x_num += 1
                    y_num += 1
    else:
        for only_img in only_img_list:
            drawing = cv2.imread(only_img)
            imgName = os.path.splitext(os.path.basename(only_img))[0]
            print(imgName)

            cv2.imwrite(os.path.join(result_root, imgName + ".jpg"), drawing)


def mergeResult(dir, resultRoot): #per img

    txtNames_withExt = os.listdir(dir)

    img_name = os.path.basename(dir)
    img_name = str(img_name.split('_')[0])
    final_txt_result_path = os.path.join(resultRoot, img_name + ".txt")
    f_write = open(final_txt_result_path, 'w')

    full_img_path = os.path.join(resultRoot, img_name + ".jpg")
    drawing = cv2.imread(full_img_path)
    drawing_width = drawing.shape[1]
    drawing_height = drawing.shape[0]

    xPosList, yPosList = getXposYpos(drawing_width, drawing_height)


    for txtName_withExt in txtNames_withExt: # per subDrawing
        recognition_txt_path = os.path.join(dir, txtName_withExt)
        txtName = str(txtName_withExt.split('.')[0])

        relative_xpos = int(txtName.split('_')[1])
        relative_ypos = int(txtName.split('_')[2])


        sub_drawing_L = xPosList[relative_xpos]
        sub_drawing_T = yPosList[relative_ypos]
        sub_drawing_R = sub_drawing_L + crop_size
        sub_drawing_B = sub_drawing_T + crop_size

        xPosList_LastIndex = len(xPosList) - 1
        yPosList_LastIndex = len(yPosList) - 1

        case = 0
        right_side_in_common_L = 0
        down_side_in_common_T = 0

        if relative_xpos != xPosList_LastIndex and relative_ypos != yPosList_LastIndex:
            case = 1
            right_side_in_common_L = xPosList[relative_xpos + 1]
            down_side_in_common_T = yPosList[relative_ypos + 1]

        elif relative_ypos != yPosList_LastIndex:  # end of X
            case = 2
            down_side_in_common_T = yPosList[int(relative_ypos) + 1]

        elif relative_xpos != xPosList_LastIndex:  # end of Y
            case = 3
            right_side_in_common_L = xPosList[int(relative_xpos) + 1]

        else:  # end of X and Y
            case = 4

        box_detection_result_file = open(recognition_txt_path, 'r')
        lines = box_detection_result_file.readlines()
        box_detection_result_file.close()

        for line in lines: #per detection Box

            parsedBox = line.split(symbol_to_split_result)
            relB_xmin = int(parsedBox[0])
            relB_ymin = int(parsedBox[1])
            relB_xmax = int(parsedBox[2])
            relB_ymax = int(parsedBox[3])

            absB_xmin = sub_drawing_L + relB_xmin
            absB_ymin = sub_drawing_T + relB_ymin
            absB_xmax = sub_drawing_L + relB_xmax
            absB_ymax = sub_drawing_T + relB_ymax

            if case == 1:
                if sub_drawing_L + margin_to_include < absB_xmin < right_side_in_common_L and sub_drawing_T + margin_to_include < absB_ymin < down_side_in_common_T:
                    resultData = str(absB_xmin) + symbol_to_split_result + str(absB_ymin) + symbol_to_split_result + str(absB_xmax) + symbol_to_split_result + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 2:  # end of X
                if sub_drawing_L + margin_to_include < absB_xmin and sub_drawing_T + margin_to_include < absB_ymin < down_side_in_common_T:
                    resultData = str(absB_xmin) + symbol_to_split_result + str(absB_ymin) + symbol_to_split_result + str(absB_xmax) + symbol_to_split_result + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 3:  # end of Y
                if sub_drawing_L + margin_to_include < absB_xmin < right_side_in_common_L and sub_drawing_T + margin_to_include < absB_ymin:
                    resultData = str(absB_xmin) + symbol_to_split_result + str(absB_ymin) + symbol_to_split_result + str(absB_xmax) + symbol_to_split_result + str(absB_ymax) + "\n"
                    f_write.write(resultData)

            elif case == 4:  # end of X and Y
                if sub_drawing_L + margin_to_include < absB_xmin and sub_drawing_T + margin_to_include < absB_ymin:
                    resultData = str(absB_xmin) + symbol_to_split_result + str(absB_ymin) + symbol_to_split_result + str(absB_xmax) + symbol_to_split_result + str(absB_ymax) + "\n"
                    f_write.write(resultData)

    f_write.close()

#
# def return_to_original_size(exceptXpos, exceptYpos, txt_dir, outpath):
#     basename = os.path.basename(txt_dir)
#     txt_name = str(basename.split('_')[0])
#     filename_to_save = os.path.join(outpath, txt_name + "_origin_result.txt")
#
#     f_to_read = open(txt_dir, 'r', encoding='UTF8')
#     lines = f_to_read.readlines()
#     f_to_read.close()
#
#     f_to_write = open(filename_to_save, 'w', encoding='UTF8')
#     for line in lines:
#         parsed_box = line.split('ㅣ')
#         resized_xmin = int(parsed_box[0])
#         resized_ymin = int(parsed_box[1])
#         resized_xmax = int(parsed_box[2])
#         resized_ymax = int(parsed_box[3])
#         Tstring = parsed_box[4]
#         orientation = parsed_box[5]
#         confidence = parsed_box[6]
#
#         #
#         # origin_xmin = int(resized_xmin*3/2)
#         # origin_ymin = int(resized_ymin*3/2)
#         # origin_xmax = int(resized_xmax*3/2)
#         # origin_ymax = int(resized_ymax*3/2)
#         #
#
#         if not(origin_xmax > exceptXpos and origin_ymax > exceptYpos):
#             data = str(origin_xmin) + "ㅣ" + str(origin_ymin) + "ㅣ" + str(origin_xmax) + "ㅣ" + str(origin_ymax) + "ㅣ" + Tstring + "ㅣ" + orientation + 'ㅣ' + confidence
#             f_to_write.write(data)
#         # data = str(origin_xmin) + "ㅣ" + str(origin_ymin) + "ㅣ" + str(origin_xmax) + "ㅣ" + str(
#         #     origin_ymax) + "ㅣ" + Tstring + "ㅣ" + orientation + 'ㅣ' + confidence
#         # f_to_write.write(data)
#
#     f_to_write.close()












