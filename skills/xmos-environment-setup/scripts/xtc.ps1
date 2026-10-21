# Activate the XTC Tools environment in this PowerShell process, then run a command in it.
#
#   & <path>\xtc.ps1 xmake -C build      # activate, run, exit with the command's exit code
#   . <path>\xtc.ps1                     # dot-source: activate the current session only
#
# Version defaults to 15.3.1; override with $env:XTC_VERSION, or point $env:XTC_SETENV at a
# specific SetEnv.bat.

$version = if ($env:XTC_VERSION) { $env:XTC_VERSION } else { '15.3.1' }
$setenv = if ($env:XTC_SETENV) { $env:XTC_SETENV } else { "C:\Program Files\XMOS\XTC\$version\SetEnv.bat" }

# Errors use `throw` rather than `exit` so that a failed activation stops the rest of the command
# line, and does not close the caller's shell when the script is dot-sourced.
if (-not (Test-Path $setenv)) {
    throw "xtc.ps1: SetEnv.bat not found at '$setenv'. Set XTC_VERSION or XTC_SETENV."
}

# A batch file cannot export variables into PowerShell, so capture `set` from the child cmd.exe.
# Only import it if SetEnv.bat succeeded, so a failure cannot leave a half-updated environment.
$vars = cmd /c "`"$setenv`" >nul && set"
if ($LASTEXITCODE -ne 0) {
    throw "xtc.ps1: '$setenv' failed with exit code $LASTEXITCODE."
}
$vars | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        Set-Item -Path "env:$($matches[1])" -Value $matches[2]
    }
}

# Check xcc comes from the install just activated, not another toolchain already on PATH.
$root = Split-Path -Parent $setenv
$xcc = Get-Command xcc -ErrorAction SilentlyContinue
if (-not $xcc) {
    throw "xtc.ps1: XTC Tools not activated - xcc is not on PATH after running '$setenv'."
}
if (-not $xcc.Source.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) {
    throw "xtc.ps1: xcc resolves to '$($xcc.Source)', not the install at '$root'."
}

if ($args.Count -eq 0) {
    xcc --version
    return
}

$exe = $args[0]
if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) {
    throw "xtc.ps1: command '$exe' not found."
}
$rest = @()
if ($args.Count -gt 1) { $rest = @($args[1..($args.Count - 1)]) }

# $LASTEXITCODE is only set by native programs, so reset it and fall back on $? for anything else.
$global:LASTEXITCODE = 0
& $exe @rest
$ok = $?
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if (-not $ok) { exit 1 }
exit 0
