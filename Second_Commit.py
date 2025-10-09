import datetime
import traceback

# Function to log all errors to a file with detailed info
def log_errors_to_file(filename, error_message):
    with open(filename, "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"[{timestamp}] {error_message}\n")

# Simulate user input (for testing purposes)
def get_input(prompt):
    return input(f"Enter {prompt}: ")

# Simulated message display
def show_message(message):
    print(message)

# Main function with enhanced error handling and enumeration logic
def main():
    try:
        username = get_input("username")
        password = get_input("password")

        # Input validation checks (simulate possible enumeration cases)
        if len(username) == 0 or len(password) == 0:
            raise ValueError("Input fields cannot be empty")

        # Simulated enumeration logic
        if username == "admin":
            # Case 1: Correct username, wrong password
            if password != "secret123":
                raise PermissionError("Incorrect password for admin user")
            else:
                show_message("Login successful!")
        else:
            # Case 2: Non-existent user
            raise LookupError("User not found in the database")

    except ValueError as e:
        # Input errors
        error_details = f"Validation error: {e}\n{traceback.format_exc()}"
        log_errors_to_file("errors.log", error_details)
        show_message("Invalid input. Please ensure all fields are filled.")

    except PermissionError as e:
        # Password-related errors (useful for enumeration testing)
        error_details = f"Permission error: {e}\n{traceback.format_exc()}"
        log_errors_to_file("errors.log", error_details)
        show_message("Invalid password.")

    except LookupError as e:
        # Username enumeration case
        error_details = f"Lookup error: {e}\n{traceback.format_exc()}"
        log_errors_to_file("errors.log", error_details)
        show_message("Invalid username.")

    except Exception as e:
        # Catch-all for unexpected errors
        error_details = f"Unexpected error occurred: {e}\n{traceback.format_exc()}"
        log_errors_to_file("errors.log", error_details)
        show_message("An unexpected error occurred. Please try again later.")

# Run the program
if __name__ == "__main__":
    main()
