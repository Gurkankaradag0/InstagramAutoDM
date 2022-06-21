import pyqt5ac

pyqt5ac.main(uicOptions='--from-imports', force=False, initPackage=True, ioPaths=[
        ['*.qrc', '%%FILENAME%%_rc.py']
    ])