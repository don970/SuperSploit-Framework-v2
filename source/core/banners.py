import traceback
import pyfiglet
from .ToStdOut import ToStdout
import os
import random

installation = f'{os.getenv("HOME")}/.SuperSploit'


class Banners:
     def __init__(self, a):
        os.system("clear")
        try:
            # this will open the fun facts or osnit fact file and save it to a variable
            with open(f"{installation}/.data/.banners/{random.choice(os.listdir(f'{installation}/.data/.banners/'))}") as file:
                data = file.read()
                file.close()
            # first we make a list out of the data each entry in the list contains a fact about computers
            data = data.split("#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!#!")
            choice = random.choice(data)
            ToStdout.write(pyfiglet.figlet_format("Supersploit"))
            ToStdout.write(choice)
            return
        except RuntimeError:
            ToStdout.write(traceback.format_exc())

