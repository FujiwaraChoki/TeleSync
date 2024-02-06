# Get all sys args after file name
args=("$@")

# Run src/main.py with sys args
python src/main.py ${args[@]}
