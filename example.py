import CIMR
import os
import time


# set CIMR parameter --------------------
CIMR.sizeForCrop = 2000
CIMR.sizeForStride = 1000
CIMR.margin_to_include = 2
symbol_to_split_result = ','

img_dir = "./data"
result_dir = './result'
setDate = time.localtime()
#-----------------------------------------


# time_info = str(setDate.tm_year) + (str(setDate.tm_mon)).zfill(2) + \
#             (str(setDate.tm_mday)).zfill(2) + '_' + (str(setDate.tm_hour)).zfill(2) + '.' \
#             + (str(setDate.tm_min)).zfill(2) + '_'
# result_dir_for_each_test = result_dir + '/' + time_info
# os.mkdir(result_dir_for_each_test)


print("Cropping...")
original_img_list = []
CIMR.crop_big_image(result_dir, img_dir)
resized_img_list = []

sub_txt_result_dir_List = []  # to merge the result

print("Detecting...")

for foldername in os.listdir(img_dir):  # ./data
    subImgDir = os.path.join(img_dir, foldername)

    if os.path.isdir(subImgDir):

        sub_txt_result_dir = os.path.join(result_dir, foldername + '_txt')
        sub_img_result_dir = os.path.join(result_dir, foldername)
        sub_txt_result_dir_List.append(sub_txt_result_dir)  # ['img1_txt', img2_txt']  _txt folder

        os.mkdir(sub_txt_result_dir)

        for file in os.listdir(subImgDir):  # per subImg

            full_cropped_img_file_path = os.path.join(subImgDir, file)
            cropped_img_name = os.path.basename(full_cropped_img_file_path)
            cropped_img_name = str(cropped_img_name.split('.')[0])
            fullCropTxtFilePath = os.path.join(sub_txt_result_dir, cropped_img_name + ".txt")


            '''
            
            Run your detection engine
            '''

    else:  # 그냥 도면 원본파일
        original_img_list.append(subImgDir)

# --- merge ---------------------------
print("Merging detected boxes...")
for sub_txt_result_dir in sub_txt_result_dir_List:
    CIMR.merge_result(sub_txt_result_dir, result_dir)

# -- recognize --------------------------
print("Recognizing...")
merged_text_list = []
for file in os.listdir(result_dir):
    if file.endswith(".txt"):
        merged_text_list.append(os.path.join(result_dir, file))

for merged_text_path, resizedIm in zip(merged_text_list, resized_img_list):
    '''

    Run your detection engine
    '''

