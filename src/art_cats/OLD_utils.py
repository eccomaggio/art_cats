import logging

# ----------------------------------------------------
# CONFIGURE THE ROOT LOGGER
# This function is run when the module is imported.
# ----------------------------------------------------

# Check if the root logger has any handlers to prevent redundant configuration.
# This ensures basicConfig() is only called once per application run,
# even if utils is imported multiple times by different modules.
if not logging.getLogger().handlers:
    try:
        logging.basicConfig(
            filename="output.log",  # Log to a file
            filemode="w",  # Overwrite the file on each run
            encoding="utf-8",
            # Standard format showing level, time, and the module name
            format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
            level=logging.DEBUG,  # Capture all messages (DEBUG and above)
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Optional: add stream handler for immediate console feedback with file logging still active.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only show INFO and above on console
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logging.getLogger().addHandler(console_handler)

    except Exception as e:
        # Fallback if file writing fails (e.g., permission error)
        logging.warning(f"Failed to configure file logging: {e}")

# This import statement is crucial. It must be called by the entry point
# BEFORE any other module tries to log something.
