pyinstaller run_gui.py  --noconfirm --log-level=WARN ^
    --onefile ^
    --name "folderhide-gui" ^
    --windowed ^
    --icon "NONE" ^
    --workpath ./build/gui ^
    --distpath ./dist/

pyinstaller run.py  --noconfirm --log-level=WARN ^
    --onefile ^
    --name "folderhide" ^
    --console ^
    --icon "NONE" ^
    --workpath ./build/cli ^
    --distpath ./dist/