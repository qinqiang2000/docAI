import os
from pdf2image import convert_from_path

# 指定包含PDF文件的文件夹路径
pdf_folder = "/Users/qinqiang02/job/客户/索菲亚电子档案/银行回单测试_banks"
# 指定输出图像格式，如'jpeg'、'png'
image_format = 'png'

# 遍历文件夹中的所有PDF文件
for filename in os.listdir(pdf_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        # 将PDF文件的每一页转换为图像
        images = convert_from_path(pdf_path)

        # 保存每一页图像
        for i, image in enumerate(images):
            # 构造输出图像文件的路径
            image_filename = f"{os.path.splitext(filename)[0]}_page_{i + 1}.{image_format}"
            image_path = os.path.join(pdf_folder, 'img', image_filename)
            # 保存图像
            image.save(image_path, image_format)

        print(f"已将 {filename} 转换为图像。")

print("所有PDF文件转换完成。")