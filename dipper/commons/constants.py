"""Constants for the dipper annotation tool"""

# Number of colour groups available to the user (1-9)
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

# Group header line in the summary section; RANGES is comma-separated run-length encoded ranges
GROUP_FORMAT = "%%dipper:group:{group}:{ranges}%%"

# Metadata line emitted as the first line of output when a source filepath is known
META_FILEPATH_FORMAT = "%%dipper:meta:filepath:{filepath}%%"

# Metadata line storing a SHA-256 hash of the source content at write time
META_HASH_FORMAT = "%%dipper:meta:hash:{hash}%%"

# Prefix of mark lines in annotations files; used to detect whether a sidecar has any selections
MARK_LINE_PREFIX = "%%dipper:mark:"

# Prefix of the filepath metadata line; used to detect annotation files by content
META_FILEPATH_PREFIX = "%%dipper:meta:filepath:"

# Filename suffix dipper uses for annotation sidecars
ANNOTATION_SUFFIX = ".annotations"

# Sentinel returned by ClipperApp when the user aborts the entire --files batch (ctrl+q)
ABORT_BATCH = "__abort_batch__"

# Sentinel returned by ClipperApp when the user navigates to the previous file in a batch
PREV_FILE = "__prev_file__"

# Number of parts in a colour-prefixed search query "!<colour> <pattern>"
COLOUR_PREFIX_PARTS = 2

# Semantic label for git-added lines (new lines with no prior content)
DIFF_ADDED = "added"

# Semantic label for git-modified lines (lines replacing existing content)
DIFF_MODIFIED = "modified"

# Fallback hex colours used when no suitable colour is found in the active theme
DIFF_ADDED_FALLBACK = "#00af5f"
DIFF_MODIFIED_FALLBACK = "#00afaf"

# Gutter glyphs marking git-changed lines: '+' for added, '~' for modified
DIFF_ADDED_MARK = "+"
DIFF_MODIFIED_MARK = "~"

# Maps a diff semantic label to its gutter glyph
DIFF_MARKS: dict[str, str] = {DIFF_ADDED: DIFF_ADDED_MARK, DIFF_MODIFIED: DIFF_MODIFIED_MARK}

# Named group presets built into dipper (user config can add more or override)
BUILTIN_PRESETS: dict[str, str] = {
    "priorities": "p1,p2,p3,p4,p5",
    "cr": "note,minor,bug,critical,question,praise",
}

# Default highlight colour for search matches
DEFAULT_SEARCH_COLOUR = "yellow"

# Colours for groups 1-9, indexed by group number (1-based, index 0 unused)
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
