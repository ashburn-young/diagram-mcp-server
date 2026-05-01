$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir '..')

$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
	throw "Missing venv at $python. Create it with: python -m venv .venv"
}

# Ensure Graphviz is usable in this session
$graphvizBin = 'C:\Program Files\Graphviz\bin'
if (Test-Path (Join-Path $graphvizBin 'dot.exe')) {
	$env:PATH = "$graphvizBin;$env:PATH"
}

# Reduce noise unless debugging
if (-not $env:FASTMCP_LOG_LEVEL) {
	$env:FASTMCP_LOG_LEVEL = 'ERROR'
}

& $python -m infrastructure_diagram_mcp_server.server
