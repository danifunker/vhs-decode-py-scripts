# --- Configurable variables ---
$ROMDrive = "P:"                # Change to your ROM drive letter
$DestFolder = "C:\Temp"         # Change to your desired output folder
$CSVFile = "C:\Temp\TransferList.csv"    # Path to your CSV file

# --- Help parameter ---
param(
    [switch]$Help
)

if ($Help) {
    Write-Host "Usage: .\convert-to-mkv.ps1"
    Write-Host ""
    Write-Host "This script converts .m2ts files to .mkv using ffmpeg."
    Write-Host "It reads a CSV file with the following format:"
    Write-Host ""
    Write-Host "Source,Destination"
    Write-Host "00001.m2ts,movie1.mkv"
    Write-Host "00002.m2ts,movie2.mkv"
    Write-Host ""
    Write-Host "Source: Filename of the input .m2ts file (located in ROMDrive\BDMV\STREAM)"
    Write-Host "Destination: Filename for the output .mkv file (saved in DestFolder)"
    exit 0
}

# --- Check if Xreveal is running ---
$process = Get-Process -Name "Xreveal" -ErrorAction SilentlyContinue
if (-not $process) {
    Write-Host "Please launch Xreveal before running this script."
    exit 1
}

# --- Read CSV file ---
if (-not (Test-Path $CSVFile)) {
    Write-Host "CSV file not found: $CSVFile"
    exit 1
}
$files = Import-Csv $CSVFile

# --- Process each file ---
$totalFiles = $files.Count
$index = 1
foreach ($file in $files) {
    $inputPath = Join-Path "$ROMDrive\BDMV\STREAM" $file.Source
    $outputPath = Join-Path $DestFolder $file.Destination

    Write-Host "Processing file $index of ${totalFiles}: $file.Source -> $file.Destination"

    if (-not (Test-Path $inputPath)) {
        Write-Host "Input file not found: $inputPath"
        $index++
        continue
    }

    Write-Host "Converting $inputPath to $outputPath..."
    ffmpeg -fflags +genpts -analyzeduration 20000000 -probesize 50000000 -i "$inputPath" -map 0 -c copy "$outputPath"
    $index++
}
Write-Host "Conversion completed. All files processed."
