# -*- coding: UTF-8 -*-
"""
@Project ：CountBoard
@File ：CustomWindow.py
@Author ：Gao yongxian
@Date ：2021/11/8 11:00
@contact: g1695698547@163.com
"""
import os
import re
import sys
import traceback
from win32api import GetMonitorInfo, MonitorFromPoint


class CustomWindow:
    """
    自定义模板(用来窗口初始化): self.root要在继承之前使用，tk.Toplevel() 或 tk.TK()
    """

    def __init__(self, *args, **kwargs):
        """初始化"""
        super().__init__()
        self.__init2__(**kwargs)

    @staticmethod
    def get_monitor_work_area(x=0, y=0):
        """获取指定屏幕工作区坐标 (left, top, width, height)"""
        try:
            info = GetMonitorInfo(MonitorFromPoint((int(x), int(y))))
            work = info.get('Work')
            left, top, right, bottom = work[0], work[1], work[2], work[3]
            return left, top, max(100, right - left), max(100, bottom - top)
        except Exception:
            return 0, 0, 1920, 1080

    def _parse_geometry(self, geo):
        """安全解析窗口几何参数为 (width, height, x, y)"""
        if isinstance(geo, list) and geo:
            geo = geo[0]
        if isinstance(geo, (tuple, list)) and len(geo) >= 4:
            return int(geo[0]), int(geo[1]), int(geo[2]), int(geo[3])
        if isinstance(geo, str):
            nums = [int(n) for n in re.findall(r'-?\d+', geo)]
            if len(nums) >= 4:
                return nums[0], nums[1], nums[2], nums[3]
        return 300, 300, 100, 100

    def __init2__(self, **kwargs):
        """布局初始化"""
        try:
            self.root.withdraw()
        except Exception:
            pass

        self.overrideredirect = kwargs.get("overrideredirect", 0)
        self.width = kwargs.get("width", 300)
        self.height = kwargs.get("height", 300)
        self.title = kwargs.get("title", "无标题")
        self.position = kwargs.get("position", "center")
        self.icon = kwargs.get("icon", os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "favicon.ico"))
        self.topmost = kwargs.get("topmost", 1)
        self.alpha = kwargs.get("alpha", 1)
        self.pre_window = kwargs.get("pre_window", None)
        self._geometry = kwargs.get("_geometry", (300, 300, 100, 100))
        self._auto_margin = kwargs.get("_auto_margin", False)
        self.exe_dir_path = kwargs.get("exe_dir_path", os.path.dirname(os.path.abspath(sys.argv[0])))
        self.offset = kwargs.get("offset", 0)
        self.show = kwargs.get("show", 1)

        # 窗体基本设置
        try:
            self.root.title(self.title)
        except Exception:
            pass

        try:
            if os.path.exists(self.icon):
                self.root.iconbitmap(self.icon)
        except Exception:
            pass

        try:
            self.root.wm_attributes('-alpha', self.alpha)
            self.root.wm_attributes('-topmost', self.topmost)
        except Exception:
            pass

        # 无边框窗体设置
        try:
            self.root.overrideredirect(self.overrideredirect)
        except Exception:
            pass

        # 工作区与屏幕尺寸
        self.work_x, self.work_y, self.work_width, self.work_heigh = self.get_monitor_work_area(0, 0)
        try:
            self.win_width = self.root.winfo_screenwidth()
            self.win_heigth = self.root.winfo_screenheight()
        except Exception:
            self.win_width, self.win_heigth = self.work_width, self.work_heigh

        # 设置窗体位置
        if self.position == "custom":
            w, h, _, _ = self._parse_geometry(self._geometry)
            self.width = w
            self.height = h

        self.set_position(self.position, self.pre_window, self._geometry)
        self.set_auto_margin(self._auto_margin)

        if self.show:
            try:
                self.root.deiconify()
            except Exception:
                pass

    def modify_offset(self, offset):
        """外部调用，修改贴边距离"""
        self.offset = offset

    def modify_auto_margin(self, _auto_margin):
        """外部调用，修改是否贴边"""
        self._auto_margin = _auto_margin

    def set_position(self, position="center", pre_window=None, _geometry=None):
        """设置窗体位置"""
        if position == "center":
            width_adjust = int(self.work_x + (self.work_width - self.width) / 2)
            higth_adjust = int(self.work_y + (self.work_heigh - self.height) / 2)
            self.root.geometry(f"{int(self.width)}x{int(self.height)}+{width_adjust}+{higth_adjust}")
        elif position == "follow" and pre_window:
            try:
                self.pre_window_root = pre_window.root
                self.width = pre_window.width
                x = self.pre_window_root.winfo_x()
                y = self.pre_window_root.winfo_y()
                h = self.pre_window_root.winfo_height()
                self.width_adjust = x
                self.height_adjust = y + h + 40
                self.root.geometry(f"{int(self.width)}x{int(self.height)}+{self.width_adjust}+{self.height_adjust}")
            except Exception:
                pass
        elif position == "custom":
            geo_source = _geometry if _geometry is not None else self._geometry
            w, h, x, y = self._parse_geometry(geo_source)
            self.width, self.height = w, h
            self.root.geometry(f"{w}x{h}+{x}+{y}")

    def exit(self):
        """退出窗体"""
        try:
            self.root.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def set_auto_margin(self, flag):
        """设置自动贴边"""
        self.root_x, self.root_y, self.abs_x, self.abs_y = 0, 0, 0, 0

        if flag:
            self.root.bind('<B1-Motion>', self._on_move)
            self.root.bind('<ButtonPress-1>', self._on_tap)
            self.root.bind('<ButtonRelease-1>', self._on_release)
        else:
            try:
                self.root.unbind('<B1-Motion>')
                self.root.unbind('<ButtonPress-1>')
                self.root.unbind('<ButtonRelease-1>')
            except Exception:
                pass

    def _on_move(self, event):
        """移动"""
        offset_x = event.x_root - self.root_x
        offset_y = event.y_root - self.root_y
        x_adjust = self.abs_x + offset_x
        y_adjust = self.abs_y + offset_y
        self.root.geometry(f"{int(self.width)}x{int(self.height)}+{int(x_adjust)}+{int(y_adjust)}")

    def _on_tap(self, event):
        """鼠标左键按下：更新窗口信息"""
        self.root_x, self.root_y = event.x_root, event.y_root
        self.abs_x, self.abs_y = self.root.winfo_x(), self.root.winfo_y()
        self.width = self.root.winfo_width()
        self.height = self.root.winfo_height()

    def _on_release(self, event, **kwargs):
        """鼠标左键弹起"""
        offset_x = event.x_root - self.root_x
        offset_y = event.y_root - self.root_y
        target_x = self.abs_x + offset_x
        target_y = self.abs_y + offset_y

        if self._auto_margin:
            # 动态获取当前鼠标所在屏幕的工作区
            work_x, work_y, work_w, work_h = self.get_monitor_work_area(event.x_root, event.y_root)

            # 磁贴吸附边缘判定
            if target_x + self.width > work_x + work_w - self.offset:
                x_adjust = work_x + work_w - self.width - self.offset
            elif target_x < work_x + self.offset:
                x_adjust = work_x + self.offset
            else:
                x_adjust = target_x

            if target_y + self.height > work_y + work_h - self.offset:
                y_adjust = work_y + work_h - self.height - self.offset
            elif target_y < work_y + self.offset:
                y_adjust = work_y + self.offset
            else:
                y_adjust = target_y
        else:
            x_adjust = target_x
            y_adjust = target_y

        geo_str = f"{int(self.width)}x{int(self.height)}+{int(x_adjust)}+{int(y_adjust)}"

        if "mysetting_dict" in kwargs and kwargs["mysetting_dict"] is not None:
            try:
                kwargs["mysetting_dict"]["tile_geometry"] = [(int(self.width), int(self.height), int(x_adjust), int(y_adjust))]
            except Exception:
                pass

        try:
            self.root.geometry(geo_str)
        except Exception:
            pass
