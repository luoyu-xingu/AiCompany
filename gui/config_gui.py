import tkinter as tk
import os
import json
from PIL import Image, ImageDraw, ImageFont, ImageTk

class ConfigGUI:
    """配置GUI界面"""
    def __init__(self, root, on_config_save):
        """初始化配置GUI"""
        self.root = root
        self.root.title("AI陪伴系统配置")
        self.on_config_save = on_config_save
        
        # 禁用放大按钮
        self.root.resizable(False, False)
        
        # 窗口大小
        self.window_width = 500
        self.window_height = 300
        self.root.geometry(f"{self.window_width}x{self.window_height}")
        
        # 设置背景图片
        self.bg_image_path = r"d:\AiCompany\photo1.jpg"
        
        # 配置文件路径 - 项目根目录
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        print(f"[Debug] 配置文件路径: {self.config_file}")
        
        # 先加载原始背景图片
        self.load_background_image()
        
        # 创建第一个配置界面
        self.create_first_config_area()
    
    def load_background_image(self):
        """加载背景图片"""
        try:
            self.original_bg_image = Image.open(self.bg_image_path)
            self.original_bg_image = self.original_bg_image.resize(
                (self.window_width, self.window_height), Image.Resampling.LANCZOS
            )
        except Exception as e:
            self.original_bg_image = None
    
    def setup_main_background(self):
        """设置主背景"""
        if self.original_bg_image:
            self.bg_image = ImageTk.PhotoImage(self.original_bg_image)
            self.background_label = tk.Label(self.root, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    log_path = config.get('log_path', None)
                    print(f"[Debug] 加载配置文件成功: {log_path}")
                    return log_path
            else:
                print(f"[Debug] 配置文件不存在: {self.config_file}")
        except Exception as e:
            print(f"[Debug] 加载配置文件失败: {e}")
        return None
    
    def save_config(self, log_path):
        """保存配置文件"""
        try:
            config = {'log_path': log_path}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"[Debug] 保存配置文件成功: {log_path}")
        except Exception as e:
            print(f"[Debug] 保存配置文件失败: {e}")
    
    def delete_logs(self, log_path):
        """删除logs目录"""
        try:
            if os.path.exists(log_path):
                import shutil
                # 尝试删除目录
                try:
                    shutil.rmtree(log_path)
                    print(f"[Info] 已删除logs目录: {log_path}")
                except Exception as e:
                    # 如果删除目录失败，尝试删除目录中的文件
                    print(f"[Debug] 删除logs目录失败，尝试删除目录中的文件: {e}")
                    
                    # 遍历目录中的所有文件
                    for file_name in os.listdir(log_path):
                        file_path = os.path.join(log_path, file_name)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                print(f"[Info] 已删除文件: {file_path}")
                        except Exception as file_error:
                            print(f"[Debug] 删除文件失败: {file_error}")
                            # 跳过被占用的文件
                            continue
                    
                    # 再次尝试删除目录
                    try:
                        shutil.rmtree(log_path)
                        print(f"[Info] 已删除logs目录: {log_path}")
                    except Exception as final_error:
                        print(f"[Debug] 最终删除logs目录失败: {final_error}")
        except Exception as e:
            print(f"[Debug] 删除logs目录失败: {e}")
    
    def create_first_config_area(self):
        """创建第一个配置界面 - 标题和开始按钮"""
        # 1. 清空所有现有组件
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 2. 加载背景图片并直接绘制标题
        try:
            # 加载背景图片
            bg_image = Image.open(self.bg_image_path)
            bg_image = bg_image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
            
            # 在背景图片上绘制标题
            draw = ImageDraw.Draw(bg_image)
            text = "AICompany"
            
            # 尝试使用字体
            try:
                font = ImageFont.truetype("simhei.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (self.window_width - text_width) // 2
            y = 100
            
            # 绘制白色描边和黑色文字
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x+dx, y+dy), text, font=font, fill="white")
            draw.text((x, y), text, font=font, fill="#1a1a1a")
            
            # 保存绘制后的背景图片
            self.original_bg_image = bg_image
        except Exception as e:
            print(f"[Debug] 绘制背景图片失败: {e}")
        
        # 3. 设置背景
        self.setup_main_background()
        
        # 4. 创建开始按钮（红色）
        self.start_button = tk.Button(
            self.root, 
            text="开始", 
            command=self.show_second_config, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#d9534f', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#c9302c', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.start_button.place(x=215, y=200)
    
    def show_second_config(self):
        """显示第二个配置界面"""
        # 清空所有现有组件
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建第二个配置界面
        self.create_second_config_area()
    
    def create_second_config_area(self):
        """创建第二个配置界面 - 日志路径输入"""
        # 1. 清空所有现有组件
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 2. 加载背景图片并直接绘制标题
        try:
            # 加载背景图片
            bg_image = Image.open(self.bg_image_path)
            bg_image = bg_image.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
            
            # 在背景图片上绘制标题
            draw = ImageDraw.Draw(bg_image)
            text = "AICompany"
            
            # 尝试使用字体
            try:
                font = ImageFont.truetype("simhei.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            x = (self.window_width - text_width) // 2
            y = 50
            
            # 绘制白色描边和黑色文字
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                draw.text((x+dx, y+dy), text, font=font, fill="white")
            draw.text((x, y), text, font=font, fill="#1a1a1a")
            
            # 绘制日志保存路径标签（放大加粗）
            label_text = "日志保存路径:"
            try:
                label_font = ImageFont.truetype("simhei.ttf", 14)
            except:
                label_font = font
            
            # 绘制文字（使用双重绘制实现加粗效果）
            draw.text((50, 100), label_text, font=label_font, fill="#333333")
            for dx, dy in [(0.5, 0.5), (-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5)]:
                draw.text((50+dx, 100+dy), label_text, font=label_font, fill="#333333")
            
            # 保存绘制后的背景图片
            self.original_bg_image = bg_image
        except Exception as e:
            print(f"[Debug] 绘制背景图片失败: {e}")
        
        # 3. 设置背景
        self.setup_main_background()
        
        # 4. 创建其他组件
        # 加载之前保存的logs路径
        saved_log_path = self.load_config()
        # 默认logs路径 - 项目根目录下的logs文件夹
        default_log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        
        # 如果存在保存的logs路径，使用保存的路径；否则使用默认路径
        final_log_path = saved_log_path if saved_log_path else default_log_path
        print(f"[Debug] 最终logs路径: {final_log_path}")
        
        # 路径输入框
        self.path_var = tk.StringVar(value=final_log_path)
        self.path_entry = tk.Entry(
            self.root, 
            textvariable=self.path_var, 
            font=("SimHei", 11), 
            bg='#ffffff', 
            relief='flat', 
            bd=0, 
            highlightthickness=1, 
            highlightbackground='#888888', 
            insertbackground='#000000', 
            fg='#1a1a1a'
        )
        self.path_entry.place(x=50, y=125, width=400, height=30)
        
        # 继续按钮（蓝色）- 第一个按钮
        self.continue_button = tk.Button(
            self.root, 
            text="继续", 
            command=self.continue_config, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#4a90d9', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#357abd', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.continue_button.place(x=215, y=170)
        
        # 新的开始按钮（绿色）- 第二个按钮
        self.new_start_button = tk.Button(
            self.root, 
            text="新的开始", 
            command=self.new_start_config, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#5cb85c', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#449d44', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.new_start_button.place(x=215, y=210)
        
        # 返回上一步按钮（红色）- 第三个按钮
        self.back_button = tk.Button(
            self.root, 
            text="返回上一步", 
            command=self.create_first_config_area, 
            font=('SimHei', 12, 'bold'), 
            width=12, 
            bg='#d9534f', 
            relief='flat', 
            bd=0, 
            highlightthickness=0,
            activebackground='#c9302c', 
            fg='#ffffff', 
            cursor='hand2'
        )
        self.back_button.place(x=215, y=250)
    
    def continue_config(self):
        """继续配置 - 使用之前保存的logs路径"""
        log_path = self.path_var.get()
        print(f"[Debug] 继续配置 - logs路径: {log_path}")
        
        # 检查logs目录是否存在
        if not os.path.exists(log_path):
            # 如果不存在，创建目录
            try:
                os.makedirs(log_path)
                print(f"[Info] 创建logs目录: {log_path}")
            except Exception as e:
                print(f"[Debug] 创建logs目录失败: {e}")
                return
        
        # 保存配置
        self.save_config(log_path)
        
        # 调用回调函数
        if self.on_config_save:
            self.on_config_save(log_path)
        
        self.root.quit()
    
    def new_start_config(self):
        """新的开始 - 删除之前的logs并重新开始"""
        log_path = self.path_var.get()
        print(f"[Debug] 新的开始 - logs路径: {log_path}")
        
        # 删除之前的logs目录
        self.delete_logs(log_path)
        
        # 尝试创建新的logs目录
        try:
            # 确保目录不存在
            if os.path.exists(log_path):
                # 如果目录存在，清空目录内容
                for file_name in os.listdir(log_path):
                    file_path = os.path.join(log_path, file_name)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception:
                        pass
            else:
                # 如果目录不存在，创建目录
                os.makedirs(log_path)
            print(f"[Info] 创建新的logs目录: {log_path}")
        except Exception as e:
            print(f"[Debug] 创建logs目录失败: {e}")
            # 即使创建失败，也要继续执行，因为logs目录可能已经存在
        
        # 保存配置
        self.save_config(log_path)
        
        # 调用回调函数
        if self.on_config_save:
            self.on_config_save(log_path)
        
        self.root.quit()
