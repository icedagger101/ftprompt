#!/usr/bin/env bash

set -euo pipefail

# Paths
VENV_PATH="./venv"
JSON_FILE="config.json"

activate_venv() {
    if [[ -d "$VENV_PATH" ]]; then
        source "$VENV_PATH/bin/activate"
        echo "Virtual environment activated: $VENV_PATH"
    else
        echo "Error: venv not found at $VENV_PATH"
        exit 1
    fi
}

check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "Error: jq not installed. Install it (sudo apt install jq or equivalent)."
        exit 1
    fi
}

show_menu_and_run() {
    check_jq

    if [[ ! -f "$JSON_FILE" ]]; then
        echo "Error: JSON file '$JSON_FILE' not found."
        exit 1
    fi

    # Extract project names into array
    mapfile -t names < <(jq -r '.[].name' "$JSON_FILE")

    if [[ ${#names[@]} -eq 0 ]]; then
        echo "Error: No projects in JSON file."
        exit 1
    fi

    echo "=== Available projects ==="
    PS3="Select project (or 'q' to quit): "
    select name in "${names[@]}"; do
        if [[ $REPLY == "q" || $REPLY == "Q" ]]; then
            echo "Exiting."
            exit 0
        fi

        if [[ -n "$name" ]]; then
            # Extract absolute_path and rules_file_path by name
            abs_path=$(jq -r --arg n "$name" '.[] | select(.name == $n) | .absolute_path' "$JSON_FILE")
            rules_path=$(jq -r --arg n "$name" '.[] | select(.name == $n) | .rules_file_path' "$JSON_FILE")

            if [[ "$abs_path" == "null" || "$rules_path" == "null" ]]; then
                echo "Error: One of the paths not found for '$name'."
                continue
            fi

            echo "Running for '$name' with path: $abs_path and rules_file: $rules_path"
            python main.py "$abs_path" --rules-file "$rules_path" -v
            break
        else
            echo "Invalid choice, try again."
        fi
    done
}

# Main execution
activate_venv
show_menu_and_run
