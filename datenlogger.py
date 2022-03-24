from cmath import log
from datetime import datetime
import os, json

# Definition der Keys
LOG_SPEED = "speed"
LOG_DIR = "dir"
LOG_ANGLE = "angle"
LOG_US = "us"
LOG_IR = "ir"


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
        self._log_file = {}
        self._log_data = []
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """starten des Loggers"""
        self._logger_running = True
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Daten an den Logger senden

        Args:
            data (_type_): ein Element (Tuple, Liste, Dict) wird an den Logger uebergeben
        """
        ts = str(datetime.now()).partition(".")[0]
        self._log_data.append({ts: data})

    def save(self):
        """speichert die uebergebenen Daten"""
        self._logger_running = False
        self._log_file["data"] = self._log_data
        self._log_file["ende"] = str(datetime.now()).partition(".")[0]
        filename = self._log_file.get("start").partition(".")[0]
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
        self._log_file.clear()
        self._log_data.clear()
        print("Log-File saved to:", logfile)


def main():
    dl = Datenlogger()
    dl.start()
    dl.append((12, 3))
    dl.save()

    dl = Datenlogger(log_file_path="Logger")
    dl.start()
    dl.append((12, 3))
    dl.save()


if __name__ == "__main__":
    main()
