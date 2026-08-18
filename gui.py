import customtkinter as ctk
import threading
from PIL import Image
import os
import json
import sys
import keyboard
from typer import AutoTyper
from quotes import QUOTES
from config import ConfigManager, APP_VERSION
from hotkey_blocker import HotkeyBlocker
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Premium Dark Palette Tokens
THEME = {
    "bg_dark": "#0B0E14",
    "sidebar_bg": "#121721",
    "header_bg": "#161C28",
    "card_bg": "#1A2130",
    "card_hover": "#222B3E",
    "border": "#2A3447",
    "accent_indigo": "#6366F1",
    "accent_indigo_hover": "#4F46E5",
    "status_running": "#10B981",
    "status_stopped": "#EF4444",
    "text_main": "#F8FAFC",
    "text_sub": "#94A3B8",
    "btn_gray": "#334155",
    "btn_gray_hover": "#475569"
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.config = ConfigManager()
        
        self.title(self.config.get_text("app_title"))
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.resizable(True, True)
        self.configure(fg_color=THEME["bg_dark"])

        self.typer = AutoTyper()
        self.hotkey_blocker = HotkeyBlocker()
        self.is_detecting_key = False
        self.active_binding_btn = None 

        # Load Settings
        saved_keys = self.config.settings.get("keys", {})
        saved_modes = self.config.settings.get("modes", {})
        self.custom_icons = self.config.settings.get("icons", {})
        self.click_after_typing = ctk.BooleanVar(value=self.config.settings.get("click_after_typing", True))
        self.block_hotkeys_var = ctk.BooleanVar(value=self.config.settings.get("block_low_level_hotkeys", False))
        self.target_nickname_var = ctk.StringVar(value=self.config.settings.get("target_nickname", ""))
        self.typer.set_target_nickname(self.target_nickname_var.get())
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Dynamic key map initialization
        self.key_map = {'custom': saved_keys.get('custom')}
        self.mode_map = {} 
        
        for category in QUOTES.keys():
            self.key_map[category] = saved_keys.get(category)
            self.mode_map[category] = ctk.BooleanVar(value=saved_modes.get(category, False)) 
            
        self.binding_buttons = {} 
        self.labels_to_update = {}
        self.icon_labels = {}
        self.icon_images = {}

        self.setup_ui()
        
        # Apply loaded settings to UI
        self.delay_slider.set(self.config.settings.get("delay", 0.01))
        self.update_delay_label(self.config.settings.get("delay", 0.01))
        self.message_entry.delete("1.0", "end")
        self.message_entry.insert("1.0", self.config.settings.get("custom_message", "GG WP"))
        
        self._update_button_texts()
        self._update_active_keys_count()

        if self.block_hotkeys_var.get():
            self.hotkey_blocker.start()

    def _load_image(self, path, size=(64, 64)):
        if path:
            if not os.path.isabs(path):
                path = os.path.join(BASE_DIR, path)
            
            if os.path.exists(path):
                try:
                    pil_img = Image.open(path)
                    pil_img.load()
                    return ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
                except Exception as e:
                    print(f"Error loading image {path}: {e}")
        
        return self._create_placeholder_image(size)

    def _create_placeholder_image(self, size):
        img = Image.new("RGBA", (256, 256), (30, 41, 59, 255))
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)

    def setup_ui(self):
        # Master Grid: Row 0 Header, Row 1 Content (Sidebar + Main)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Body
        self.grid_columnconfigure(0, weight=0) # Sidebar
        self.grid_columnconfigure(1, weight=1) # Main View Area

        # --- Top Header Bar ---
        self.header_frame = ctk.CTkFrame(self, height=64, corner_radius=0, fg_color=THEME["header_bg"], border_width=1, border_color=THEME["border"])
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_propagate(False)

        # Header Title & Logo
        logo_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        logo_box.pack(side="left", padx=20, pady=10)
        
        self.logo_label = ctk.CTkLabel(logo_box, text="⚡ EZ-GAME-CHAT", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color=THEME["text_main"])
        self.logo_label.pack(anchor="w")
        
        self.subtitle_label = ctk.CTkLabel(logo_box, text=f"Auto-Typer & Voice-Line Studio • v{APP_VERSION}", font=ctk.CTkFont(size=11), text_color=THEME["text_sub"])
        self.subtitle_label.pack(anchor="w")

        # Header Quick Controls (Right side)
        header_ctrls = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        header_ctrls.pack(side="right", padx=20, pady=10)

        # Language Select Dropdown
        self.lang_option = ctk.CTkOptionMenu(header_ctrls, values=["English", "Polski", "Español", "Português", "Deutsch"],
                                             width=110, height=34, fg_color=THEME["card_bg"], button_color=THEME["accent_indigo"],
                                             command=self._change_language)
        self.lang_option.pack(side="left", padx=(0, 8))
        self._set_lang_dropdown_value()

        # Refresh / Restart App Button
        self.refresh_btn = ctk.CTkButton(header_ctrls, text="🔄 Restart", fg_color=THEME["card_bg"], hover_color=THEME["card_hover"], border_width=1, border_color=THEME["border"], width=90, height=34, font=ctk.CTkFont(size=12, weight="bold"), command=self._restart_app)
        self.refresh_btn.pack(side="left", padx=(0, 12))

        # Status Badge Pill
        self.status_pill = ctk.CTkFrame(header_ctrls, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=16)
        self.status_pill.pack(side="left", padx=(0, 12), pady=5)
        
        self.status_dot = ctk.CTkLabel(self.status_pill, text="●", font=ctk.CTkFont(size=14), text_color=THEME["status_stopped"])
        self.status_dot.pack(side="left", padx=(10, 4), pady=4)
        
        self.status_text = ctk.CTkLabel(self.status_pill, text=self.config.get_text("status_stopped"), font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["text_main"])
        self.status_text.pack(side="left", padx=(0, 12), pady=4)

        # Active Hotkeys Readout
        self.active_keys_pill = ctk.CTkLabel(header_ctrls, text="0 Hotkeys Active", font=ctk.CTkFont(size=12), text_color=THEME["text_sub"])
        self.active_keys_pill.pack(side="left", padx=(0, 15))

        # Start / Stop Action Buttons
        self.start_btn = ctk.CTkButton(header_ctrls, text=self.config.get_text("btn_start"), fg_color=THEME["status_running"], hover_color="#059669", width=90, height=34, font=ctk.CTkFont(weight="bold"), command=self.start_typer)
        self.start_btn.pack(side="left", padx=(0, 8))
        self.labels_to_update["btn_start"] = self.start_btn

        self.stop_btn = ctk.CTkButton(header_ctrls, text=self.config.get_text("btn_stop"), fg_color=THEME["status_stopped"], hover_color="#DC2626", width=90, height=34, state="disabled", font=ctk.CTkFont(weight="bold"), command=self.stop_typer)
        self.stop_btn.pack(side="left")
        self.labels_to_update["btn_stop"] = self.stop_btn

        # --- Sidebar (Left Navigation) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=THEME["sidebar_bg"], border_width=1, border_color=THEME["border"])
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # Navigation Buttons Container
        nav_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        nav_box.pack(fill="x", padx=12, pady=(15, 0))

        self.nav_quotes_btn = self._create_nav_button(nav_box, "⚡  Config Cards", "nav_quotes", self._show_quotes_view)
        self.nav_visualizer_btn = self._create_nav_button(nav_box, "⌨️  Keyboard Map", "nav_visualizer", self._show_visualizer_view)
        self.nav_editor_btn = self._create_nav_button(nav_box, "📝  Quote Studio", "nav_editor", self._show_editor_view)

        # Sidebar Divider
        sidebar_sep = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=THEME["border"])
        sidebar_sep.pack(fill="x", padx=15, pady=(20, 15))

        # Sidebar Quick Options Section
        self.click_checkbox = ctk.CTkCheckBox(self.sidebar_frame, text="Right click on type", variable=self.click_after_typing, font=ctk.CTkFont(size=12), text_color=THEME["text_sub"], border_width=2, command=self._save_state)
        self.click_checkbox.pack(padx=20, pady=(0, 10), anchor="w")

        self.block_hotkeys_checkbox = ctk.CTkCheckBox(self.sidebar_frame, text=self.config.get_text("lbl_block_hotkeys"), variable=self.block_hotkeys_var, font=ctk.CTkFont(size=12), text_color=THEME["text_sub"], border_width=2, command=self._toggle_hotkey_blocker)
        self.block_hotkeys_checkbox.pack(padx=20, pady=(0, 15), anchor="w")
        self.labels_to_update["lbl_block_hotkeys"] = self.block_hotkeys_checkbox

        # Target Nickname Section
        target_header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        target_header.pack(fill="x", padx=20, pady=(0, 4))
        
        self.lbl_target_nickname = ctk.CTkLabel(target_header, text="🎯 " + self.config.get_text("lbl_target_nickname"), font=ctk.CTkFont(size=12), text_color=THEME["text_sub"])
        self.lbl_target_nickname.pack(side="left")
        self.labels_to_update["lbl_target_nickname"] = self.lbl_target_nickname

        self.target_nickname_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="e.g. Noobmaster69", 
                                                 textvariable=self.target_nickname_var,
                                                 fg_color=THEME["bg_dark"], border_width=1, border_color=THEME["border"], font=ctk.CTkFont(size=12))
        self.target_nickname_entry.pack(fill="x", padx=20, pady=(0, 15))
        self.target_nickname_entry.bind("<KeyRelease>", lambda e: self._on_target_nickname_change())

        # Typing Delay Section
        delay_header = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        delay_header.pack(fill="x", padx=20, pady=(0, 5))
        
        self.settings_label = ctk.CTkLabel(delay_header, text=self.config.get_text("settings_delay"), font=ctk.CTkFont(size=12), text_color=THEME["text_sub"])
        self.settings_label.pack(side="left")
        self.labels_to_update["settings_delay"] = self.settings_label
        
        self.delay_value_label = ctk.CTkLabel(delay_header, text="10ms", font=ctk.CTkFont(size=12, weight="bold"), text_color=THEME["accent_indigo"])
        self.delay_value_label.pack(side="right")

        self.delay_slider = ctk.CTkSlider(self.sidebar_frame, from_=0.01, to=0.05, number_of_steps=8, button_color=THEME["accent_indigo"], button_hover_color=THEME["accent_indigo_hover"], command=self.update_delay_label)
        self.delay_slider.pack(fill="x", padx=20, pady=(0, 20))
        self.delay_slider.bind("<ButtonRelease-1>", lambda event: self._save_state())

        # Footer Utilities
        self.changelog_btn = ctk.CTkButton(self.sidebar_frame, text="Changelog", fg_color="transparent", border_width=1, border_color=THEME["border"], text_color=THEME["text_sub"], hover_color=THEME["card_bg"], height=32, command=self._show_changelog)
        self.changelog_btn.pack(fill="x", padx=20, pady=(0, 8))

        self.reset_keys_btn = ctk.CTkButton(self.sidebar_frame, text="Reset Keys", fg_color="transparent", border_width=1, border_color=THEME["border"], text_color=THEME["text_sub"], hover_color=THEME["card_bg"], height=32, command=self._reset_all_keys)
        self.reset_keys_btn.pack(fill="x", padx=20, pady=(0, 15))

        # --- Main Content Area (Right) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=1, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Initialize Views
        self._init_quotes_view()
        self._init_visualizer_view()
        self._init_editor_view()

        # Show default view
        self._show_quotes_view()

    def _create_nav_button(self, parent, default_text, label_key, command_fn):
        btn = ctk.CTkButton(parent, text=default_text, corner_radius=8, height=38, width=196, 
                            fg_color="transparent", text_color=THEME["text_sub"], 
                            hover_color=THEME["card_bg"], font=ctk.CTkFont(size=13, weight="bold"),
                            anchor="w", command=command_fn)
        btn.pack(fill="x", pady=3)
        return btn

    def _init_quotes_view(self):
        self.config_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.config_container.grid_columnconfigure(0, weight=1)
        self.config_container.grid_rowconfigure(0, weight=1)

        self.quotes_view = ctk.CTkScrollableFrame(self.config_container, fg_color="transparent", corner_radius=0)
        self.quotes_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.quotes_view.grid_columnconfigure(0, weight=1)
        self.quotes_view.grid_columnconfigure(1, weight=1)

        # Custom Message Card (Full Width Banner)
        self.custom_card = ctk.CTkFrame(self.quotes_view, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        self.custom_card.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        custom_header = ctk.CTkFrame(self.custom_card, fg_color="transparent")
        custom_header.pack(fill="x", padx=15, pady=(12, 5))
        
        self.lbl_custom_msg = ctk.CTkLabel(custom_header, text="💬 " + self.config.get_text("lbl_custom_msg"), font=ctk.CTkFont(size=15, weight="bold"), text_color=THEME["text_main"])
        self.lbl_custom_msg.pack(side="left")
        self.labels_to_update["lbl_custom_msg"] = self.lbl_custom_msg

        self.custom_key_btn = ctk.CTkButton(custom_header, text=self.config.get_text("btn_set_key") + " (None)", 
                                            fg_color=THEME["btn_gray"], hover_color=THEME["btn_gray_hover"], 
                                            height=32, font=ctk.CTkFont(size=12, weight="bold"),
                                            command=lambda: self.start_key_detection('custom', self.custom_key_btn))
        self.custom_key_btn.pack(side="right")
        self.binding_buttons['custom'] = self.custom_key_btn

        self.message_entry = ctk.CTkTextbox(self.custom_card, height=55, fg_color=THEME["bg_dark"], border_width=1, border_color=THEME["border"], font=ctk.CTkFont(size=13))
        self.message_entry.pack(padx=15, pady=(0, 12), fill="x")

        # Refresh Dynamic Category Cards
        self._refresh_quotes_view_cards()

    def _refresh_quotes_view_cards(self):
        for widget in self.quotes_view.winfo_children():
            if widget != self.custom_card:
                widget.destroy()
        
        row = 1
        col = 0
        
        default_icon_map = {
            "Duke Nukem": "icons/custom_duke_nukem.png",
            "Duke Nukem Offensive": "icons/duke_nukem_offensive.png",
            "Duke Nukem Defensive": "icons/duke_nukem_defensive.png",
            "Evil Dead": "icons/evil_dead.png",
            "Terminator": "icons/terminator.png",
            "Gattuso": "icons/gattuso.png",
            "ASCII_Toxic": "icons/ascii_funny.png",
            "HACKER": "icons/hacker.png",
            "x-mas": "icons/x_mas.png",
            "ASCII_Neutral": "icons/ascii_neutral.png",
            "Shotty_gospel": "icons/shotty_gospel.png",
            "JEFFREY, BIBI": "icons/trump.png",
            "Genesis": "icons/custom_genesis.png",
            "ROZHUJNIACZ": "icons/rozhujniacz.png",
            "Direct Insult": "icons/direct_insult.png",
            "Rap God": "icons/rap_god.png",
            "MINA": "icons/mina.png",
            "Dirty Gay Jokes": "icons/dirty_gay_jokes.png",
            "blue_nade": "icons/pacpacman.png"
        }

        for category, q_list in QUOTES.items():
            if category not in self.key_map:
                self.key_map[category] = None
            if category not in self.mode_map:
                self.mode_map[category] = ctk.BooleanVar(value=False)

            icon_path = self.custom_icons.get(category, default_icon_map.get(category))
            quote_count = len(q_list)
            self._create_quote_card(self.quotes_view, category, icon_path, category, quote_count, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

    def _create_quote_card(self, parent, title, icon_path, binding_name, quote_count, row, col):
        card = ctk.CTkFrame(parent, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Header Box: Title + Count Badge
        card_header = ctk.CTkFrame(card, fg_color="transparent")
        card_header.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(card_header, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color=THEME["text_main"]).pack(side="left")
        
        # Badge Pill
        badge = ctk.CTkFrame(card_header, fg_color=THEME["bg_dark"], corner_radius=10)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=f"{quote_count} quotes", font=ctk.CTkFont(size=10, weight="bold"), text_color=THEME["accent_indigo"]).pack(padx=8, pady=2)

        # Body Box (Icon + Key + Switch)
        card_body = ctk.CTkFrame(card, fg_color="transparent")
        card_body.pack(fill="x", padx=15, pady=(0, 12))

        # Drag and Drop Icon Label
        icon_frame = ctk.CTkFrame(card_body, fg_color=THEME["bg_dark"], width=72, height=72, corner_radius=10, border_width=1, border_color=THEME["border"])
        icon_frame.pack(side="left", padx=(0, 15))
        icon_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(icon_frame, text="", cursor="hand2")
        icon_label.pack(expand=True, fill="both")
        
        icon_label.bind("<Button-1>", lambda e, c=binding_name: self._change_icon(c))
        icon_label.drop_target_register(DND_FILES)
        icon_label.dnd_bind('<<Drop>>', lambda e, c=binding_name: self._handle_drop_icon(e, c))
        
        icon_img = self._load_image(icon_path, size=(54, 54))
        icon_label.configure(image=icon_img)
        
        self.icon_labels[binding_name] = icon_label
        self.icon_images[binding_name] = icon_img

        # Controls Box
        ctrl_box = ctk.CTkFrame(card_body, fg_color="transparent")
        ctrl_box.pack(side="left", fill="both", expand=True)

        # Set Key Button
        btn = ctk.CTkButton(ctrl_box, text=self.config.get_text("btn_set_key") + " (None)", 
                            fg_color=THEME["btn_gray"], hover_color=THEME["btn_gray_hover"],
                            height=34, font=ctk.CTkFont(size=12, weight="bold"),
                            command=lambda b=binding_name: self.start_key_detection(b, self.binding_buttons[b]))
        btn.pack(fill="x", pady=(0, 6))

        # Random Toggle Switch
        switch = ctk.CTkSwitch(ctrl_box, text=self.config.get_text("lbl_random"), 
                               variable=self.mode_map[binding_name], font=ctk.CTkFont(size=11),
                               text_color=THEME["text_sub"], progress_color=THEME["accent_indigo"],
                               command=self._save_state)
        switch.pack(anchor="w")
        self.labels_to_update[f"lbl_random_{binding_name}"] = switch 
        
        self.binding_buttons[binding_name] = btn 
        return btn

    def _change_icon(self, category):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self._update_icon_from_path(file_path, category)

    def _handle_drop_icon(self, event, category):
        file_path = event.data
        if file_path:
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                self._update_icon_from_path(file_path, category)
            else:
                messagebox.showerror("Error", "Unsupported file type. Please drop an image (.png, .jpg, .jpeg)")

    def _update_icon_from_path(self, file_path, category):
        try:
            img = Image.open(file_path)
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            
            icons_dir = os.path.join(BASE_DIR, "icons")
            if not os.path.exists(icons_dir):
                os.makedirs(icons_dir)
                
            new_filename = os.path.join("icons", f"custom_{category.replace(' ', '_').lower()}.png")
            full_save_path = os.path.join(BASE_DIR, new_filename)
            img.save(full_save_path)
            
            new_ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(54, 54))
            if category in self.icon_labels:
                self.icon_labels[category].configure(image=new_ctk_img)
                self.icon_images[category] = new_ctk_img
                
            self.custom_icons[category] = new_filename.replace("\\", "/")
            self._save_state()
            
        except Exception as e:
            print(f"Error changing icon: {e}")
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def _init_visualizer_view(self):
        self.visualizer_view = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Heatmap Header
        v_header = ctk.CTkFrame(self.visualizer_view, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        v_header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(v_header, text="⌨️ Live Keyboard Visualizer", font=ctk.CTkFont(size=16, weight="bold"), text_color=THEME["text_main"]).pack(side="left", padx=15, pady=12)

        self._build_visualizer_content(self.visualizer_view, scale=0.75)

    def _init_editor_view(self):
        self.editor_view = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.editor_view.grid_columnconfigure(0, weight=1)
        self.editor_view.grid_rowconfigure(1, weight=1)

        # Top Bar (Category Selection & Actions)
        top_bar = ctk.CTkFrame(self.editor_view, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        top_bar.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(top_bar, text=self.config.get_text("lbl_select_cat"), font=ctk.CTkFont(size=13, weight="bold"), text_color=THEME["text_main"]).pack(side="left", padx=(15, 8), pady=12)
        
        self.cat_var = ctk.StringVar(value="")
        self.cat_option = ctk.CTkOptionMenu(top_bar, variable=self.cat_var, fg_color=THEME["btn_gray"], button_color=THEME["accent_indigo"], button_hover_color=THEME["accent_indigo_hover"], command=self._on_cat_selected)
        self.cat_option.pack(side="left", padx=5)
        
        ctk.CTkButton(top_bar, text="+ " + self.config.get_text("btn_add_cat"), fg_color=THEME["accent_indigo"], hover_color=THEME["accent_indigo_hover"], command=self._add_category, width=110).pack(side="left", padx=8)
        ctk.CTkButton(top_bar, text="🗑️ " + self.config.get_text("btn_del_cat"), command=self._del_category, width=110, fg_color=THEME["status_stopped"], hover_color="#DC2626").pack(side="left", padx=5)
        
        ctk.CTkButton(top_bar, text="💾 " + self.config.get_text("btn_save"), command=self._save_quotes, fg_color=THEME["status_running"], hover_color="#059669").pack(side="right", padx=15)

        # Quotes List Frame
        self.quotes_list_frame = ctk.CTkScrollableFrame(self.editor_view, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        self.quotes_list_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Bottom Bar (Add New Quote)
        bottom_bar = ctk.CTkFrame(self.editor_view, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], corner_radius=12)
        bottom_bar.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        
        self.new_quote_entry = ctk.CTkEntry(bottom_bar, placeholder_text="Type new quote text here...", fg_color=THEME["bg_dark"], border_width=1, border_color=THEME["border"], font=ctk.CTkFont(size=13))
        self.new_quote_entry.pack(side="left", fill="x", expand=True, padx=15, pady=12)
        
        ctk.CTkButton(bottom_bar, text="+ " + self.config.get_text("btn_add_quote"), fg_color=THEME["accent_indigo"], hover_color=THEME["accent_indigo_hover"], command=self._add_quote).pack(side="right", padx=15)
        
        self._refresh_cat_option()

    def _refresh_cat_option(self):
        cats = list(QUOTES.keys())
        self.cat_option.configure(values=cats)
        if cats:
            if self.cat_var.get() not in cats:
                self.cat_var.set(cats[0])
            self._on_cat_selected(self.cat_var.get())
        else:
            self.cat_var.set("")
            self._clear_quotes_list()

    def _on_cat_selected(self, choice):
        self._clear_quotes_list()
        if choice in QUOTES:
            for i, quote in enumerate(QUOTES[choice]):
                self._create_quote_item(i, quote)

    def _clear_quotes_list(self):
        for widget in self.quotes_list_frame.winfo_children():
            widget.destroy()

    def _create_quote_item(self, index, text):
        item = ctk.CTkFrame(self.quotes_list_frame, fg_color=THEME["bg_dark"], border_width=1, border_color=THEME["border"], corner_radius=8)
        item.pack(fill="x", pady=4, padx=5)
        
        ctk.CTkButton(item, text="▲", width=28, height=28, fg_color=THEME["btn_gray"], hover_color=THEME["btn_gray_hover"], command=lambda idx=index: self._move_quote_up(idx)).pack(side="left", padx=(6, 2), pady=6)
        ctk.CTkButton(item, text="▼", width=28, height=28, fg_color=THEME["btn_gray"], hover_color=THEME["btn_gray_hover"], command=lambda idx=index: self._move_quote_down(idx)).pack(side="left", padx=2, pady=6)

        entry = ctk.CTkEntry(item, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], font=ctk.CTkFont(size=12))
        entry.insert(0, text)
        entry.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        entry.bind("<FocusOut>", lambda e, idx=index: self._update_quote_text(idx, entry.get()))
        
        ctk.CTkButton(item, text="✕", width=28, height=28, fg_color=THEME["status_stopped"], hover_color="#DC2626", 
                      command=lambda idx=index: self._del_quote(idx)).pack(side="right", padx=6, pady=6)

    def _move_quote_up(self, index):
        cat = self.cat_var.get()
        if cat in QUOTES and index > 0:
            QUOTES[cat][index], QUOTES[cat][index-1] = QUOTES[cat][index-1], QUOTES[cat][index]
            self._on_cat_selected(cat)

    def _move_quote_down(self, index):
        cat = self.cat_var.get()
        if cat in QUOTES and index < len(QUOTES[cat]) - 1:
            QUOTES[cat][index], QUOTES[cat][index+1] = QUOTES[cat][index+1], QUOTES[cat][index]
            self._on_cat_selected(cat)

    def _update_quote_text(self, index, new_text):
        cat = self.cat_var.get()
        if cat in QUOTES and 0 <= index < len(QUOTES[cat]):
            QUOTES[cat][index] = new_text

    def _add_category(self):
        dialog = ctk.CTkInputDialog(text="Enter New Category Name:", title="New Category")
        name = dialog.get_input()
        if name:
            if name not in QUOTES:
                QUOTES[name] = []
                self._refresh_cat_option()
                self.cat_var.set(name)
                self._on_cat_selected(name)
            else:
                messagebox.showerror("Error", "Category already exists!")

    def _del_category(self):
        cat = self.cat_var.get()
        if cat and messagebox.askyesno("Confirm", f"Delete category '{cat}'?"):
            del QUOTES[cat]
            self._save_quotes()
            self._refresh_cat_option()

    def _add_quote(self):
        cat = self.cat_var.get()
        text = self.new_quote_entry.get()
        if cat and text:
            QUOTES[cat].append(text)
            self.new_quote_entry.delete(0, "end")
            self._on_cat_selected(cat)

    def _del_quote(self, index):
        cat = self.cat_var.get()
        if cat and 0 <= index < len(QUOTES[cat]):
            QUOTES[cat].pop(index)
            self._on_cat_selected(cat)

    def _save_quotes(self):
        try:
            quotes_file = os.path.join(BASE_DIR, "quotes.json")
            with open(quotes_file, "w", encoding="utf-8") as f:
                json.dump(QUOTES, f, indent=4)
            messagebox.showinfo("Success", "Quotes saved successfully!")
            self._refresh_quotes_view_cards()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save quotes: {e}")

    def _show_quotes_view(self):
        self._hide_all_views()
        self.config_container.grid(row=0, column=0, sticky="nsew")
        self._set_nav_active(self.nav_quotes_btn)

    def _show_visualizer_view(self):
        self._hide_all_views()
        self.visualizer_view.grid(row=0, column=0, sticky="nsew")
        self._set_nav_active(self.nav_visualizer_btn)

    def _show_editor_view(self):
        self._hide_all_views()
        self.editor_view.grid(row=0, column=0, sticky="nsew")
        self._set_nav_active(self.nav_editor_btn)

    def _hide_all_views(self):
        self.config_container.grid_forget()
        self.visualizer_view.grid_forget()
        self.editor_view.grid_forget()

    def _set_nav_active(self, active_btn):
        for btn in [self.nav_quotes_btn, self.nav_visualizer_btn, self.nav_editor_btn]:
            if btn == active_btn:
                btn.configure(fg_color=THEME["accent_indigo"], text_color=THEME["text_main"])
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_sub"])

    def _build_visualizer_content(self, parent, scale=0.75):
        self.debug_label = ctk.CTkLabel(parent, text=self.config.get_text("lbl_last_key") + " None", font=ctk.CTkFont(size=12), text_color=THEME["accent_indigo"])
        self.debug_label.pack(pady=5)
        self.labels_to_update["lbl_last_key"] = self.debug_label

        self.kb_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.kb_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.key_widgets = {}

        self.g_frame = ctk.CTkFrame(self.kb_container, fg_color="transparent")
        self.g_frame.grid(row=0, column=0, sticky="ns", padx=(0, int(8*scale)))

        self.main_block = ctk.CTkFrame(self.kb_container, fg_color="transparent")
        self.main_block.grid(row=0, column=1, sticky="ns")

        self.arrow_frame = ctk.CTkFrame(self.kb_container, fg_color="transparent")
        self.arrow_frame.grid(row=0, column=2, sticky="s", padx=int(8*scale))

        self.numpad_frame = ctk.CTkFrame(self.kb_container, fg_color="transparent")
        self.numpad_frame.grid(row=0, column=3, sticky="s", padx=(0, 0))

        # Build G-Keys
        for i in range(5):
            g_num = i + 1
            f_num = 13 + i
            self._create_key_btn(self.g_frame, f"F{f_num}", width=48, height=38, display_text=f"G{g_num}", scale=scale)

        # Build Main Block
        g_row_frame = ctk.CTkFrame(self.main_block, fg_color="transparent")
        g_row_frame.pack(fill="x", pady=(0, int(4*scale)))
        for i in range(4):
            g_num = 6 + i
            f_num = 18 + i
            self._create_key_btn(g_row_frame, f"F{f_num}", width=48, height=28, side="left", display_text=f"G{g_num}", scale=scale)

        f_row_frame = ctk.CTkFrame(self.main_block, fg_color="transparent")
        f_row_frame.pack(fill="x", pady=(0, int(4*scale)))
        f_keys = ['ESC', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'PRTSC', 'SCRLK', 'PAUSE']
        for key in f_keys:
            w = 38
            if key in ['PRTSC', 'SCRLK', 'PAUSE']: w = 46
            self._create_key_btn(f_row_frame, key, width=w, height=28, side="left", scale=scale)

        rows = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE'],
            ['TAB', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['CAPS', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'ENTER'],
            ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'RSHIFT'],
            ['CTRL', 'WIN', 'ALT', 'SPACE', 'RALT', 'FN', 'MENU', 'RCTRL']
        ]
        
        for r_idx, row_keys in enumerate(rows):
            row_frame = ctk.CTkFrame(self.main_block, fg_color="transparent")
            row_frame.pack(fill="x", pady=int(2*scale))
            for key in row_keys:
                w = 38
                if key == 'BACKSPACE': w = 68
                elif key == 'TAB': w = 58
                elif key == 'CAPS': w = 68
                elif key == 'ENTER': w = 78
                elif key == 'SHIFT': w = 88
                elif key == 'SPACE': w = 210
                elif len(key) > 1: w = 46
                
                self._create_key_btn(row_frame, key, width=w, height=38, side="left", scale=scale)

        # Build Arrow Block
        ctrl_frame = ctk.CTkFrame(self.arrow_frame, fg_color="transparent")
        ctrl_frame.pack(pady=(0, int(15*scale)))
        
        ctrl_keys = [
            ['INSERT', 'HOME', 'PAGE UP'],
            ['DELETE', 'END', 'PAGE DOWN']
        ]
        for row in ctrl_keys:
            r_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
            r_frame.pack()
            for k in row:
                text = k
                if k == 'PAGE UP': text = 'PGUP'
                if k == 'PAGE DOWN': text = 'PGDN'
                if k == 'INSERT': text = 'INS'
                if k == 'DELETE': text = 'DEL'
                
                self._create_key_btn(r_frame, k, width=38, height=38, side="left", display_text=text, scale=scale)

        arr_frame = ctk.CTkFrame(self.arrow_frame, fg_color="transparent")
        arr_frame.pack(pady=(int(15*scale), 0))
        
        up_frame = ctk.CTkFrame(arr_frame, fg_color="transparent")
        up_frame.pack()
        self._create_key_btn(up_frame, 'UP', width=38, height=38, scale=scale)
        
        down_frame = ctk.CTkFrame(arr_frame, fg_color="transparent")
        down_frame.pack()
        for k in ['LEFT', 'DOWN', 'RIGHT']:
            self._create_key_btn(down_frame, k, width=38, height=38, side="left", scale=scale)

        # Build Numpad
        num_grid = [
            ['NUM', '/', '*', '-'],
            ['7', '8', '9', '+'],
            ['4', '5', '6', ''],
            ['1', '2', '3', 'ENTER'],
            ['0', '', '.', '']
        ]
        for r, row_keys in enumerate(num_grid):
            for c, key in enumerate(row_keys):
                if key:
                    m_name = None
                    if key.isdigit():
                        m_name = f"num {key}"
                    elif key == '.': m_name = "num ."
                    elif key == '/': m_name = "num /"
                    elif key == '*': m_name = "num *"
                    elif key == '-': m_name = "num -"
                    elif key == '+': m_name = "num +"
                    elif key == 'ENTER': m_name = "num enter"
                    
                    btn = self._create_key_btn(self.numpad_frame, key, width=38, height=38, pack=False, scale=scale, map_name=m_name)
                    if key == '0':
                        btn.configure(width=int(80*scale))
                        btn.grid(row=r, column=c, columnspan=2, padx=int(2*scale), pady=int(2*scale))
                    elif key == '+':
                        btn.configure(height=int(80*scale))
                        btn.grid(row=r, column=c, rowspan=2, padx=int(2*scale), pady=int(2*scale))
                    elif key == 'ENTER' and r == 3:
                        btn.configure(height=int(80*scale))
                        btn.grid(row=r, column=c, rowspan=2, padx=int(2*scale), pady=int(2*scale))
                    else:
                        btn.grid(row=r, column=c, padx=int(2*scale), pady=int(2*scale))

        try:
            keyboard.unhook_all()
        except:
            pass
        keyboard.hook(self._on_key_event)

    def _create_key_btn(self, parent, text, width=38, height=38, side="top", pack=True, display_text=None, scale=1.0, map_name=None):
        if map_name is None:
            map_name = text.lower()
            if map_name == 'esc': map_name = 'escape'
            if map_name == 'win': map_name = 'left windows'
            if map_name == 'menu': map_name = 'right menu'
            if map_name == 'num': map_name = 'num lock'
            if map_name == 'prtsc': map_name = 'print screen'
            if map_name == 'scrlk': map_name = 'scroll lock'
            if map_name == 'enter': map_name = 'enter'
            if map_name == 'backspace': map_name = 'backspace'
            if map_name == 'caps': map_name = 'caps lock'
            if map_name == 'shift': map_name = 'shift'
            if map_name == 'rshift': map_name = 'right shift'
            if map_name == 'ctrl': map_name = 'ctrl'
            if map_name == 'rctrl': map_name = 'right ctrl'
            if map_name == 'alt': map_name = 'alt'
            if map_name == 'ralt': map_name = 'right alt'
        
        btn_text = display_text if display_text else text
        
        s_width = int(width * scale)
        s_height = int(height * scale)
        s_font = int(11 * scale)
        if s_font < 8: s_font = 8
        
        btn = ctk.CTkButton(parent, text=btn_text, width=s_width, height=s_height, 
                            fg_color=THEME["card_bg"], hover_color=THEME["card_bg"], state="disabled", text_color="white",
                            border_width=1, border_color=THEME["border"], corner_radius=6,
                            font=("Roboto", s_font))
        if pack:
            btn.pack(side=side, padx=int(2*scale), pady=int(2*scale))
        
        self.key_widgets[map_name] = btn
        if len(text) == 1 and not map_name.startswith("num "):
             self.key_widgets[text.lower()] = btn
             
        return btn

    def _on_key_event(self, e):
        try:
            key_name = e.name.lower()
            event_type = e.event_type
            self.after(0, lambda: self._update_key_visual(key_name, event_type))
        except:
            pass

    def _update_key_visual(self, key_name, event_type):
        prefix = self.config.get_text("lbl_last_key")
        self.debug_label.configure(text=f"{prefix} {key_name.upper()} ({event_type.upper()})")
        
        if key_name in self.key_widgets:
            btn = self.key_widgets[key_name]
            if event_type == keyboard.KEY_DOWN:
                btn.configure(fg_color=THEME["accent_indigo"], border_color=THEME["accent_indigo_hover"])
            elif event_type == keyboard.KEY_UP:
                btn.configure(fg_color=THEME["card_bg"], border_color=THEME["border"])

    def update_delay_label(self, value):
        ms = int(round((float(value) * 1000) / 5.0) * 5)
        ms = max(10, min(50, ms))
        self.delay_value_label.configure(text=f"{ms}ms")

    def start_key_detection(self, binding_name, btn_widget):
        if self.is_detecting_key:
            return
            
        btn_widget.configure(text=self.config.get_text("btn_press_key"), state="disabled", fg_color=THEME["accent_indigo"])
        self.is_detecting_key = True
        self.active_binding_btn = btn_widget
        
        threading.Thread(target=self._detect_key_thread, args=(binding_name,), daemon=True).start()

    def _detect_key_thread(self, binding_name):
        key = self.typer.detect_key()
        
        if key:
            for name, assigned_key in self.key_map.items():
                if name != binding_name and assigned_key == key:
                    self.key_map[name] = None
                    self.after(0, lambda n=name: self._update_single_button(n))

            self.key_map[binding_name] = key
            self._save_state()
            
        self.after(0, lambda: self._update_single_button(binding_name))
        self.after(0, self._update_active_keys_count)
        
        self.is_detecting_key = False
        self.active_binding_btn = None

    def _update_single_button(self, binding_name):
        btn = self.binding_buttons.get(binding_name)
        if btn:
            key = self.key_map.get(binding_name)
            prefix = self.config.get_text("btn_set_key")
            btn.configure(text=f"{prefix} ({key.upper() if key else 'None'})", state="normal",
                          fg_color=THEME["accent_indigo"] if key else THEME["btn_gray"])

    def _update_button_texts(self):
        for name in self.binding_buttons.keys():
            self._update_single_button(name)

    def _update_active_keys_count(self):
        active_count = sum(1 for k in self.key_map.values() if k is not None)
        self.active_keys_pill.configure(text=f"⚡ {active_count} Hotkeys Active")

    def start_typer(self):
        self.typer.clear_bindings()
        self._save_state()
        
        has_binding = False
        
        custom_key = self.key_map['custom']
        if custom_key:
            msg = self.message_entry.get("1.0", "end-1c")
            self.typer.set_custom_message(msg)
            self.typer.add_binding(custom_key, 'custom')
            has_binding = True
            
        for category in QUOTES.keys():
            key = self.key_map.get(category)
            if key:
                self.typer.add_binding(key, 'quote', category)
                has_binding = True
            
            is_random = self.mode_map[category].get()
            self.typer.set_mode(category, is_random)

        if not has_binding:
            self.status_text.configure(text=self.config.get_text("err_no_keys"), text_color="orange")
            self.status_dot.configure(text_color="orange")
            return

        self.typer.set_delay(self.delay_slider.get())
        self.typer.set_click_after_typing(self.click_after_typing.get())
        self.typer.set_target_nickname(self.target_nickname_var.get())

        if self.typer.start():
            self.status_dot.configure(text_color=THEME["status_running"])
            self.status_text.configure(text=self.config.get_text("status_running"))
            self._set_inputs_state("disabled")

    def stop_typer(self):
        self.typer.stop()
        self.status_dot.configure(text_color=THEME["status_stopped"])
        self.status_text.configure(text=self.config.get_text("status_stopped"))
        self._set_inputs_state("normal")

    def _on_target_nickname_change(self):
        nickname = self.target_nickname_var.get()
        self.typer.set_target_nickname(nickname)
        self._save_state()

    def _set_inputs_state(self, state):
        self.start_btn.configure(state="disabled" if state == "disabled" else "normal")
        self.stop_btn.configure(state="normal" if state == "disabled" else "disabled")
        
        for btn in self.binding_buttons.values():
            btn.configure(state=state)
            
        self.message_entry.configure(state=state)
        self.delay_slider.configure(state=state)

    def _change_language(self, choice):
        lang_map = {
            "English": "en",
            "Polski": "pl",
            "Español": "es",
            "Português": "pt",
            "Deutsch": "de"
        }
        code = lang_map.get(choice, "en")
        self.config.set_language(code)
        self._update_ui_text()

    def _set_lang_dropdown_value(self):
        lang_map_rev = {
            "en": "English",
            "pl": "Polski",
            "es": "Español",
            "pt": "Português",
            "de": "Deutsch"
        }
        val = lang_map_rev.get(self.config.current_lang, "English")
        self.lang_option.set(val)

    def _update_ui_text(self):
        self.title(self.config.get_text("app_title"))
        
        for key, widget in self.labels_to_update.items():
            if key.startswith("lbl_random_"):
                widget.configure(text=self.config.get_text("lbl_random"))
            else:
                widget.configure(text=self.config.get_text(key))
                
        self._update_button_texts()
        
        if self.typer.is_running:
            self.status_text.configure(text=self.config.get_text("status_running"))
        else:
            self.status_text.configure(text=self.config.get_text("status_stopped"))

    def _restart_app(self):
        if self.typer.is_running:
            self.stop_typer()
        if self.hotkey_blocker.is_active():
            self.hotkey_blocker.stop()
        self._save_state()
        self.destroy()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _reset_all_keys(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear ALL key bindings?"):
            for key in self.key_map:
                self.key_map[key] = None
            self._save_state()
            self._update_button_texts()
            self._update_active_keys_count()

    def _show_changelog(self):
        try:
            changelog_file = os.path.join(BASE_DIR, "CHANGELOG.md")
            with open(changelog_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            top = ctk.CTkToplevel(self)
            top.title("Changelog")
            top.geometry("600x500")
            top.configure(fg_color=THEME["bg_dark"])
            
            textbox = ctk.CTkTextbox(top, fg_color=THEME["card_bg"], border_width=1, border_color=THEME["border"], font=ctk.CTkFont(size=12))
            textbox.pack(fill="both", expand=True, padx=15, pady=15)
            textbox.insert("1.0", content)
            textbox.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load changelog: {e}")

    def _toggle_hotkey_blocker(self):
        is_enabled = self.block_hotkeys_var.get()
        if is_enabled:
            self.hotkey_blocker.start()
        else:
            self.hotkey_blocker.stop()
        self._save_state()

    def _on_close(self):
        if self.typer.is_running:
            self.stop_typer()
        if self.hotkey_blocker.is_active():
            self.hotkey_blocker.stop()
        self._save_state()
        self.destroy()

    def _save_state(self):
        settings = {
            "language": self.config.current_lang,
            "delay": round(max(10, min(50, int(round((self.delay_slider.get() * 1000) / 5.0) * 5))) / 1000.0, 3),
            "custom_message": self.message_entry.get("1.0", "end-1c"),
            "target_nickname": self.target_nickname_var.get(),
            "keys": self.key_map,
            "modes": {k: v.get() for k, v in self.mode_map.items()},
            "icons": self.custom_icons,
            "click_after_typing": self.click_after_typing.get(),
            "block_low_level_hotkeys": self.block_hotkeys_var.get()
        }
        self.config.save_settings(settings)

if __name__ == "__main__":
    app = App()
    app.mainloop()
