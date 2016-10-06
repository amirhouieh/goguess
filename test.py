import os
from goguess import Goguess

input_dir = os.path.abspath( "test" )

ggs = Goguess(inputDir=input_dir)
ggs.go()