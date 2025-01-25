import chess_server
# import keywords
import vectordb

def show_menu():
    print("Chess")
    print("1. Play")
    print("2. Ask chess AI")
    print("3. Maintain data")
    print("9. Exit")
    choice = input("Enter your choice: ")
    return choice

def app():
    choice = show_menu()


if __name__ == "__main__":
    app()