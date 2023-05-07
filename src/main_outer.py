#Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import KFS.log      #setup logging
import logging      #standard logging
import traceback    #exception message full when program crashes as .exe
from main import main


KFS.log.setup_logging("", logging.INFO)
#KFS.log.setup_logging("", logging.DEBUG)
try:
    main()
except:
    logging.critical(traceback.format_exc())
    
    print("\n\nPress enter to close program.", flush=True)
    input() #pause
else:
    print("\n", end="", flush=True)