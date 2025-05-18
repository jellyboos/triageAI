#!/bin/bash

# Start Firebase emulators in the background
echo "Starting Firebase emulators..."
firebase emulators:start --project demo-myapp &
FIREBASE_PID=$!

# Wait for emulators to initialize
sleep 5

# Start the development server
echo "Starting development server..."
npm run dev

# Cleanup on exit
trap "kill $FIREBASE_PID" EXIT 