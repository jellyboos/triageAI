# Start Firebase emulators in a new window
Start-Process powershell -ArgumentList "firebase emulators:start --project demo-myapp"

# Wait for emulators to initialize
Start-Sleep -Seconds 5

# Start the development server
Write-Host "Starting development server..."
npm run dev 