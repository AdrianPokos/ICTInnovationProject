# Importing scripts
from malwaressti import mainssti
from bruteforcing import run_demo_sequence
from bruteforcing import interactive_mode
from ebe import mainebe
from xxe_detectorv1 import mainxxe
# From sqli import mainsqli <-- For sqli to work on you will need to install the missing frameworks through pip.

# importing tests <-- Used before implementation of subprocess manager
import tests_brute
import tests_ebe
import tests_malwssti
import tests_sqli
import tests_xxe

# Importing python subprocess manager
import subprocess


def solutions():
  print("\n"
  "These are the solutions the team has worked on which includes Malware SSTI, Bruteforcing,\n"
  "Error-based Enumeration, XML External Entity, and SQL Injection. Each of the vulnerabilities corresponds\n" 
  "to a number ranging from 1 to 5 within the order listed before.")

  select_solution = input("Please select a number: ")

  if select_solution == "1":
    if __name__ == "__main__":
      mainssti()

  elif select_solution == "2":
    print("\n"
    "There are two methods of running bruteforcing with one being a demo sequence and one being the interactive mode.\n"
    "The two methods of running the script correspond to a number between 1 and 2.")
    select_brute = input("Please select a number: ")
    if select_brute == "1":
      if __name__ == "__main__":
        run_demo_sequence()
    elif select_brute == "2":
      if __name__ == "__main__":
        interactive_mode()
    else:
      print("Please select an appropriate number.")
  
  elif select_solution == "3":
    if __name__ == "__main__":
      mainebe()
  
  elif select_solution == "4":
    if __name__ == "__main__":
      mainxxe()
  
  elif select_solution == "5":
    if __name__ == "__main__":
      print("Download the required frameworks through pip.")


def unittests():
  print("\n"
  "Please select what test you want to do (select a number between 1 and 5 for the respective vulnerabilities.)")
  
  select_test = input("Please select a number: ")

  if select_test == "1":
    if __name__ == "__main__":
      subprocess.run("python tests_malwssti.py", shell=True)

  elif select_test == "2":
    if __name__ == "__main__":
      subprocess.run("python tests_brute.py", shell=True)

  elif select_test == "3":
    if __name__ == "__main__":
      subprocess.run("python tests_ebe.py", shell=True)
  
  elif select_test == "4":
    if __name__ == "__main__":
      subprocess.run("python tests_xxe.py", shell=True)
  
  elif select_test == "5":
    if __name__ == "__main__":
      subprocess.run("python tests_sqli.py", shell=True)
  
  else:
    print("Please select an appropriate number.")


def main():
  try:
    print("""\033[31m     _____________________ ____  ____ ________    __________  ____ 
    /  _/ ____/_  __/__  // __ \\/ __ <  / ___/   / ____/ __ \\/ __ \\
    / // /     / /   /_ </ / / / / / / / __ \\   / __/ / / / / /_/ /
  _/ // /___  / /  ___/ / /_/ / /_/ / / /_/ /  / /___/ /_/ / _, _/ 
 /___/\\____/ /_/  /____/\\____/\\____/_/\\____/  /_____/_____/_/ |_| \n\033[0m""")
      
    print("This is our groups EDR solution, it offers detection and protection from Malware SSTI, "
    "Bruteforcing, Error-based Enumeration, XML External Entity, and SQL Injection.\n" 
    "It also offers unit testing for the scripts developed by the team.\n")
    print("There are two modes included with the main script which includes running the individual developed scripts and running the unit tests.\n"
    "Select a number between 1 and 2 to select which mode you want to continue with.")

    select = input("Please select a number: ")

    if select == "1":
      solutions()

    elif select == "2":
      unittests()

    else:
      print("Please select an apporpriate number.")

  except KeyboardInterrupt:
    print("\nCtrl+C pressed. Exiting...")


if __name__ == "__main__":
  main()
