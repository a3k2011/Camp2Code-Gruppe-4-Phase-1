import pprint
from datetime import datetime
import os, json, time

# Definition der Keys
LOG_SPEED = "speed"
LOG_DIR = "dir"
LOG_ANGLE = "angle"
LOG_US = "us"
LOG_IR = "ir"


class Datenlogger:
    """Datenlogger Klasse
    speichert übergebene Tupels oder Listen mit Angabe des Zeitdeltas seid Start der Aufzeichnung in ein json-File
    """

    def __init__(self, log_file_path=None):
        """Zielverzeichnis fuer Logfiles kann beim Init mit uebergeben werden
            Wenn der Ordner nicht existiert wird er erzeugt

        Args:
            log_file_path (_type_, optional): Angabe des Zielordners. Defaults to None.
        """
        self._log_file = {}
        self._log_data = []
        self._start_timestamp = 0
        self._logger_running = False
        self._log_file_path = log_file_path

    def start(self):
        """starten des Loggers"""
        print("Logger gestartet")
        self._logger_running = True
        self._start_timestamp = time.time()
        self._log_file["start"] = str(datetime.now()).partition(".")[0]

    def append(self, data):
        """Daten an den Logger senden

        Args:
            data (list): ein Element (Liste) wird an den Logger uebergeben
        """
        if self._logger_running:
            ts = round((time.time() - self._start_timestamp), 2)
            self._log_data.append([ts] + data)

    def save(self):
        """speichert die uebergebenen Daten"""
        pprint.pprint(self._log_file)
        if self._logger_running:
            self._logger_running = False
            self._log_file["data"] = self._log_data
            self._log_file["ende"] = str(datetime.now()).partition(".")[0]
            filename = self._log_file.get("start").partition(".")[0]
            filename = (
                filename.replace("-", "").replace(":", "").replace(" ", "_")
                + "_drive.log"
            )
            if self._log_file_path != None:
                logfile = os.path.join(self._log_file_path, filename)
                if not os.path.isdir(self._log_file_path):
                    os.mkdir(self._log_file_path)
            else:
                logfile = filename
            with open(logfile, "w") as f:
                json.dump(self._log_data, f)
            self._log_file.clear()
            self._log_data.clear()
            print("Log-File saved to:", logfile)


def main():
    dl = Datenlogger()
    dl.start()
    dl.append([12, 3])
    time.sleep(0.3)
    dl.append([1, 13])
    time.sleep(0.5)
    dl.append([123, 43])
    time.sleep(1.2)
    dl.append([12, 5, 6])
    time.sleep(0.3)
    dl.save()

    dl = Datenlogger(log_file_path="Logger")
    dl.start()
    dl.append([12, 3])
    dl.save()


if __name__ == "__main__":
    main()
