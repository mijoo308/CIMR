import CIMR
import os
import time


# set CIMR parameter --------------------
CIMR.crop_size = 2000
CIMR.stride_size = 1000
CIMR.margin_to_include = 2
symbol_to_split_result = ','

img_dir = "./data"
result_dir = './result'
setDate = time.localtime()
#-----------------------------------------


print("Cropping...")
original_img_list = []
CIMR.crop_big_image(result_dir, img_dir)


sub_txt_result_dir_List = []  # to merge the result

print("Detecting...")

for foldername in os.listdir(img_dir):  # ./data
    sub_img_dir = os.path.join(img_dir, foldername)

    if os.path.isdir(sub_img_dir):

        sub_txt_result_dir = os.path.join(result_dir, foldername + '_txt')
        sub_img_result_dir = os.path.join(result_dir, foldername)
        sub_txt_result_dir_List.append(sub_txt_result_dir)  # ['img1_txt', img2_txt']  _txt folder

        os.mkdir(sub_txt_result_dir)

        for file in os.listdir(sub_img_dir):  # per subImg

            full_cropped_img_file_path = os.path.join(sub_img_dir, file)
            cropped_img_name = os.path.basename(full_cropped_img_file_path)
            cropped_img_name = str(cropped_img_name.split('.')[0])
            full_crop_txt_file_path = os.path.join(sub_txt_result_dir, cropped_img_name + ".txt")


            '''
            
            Run your detection engine
            '''

    else:
        original_img_list.append(sub_img_dir)

print("Merging detected boxes...")
for sub_txt_result_dir in sub_txt_result_dir_List:
    CIMR.merge_result(sub_txt_result_dir, result_dir)

print("Recognizing...")
merged_text_list = []
for file in os.listdir(result_dir):
    if file.endswith(".txt"):
        merged_text_list.append(os.path.join(result_dir, file))

for merged_text_path, resizedIm in zip(merged_text_list, original_img_list):
    '''

    Run your recognition engine
    '''

