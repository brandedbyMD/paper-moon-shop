@echo off
rem PaperMoon morning shopkeeper - runs headless Claude (Saku) once
cd /d C:\Users\Miteki\projects\shop
call C:\Users\Miteki\AppData\Roaming\npm\claude.cmd -p "Read tools/tenban-prompt.md and carry out the shop-keeping duties exactly as written, then exit." --permission-mode acceptEdits >> tools\tenban-log.txt 2>&1
