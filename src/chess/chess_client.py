import chess_server
#import keywords
import vectordb

def show_menu():
    print("Chess")
    print("1. Play")
    print("2. Ask chess AI")
    print("3. Maintain data")# Dont know exactly what that means.
    print("9. Exit")
    choice = input("Enter your choice: ")
    return choice

def app():
    choice = show_menu()

    if choice == "1":
        chess_server.play_game()
    elif choice == "2":
        vectordb.main()
    elif choice == "3":
        pass
    elif choice == "9":
        exit()




if __name__ == "__main__":
    app()