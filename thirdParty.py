import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import ast
import os
import sys
import pkgutil

def get_stdlib_modules():
    stdlib_paths = [p for p in sys.path if 'site-packages' not in p]
    stdlib_modules = set()
    for path in stdlib_paths:
        if os.path.isdir(path):
            for module_info in pkgutil.iter_modules([path]):
                stdlib_modules.add(module_info.name)
    return stdlib_modules

# 从 .py 文件中提取 import 的模块名
def extract_imports(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                imports.add(node.module.split('.')[0])
    return imports
    
def analyze_file():
    file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if not file_path:
        return

    try:
        stdlib_modules = get_stdlib_modules()
        imported = extract_imports(file_path)
        third_party = {pkg for pkg in imported if pkg not in stdlib_modules}

        if not third_party:
            output_box.delete(1.0, tk.END)
            output_box.insert(tk.END, "未检测到第三方包。")
            return

        sorted_pkgs = sorted(third_party)
        install_cmd = "pip install " + ' '.join(sorted_pkgs)

        output_box.delete(1.0, tk.END)
        output_box.insert(tk.END, f"检测到以下第三方包：\n\n")
        output_box.insert(tk.END, "\n".join(sorted_pkgs))
        output_box.insert(tk.END, f"\n\n推荐 pip 安装命令：\n{install_cmd}\n")

        # 如果选择的是保存为文件
        if mode_var.get() == "save_file":
            filename = os.path.basename(file_path)
            filename_without_ext = os.path.splitext(filename)[0]
            output_name = f"{filename_without_ext}_的依赖.txt"
            with open(output_name, "w", encoding="utf-8") as f:
                f.write("第三方依赖包列表：\n")
                for pkg in sorted_pkgs:
                    f.write(pkg + "\n")
                f.write("\n推荐 pip 安装命令：\n")
                f.write(install_cmd + "\n")

            messagebox.showinfo("完成", f"已生成文件：{output_name}")

    except Exception as e:
        messagebox.showerror("错误", f"发生错误：{str(e)}")


# 创建 GUI
root = tk.Tk()
root.title("Python 第三方依赖检测工具 BY Rainyy")
root.geometry("600x400")

frame = tk.Frame(root)
frame.pack(pady=20)

button = tk.Button(frame, text="选择需要查找依赖的 Python 文件", command=analyze_file, height=2, width=25)
button.pack()

output_box = scrolledtext.ScrolledText(root, height=15, width=70)
output_box.pack(padx=10, pady=10)

# 模式选择：只显示命令 or 生成文件
mode_var = tk.StringVar(value="save_file")  # 默认：保存文件

mode_frame = tk.LabelFrame(root, text="选择输出模式")
mode_frame.pack(pady=5)

rb1 = tk.Radiobutton(mode_frame, text="仅显示 pip 安装命令", variable=mode_var, value="show_only")
rb2 = tk.Radiobutton(mode_frame, text="同时生成适合保存和分享的文本文件", variable=mode_var, value="save_file")

rb1.pack(anchor="w", padx=10)
rb2.pack(anchor="w", padx=10)


root.mainloop()
