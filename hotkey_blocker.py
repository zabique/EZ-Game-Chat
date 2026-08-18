import ctypes
from ctypes import wintypes
import threading
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WM_NULL = 0x0000

VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12      # Alt key
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_F4 = 0x73

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('vkCode', wintypes.DWORD),
        ('scanCode', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.POINTER(wintypes.ULONG))
    ]

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT))

class HotkeyBlocker:
    """
    Low-level Windows Keyboard Hook (WH_KEYBOARD_LL) to intercept and suppress
    system hotkeys involving Windows Key, Ctrl, Shift, and Alt combinations.
    """
    def __init__(self):
        self._hook = None
        self._thread = None
        self._thread_id = None
        self._running = False
        self._callback_ref = None

    def _is_pressed(self, vk):
        return bool(user32.GetAsyncKeyState(vk) & 0x8000)

    def _hook_callback(self, nCode, wParam, lParam):
        if nCode >= 0 and wParam in (WM_KEYDOWN, WM_SYSKEYDOWN, WM_KEYUP, WM_SYSKEYUP):
            vk = lParam.contents.vkCode
            
            win_pressed = self._is_pressed(VK_LWIN) or self._is_pressed(VK_RWIN) or (vk in (VK_LWIN, VK_RWIN))
            ctrl_pressed = self._is_pressed(VK_CONTROL) or (vk in (0xA2, 0xA3))
            shift_pressed = self._is_pressed(VK_SHIFT) or (vk in (0xA0, 0xA1))
            alt_pressed = self._is_pressed(VK_MENU) or (vk in (0xA4, 0xA5))

            # 1. Suppress single Win key or any Win + [Key] combination (Win+R, Win+E, Win+Tab, Win+Shift+S, etc.)
            if win_pressed:
                return 1

            # 2. Suppress system Ctrl combinations (Ctrl+Esc, Ctrl+Shift+Esc, Ctrl+Alt+Tab)
            if ctrl_pressed:
                if vk in (VK_ESCAPE, VK_TAB):
                    return 1
                if alt_pressed and vk == VK_TAB:
                    return 1

            # 3. Suppress Alt system combinations (Alt+Tab, Alt+Esc, Alt+F4, Alt+Space)
            if alt_pressed:
                if vk in (VK_TAB, VK_ESCAPE, VK_F4, VK_SPACE):
                    return 1

            # 4. Suppress Ctrl+Shift system shortcuts (e.g. Ctrl+Shift+Esc, Win+Shift+S)
            if shift_pressed and ctrl_pressed and vk in (VK_ESCAPE, VK_TAB):
                return 1

        return user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

    def start(self):
        if self._running:
            return True
        self._running = True
        self._thread = threading.Thread(target=self._run_hook, daemon=True)
        self._thread.start()
        return True

    def _run_hook(self):
        self._thread_id = kernel32.GetCurrentThreadId()
        self._callback_ref = HOOKPROC(self._hook_callback)
        self._hook = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._callback_ref,
            None,
            0
        )
        if not self._hook:
            self._running = False
            print("[HotkeyBlocker] Failed to install low-level keyboard hook.")
            return

        msg = wintypes.MSG()
        while self._running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0 or not self._running:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self._hook:
            user32.UnhookWindowsHookEx(self._hook)
            self._hook = None

    def stop(self):
        if not self._running:
            return
        self._running = False
        if self._thread_id:
            # Post WM_NULL to unblock GetMessageW in the hook thread
            user32.PostThreadMessageW(self._thread_id, WM_NULL, 0, 0)
        if self._hook:
            user32.UnhookWindowsHookEx(self._hook)
            self._hook = None

    def is_active(self):
        return self._running
