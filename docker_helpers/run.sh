# Start the cog server in the background - Ensure correct path to cog
cd /src && python3 -m cog.server.http --threads=10 &

# Initialize counter for the first loop
counter1=0

# Continuous loop for reliably checking cog server's readiness on port 5000
while true; do
  if nc -z localhost 5000; then
    echo "Cog server is running on port 5000."
    break  # Exit the loop when the server is up
  fi
  echo "Waiting for cog server to start on port 5000..."
  sleep 5
  ((counter1++))
  if [ $counter1 -ge 250 ]; then
    echo "Error: Cog server did not start on port 5000 after 250 attempts."
    exit 1  # Exit the script with an error status
  fi
done

# Initialize counter for the second loop
counter2=0

# New check: Waiting for the cog server to be fully ready
while true; do
  response=$(curl -s http://localhost:5000/health-check) # Replace localhost:5000 with actual hostname and port if necessary
  status=$(echo $response | jq -r '.status') # Parse status from JSON response
  if [ "$status" = "READY" ]; then
    echo "Cog server is fully ready."
    break # Exit the loop when the server is fully ready
  else
    echo "Waiting for cog server (models loading) on port 5000..."
    sleep 5
  fi
  ((counter2++))
  if [ $counter2 -ge 250 ]; then
    echo "Error: Cog server did not become fully ready after 250 attempts."
    exit 1  # Exit the script with an error status
  fi
done

# Run the application - only when cog server is fully ready
cd $HOME/app && . $HOME/.venv/bin/activate && python app.py