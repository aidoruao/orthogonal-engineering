' START_V57.vbs - Double-click to run Maximal Oracle v57
' This Visual Basic Script will work on any Windows system
' No batch file issues, no PowerShell execution policies

Option Explicit

' Main function
Sub Main()
    Dim shell, fso, currentDir, pythonExe, apiKey, command

    ' Create objects
    Set shell = CreateObject("WScript.Shell")
    Set fso = CreateObject("Scripting.FileSystemObject")

    ' Get current directory
    currentDir = fso.GetAbsolutePathName(".")

    ' Check if we're in the right directory
    If Not fso.FileExists(currentDir & "\maximal_oracle_v57.py") Then
        MsgBox "ERROR: maximal_oracle_v57.py not found in:" & vbCrLf & vbCrLf & currentDir & _
               vbCrLf & vbCrLf & "Please run this script from the minimal_ai_ide directory.", _
               vbCritical, "Maximal Oracle v57 - File Not Found"
        Exit Sub
    End If

    ' Find Python executable
    pythonExe = FindPython()
    If pythonExe = "" Then
        MsgBox "ERROR: Python not found!" & vbCrLf & vbCrLf & _
               "Please install Python 3.8 or higher from python.org", _
               vbCritical, "Maximal Oracle v57 - Python Not Found"
        Exit Sub
    End If

    ' Check for API key
    apiKey = shell.ExpandEnvironmentStrings("%DEEPSEEK_API_KEY%")
    If apiKey = "" Or apiKey = "%DEEPSEEK_API_KEY%" Then
        Dim response
        response = MsgBox("DEEPSEEK_API_KEY environment variable is not set." & vbCrLf & vbCrLf & _
                          "Do you want to continue anyway?" & vbCrLf & _
                          "(The system might fail without an API key)", _
                          vbQuestion + vbYesNo, "Maximal Oracle v57 - API Key Warning")
        If response = vbNo Then
            MsgBox "Please set your API key:" & vbCrLf & vbCrLf & _
                   "Command Prompt:" & vbCrLf & "  set DEEPSEEK_API_KEY=your_key_here" & vbCrLf & vbCrLf & _
                   "PowerShell:" & vbCrLf & "  $env:DEEPSEEK_API_KEY='your_key_here'" & vbCrLf & vbCrLf & _
                   "Then run this script again.", _
                   vbInformation, "Maximal Oracle v57 - Setup Instructions"
            Exit Sub
        End If
    Else
        ' Show API key is set (first few chars only)
        MsgBox "API Key found: " & Left(apiKey, 10) & "..." & vbCrLf & vbCrLf & _
               "Starting Maximal Oracle v57...", _
               vbInformation, "Maximal Oracle v57 - Ready"
    End If

    ' Create command
    command = Chr(34) & pythonExe & Chr(34) & " maximal_oracle_v57.py"

    ' Display information
    Dim info
    info = "MAXIMAL ORACLE v57 - STARTING" & vbCrLf & vbCrLf & _
           "Python: " & pythonExe & vbCrLf & _
           "Directory: " & currentDir & vbCrLf & vbCrLf & _
           "Features:" & vbCrLf & _
           "• Paraconsistent Logic (True/False/Both/Neither)" & vbCrLf & _
           "• Category Theory (Morphisms, Natural Transformations)" & vbCrLf & _
           "• Modal Logic (Temporal, Epistemic, Deontic)" & vbCrLf & _
           "• Homotopy Type Theory" & vbCrLf & _
           "• Falsificationist Validation Engine" & vbCrLf & vbCrLf & _
           "Prometheus metrics: http://localhost:8057" & vbCrLf & _
           "Press Ctrl+C in the console to stop"

    MsgBox info, vbInformation, "Maximal Oracle v57 - Information"

    ' Change to current directory and run Python
    shell.CurrentDirectory = currentDir

    ' Run the command in a visible console window
    shell.Run "cmd.exe /K " & command, 1, True

    ' Show completion message
    MsgBox "Maximal Oracle v57 has stopped." & vbCrLf & vbCrLf & _
           "Check maximal_oracle_v57.log for details.", _
           vbInformation, "Maximal Oracle v57 - Stopped"
End Sub

' Function to find Python executable
Function FindPython()
    Dim shell, fso, pythonPaths, path, pythonExe

    Set shell = CreateObject("WScript.Shell")
    Set fso = CreateObject("Scripting.FileSystemObject")

    ' Common Python executable paths
    pythonPaths = Array( _
        "python.exe", _
        "python3.exe", _
        "py.exe", _
        shell.ExpandEnvironmentStrings("%ProgramFiles%\Python*\python.exe"), _
        shell.ExpandEnvironmentStrings("%LocalAppData%\Programs\Python\Python*\python.exe"), _
        shell.ExpandEnvironmentStrings("%UserProfile%\AppData\Local\Programs\Python\Python*\python.exe") _
    )

    ' Check each path
    For Each path In pythonPaths
        If fso.FileExists(path) Then
            FindPython = path
            Exit Function
        End If

        ' Try to run python --version
        On Error Resume Next
        Dim output
        output = shell.Exec(path & " --version").StdOut.ReadAll()
        If Err.Number = 0 And InStr(output, "Python") > 0 Then
            FindPython = path
            Exit Function
        End If
        On Error GoTo 0
    Next

    ' Try using "where python" command
    On Error Resume Next
    Dim whereOutput
    Set whereOutput = shell.Exec("where python")
    If Err.Number = 0 Then
        Dim line
        Do While Not whereOutput.StdOut.AtEndOfStream
            line = Trim(whereOutput.StdOut.ReadLine())
            If fso.FileExists(line) Then
                FindPython = line
                Exit Function
            End If
        Loop
    End If
    On Error GoTo 0

    ' Python not found
    FindPython = ""
End Function

' Function to check if dependencies are installed
Sub CheckDependencies()
    Dim shell, fso, pythonExe, currentDir

    Set shell = CreateObject("WScript.Shell")
    Set fso = CreateObject("Scripting.FileSystemObject")
    currentDir = fso.GetAbsolutePathName(".")

    pythonExe = FindPython()
    If pythonExe = "" Then Exit Sub

    ' Check for requirements.txt
    If fso.FileExists(currentDir & "\requirements_v57.txt") Then
        Dim response
        response = MsgBox("Do you want to check and install dependencies?" & vbCrLf & vbCrLf & _
                          "This will run: pip install -r requirements_v57.txt", _
                          vbQuestion + vbYesNo, "Maximal Oracle v57 - Dependencies")

        If response = vbYes Then
            shell.CurrentDirectory = currentDir
            shell.Run "cmd.exe /K " & Chr(34) & pythonExe & Chr(34) & " -m pip install -r requirements_v57.txt", 1, True
        End If
    End If
End Sub

' Function to create a shortcut on desktop
Sub CreateShortcut()
    Dim shell, fso, desktopPath, shortcut, currentDir

    Set shell = CreateObject("WScript.Shell")
    Set fso = CreateObject("Scripting.FileSystemObject")

    desktopPath = shell.SpecialFolders("Desktop")
    currentDir = fso.GetAbsolutePathName(".")

    Set shortcut = shell.CreateShortcut(desktopPath & "\Maximal Oracle v57.lnk")
    shortcut.TargetPath = "wscript.exe"
    shortcut.Arguments = Chr(34) & currentDir & "\START_V57.vbs" & Chr(34)
    shortcut.WorkingDirectory = currentDir
    shortcut.Description = "Launch Maximal Oracle v57 AI Controller"
    shortcut.IconLocation = currentDir & "\START_V57.vbs, 0"
    shortcut.Save

    MsgBox "Shortcut created on desktop: 'Maximal Oracle v57.lnk'", _
           vbInformation, "Maximal Oracle v57 - Shortcut Created"
End Sub

' Function to show help
Sub ShowHelp()
    Dim helpText
    helpText = "MAXIMAL ORACLE v57 - HELP" & vbCrLf & vbCrLf & _
               "System Requirements:" & vbCrLf & _
               "• Python 3.8 or higher" & vbCrLf & _
               "• DeepSeek API key (set as DEEPSEEK_API_KEY)" & vbCrLf & vbCrLf & _
               "Setup Steps:" & vbCrLf & _
               "1. Install Python from python.org" & vbCrLf & _
               "2. Set API key:" & vbCrLf & _
               "   Command Prompt: set DEEPSEEK_API_KEY=your_key" & vbCrLf & _
               "   PowerShell: $env:DEEPSEEK_API_KEY='your_key'" & vbCrLf & _
               "3. Double-click START_V57.vbs" & vbCrLf & vbCrLf & _
               "Features:" & vbCrLf & _
               "• Paraconsistent Logic (embraces contradictions)" & vbCrLf & _
               "• Category Theory (mathematical rigor)" & vbCrLf & _
               "• Modal Logic (temporal/epistemic/deontic)" & vbCrLf & _
               "• Homotopy Type Theory (advanced type equality)" & vbCrLf & _
               "• Falsificationist Validation (Popperian)" & vbCrLf & vbCrLf & _
               "Access:" & vbCrLf & _
               "• Prometheus metrics: http://localhost:8057" & vbCrLf & _
               "• Workspace: workspace_v57 folder" & vbCrLf & _
               "• Logs: maximal_oracle_v57.log" & vbCrLf & vbCrLf & _
               "Troubleshooting:" & vbCrLf & _
               "• Run test_v57.py to check installation" & vbCrLf & _
               "• Check Python: python --version" & vbCrLf & _
               "• Install deps: pip install -r requirements_v57.txt"

    MsgBox helpText, vbInformation, "Maximal Oracle v57 - Help"
End Sub

' Main menu
Dim choice
choice = InputBox( _
    "MAXIMAL ORACLE v57 - MAIN MENU" & vbCrLf & vbCrLf & _
    "Choose an option:" & vbCrLf & _
    "1. Start Maximal Oracle v57" & vbCrLf & _
    "2. Check/Install Dependencies" & vbCrLf & _
    "3. Create Desktop Shortcut" & vbCrLf & _
    "4. Show Help" & vbCrLf & _
    "5. Exit" & vbCrLf & vbCrLf & _
    "Enter choice (1-5):", _
    "Maximal Oracle v57", "1")

Select Case choice
    Case "1"
        Main
    Case "2"
        CheckDependencies
    Case "3"
        CreateShortcut
    Case "4"
        ShowHelp
    Case "5", ""
        ' Exit - do nothing
    Case Else
        MsgBox "Invalid choice. Please run again and select 1-5.", vbExclamation, "Maximal Oracle v57"
End Select
