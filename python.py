import os
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw


def select_image():
    """让用户选择图片文件并预览"""
    file_path = filedialog.askopenfilename(
        title="选择图片",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )
    image_entry.delete(0, END)  # 清除当前输入框内容
    image_entry.insert(0, file_path)  # 插入选中的图片路径

    # 显示图片预览
    if file_path:
        load_image_preview(file_path)


def load_image_preview(image_path):
    """加载图片预览"""
    global original_img
    try:
        original_img = Image.open(image_path)
        original_img.thumbnail((400, 300))  # 缩小图片以适合预览区域
        update_preview()  # 更新预览图片显示
    except Exception as e:
        messagebox.showerror("图片加载错误", f"无法加载图片: {e}")  # 显示错误信息


def update_preview():
    """更新图片预览，并根据行列数绘制参考线"""
    if original_img is None:
        return

    # 获取当前输入的行数和列数
    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
    except ValueError:
        rows, cols = 1, 1  # 如果输入无效，使用默认值避免崩溃

    # 复制原始图片用于绘制参考线
    preview_img = original_img.copy()
    draw = ImageDraw.Draw(preview_img)

    # 获取图片尺寸
    width, height = preview_img.size

    # 绘制列参考线
    for col in range(1, cols):
        x = width * col // cols
        draw.line([(x, 0), (x, height)], fill="red", width=2)  # 绘制垂直参考线

    # 绘制行参考线
    for row in range(1, rows):
        y = height * row // rows
        draw.line([(0, y), (width, y)], fill="red", width=2)  # 绘制水平参考线

    # 更新图片预览显示
    img_tk = ImageTk.PhotoImage(preview_img)
    image_label.config(image=img_tk)
    image_label.image = img_tk


def select_output_folder():
    """让用户选择输出目录"""
    folder_path = filedialog.askdirectory(title="选择输出目录")
    output_entry.delete(0, END)
    output_entry.insert(0, folder_path)  # 插入用户选择的文件夹路径


def split_image():
    """根据用户输入的行列数，分割并保存图片"""
    image_path = image_entry.get()  # 获取图片路径
    output_dir = output_entry.get()  # 获取输出目录路径

    # 获取用户输入的行数和列数
    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
    except ValueError:
        messagebox.showerror("输入错误", "行数和列数必须是有效的数字")
        return

    # 检查图片路径是否存在
    if not os.path.exists(image_path):
        messagebox.showerror("路径错误", "图片文件不存在")
        return

    # 如果输出目录不存在则创建
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        img = Image.open(image_path)
        width, height = img.size
        part_width = width // cols  # 每块图像的宽度
        part_height = height // rows  # 每块图像的高度

        # 获取原始文件名（不包含扩展名）
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        # 开始分割并保存
        for row in range(rows):
            for col in range(cols):
                left = col * part_width
                upper = row * part_height
                right = (col + 1) * part_width if col < cols - 1 else width
                lower = (row + 1) * part_height if row < rows - 1 else height

                # 裁剪图像
                cropped_image = img.crop((left, upper, right, lower))

                # 如果图像是RGBA模式，转换为RGB模式
                if cropped_image.mode == "RGBA":
                    cropped_image = cropped_image.convert("RGB")

                # 使用原始文件名作为分割图片的前缀
                part_image_path = os.path.join(output_dir, f"{base_name}_{row + 1}_{col + 1}.jpg")
                cropped_image.save(part_image_path)

        # 提示用户分割完成
        messagebox.showinfo("完成", "图片分割完成并保存到指定目录！")
    except Exception as e:
        messagebox.showerror("分割错误", f"图片分割时发生错误: {e}")


# 构建GUI界面
root = Tk()
root.title("图片均等分割工具")
root.geometry("500x600")

# 初始化图片变量
original_img = None

# 主框架
frame = Frame(root)
frame.pack(pady=20)

# 图片路径选择
Label(frame, text="选择图片：").grid(row=0, column=0, padx=10, pady=10)
image_entry = Entry(frame, width=40)
image_entry.grid(row=0, column=1, padx=10, pady=10)
Button(frame, text="浏览", command=select_image, bg="#4CAF50", fg="white").grid(row=0, column=2, padx=10, pady=10)

# 输出路径选择
Label(frame, text="输出目录：").grid(row=1, column=0, padx=10, pady=10)
output_entry = Entry(frame, width=40)
output_entry.grid(row=1, column=1, padx=10, pady=10)
Button(frame, text="浏览", command=select_output_folder, bg="#4CAF50", fg="white").grid(row=1, column=2, padx=10, pady=10)

# 行列输入框
row_col_frame = Frame(frame)
row_col_frame.grid(row=2, column=0, columnspan=3, pady=10)

Label(row_col_frame, text="行数：").grid(row=0, column=0, padx=10)
rows_entry = Entry(row_col_frame, width=10)
rows_entry.grid(row=0, column=1, padx=10)
rows_entry.bind("<KeyRelease>", lambda event: update_preview())  # 输入行数时更新预览

Label(row_col_frame, text="列数：").grid(row=0, column=2, padx=10)
cols_entry = Entry(row_col_frame, width=10)
cols_entry.grid(row=0, column=3, padx=10)
cols_entry.bind("<KeyRelease>", lambda event: update_preview())  # 输入列数时更新预览

# 图片预览
image_label = Label(root)
image_label.pack(pady=10)

# 开始分割按钮
Button(root, text="开始分割", command=split_image, bg="#f44336", fg="white", font=("Arial", 12)).pack(pady=20)

# 启动应用
root.mainloop()
