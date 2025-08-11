#!/bin/bash

# Women EmpowerHer - Crime Prediction Model
# Complete system startup script

echo "=========================================="
echo "WOMEN EMPOWERHER - CRIME PREDICTION SYSTEM"
echo "=========================================="

# Function to check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python is not installed or not in PATH"
        exit 1
    fi
    echo "Using Python: $PYTHON_CMD"
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "Dependencies installed successfully"
    else
        echo "Error: Failed to install dependencies"
        exit 1
    fi
}

# Function to train the model
train_model() {
    echo "Training the crime prediction model..."
    $PYTHON_CMD train_model.py
    if [ $? -eq 0 ]; then
        echo "Model training completed successfully"
    else
        echo "Error: Model training failed"
        exit 1
    fi
}

# Function to start the API server
start_api_server() {
    echo "Starting Flask API server..."
    echo "API will be available at: http://localhost:5000"
    echo "Press Ctrl+C to stop the server"
    
    # Start the API server in the background
    $PYTHON_CMD api/app.py &
    API_PID=$!
    echo "API server started with PID: $API_PID"
    
    # Wait a moment for server to start
    sleep 3
    
    # Test the API
    echo "Testing API health endpoint..."
    curl -s http://localhost:5000/health
    echo ""
}

# Function to start feedback processing
start_feedback_processing() {
    echo "Starting feedback processing..."
    echo "This will monitor Firebase for new feedback and update the model"
    echo "Press Ctrl+C to stop feedback processing"
    
    # Start feedback processing in the background
    $PYTHON_CMD model/feedback_trainer.py &
    FEEDBACK_PID=$!
    echo "Feedback processing started with PID: $FEEDBACK_PID"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  train       - Train the model only"
    echo "  api         - Start API server only"
    echo "  feedback    - Start feedback processing only"
    echo "  all         - Train model, start API, and feedback processing (default)"
    echo "  install     - Install dependencies only"
    echo "  test        - Test the system"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 train     # Train the model"
    echo "  $0 api       # Start API server"
    echo "  $0 all       # Complete system startup"
}

# Function to test the system
test_system() {
    echo "Testing the Women EmpowerHer system..."
    
    # Check if model exists
    if [ -f "model/crime_predictor.pkl" ]; then
        echo "✓ Model file exists"
    else
        echo "✗ Model file not found. Run training first."
        return 1
    fi
    
    # Check if preprocessor exists
    if [ -f "model/preprocessor.pkl" ]; then
        echo "✓ Preprocessor file exists"
    else
        echo "✗ Preprocessor file not found. Run training first."
        return 1
    fi
    
    # Test API if running
    echo "Testing API endpoints..."
    if curl -s http://localhost:5000/health > /dev/null; then
        echo "✓ API is running"
        
        # Test prediction endpoint
        curl -s -X POST http://localhost:5000/predict \
            -H "Content-Type: application/json" \
            -d '{
                "latitude": 10.9467,
                "longitude": 76.8653,
                "time": "04:00",
                "severity": 4,
                "crime_type": "Sexual Harassment"
            }' | python3 -m json.tool
    else
        echo "✗ API is not running. Start it with: $0 api"
    fi
    
    echo "System test completed"
}

# Main script logic
main() {
    check_python
    
    case "${1:-all}" in
        "install")
            install_dependencies
            ;;
        "train")
            install_dependencies
            train_model
            ;;
        "api")
            start_api_server
            wait
            ;;
        "feedback")
            start_feedback_processing
            wait
            ;;
        "all")
            install_dependencies
            train_model
            start_api_server
            start_feedback_processing
            echo ""
            echo "=========================================="
            echo "SYSTEM STARTED SUCCESSFULLY"
            echo "=========================================="
            echo "API Server: http://localhost:5000"
            echo "Health Check: http://localhost:5000/health"
            echo "Example Request: http://localhost:5000/example_request"
            echo ""
            echo "Press Ctrl+C to stop all services"
            wait
            ;;
        "test")
            test_system
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Trap to clean up background processes
cleanup() {
    echo ""
    echo "Stopping all services..."
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null
        echo "API server stopped"
    fi
    if [ ! -z "$FEEDBACK_PID" ]; then
        kill $FEEDBACK_PID 2>/dev/null
        echo "Feedback processing stopped"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Run main function
main "$@" 