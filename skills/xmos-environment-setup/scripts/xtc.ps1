# Activate the XTC Tools environment in this PowerShell process, then run a command in it.
#
#   & <path>\xtc.ps1 xmake -C build      # activate, run, exit with the command's exit code
#   . <path>\xtc.ps1                     # dot-source: activate the current session only
#
# Version defaults to 15.3.1; override with $env:XTC_VERSION, or point $env:XTC_SETENV at a
# specific SetEnv.bat.

$version = if ($env:XTC_VERSION) { $env:XTC_VERSION } else { '15.3.1' }
$setenv = if ($env:XTC_SETENV) { $env:XTC_SETENV } else { "C:\Program Files\XMOS\XTC\$version\SetEnv.bat" }

if (-not (Test-Path $setenv)) {
    Write-Error "SetEnv.bat not found at '$setenv'. Set XTC_VERSION or XTC_SETENV."
    exit 1
}

# A batch file cannot export variables into PowerShell, so capture `set` from the child cmd.exe.
cmd /c "`"$setenv`" >nul && set" | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
}

if ($args.Count -eq 0) {
    xcc --version
    return
}

$exe = $args[0]
$rest = @()
if ($args.Count -gt 1) { $rest = @($args[1..($args.Count - 1)]) }
& $exe @rest
exit $LASTEXITCODE
