# Constants for the dipper annotation tool

# Number of colour groups available to the user (1–9)
GROUP_COUNT = 9

# Prefix shared by all dipper-generated output lines
DIPPER_PREFIX = "%%dipper:"

# Mark line emitted after each selected source line; N=group, L=1-based line number
MARK_FORMAT = "%%dipper:mark:{group}:{line}%% {underline}"

# Visual underline character repeated after the mark prefix
UNDERLINE_CHAR = "^"

# Minimum underline length in characters
UNDERLINE_MIN = 6

# Separator between annotated body and group summary
SEPARATOR_LINE = "%%dipper:separator%%"

# Group header line in the summary section; RANGES is comma-separated run-length encoded line numbers
GROUP_FORMAT = "%%dipper:group:{group}:{ranges}%%"

# Colours for groups 1–9, indexed by group number (1-based, index 0 unused)
GROUP_COLOURS = [
    "",          # placeholder, groups are 1-based
    "bright_red",
    "bright_yellow",
    "bright_green",
    "bright_cyan",
    "bright_blue",
    "bright_magenta",
    "orange3",
    "deep_pink2",
    "grey82",
]
