# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import KFS.log
import logging
import traceback
from main import main


KFS.log.setup_logging("", logging.INFO)
#KFS.log.setup_logging("", logging.DEBUG, filepath_format="./log/%Y-%m-%dT%H_%M.log", rotate_filepath_when="M")

try:
    main()
except:
    logging.critical(traceback.format_exc())
    print("\nPress enter to close program.", flush=True)
    input() # pause