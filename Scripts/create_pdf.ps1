param (
    [Parameter(Mandatory=$true)]
    [string]$InputHtml,

    [Parameter(Mandatory=$true)]
    [string]$OutputPdf
)

$resolvedHtml = Resolve-Path $InputHtml
$resolvedPdfDir = Split-Path (Resolve-Path -Path (Split-Path $OutputPdf -Parent) -ErrorAction SilentlyContinue)
if (-not $resolvedPdfDir) {
    $parentDir = Split-Path $OutputPdf -Parent
    if ($parentDir) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }
}

$fullPdfPath = [System.IO.Path]::GetFullPath($OutputPdf)

$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if (-not (Test-Path $edgePath)) {
    $edgePath = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
}

if (-not (Test-Path $edgePath)) {
    Write-Error "Microsoft Edge executable not found."
    exit 1
}

Write-Host "Rendering HTML to PDF..."
Write-Host "Input HTML: $resolvedHtml"
Write-Host "Output PDF: $fullPdfPath"

$argList = @(
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--print-to-pdf=`"$fullPdfPath`"",
    "`"$resolvedHtml`""
)

Start-Process -FilePath $edgePath -ArgumentList $argList -Wait -NoNewWindow

if (Test-Path $fullPdfPath) {
    $size = (Get-Item $fullPdfPath).Length
    Write-Host "PDF generation successful! File size: $size bytes."
    exit 0
} else {
    Write-Error "Failed to generate PDF."
    exit 1
}
