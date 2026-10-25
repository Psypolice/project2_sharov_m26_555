import prompt
def welcome():

print("\nПервая попытка запустить проект!")
print()
print("***")
print("<command> exit - выйти из программы")
print(" <command> help - справочная информация")

while True:
    command = prompt.string(" Введите команду: _")
    if command == "exit":
            print("Выход из программы. До свидания!")
            break
    if command == "help":
        print()
        print("<command> exit - выйти из программы")
        print("<command> help - справочная информация")
        print()
        continue