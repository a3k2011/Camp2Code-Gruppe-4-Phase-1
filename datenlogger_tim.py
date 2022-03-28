import os, json
import pandas as pd
import time
from datetime import datetime

class Datenlogger:
    """Datenlogger Klasse
    speichert übergebene Tupels oder Listen mit Zeitstempeln in ein json-File
    """

    def __init__(self, log_file_path=None):
        """Zielverzeichnis fuer Logfiles kann beim Init mit uebergeben werden
            Wenn der Ordner nicht existiert wird er erzeugt
        Args:
            log_file_path (_type_, optional): Angabe des Zielordners. Defaults to None.
        """
        self._log_name = None
        self._log_file = None
        self._dataframe = pd.DataFrame()
        self._cntTime = None
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """starten des Loggers"""
        self._logger_running = True
        self._log_name = str(datetime.now()).partition(".")[0]
        self._cntTime = time.perf_counter()

    def append(self, data):
        """Daten an den Logger senden
        Args:
            data (_type_): ein Element (Tuple, Liste, Dict) wird an den Logger uebergeben
        """
        dataDF = pd.DataFrame(data, index=[round((time.perf_counter()-self._cntTime),2)])
        self._dataframe = pd.concat([self._dataframe, dataDF], verify_integrity=True)

    def save(self):
        """speichert die uebergebenen Daten"""
        self._logger_running = False
        self._log_file = self._dataframe.to_json(orient="index")

        filename = self._log_name
        filename = (
            filename.replace("-", "_").replace(" ", "_").replace(":", "_")
            + "_drive.log"
        )
        if self._log_file_path != None:
            logfile = os.path.join(self._log_file_path, filename)
            if not os.path.isdir(self._log_file_path):
                os.mkdir(self._log_file_path)
        else:
            logfile = filename
        with open(logfile, "w") as f:
            json.dump(self._log_file, f)
        print("Log-File saved to:", logfile)