import sys
from ctypes import POINTER, c_bool, c_int, pointer, sizeof, WinDLL, byref, Structure, c_void_p
from ctypes.wintypes import DWORD, HWND, ULONG, POINT, RECT, UINT, LONG, LPCVOID
import win32api
import win32gui
from win32.lib import win32con
from enum import Enum


class WINDOWCOMPOSITIONATTRIB(Enum):
    WCA_UNDEFINED = 0,
    WCA_NCRENDERING_ENABLED = 1,
    WCA_NCRENDERING_POLICY = 2,
    WCA_TRANSITIONS_FORCEDISABLED = 3,
    WCA_ALLOW_NCPAINT = 4,
    WCA_CAPTION_BUTTON_BOUNDS = 5,
    WCA_NONCLIENT_RTL_LAYOUT = 6,
    WCA_FORCE_ICONIC_REPRESENTATION = 7,
    WCA_EXTENDED_FRAME_BOUNDS = 8,
    WCA_HAS_ICONIC_BITMAP = 9,
    WCA_THEME_ATTRIBUTES = 10,
    WCA_NCRENDERING_EXILED = 11,
    WCA_NCADORNMENTINFO = 12,
    WCA_EXCLUDED_FROM_LIVEPREVIEW = 13,
    WCA_VIDEO_OVERLAY_ACTIVE = 14,
    WCA_FORCE_ACTIVEWINDOW_APPEARANCE = 15,
    WCA_DISALLOW_PEEK = 16,
    WCA_CLOAK = 17,
    WCA_CLOAKED = 18,
    WCA_ACCENT_POLICY = 19,
    WCA_FREEZE_REPRESENTATION = 20,
    WCA_EVER_UNCLOAKED = 21,
    WCA_VISUAL_OWNER = 22,
    WCA_LAST = 23


class ACCENT_STATE(Enum):
    """ Client area status enumeration class """
    ACCENT_DISABLED = 0,
    ACCENT_ENABLE_GRADIENT = 1,
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2,
    ACCENT_ENABLE_BLURBEHIND = 3,          # Aero effect
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4,   # Acrylic effect
    ACCENT_INVALID_STATE = 5,


class ACCENT_POLICY(Structure):
    """ Specific attributes of client area """
    _fields_ = [
        ("AccentState",     DWORD),
        ("AccentFlags",     DWORD),
        ("GradientColor",   DWORD),
        ("AnimationId",     DWORD),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute",   DWORD),
        ("Data",        POINTER(ACCENT_POLICY)),
        ("SizeOfData",  ULONG),
    ]


class DWMNCRENDERINGPOLICY(Enum):
    DWMNCRP_USEWINDOWSTYLE = 0
    DWMNCRP_DISABLED = 1
    DWMNCRP_ENABLED = 2
    DWMNCRP_LAS = 3


class DWMWINDOWATTRIBUTE(Enum):
    DWMWA_NCRENDERING_ENABLED = 1
    DWMWA_NCRENDERING_POLICY = 2
    DWMWA_TRANSITIONS_FORCEDISABLED = 3
    DWMWA_ALLOW_NCPAINT = 4
    DWMWA_CAPTION_BUTTON_BOUNDS = 5
    DWMWA_NONCLIENT_RTL_LAYOUT = 6
    DWMWA_FORCE_ICONIC_REPRESENTATION = 7
    DWMWA_FLIP3D_POLICY = 8
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    DWMWA_HAS_ICONIC_BITMAP = 10
    DWMWA_DISALLOW_PEEK = 11
    DWMWA_EXCLUDED_FROM_PEEK = 12
    DWMWA_CLOAK = 13
    DWMWA_CLOAKED = 14
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_WINDOW_CORNER_PREFERENCE = 33
    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_FREEZE_REPRESENTATION = 25
    DWMWA_MICA_EFFECT = 1029
    DWMWA_LAST = 16


class DWM_WINDOW_CORNER_PREFERENCE(Enum):
    DWMWCP_DEFAULT = 0
    DWMWCP_DONOTROUND = 1
    DWMWCP_ROUND = 2
    DWMWCP_ROUNDSMALL = 3


class DWM_SYSTEMBACKDROP_TYPE(Enum):
    DWMSBT_AUTO = 0
    DWMSBT_NONE = 1
    DWMSBT_MAINWINDOW = 2       # Mica
    DWMSBT_TRANSIENTWINDOW = 3  # Acrylic
    DWMSBT_TABBEDWINDOW = 4     # Mica Alt


class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth",     c_int),
        ("cxRightWidth",    c_int),
        ("cyTopHeight",     c_int),
        ("cyBottomHeight",  c_int),
    ]


class MINMAXINFO(Structure):
    _fields_ = [
        ("ptReserved",      POINT),
        ("ptMaxSize",       POINT),
        ("ptMaxPosition",   POINT),
        ("ptMinTrackSize",  POINT),
        ("ptMaxTrackSize",  POINT),
    ]


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd',            HWND),
        ('hwndInsertAfter', HWND),
        ('x',               c_int),
        ('y',               c_int),
        ('cx',              c_int),
        ('cy',              c_int),
        ('flags',           UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc', RECT*3),
        ('lppos', POINTER(PWINDOWPOS))
    ]


class WindowEffect:
    """ A class that calls Windows API to realize window effect """

    def __init__(self):
        self.user32 = WinDLL("user32")
        self.dwmapi = WinDLL("dwmapi")

        self.SetWindowCompositionAttribute = self.user32.SetWindowCompositionAttribute
        self.DwmExtendFrameIntoClientArea = self.dwmapi.DwmExtendFrameIntoClientArea
        self.DwmSetWindowAttribute = self.dwmapi.DwmSetWindowAttribute

        self.SetWindowCompositionAttribute.restype = c_bool
        self.DwmExtendFrameIntoClientArea.restype = LONG
        self.DwmSetWindowAttribute.restype = LONG

        # 64-bit HWND argument types for safe handle passing
        self.SetWindowCompositionAttribute.argtypes = [
            HWND,
            POINTER(WINDOWCOMPOSITIONATTRIBDATA),
        ]
        self.DwmSetWindowAttribute.argtypes = [HWND, DWORD, LPCVOID, DWORD]
        self.DwmExtendFrameIntoClientArea.argtypes = [HWND, POINTER(MARGINS)]

        # OS version detection
        self.win_build = sys.getwindowsversion().build if sys.platform == "win32" else 0
        self.is_win11 = self.win_build >= 22000
        self.is_win11_22h2 = self.win_build >= 22621

        # Initialize structure
        self.accentPolicy = ACCENT_POLICY()
        self.winCompAttrData = WINDOWCOMPOSITIONATTRIBDATA()

        self.winCompAttrData.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY.value[0]
        self.winCompAttrData.SizeOfData = sizeof(self.accentPolicy)
        self.winCompAttrData.Data = pointer(self.accentPolicy)

    def setAcrylicEffect(self, hWnd, *args, gradientColor: str = "01010100", isEnableShadow: bool = True,
                         animationId: int = 0, **kwargs):
        """ Add the acrylic effect to the window """
        is_transparent = 0
        if args:
            is_transparent = args[0]
        elif "setAcrylicEffect" in kwargs:
            is_transparent = kwargs["setAcrylicEffect"]
        elif "is_transparent" in kwargs:
            is_transparent = kwargs["is_transparent"]

        try:
            hwnd_val = int(hWnd)
        except Exception:
            return

        if is_transparent == 1:
            gradientColor = "00000000"

        if isinstance(gradientColor, str) and len(gradientColor) == 8:
            gradientColor_rev = (
                gradientColor[6:]
                + gradientColor[4:6]
                + gradientColor[2:4]
                + gradientColor[:2]
            )
            gradient_dw = DWORD(int(gradientColor_rev, base=16))
        else:
            gradient_dw = DWORD(0)

        animationId = DWORD(animationId)
        accentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100) if isEnableShadow else DWORD(0)

        self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_ACRYLICBLURBEHIND.value[0]
        self.accentPolicy.GradientColor = gradient_dw
        self.accentPolicy.AccentFlags = accentFlags
        self.accentPolicy.AnimationId = animationId

        try:
            self.SetWindowCompositionAttribute(hwnd_val, pointer(self.winCompAttrData))
        except Exception:
            pass

        # Windows 11 DWM backdrop enhancement
        if self.is_win11_22h2:
            try:
                backdrop = c_int(DWM_SYSTEMBACKDROP_TYPE.DWMSBT_TRANSIENTWINDOW.value)
                self.DwmSetWindowAttribute(
                    hwnd_val,
                    DWMWINDOWATTRIBUTE.DWMWA_SYSTEMBACKDROP_TYPE.value,
                    byref(backdrop),
                    sizeof(backdrop)
                )
            except Exception:
                pass

    def setAeroEffect(self, hWnd):
        """ Add the aero effect to the window """
        try:
            hwnd_val = int(hWnd)
            self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_ENABLE_BLURBEHIND.value[0]
            self.accentPolicy.AccentFlags = DWORD(0x20 | 0x40 | 0x80 | 0x100)
            self.SetWindowCompositionAttribute(hwnd_val, pointer(self.winCompAttrData))
        except Exception:
            pass

    def removeBackgroundEffect(self, hWnd):
        """ Remove background effect """
        try:
            hwnd_val = int(hWnd)
            self.accentPolicy.AccentState = ACCENT_STATE.ACCENT_DISABLED.value[0]
            self.SetWindowCompositionAttribute(hwnd_val, pointer(self.winCompAttrData))
            if self.is_win11_22h2:
                none_val = c_int(DWM_SYSTEMBACKDROP_TYPE.DWMSBT_NONE.value)
                self.DwmSetWindowAttribute(
                    hwnd_val,
                    DWMWINDOWATTRIBUTE.DWMWA_SYSTEMBACKDROP_TYPE.value,
                    byref(none_val),
                    sizeof(none_val)
                )
        except Exception:
            pass

    def setWindowCorner(self, hWnd, preference: int = 2):
        """ Set Windows 11 window corner preference:
        0: default, 1: do not round (sharp), 2: round, 3: small round
        """
        if self.is_win11:
            try:
                hwnd_val = int(hWnd)
                pref = c_int(preference)
                self.DwmSetWindowAttribute(
                    hwnd_val,
                    DWMWINDOWATTRIBUTE.DWMWA_WINDOW_CORNER_PREFERENCE.value,
                    byref(pref),
                    sizeof(pref)
                )
            except Exception:
                pass

    def setDarkMode(self, hWnd, enable: bool = True):
        """ Set Windows 10/11 immersive dark mode for title bar """
        try:
            hwnd_val = int(hWnd)
            dark = c_int(1 if enable else 0)
            self.DwmSetWindowAttribute(
                hwnd_val,
                DWMWINDOWATTRIBUTE.DWMWA_USE_IMMERSIVE_DARK_MODE.value,
                byref(dark),
                sizeof(dark)
            )
        except Exception:
            pass

    def addShadowEffect(self, hWnd):
        """ Add DWM shadow to the window """
        try:
            hwnd_val = int(hWnd)
            self.DwmSetWindowAttribute(
                hwnd_val,
                DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value,
                byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_ENABLED.value)),
                sizeof(c_int),
            )
            margins = MARGINS(-1, -1, -1, -1)
            self.DwmExtendFrameIntoClientArea(hwnd_val, byref(margins))
        except Exception:
            pass

    def removeShadowEffect(self, hWnd):
        """ Remove DWM shadow from the window """
        try:
            hwnd_val = int(hWnd)
            self.DwmSetWindowAttribute(
                hwnd_val,
                DWMWINDOWATTRIBUTE.DWMWA_NCRENDERING_POLICY.value,
                byref(c_int(DWMNCRENDERINGPOLICY.DWMNCRP_DISABLED.value)),
                sizeof(c_int),
            )
        except Exception:
            pass

    @staticmethod
    def removeMenuShadowEffect(hWnd):
        """ Remove shadow from pop-up menu """
        try:
            hwnd_val = int(hWnd)
            style = win32gui.GetClassLong(hwnd_val, win32con.GCL_STYLE)
            style &= ~0x00020000  # CS_DROPSHADOW
            win32api.SetClassLong(hwnd_val, win32con.GCL_STYLE, style)
        except Exception:
            pass

    @staticmethod
    def addWindowAnimation(hWnd):
        """ Enables the maximize and minimize animation of the window """
        try:
            hwnd_val = int(hWnd)
            style = win32gui.GetWindowLong(hwnd_val, win32con.GWL_STYLE)
            win32gui.SetWindowLong(
                hwnd_val,
                win32con.GWL_STYLE,
                style
                | win32con.WS_MAXIMIZEBOX
                | win32con.WS_CAPTION
                | win32con.CS_DBLCLKS
                | win32con.WS_THICKFRAME,
            )
        except Exception:
            pass
