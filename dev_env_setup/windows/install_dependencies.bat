@echo OFF

set LOCAL_PROGRAM_FILES=%ProgramFiles%
if exist "C:\Program Files (x86)" set LOCAL_PROGRAM_FILES=%ProgramFiles(x86)%

REM INSTALL WGET & UNZIP UTILITIES (NEEDED FOR LATER)
start http://downloads.sourceforge.net/gnuwin32/wget-1.11.4-1-setup.exe
@echo.
@echo.
@echo double-click on the downloaded file, follow the setup process and ***INSTALL in folder C:\GnuWin32 (Important)***
@echo.
pause
set GNUWIN32_HOME=C:\GnuWin32
if not exist %GNUWIN32_HOME%\bin\wget.exe echo "You have not installed the program in %GNUWIN32_HOME% folder. Setup will exit now." && pause && exit

REM INSTALL WGET & UNZIP UTILITIES (NEEDED FOR LATER)
setx GNUWIN32_HOME "%GNUWIN32_HOME%"
set PATH=%PATH%;%GNUWIN32_HOME%\bin

set DEPS=%CD%\downloaded_dependencies
mkdir "%DEPS%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/unzip/5.51-1/unzip-5.51-1.exe"
@echo.
@echo.
@echo INSTALLING Gnuwin32 Utils
echo Follow setup processes and ***DON'T CHANGE ANY OPTIONS***
@echo.
pause
"%DEPS%\unzip-5.51-1.exe"

REM INSTALL OTHERS GUNWIN32 TOOLS (NEEDED FOR LATER)
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/sed/4.2.1/sed-4.2.1-dep.zip"
unzip -o "%DEPS%\sed-4.2.1-dep.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/sed/4.2.1/sed-4.2.1-bin.zip"
unzip -o "%DEPS%\sed-4.2.1-bin.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/grep/2.5.4/grep-2.5.4-dep.zip"
unzip -o "%DEPS%\grep-2.5.4-dep.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/grep/2.5.4/grep-2.5.4-bin.zip"
unzip -o "%DEPS%\grep-2.5.4-bin.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/zip/3.0/zip-3.0-bin.zip"
unzip -o "%DEPS%\zip-3.0-bin.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/zip/3.0/zip-3.0-dep.zip"
unzip -o "%DEPS%\zip-3.0-dep.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/coreutils/5.3.0/coreutils-5.3.0-bin.zip"
unzip -o "%DEPS%\coreutils-5.3.0-bin.zip" -d "%GNUWIN32_HOME%"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/gnuwin32/coreutils/5.3.0/coreutils-5.3.0-dep.zip"
unzip -o "%DEPS%\coreutils-5.3.0-dep.zip" -d "%GNUWIN32_HOME%"

REM REM INSTALL GIT SCM TOOL
REM REM wget -nc -c -P %DEPS% https://github.com/msysgit/msysgit/releases/download/Git-1.9.5-preview20141217/Git-1.9.5-preview20141217.exe
REM REM @echo.
REM REM @echo.
REM REM @echo INSTALLING Git
REM REM @echo Follow the setup process, and:
REM REM @echo ***INSTALL in C:\Git (important)***
REM REM @echo ***Choose option "Use git from the Windows Command Prompt"***
REM REM @echo ***Choose option "Checkout as-is, commit as-is"***
REM REM @echo.
REM REM pause
REM REM %DEPS%\Git-1.9.5-preview20141217.exe
REM REM pause

REM INSTALL PYTHON 2.7
wget -nc --no-check-certificate -c -P "%DEPS%" "https://www.python.org/ftp/python/2.7.10/python-2.7.10.msi"
@echo.
@echo.
@echo INSTALLING Python 2.7.10
@echo Follow the setup process, and ***INSTALL in C:\Python27 (important)***
@echo.
pause
"%DEPS%\python-2.7.10.msi"
pause
setx PYTHON_HOME "C:\Python27"
set PYTHON_HOME=C:\Python27
set PATH=%PATH%;%PYTHON_HOME%;%PYTHON_HOME%\Scripts

REM INSTALL VISUAL STUDIO 2008 C++ EXPRESS
wget -nc -c -P "%DEPS%" "http://go.microsoft.com/?linkid=7729279"
@echo.
@echo.
@echo INSTALLING VISUAL STUDIO 2008 C++ EXPRESS
@echo Follow the setup process, and ***UNTICK "Microsoft Silverligght Runtime" and "Microsoft SQl Server 2008 Express Edition"***
@echo.
@echo Take a coffee...
@echo.
pause
call "%DEPS%\vcsetup.exe"
pause
set NOVS2008_PATH=%PATH%
set VS90COMNTOOLS=%LOCAL_PROGRAM_FILES%\Microsoft Visual Studio 9.0\Common7\Tools\

REM DOWNLOAD QT AND BUILD FROM SOURCE BECAUSE YOU NEED TO BUILD WITH THE SAME COMPILER AS PYTHON: VS2008
@echo.
@echo.
@echo INSTALLING QT 5.3.2
@echo.
@echo It takes ages! Take a nap...
@echo.
pause
wget -nc -c -P "%DEPS%" "http://www.7-zip.org/a/7za920.zip"
pushd "%DEPS%"
unzip -o -q 7za920.zip -d .
popd

set QMAKESPEC=win32-msvc2008
set QT5_FOLDER=qt5
set QT5_HOME=C:\%QT5_FOLDER%
mkdir "%QT5_HOME%"
wget -nc -c -P "%QT5_HOME%" "http://download.qt.io/archive/qt/5.3/5.3.2/single/qt-everywhere-opensource-src-5.3.2.zip"
pushd "%QT5_HOME%"
"%DEPS%\7za.exe" x qt-everywhere-opensource-src-5.3.2.zip > nul
mv qt-everywhere-opensource-src-5.3.2/* .
call "%LOCAL_PROGRAM_FILES%\microsoft visual studio 9.0\vc\vcvarsall.bat"
call configure -prefix "%CD%\qtbase" -opensource -nomake tests -nomake examples -confirm-license -release -skip WebKit -no-opengl 2>&1 | tee -a "%DEPS%\build_qt.log"
sed -i.orig s/\(Interlocked.*crement(\)/\1(LONG\*)/g qtmultimedia\src\plugins\directshow\camera\dscamerasession.cpp
nmake 2>&1 | tee -a "%DEPS%\build_qt.log"
setx QT5_HOME "%QT5_HOME%"
setx QMAKESPEC "%QMAKESPEC%"
set PATH=%PATH%;%QT5_HOME%\qtbase\bin
set NOVS2008_PATH=%NOVS2008_PATH%;%QT5_HOME%\qtbase\bin
xcopy "%QT5_HOME%\gnuwin32" "%GNUWIN32_HOME%" /S /Y
popd

REM INSTALLING MICROSOFT VISUAL C++ 2008 REDISTRIBUABLE PACKAGE
@echo.
@echo.
@echo INSTALLING Microsoft Visual C++ 2008 Redistribuable package
echo Follow setup processes and ***DON'T CHANGE ANY OPTIONS***
@echo.
pause
wget -nc -c -P "%DEPS%" "http://download.microsoft.com/download/1/1/1/1116b75a-9ec3-481a-a3c8-1777b5381140/vcredist_x86.exe"
"%DEPS%\vcredist_x86.exe"

REM INSTALLING SEVERAL PYTHON LIBRARIES
@echo.
@echo.
@echo INSTALLING Several Python Libraries
echo Follow setup processes and ***DON'T CHANGE ANY OPTIONS***
@echo.
pause
wget -nc -c -P "%DEPS%" "http://sourceforge.net/projects/numpy/files/NumPy/1.9.2/numpy-1.9.2-win32-superpack-python2.7.exe"
"%DEPS%\numpy-1.9.2-win32-superpack-python2.7.exe" /arch nosse
wget -nc -c -P "%DEPS%" "http://sourceforge.net/projects/pywin32/files/pywin32/Build%%20219/pywin32-219.win32-py2.7.exe"
"%DEPS%\pywin32-219.win32-py2.7.exe"
wget -nc -c -P "%DEPS%" "http://www.stickpeople.com/projects/python/win-psycopg/2.6.0/psycopg2-2.6.0.win32-py2.7-pg9.4.1-release.exe"
"%DEPS%\psycopg2-2.6.0.win32-py2.7-pg9.4.1-release.exe"
wget -nc -c -P "%DEPS%" "http://downloads.sourceforge.net/project/fpdb/fpdb/pypoker-eval-win32/pokereval-138.win32-py2.7.exe"
"%DEPS%\pokereval-138.win32-py2.7.exe"
wget -nc -c -P "%DEPS%" "http://sourceforge.net/projects/mysql-python/files/mysql-python/1.2.3/MySQL-python-1.2.3.win32-py2.7.msi"
"%DEPS%\MySQL-python-1.2.3.win32-py2.7.msi"

wget -nc -c -P "%DEPS%" "http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.6/sip-4.16.6.zip"
pushd "%DEPS%"
unzip -o -q sip-4.16.6.zip -d .
cd sip-4.16.6
call "%LOCAL_PROGRAM_FILES%\Microsoft Visual Studio 9.0\VC\vcvarsall.bat"
python configure.py 2>&1 | tee -a "%DEPS%\build_python_deps.log"
nmake 2>&1 | tee -a "%DEPS%\build_python_deps.log"
nmake install 2>&1 | tee -a "%DEPS%\build_python_deps.log"
popd

wget -nc -c -P "%DEPS%" "http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.3.2/PyQt-gpl-5.3.2.zip"
pushd "%DEPS%"
unzip -o -q PyQt-gpl-5.3.2.zip -d .
cd PyQt-gpl-5.3.2
sed -i.orig s/\(\['webkitwidgets'\)\(\]\)/\1,'printsupport'\2/g configure.py
call "%LOCAL_PROGRAM_FILES%\Microsoft Visual Studio 9.0\VC\vcvarsall.bat"
python configure.py --confirm-license 2>&1 | tee -a "%DEPS%\build_python_deps.log"
nmake 2>&1 | tee -a "%DEPS%\build_python_deps.log"
nmake install 2>&1 | tee -a "%DEPS%\build_python_deps.log"
popd

pip install -r requirements.txt 2>&1 | tee -a "%DEPS%\build_python_deps.log"

REM SET PATH ENVIRONMENT
setx PATH "%NOVS2008_PATH%"

@echo.
@echo This window will close
pause
@echo ON