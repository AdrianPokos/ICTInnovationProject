# importing all necessary files

from bruteforcing import mainbrute
from xxe import mainxxe
from ebe import mainebe
from malwaressti import mainssti
from bruteforcing import run_demo_sequence
#from sqli import mainsqli

def main():
  print("""    _____________________ ____  ____ ________
   /  _/ ____/_  __/__  // __ \\/ __ <  / ___/
   / // /     / /   /_ </ / / / / / / / __ \\ 
 _/ // /___  / /  ___/ / /_/ / /_/ / / /_/ / 
/___/\\____/ /_/  /____/\\____/\\____/_/\\____/\n""")
    
  # to be improved on  
  print("This is our groups EDR solution, it offers detection and protection from bruteforcing, xxe, error-based enumeration, malware ssti, and sql injection.\n" 
  "Please select a number between 1 and 5 to select what solution you would like to perform.")
    
  selection = input()

  # Just includes demo for now, will be improved on
  if selection == "1":
    if __name__ == "__main__":
      run_demo_sequence()
      #mainbrute()

  elif selection == "2":
    if __name__ == "__main__":
      mainxxe()
  
  elif selection == "3":
    if __name__ == "__main__":
      mainebe()
  
  elif selection == "4":
    if __name__ == "__main__":
      mainssti()

  elif selection == "5":
    print("This part is not developed yet.")
    #if __name__ == "__main__":
      #mainsqli()

  else:
    print("Please select an appropriate number.")
  
if __name__ == "__main__":
  main()
