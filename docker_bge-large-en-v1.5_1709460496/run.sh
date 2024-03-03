# Start the cog server in the background - Ensure correct path to cog
cd /src && python3 -m cog.server.http --threads=10 &

# Continuous loop for reliably checking cog server's readiness
while true; do
  if nc -z localhost 5000; then
    echo "Cog server is ready."
    break  # Exit the loop when the server is up
  fi
  echo "Waiting for cog server to start on port 5000..."
  sleep 5
done

# Run the application - only when cog server is ready
cd $HOME/app && . $HOME/.venv/bin/activate && python app.py