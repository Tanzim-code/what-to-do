from flask import Flask, request, jsonify
from sympy import symbols, Eq, solve
import os
import logging
from waitress import serve

# Create a Flask application instance
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/solve', methods=['POST'])
def solve_equation():
    """Endpoint to solve mathematical equations."""
    data = request.json
    equation = data.get('equation')

    # Validate input
    if not equation:
        return jsonify({'error': 'No equation provided'}), 400

    try:
        # Define symbolic variables and equation
        x = symbols('x')
        if "=" in equation:
            lhs, rhs = equation.split("=")
        else:
            lhs, rhs = equation, "0"

        # Create the equation using SymPy's Eq
        eq = Eq(eval(lhs), eval(rhs))
        solution = solve(eq, x)
        return jsonify({'solution': str(solution)})

    except Exception as e:
        logger.error(f"Error solving equation: {e}")
        return jsonify({'error': 'Failed to solve the equation'}), 400

def main():
    """Main entry point for the application."""
    # Get the port from the environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")

    try:
        # Serve the Flask application using Waitress
        serve(app, host='0.0.0.0', port=port)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == '__main__':
    main()