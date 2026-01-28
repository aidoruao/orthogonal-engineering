Set WshShell = CreateObject("WScript.Shell")
Set objShell = CreateObject("Shell.Application")

' Get current directory
currentDir = Replace(WScript.ScriptFullName, WScript.ScriptName, "")

' Launch PowerShell with the script
command = "powershell.exe -NoExit -ExecutionPolicy Bypass -File " & currentDir & "launch_ai.ps1"""

WshShell.Run command, 1, False
