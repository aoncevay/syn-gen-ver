#!/bin/bash

# Script to setup spaCy model from a wheel file
# Usage: ./setup_model.sh [wheel_file_path] [install_type]
# - wheel_file_path: Path to the .whl file (default: models/en_core_web_trf-3.8.0-py3-none-any.whl)
# - install_type: 'local' or 'global' (default: local)

# Default values
WHEEL_FILE=${1:-"models/en_core_web_trf-3.8.0-py3-none-any.whl"}
INSTALL_TYPE=${2:-"local"}
CONFIG_FILE="src/config.json"

# Extract model name from the wheel file
MODEL_NAME=$(basename $WHEEL_FILE | cut -d'-' -f1,2,3)

echo "Setting up spaCy model from wheel file: $WHEEL_FILE"
echo "Installation type: $INSTALL_TYPE"

# Check if the wheel file exists
if [ ! -f "$WHEEL_FILE" ]; then
    echo "Error: Wheel file not found at $WHEEL_FILE"
    exit 1
fi

if [ "$INSTALL_TYPE" = "local" ]; then
    # Create extract directory
    EXTRACT_DIR="models/$MODEL_NAME"
    mkdir -p "$EXTRACT_DIR"
    
    echo "Extracting wheel file to $EXTRACT_DIR..."
    
    # Extract the wheel file (it's basically a zip file)
    unzip -q -o "$WHEEL_FILE" -d "$EXTRACT_DIR"
    
    if [ $? -eq 0 ]; then
        echo "Successfully extracted model to $EXTRACT_DIR"
        
        # Update config.json
        # This is a simple approach - for a more robust solution, use jq if available
        if [ -f "$CONFIG_FILE" ]; then
            # Create a backup
            cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
            
            # Update config using sed
            sed -i.tmp "s|\"name\": \"[^\"]*\"|\"name\": \"$MODEL_NAME\"|g" "$CONFIG_FILE"
            sed -i.tmp "s|\"local_path\": \"[^\"]*\"|\"local_path\": \"$EXTRACT_DIR\"|g" "$CONFIG_FILE"
            sed -i.tmp "s|\"use_local_model\": [^,}]*|\"use_local_model\": true|g" "$CONFIG_FILE"
            
            # Remove temporary file
            rm "${CONFIG_FILE}.tmp"
            
            echo "Updated config file: $CONFIG_FILE"
        else
            echo "Warning: Config file not found at $CONFIG_FILE"
            echo "Please update your config manually:"
            echo "{\"spacy_model\": {\"name\": \"$MODEL_NAME\", \"local_path\": \"$EXTRACT_DIR\", \"use_local_model\": true}}"
        fi
    else
        echo "Error extracting wheel file"
        exit 1
    fi
    
    echo "Setup complete! You can now run your code using the local model."
    echo "Run: python src/main.py --input data/sample.json --output data/perturbed.json"
    
elif [ "$INSTALL_TYPE" = "global" ]; then
    echo "Installing model globally using pip..."
    
    # Install using pip
    pip install "$WHEEL_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Successfully installed model globally"
        
        # Update config.json to use the installed model
        if [ -f "$CONFIG_FILE" ]; then
            # Create a backup
            cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"
            
            # Update config using sed
            sed -i.tmp "s|\"name\": \"[^\"]*\"|\"name\": \"$MODEL_NAME\"|g" "$CONFIG_FILE"
            sed -i.tmp "s|\"use_local_model\": [^,}]*|\"use_local_model\": false|g" "$CONFIG_FILE"
            
            # Remove temporary file
            rm "${CONFIG_FILE}.tmp"
            
            echo "Updated config file: $CONFIG_FILE"
        else
            echo "Warning: Config file not found at $CONFIG_FILE"
            echo "Please update your config manually:"
            echo "{\"spacy_model\": {\"name\": \"$MODEL_NAME\", \"use_local_model\": false}}"
        fi
    else
        echo "Error installing wheel file"
        exit 1
    fi
    
    echo "Setup complete! You can now run your code using the globally installed model."
    echo "Run: python src/main.py --input data/sample.json --output data/perturbed.json"
    
else
    echo "Error: Invalid installation type. Use 'local' or 'global'."
    exit 1
fi 