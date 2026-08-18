import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
APP_VERSION = "1.0.0"

TRANSLATIONS = {
    "en": {
        "app_title": "EZ-Game-Chat",
        "sidebar_title": "EZ-Game-Chat",
        "nav_quotes": "Config",
        "nav_visualizer": "Visualizer",
        "nav_editor": "Editor",
        "settings_delay": "Typing Delay:",
        "status_stopped": "STOPPED",
        "status_running": "RUNNING",
        "btn_start": "START",
        "btn_stop": "STOP",
        "lbl_custom_msg": "Custom Message",
        "btn_set_key": "Set Key",
        "btn_press_key": "Press Key...",
        "lbl_random": "Random Order",
        "lbl_last_key": "Last Key:",
        "err_no_keys": "Error: No keys set!",
        "lbl_language": "Language:",
        "editor_title": "Quotes Editor",
        "btn_save": "Save Changes",
        "btn_add_cat": "Add Category",
        "btn_del_cat": "Delete Category",
        "btn_add_quote": "Add Quote",
        "btn_del_quote": "Delete Quote",
        "lbl_select_cat": "Select Category:",
        "lbl_cat_name": "Category Name:",
        "lbl_quote_text": "Quote Text:",
        "lbl_test_area": "Test Area (Type Here):",
        "btn_clear": "Clear",
        "lbl_target_nickname": "Target Nickname:",
        "lbl_block_hotkeys": "Block Hotkeys (Win/Ctrl/Shift)",
        "lbl_block_hotkeys_sub": "Low-level hook suppresses system shortcuts"
    },
    "pl": {
        "app_title": "EZ-Game-Chat",
        "sidebar_title": "EZ-Game-Chat",
        "nav_quotes": "Konfiguracja",
        "nav_visualizer": "Wizualizacja",
        "nav_editor": "Edytor",
        "settings_delay": "Opóźnienie:",
        "status_stopped": "ZATRZYMANE",
        "status_running": "DZIAŁA",
        "btn_start": "START",
        "btn_stop": "STOP",
        "lbl_custom_msg": "Własna Wiadomość",
        "btn_set_key": "Ustaw Klawisz",
        "btn_press_key": "Naciśnij...",
        "lbl_random": "Losowa Kolejność",
        "lbl_last_key": "Ostatni Klawisz:",
        "err_no_keys": "Błąd: Brak klawiszy!",
        "lbl_language": "Język:",
        "editor_title": "Edytor Cytatów",
        "btn_save": "Zapisz Zmiany",
        "btn_add_cat": "Dodaj Kategorię",
        "btn_del_cat": "Usuń Kategorię",
        "btn_add_quote": "Dodaj Cytat",
        "btn_del_quote": "Usuń Cytat",
        "lbl_select_cat": "Wybierz Kategorię:",
        "lbl_cat_name": "Nazwa Kategorii:",
        "lbl_quote_text": "Treść Cytatu:",
        "lbl_test_area": "Obszar Testowy:",
        "btn_clear": "Wyczyść",
        "lbl_target_nickname": "Nick Celu:",
        "lbl_block_hotkeys": "Blokuj skróty (Win/Ctrl/Shift)",
        "lbl_block_hotkeys_sub": "Niskopoziomowe blokowanie skrótów systemowych"
    },
    "es": {
        "app_title": "EZ-Game-Chat",
        "sidebar_title": "EZ-Game-Chat",
        "nav_quotes": "Configuración",
        "nav_visualizer": "Visualizador",
        "nav_editor": "Editor",
        "settings_delay": "Retraso:",
        "status_stopped": "DETENIDO",
        "status_running": "EJECUTANDO",
        "btn_start": "INICIAR",
        "btn_stop": "PARAR",
        "lbl_custom_msg": "Mensaje Personalizado",
        "btn_set_key": "Asignar Tecla",
        "btn_press_key": "Presiona Tecla...",
        "lbl_random": "Orden Aleatorio",
        "lbl_last_key": "Última Tecla:",
        "err_no_keys": "Error: ¡Sin teclas!",
        "lbl_language": "Idioma:",
        "editor_title": "Editor de Citas",
        "btn_save": "Guardar Cambios",
        "btn_add_cat": "Añadir Categoría",
        "btn_del_cat": "Eliminar Categoría",
        "btn_add_quote": "Añadir Cita",
        "btn_del_quote": "Eliminar Cita",
        "lbl_select_cat": "Seleccionar Categoría:",
        "lbl_cat_name": "Nombre de Categoría:",
        "lbl_quote_text": "Texto de la Cita:",
        "lbl_test_area": "Área de Prueba:",
        "btn_clear": "Limpiar",
        "lbl_target_nickname": "Apodo Objetivo:",
        "lbl_block_hotkeys": "Bloquear Atajos (Win/Ctrl/Shift)",
        "lbl_block_hotkeys_sub": "Gancho de bajo nivel suprime atajos de sistema"
    },
    "pt": {
        "app_title": "EZ-Game-Chat",
        "sidebar_title": "EZ-Game-Chat",
        "nav_quotes": "Configuração",
        "nav_visualizer": "Visualizador",
        "nav_editor": "Editor",
        "settings_delay": "Atraso:",
        "status_stopped": "PARADO",
        "status_running": "RODANDO",
        "btn_start": "INICIAR",
        "btn_stop": "PARAR",
        "lbl_custom_msg": "Mensagem Personalizada",
        "btn_set_key": "Definir Tecla",
        "btn_press_key": "Pressione...",
        "lbl_random": "Ordem Aleatória",
        "lbl_last_key": "Última Tecla:",
        "err_no_keys": "Erro: Sem teclas!",
        "lbl_language": "Idioma:",
        "editor_title": "Editor de Citações",
        "btn_save": "Salvar Alterações",
        "btn_add_cat": "Adicionar Categoria",
        "btn_del_cat": "Excluir Categoria",
        "btn_add_quote": "Adicionar Citação",
        "btn_del_quote": "Excluir Citação",
        "lbl_select_cat": "Selecionar Categoria:",
        "lbl_cat_name": "Nome da Categoria:",
        "lbl_quote_text": "Texto da Citação:",
        "lbl_test_area": "Área de Teste:",
        "btn_clear": "Limpar",
        "lbl_target_nickname": "Nick do Alvo:",
        "lbl_block_hotkeys": "Bloquear Atalhos (Win/Ctrl/Shift)",
        "lbl_block_hotkeys_sub": "Gancho de baixo nível suprime atalhos de sistema"
    },
    "de": {
        "app_title": "EZ-Game-Chat",
        "sidebar_title": "EZ-Game-Chat",
        "nav_quotes": "Konfiguration",
        "nav_visualizer": "Visualisierer",
        "nav_editor": "Editor",
        "settings_delay": "Verzögerung:",
        "status_stopped": "GESTOPPT",
        "status_running": "LÄUFT",
        "btn_start": "START",
        "btn_stop": "STOPP",
        "lbl_custom_msg": "Benutzerdefinierte Nachricht",
        "btn_set_key": "Taste Setzen",
        "btn_press_key": "Taste Drücken...",
        "lbl_random": "Zufällige Reihenfolge",
        "lbl_last_key": "Letzte Taste:",
        "err_no_keys": "Fehler: Keine Tasten!",
        "lbl_language": "Sprache:",
        "editor_title": "Zitat-Editor",
        "btn_save": "Änderungen Speichern",
        "btn_add_cat": "Kategorie Hinzufügen",
        "btn_del_cat": "Kategorie Löschen",
        "btn_add_quote": "Zitat Hinzufügen",
        "btn_del_quote": "Zitat Löschen",
        "lbl_select_cat": "Kategorie Wählen:",
        "lbl_cat_name": "Kategoriename:",
        "lbl_quote_text": "Zitattext:",
        "lbl_test_area": "Testbereich:",
        "btn_clear": "Löschen",
        "lbl_target_nickname": "Ziel-Nickname:",
        "lbl_block_hotkeys": "Hotkeys Sperren (Win/Strg/Shift)",
        "lbl_block_hotkeys_sub": "Low-Level Hook sperrt System-Shortcuts"
    }
}

DEFAULT_SETTINGS = {
    "language": "en",
    "delay": 0.01,
    "custom_message": "GG WP",
    "target_nickname": "",
    "keys": {},
    "modes": {},
    "click_after_typing": True,
    "block_low_level_hotkeys": False
}

class ConfigManager:
    def __init__(self):
        self.settings = self.load_settings()
        self.current_lang = self.settings.get("language", "en")

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    def save_settings(self, settings_dict):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings_dict, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_text(self, key):
        lang_dict = TRANSLATIONS.get(self.current_lang, TRANSLATIONS["en"])
        return lang_dict.get(key, key)

    def set_language(self, lang_code):
        if lang_code in TRANSLATIONS:
            self.current_lang = lang_code
            self.settings["language"] = lang_code
            self.save_settings(self.settings)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)
