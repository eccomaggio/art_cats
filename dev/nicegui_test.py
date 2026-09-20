from nicegui import ui
import yaml
from collections.abc import MutableMapping
from typing import Any #, Iterator, Tuple, Union


class DoubleHash:
  # def __init__(self, i1=0, i2=1):
  #   ## the first key is an int, the second a string
  #   ## i1 = column number (starting from 0)
  #   ## i2 = column title
  #   self.i1 = i1
  #   self.i2 = i2
  #   self.key1_type = int
  #   self.key2_type = str
  #   self._data = {}
  def __init__(self, *, indices:tuple[int, int]):
    ## the first key is an int, the second a string
    ## i1 = column number (starting from 0)
    ## i2 = column title
    self.i1 = indices[0]
    self.i2 = indices[1]
    self.key1_type = int
    self.key2_type = str
    self._data = {}

  def add(self, value: list):
    key1 = value[self.i1]
    key2 = value[self.i2]
    if isinstance(key1, self.key1_type) and isinstance(key2, self.key2_type):
      self._data[key1] = value
      self._data[key2] = value
    else:
      raise ValueError(
        f"key1 ({key1}) must be {self.key1_type} and key2 ({key2}) must be {self.key2_type}."
      )

  def remove(self, key: str | int):
    """Given one key, extracts the other and deletes both references and the content."""
    # print(f"{key=} in {self._data}")
    if isinstance(key, int):
      key1 = key
      key2 = self._data[key][self.i2]
    else:
      key2 = key
      key1 = self._data[key][self.i1]
    # print(f"\t{key=}, {key1=}, {key2=}\n")
    self._data.pop(key1, None)
    self._data.pop(key2, None)

  def __getitem__(self, key):
    return self._data[key]

  def __repr__(self):
    return repr(self._data)

  def __len__(self):
    return int(len(self._data) / 2)

  def __iter__(self):
    self.index = 0
    return self

  def __next__(self):
    if self.index < self.__len__():
      current_index = self.index
      self.index += 1
      return self._data[current_index]
    else:
      raise StopIteration


def load_configuration_file() -> DoubleHash:
  # Open and parse the YAML file
  with open("./dev/art-cats_defaults.yaml", "r") as file:
  # safe_load prevents execution of arbitrary code
    config = yaml.safe_load(file)
  # print(f"{config=}")
  return config


def load_combo_options() -> dict:
  combo_options = {
    "sublib" : ["ARTBL", "TAYBL", "BODOF"],
    "illustrations" : ["None", "Partial", "Full"],
    "default": ["unknown"]
  }
  # print(f"{combo_options=}")
  return combo_options


def get_pattern_info(config):
  pattern = config["pattern"]
  col_count = pattern["gui_column_count"]
  cols = DoubleHash(indices=(0, 6))  # col number added programatically
  for i, col in enumerate(pattern["column_info"]):
    print(f"\t** {i},{col}")
    cols.add([i, *col])
  # print(f"{col_count=}\n{cols=}")
  return col_count, cols



def get_nav_info(config):
  pattern = config["pattern"]
  nav_position = pattern["nav_position"] # 'top', 'bottom', 'left', 'right'
  nav_config = config["nav_landscape"] if nav_position in ["top", "bottom"] else config["nav_portrait"]
  nav_config["column_info"] = [[i, *values] for i, values in enumerate(nav_config["column_info"])]
  # print(f"{nav_position=}\n{nav_config=}")
  return nav_position, nav_config


def get_help_info(config):
  pattern = config["pattern"]
  help_position = pattern["help_position"] # 'left', 'right', or None (hidden)
  # print(f"{help_position}")
  return help_position


def choose_input_widget(widget_type:str, class_text: str, placeholder_text:str, combo_options):
    base_props = "dense square"
    combo_option_default = combo_options[0]

    match widget_type:
        case "text":
            return (
                ui.textarea(placeholder=placeholder_text)
                .classes(f"{class_text} resize-y")
                .props(f"{base_props} rows=1")
            )
        case "combo":
            return (
        ui.select(options=combo_options, value=combo_option_default)
      .classes(class_text)
      .props(f"{base_props} options-dense")
      )
        case "chip":
          return(
             ui.chip()
          )
          pass
        case _:
            return (
        ui.input(placeholder=placeholder_text)
      .classes(class_text)
      .props(base_props)
      )

def create_nav_bar(nav_config:dict):
  widgets = {}
  with ui.grid(columns=nav_config["gui_column_count"]).classes(
    "w-full gap-2 p-0 items-stretch max-w-4xl"
  ) as nav_grid:
    for col in nav_config["column_info"]:
      (
        col_num,
        row_span,
        col_span,
        start_row,
        start_col,
        widget_type,
        name,
        title,
      ) = col
      start_row += 1
      start_col += 1

      col_span_class = f"col-span-{col_span} " if col_span > 1 else ""
      row_span_class = f"row-span-{row_span} " if row_span > 1 else ""
      col_position = f"col_start-{start_col} row-start-{start_row} {col_span_class}{row_span_class}"
      widgets[name] = ui.chip(title) \
        .classes(col_position) \
        .props("outline square")
  return nav_grid, widgets


def create_form_grid(cols:DoubleHash, combo_options:dict, col_count:int):
  widgets = {}
  with ui.grid(columns=col_count).classes(
    "w-full gap-2 p-0 items-stretch max-w-4xl"
  ) as dynamic_grid:
    for col in cols:
      (
        col_num,
        row_span,
        col_span,
        start_row,
        start_col,
        widget_type,
        name,
        title,
      ) = col
      start_row += 1
      start_col += 1

      col_span_class = f"col-span-{col_span} " if col_span > 1 else ""
      row_span_class = f"row-span-{row_span} " if row_span > 1 else ""
      col_position = f"col-start-{start_col} row-start-{start_row} {col_span_class}{row_span_class}"
      col_styling = "bg-sky-50 gap-0 p-3 rounded-sm"
      label_styling = "text-sm font-semibold text-gray-600 p-0 leading-none"

      with ui.column().classes(f"{col_position} {col_styling} items-stretch"):
        ui.label(title).classes(label_styling)
        widgets[name] = choose_input_widget(
          widget_type,
          "w-full bg-white p-0",
          "Type here...",
          combo_options.get(name, ["unknown"]),
        )
    return dynamic_grid, widgets


def create_help_panel(target_container):
  target_container.clear()
  with target_container:
  # with ui.column() as help_wrapper:
    back_button = ui.button(
      "Back",
      on_click=lambda: ui.run_javascript(
          'document.getElementById("help-frame").contentWindow.history.back()'
      ),
    ).props("flat outline")
    help_frame = (
      ui.element("iframe")
      .props('id="help-frame" src="https://example.com"')
      .classes("w-full h-[500px] border")
      # .props(
      #     'id="help-frame" src="file://./help_art_cats.html"'
      # ).classes("w-full border")
    )
  return help_frame, back_button


def create_top_level_containers(
    nav_position:str,
    nav_config:dict,
    help_position:str,
    cols,
    combo_options,
    col_count,
):
  help_frame, back_button = None, None
  nav_grid, nav_widgets = None, None
  form_grid, form_widgets = None, None
  # 2. Top-Level Layout (3 Columns: Left Slot, Center Slot, Right Slot)
  with ui.row().classes("w-full min-h-screen p-4 gap-4 items-stretch bg-slate-50"):
    left_help_container = ui.column().classes("w-64 bg-blue-50 p-4 border rounded")
    center_wrapper = ui.column().classes("grow min-w-0 bg-white p-4 shadow rounded")
    right_help_container = ui.column().classes("w-64 bg-blue-50 p-4 border rounded")

    # Update Help Panel visibility & slot
    left_help_container.set_visibility(help_position == 'left')
    right_help_container.set_visibility(help_position == 'right')

    nav_grid, nav_widgets = None, None
    form_grid, form_widgets = None, None

    if help_position == 'left':
      help_frame, back_button = create_help_panel(left_help_container)
    else:
      help_frame, back_button = create_help_panel(right_help_container)

    with center_wrapper:
      is_vertical = nav_position in ['top', 'bottom']
      if is_vertical:
        container = ui.column().classes('w-full gap-4')
      else:
        container = ui.row().classes('w-full gap-4 items-start')

      with container:
        if nav_position in ['top', 'left']:
          nav_grid, nav_widgets = create_nav_bar(nav_config)

        form_grid, form_widgets = create_form_grid(cols, combo_options, col_count)

        if nav_position in ['bottom', 'right']:
          nav_grid, nav_widgets = create_nav_bar(nav_config)

  return help_frame, back_button, nav_grid, nav_widgets, form_grid, form_widgets

def debug_grid(cols, combo_options, col_count:int):
  grid, widgets = create_form_grid(cols, combo_options, col_count)
  return grid, widgets



def main():
  config = load_configuration_file()
  combo_options = load_combo_options()
  nav_position, nav_config = get_nav_info(config)
  help_position = get_help_info(config)
  col_count, cols = get_pattern_info(config)

  # debug_grid(cols, combo_options, col_count)

  help_frame, back_button, nav_grid, nav_widgets, form_grid, form_widgets = create_top_level_containers(
    nav_position,
    nav_config,
    help_position,
    cols,
    combo_options,
    col_count,
    )

  ui.run()


main()











# if __name__ == "__main__":
#    main()


# ui.run(frameless=True)
# ui.run(native=True, reload=False)


# css = """
#   <style>
#     body {
#       margin: 10px;
#       min-height: 100dvh;
#       display: grid;
#       width: 800px;
#       grid-template-columns: repeat(6, 1fr);
#       grid-template-rows: repeat(17, 1fr);
#       gap: 10px 10px;
#     }

#     div {
#       background-color: antiquewhite;
#     }

# """
# htm = ""
# for i, col in enumerate(cols):
#   col_num, row_span, col_span, start_row, start_col, widget_type, name, title = col
#   start_row += 1
#   start_col += 1
#   css += f"    #{name} {{\n"
#   row_rest = f" / span {row_span}" if row_span > 1 else ""
#   css += f"      grid-row: {start_row}{row_rest};\n"
#   col_rest = f" / span {col_span}" if col_span > 1 else ""
#   css += f"      grid-column: {start_col}{col_rest};\n"
#   css += "    }\n\n"

#   htm += f"    <div id=\"{name}\">{name}</div>\n"
# css += "  </style>\n"

# print(css)
# print(htm)
