from flask import Flask, request, jsonify
from sympy import symbols, Eq, solve
import os
import logging
from waitress import serve


# Create a Flask application instance
app = Flask(__name__)

# Configure logging with detailed formatting
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def safe_eval(expression):
    """Safely evaluate expressions with controlled variables."""
    allowed_names = {
        'x': symbols('x'),
        'Eq': Eq,
        'solve': solve
    }
    try:
        # Use a safe eval environment
        return eval(expression, {"__builtins__": None}, allowed_names)
    except Exception as e:
        logger.error(f"Error evaluating expression: {e}")
        raise ValueError("Invalid expression provided")


@app.route('/solve', methods=['POST'])
def solve_equation():
    """Endpoint to solve mathematical equations."""
    try:
        # Extract and validate the JSON data
        data = request.get_json()
        if not data or 'equation' not in data:
            logger.warning("No equation provided or invalid JSON format")
            return jsonify({'error': 'No equation provided'}), 400

        equation = data['equation'].strip()

        # Check for empty equation
        if not equation:
            logger.warning("Empty equation provided")
            return jsonify({'error': 'Empty equation provided'}), 400

        # Define symbolic variables and equation
        x = symbols('x')
        if "=" in equation:
            lhs, rhs = equation.split("=")
        else:
            lhs, rhs = equation, "0"

        # Create the equation using SymPy's Eq
        eq = Eq(safe_eval(lhs), safe_eval(rhs))
        solution = solve(eq, x)
        logger.info("Equation solved successfully")
        return jsonify({'solution': str(solution)})

    except SyntaxError as e:
        logger.error(f"Syntax error in equation: {e}")
        return jsonify({'error': 'Syntax error in equation'}), 400
    except ValueError as e:
        logger.error(f"Value error: {e}")
        return jsonify({'error': 'Invalid value in equation'}), 400
    except TypeError as e:
        logger.error(f"Type error: {e}")
        return jsonify({'error': 'Type error in equation'}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Failed to solve the equation'}), 500


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
