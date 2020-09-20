# Config Manager for Anki 2.1
#
# Copyright: 2020 Hikaru Y. <hkrysg@gmail.com>
#
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html


import logging
import sys
# from pathlib import Path

import aqt

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '[%(levelname)s](%(asctime)s) File "%(pathname)s",'
    ' line %(lineno)d, in %(funcName)s: "%(message)s"'
)
# console handler
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)
logger.addHandler(ch)

# file handler
# log_file = str(Path(__file__).resolve().parent / f"{__name__}_debug.log")
# fh = logging.FileHandler(filename=log_file)
# fh.setLevel(logging.WARNING)
# fh.setFormatter(formatter)
# logger.addHandler(fh)


class ConfigSignal(aqt.QObject):
    updated = aqt.pyqtSignal()
    configUpdatedActionTriggered = aqt.pyqtSignal()


class ConfigDict(dict):
    def __init__(self, dic: dict):
        super().__init__()
        self.update(dic)

    def update(self, dic, signal=False):
        for k, v in dic.items():
            if isinstance(v, dict):
                self[k] = ConfigDict(dic=v)
            else:
                self.set_item_without_signal(k, v)
        if signal:
            CONFSIGNAL.updated.emit()

    def set_item_without_signal(self, key, value):
        """
        When executing this method to update values in bulk from outside
        the class, be sure to execute CONF.on_conf_updated() at the end.
        """
        super().__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if not isinstance(value, dict):
            logger.debug("__setitem__")
            CONFSIGNAL.updated.emit()

    def __missing__(self, key):
        logger.debug("__missing__")
        return None

    def __delitem__(self, key):
        super().__delitem__(key)
        logger.debug("__delitem__")
        CONFSIGNAL.updated.emit()


class ConfigDictRoot(ConfigDict):
    def __init__(self, dic: dict):
        super().__init__(dic)

        aqt.mw.addonManager.setConfigUpdatedAction(
            __name__, self.on_ConfigUpdatedAction
        )
        CONFSIGNAL.updated.connect(self.on_conf_updated)

    def on_conf_updated(self):
        logger.debug("on_conf_updated")
        aqt.mw.addonManager.writeConfig(__name__, self)

    def on_ConfigUpdatedAction(self, new_conf: dict):
        self.clear()
        self.update(new_conf)
        CONFSIGNAL.configUpdatedActionTriggered.emit()


CONFSIGNAL = ConfigSignal()
CONF = ConfigDictRoot(dic=aqt.mw.addonManager.getConfig(__name__))
