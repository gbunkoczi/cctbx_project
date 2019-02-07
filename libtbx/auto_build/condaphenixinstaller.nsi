
; Script generated by the HM NIS Edit Script Wizard.
; MUI Settings
!define MUI_ABORTWARNING
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}${PRODUCT_VERSION}"
!define PRODUCT_INST_KEY "Software\${PRODUCT_NAME}\${PRODUCT_VERSION}"
!define PRODUCT_ROOT_KEY SHCTX ; replaced with HKLM or HKCU on runtime according to SetShellVarContext
!define PRODUCT_STARTMENU_REGVAL "NSIS:StartMenuDir"


OutFile "${PRODUCT_NAME}-${PRODUCT_VERSION}-x${BITNESS}-Setup.exe"
InstallDir "$PROGRAMFILES${BITNESS}\${PRODUCT_NAME}"

!define MUI_CUSTOMFUNCTION_GUIINIT MyOnGUIinit

!include 'LogicLib.nsh'

; -----------------------
;       UserIsAdmin macro
; -----------------------
;
;   Example:
;       ${If} ${UserIsAdmin}
;           DetailPrint "Current user security context has local administrative rights."
;       ${Else}
;           DetailPrint "Current user security context dose NOT have local administrative rights."
;       ${EndIf}
;
!macro _UserIsAdmin _a _b _t _f
   System::Store 'p0 p1 p2 p3'
   System::Call '*(&i1 0,&i4 0,&i1 5)i.r0'
   System::Call 'advapi32::AllocateAndInitializeSid(i r0,i 2,i 32,i 544,i 0,i 0,i 0,i 0,i 0,i 0,*i .r1)i.r2'
   System::Free $0
   System::Call 'advapi32::CheckTokenMembership(i n,i r1,*i .r2)i.r3'
   IntOp $3 $3 && $2 ; Function success AND was a member
   System::Call 'advapi32::FreeSid(i r1)'

   StrCmp $3 0 0 +3
   ## User is an Admin
     System::Store 'r3 r2 r1 r0'
     Goto `${_f}`

    ## User is not an Admin
     System::Store 'r3 r2 r1 r0'
     Goto `${_t}`
!macroend
!define UserIsAdmin `"" UserIsAdmin ""`



var ALL_OR_USER_TEXT

Function .onInit
  !include x64.nsh
  ${IfNot} ${RunningX64}
    ${If} ${BITNESS} > 32
  MessageBox MB_ICONEXCLAMATION|MB_OK "This build of ${PRODUCT_NAME} requires a 64 bit version of Windows. \
Please install the 32 bit build of ${PRODUCT_NAME} instead."
  Abort
    ${EndIf}
  ${EndIf}

  ${If} ${UserIsAdmin}
   StrCpy $ALL_OR_USER_TEXT "Setup will install ${PRODUCT_NAME} in the folder below \
for all users. To install in a different folder, click Browse and \
select another folder.$\r$\n$\r$\n\
To install ${PRODUCT_NAME} for just one user exit Setup now. Then run Setup as that user without \
administrative privileges."
   SetShellVarContext all
  ${Else}
   ReadEnvStr $0 HOMEDRIVE
   ReadEnvStr $1 HOMEPATH
   StrCpy $INSTDIR "$0$1\${PRODUCT_NAME}"
   StrCpy $ALL_OR_USER_TEXT "Setup will install ${PRODUCT_NAME} in the folder below. \
To install in a different folder, click Browse and select another folder.$\r$\n$\r$\n\
To install  ${PRODUCT_NAME} for all users exit Setup. Then run Setup with administrative privileges."
   SetShellVarContext current
  ${EndIf}
FunctionEnd


RequestExecutionLevel user ; everyone should be allowed to install phenix to their home folder at least
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
ShowInstDetails show
ShowUnInstDetails show
AutoCloseWindow false


Function LaunchProg
  Exec '"$SYSDIR\notepad.exe" \\?\$INSTDIR\${SOURCEDIR}\README'
FunctionEnd


; MUI 1.67 compatible ------
!include "MUI.nsh"
; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "${COPYDIR}\${SOURCEDIR}\LICENSE"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
DirText $ALL_OR_USER_TEXT
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "${PRODUCT_NAME}"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${PRODUCT_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${PRODUCT_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${PRODUCT_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_FINISHPAGE_RUN
!define MUI_FINISHPAGE_RUN_TEXT "Read the README file"
!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchProg"

!insertmacro MUI_PAGE_FINISH
; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES
; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Section "Basic components" SEC01
  SetOutPath "\\?\$INSTDIR"
  SetOverwrite off
  File /r /x *.cpp /x *.cc /x *.h /x *.hh /x *.hpp /x *.c /x *.f /x .svn ${COPYDIR}\*

  #ExecWait '"\\?\$INSTDIR\${SOURCEDIR}\base\bin\python\python" -c $\"import compileall; compileall.compile_dir($\'\\\?\$INSTDIR\${SOURCEDIR}\modules$\', 100)$\"'
  ExecWait '"\\?\$INSTDIR\${SOURCEDIR}\base\bin\python\python" -c $\"import compileall; compileall.compile_dir($\'\\?\$INSTDIR\${SOURCEDIR}\modules$\', 100)$\"'
  SetAutoClose false
  ; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Source code" SEC02
  SetOutPath "\\?\$INSTDIR"
  SetOverwrite on
  File /nonfatal /r ${COPYDIR}\*.hh
  File /nonfatal /r ${COPYDIR}\*.hpp
  File /nonfatal /r ${COPYDIR}\*.c
  File /nonfatal /r ${COPYDIR}\*.f
  File /nonfatal /r ${COPYDIR}\*.cpp
  File /nonfatal /r ${COPYDIR}\*.cc
  File /nonfatal /r ${COPYDIR}\*.h
  SetAutoClose false
; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Required executables, scripts and tutorials"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "Optional C/C++ source code for developers or expert users"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} "Microsoft Visual C++ 2008 Redistributable Components. Install these only if not already present."
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Section -AdditionalIcons
  SetOutPath "$INSTDIR"
  !define UNINSTEXE "$INSTDIR\UnInstall${PRODUCT_NAME}${PRODUCT_VERSION}.exe"
  !define MYICON "$INSTDIR\${SOURCEDIR}\modules\gui_resources\icons\custom\WinPhenix.ico"
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_INST_KEY}" "InstallPath" "$INSTDIR\${SOURCEDIR}"

  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}\${PRODUCT_NAME}${PRODUCT_VERSION}.lnk" "$INSTDIR\${SOURCEDIR}\build\bin\phenix.bat" "" "${MYICON}" 0 SW_SHOWMINIMIZED
  CreateShortCut "$DESKTOP\${PRODUCT_NAME}${PRODUCT_VERSION}.lnk" "$INSTDIR\${SOURCEDIR}\build\bin\phenix.bat" "" "${MYICON}" 0 SW_SHOWMINIMIZED
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}\Documentation ${PRODUCT_VERSION}.lnk" "$INSTDIR\${SOURCEDIR}\build\bin\phenix.doc.bat" "" "$WINDIR\hh.exe" 0
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}\Phenix.Python ${PRODUCT_VERSION}.lnk" "$INSTDIR\${SOURCEDIR}\build\bin\phenix.python.bat" "" "$INSTDIR\${SOURCEDIR}\base\bin\python\python.exe"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}\Phenix Command Prompt ${PRODUCT_VERSION}.lnk" "$SYSDIR\cmd.exe" "/k $\"$INSTDIR\${SOURCEDIR}\phenix_env.bat$\"" "$SYSDIR\cmd.exe"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}\Uninstall${PRODUCT_NAME}${PRODUCT_VERSION}.lnk" "${UNINSTEXE}" "" "${UNINSTEXE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\PHENIX Website.lnk" "${PRODUCT_WEB_SITE}" "" "$PROGRAMFILES\Internet Explorer\iexplore.exe" 0
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "${UNINSTEXE}"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "${UNINSTEXE}"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function MyOnGUIinit
;!insertmacro UnSelectSection ${SEC01}
!insertmacro SelectSection ${SEC01}
!insertmacro UnSelectSection ${SEC02}
!insertmacro SelectSection ${SEC03}
FunctionEnd



Function .onSelChange
${If}  ${SectionIsSelected} ${SEC02}
!insertmacro SelectSection ${SEC01}
!insertmacro SetSectionFlag ${SEC01} ${SF_RO}
${Else}
!insertmacro ClearSectionFlag ${SEC01} ${SF_RO}
${EndIf}
${If}  ${SectionIsSelected} ${SEC03}
!insertmacro SelectSection ${SEC03}
${Else}
!insertmacro UnSelectSection ${SEC03}
${EndIf}
FunctionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP

  RMDir /r "$SMPROGRAMS\$ICONS_GROUP\${PRODUCT_VERSION}"
  Delete "$DESKTOP\${PRODUCT_NAME}${PRODUCT_VERSION}.lnk"
  RMDir /r "\\?\$INSTDIR\${SOURCEDIR}"
  Delete "${UNINSTEXE}"

  DeleteRegKey ${PRODUCT_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey ${PRODUCT_ROOT_KEY} "${PRODUCT_INST_KEY}"

  SetAutoClose false
SectionEnd
