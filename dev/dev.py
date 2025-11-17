from dataclasses import dataclass
import json
from types import SimpleNamespace
from typing import Any, Dict, Callable, Optional
import yaml  # Requires: pip install pyyaml


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class DynamicNamespace(SimpleNamespace):
    """
    A dynamic namespace that supports:
    - Dot-access for attributes
    - Dict-like access for convenience
    - Recursive conversion of nested dicts to namespaces
    - JSON/YAML save/load
    - Nested field validation
    - Default values for missing keys
    """

    def __init__(self, defaults: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self._defaults = defaults or {}

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __getattr__(self, name: str) -> Any:
        # Return default if available, else raise AttributeError
        if name in self._defaults:
            value = self._defaults[name]
            # If default is dict, convert to DynamicNamespace
            if isinstance(value, dict):
                value = DynamicNamespace.from_dict(value)
            setattr(self, name, value)  # Cache it
            return value
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert back to a dict (recursively)."""
        result = {}
        for key, value in self.__dict__.items():
            if key == "_defaults":
                continue
            if isinstance(value, DynamicNamespace):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any], defaults: Optional[Dict[str, Any]] = None) -> "DynamicNamespace":
        """Create a DynamicNamespace from a dict (recursively)."""
        ns = cls(defaults=defaults)
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(ns, key, cls.from_dict(value, defaults.get(key) if defaults else None))
            else:
                setattr(ns, key, value)
        return ns

    # ✅ JSON Support
    def save_json(self, filepath: str, indent: int = 4) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=indent)

    @classmethod
    def load_json(cls, filepath: str, defaults: Optional[Dict[str, Any]] = None) -> "DynamicNamespace":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, defaults)

    # ✅ YAML Support
    def save_yaml(self, filepath: str) -> None:
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.to_dict(), f)

    @classmethod
    def load_yaml(cls, filepath: str, defaults: Optional[Dict[str, Any]] = None) -> "DynamicNamespace":
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.from_dict(data, defaults)

    # ✅ Validation
    def validate(self, rules: Dict[str, Callable[[Any], bool]]) -> None:
        for field_path, validator in rules.items():
            parts = field_path.split(".")
            value = self._get_nested(parts)
            if not validator(value):
                raise ValidationError(f"Validation failed for '{field_path}': value={value}")

    def _get_nested(self, parts: list) -> Any:
        obj = self
        for part in parts:
            obj = getattr(obj, part)
        return obj




# Example implementation (CoPilot 14 nov 2025)

# Define defaults
defaults = {
    "in_file": "default.xlsx",
    "out_file": "output.xlsx",
    "flavour": {
        "active_style": "modern",
        "theme": "light"
    },
    "styles": {}
}

# Partial user settings
settings_data = {
    "in_file": "custom.xlsx"
}

# Create settings with defaults
settings = DynamicNamespace.from_dict(settings_data, defaults)

# ✅ Access existing key
print(settings.in_file)  # "custom.xlsx"

# ✅ Access missing key -> returns default
print(settings.out_file)  # "output.xlsx"

# ✅ Nested default
print(settings.flavour.theme)  # "light"

# ✅ Add dynamically
settings.flavour.active_style = "classic"

# ✅ Save and load with defaults preserved
settings.save_json("settings.json")
loaded = DynamicNamespace.load_json("settings.json", defaults)
print(loaded.flavour.theme)  # "light"

settings.flavour.theme = "dark"

print(settings.flavour.theme)          # "dark"
print(settings["flavour"].theme)       # "dark"
print(settings.flavour["theme"])       # "dark"
print(settings["flavour"]["theme"])    # "dark"



@dataclass
class Files:
    in_file_full = ""
    in_file = ""
    out_file = ""
    default_output_filename = "output"
    app_dir = "app"
    data_dir = "input_files"
    output_dir = "output_files"
    help_file = "help.html"
    backup_file = "backup.bak"


@dataclass
class Validation:
    title= "art_catalogue"
    fields_to_clear = []
    fields_to_fill = [
        # E.G. [COL.sublib, "ARTBL"],
        [],
    ],
    required_fields = []
    validate_always = []
    validate_if_present = []
    validation_skip_field: COL | None = None
    validation_skip_text = "*dummy*"



@dataclass
class Styles:
    text_changed = "border: 1px solid red; background-color: white;"
    text_changed_border_only = "border: 1px solid red;"
    border_only_active = "border: 1px solid whitesmoke;"
    labels = "font-weight: bold;"
    label_active = "color: #7c6241;"
    label_locked = "color: darkgrey;"
    input_active = "border: 1px solid lightgrey; background-color: white;"
    input_locked = "border: 1px solid whitesmoke; background-color: whitesmoke;"
    combo_dropdown = "QComboBox QAbstractItemView {selection-background-color: #3B82F6; selection-color: white;}"


@dataclass
class Labels:
    show_help = "show help"
    hide_help = "hide help"


@dataclass
class Combos:
    default_text = " >> Choose <<"
    following_default_text = " (first select "
    independents = []
    leaders = []
    followers = []


@dataclass
class Settings:
    use_default_layout = True
    is_existing_file = True
    layout_template: tuple = ()
    first_row_is_header = True

    alt_title_signifier = "*//*"
    headers = [member.display_title for member in COL]
    files = Files()
    validation = Validation()
    styles = Styles()
    labels = Labels()
    locking_is_enabled = True
    show_table_view = True