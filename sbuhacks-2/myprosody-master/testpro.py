import myprosody as mysp
import pickle

p="user_input" 
c=r"myprosody"


mysp.mysptotal(p,c)
print("----------------------------------")
mysp.myspgend(p,c)
print("----------------------------------")
mysp.myspsyl(p,c)
print("----------------------------------")
mysp.mysppaus(p,c)
print("----------------------------------")
mysp.myspsr(p,c)
print("----------------------------------")
mysp.myspatc(p,c)
print("----------------------------------")
mysp.myspst(p,c)
print("----------------------------------")
mysp.myspod(p,c)
print("----------------------------------")
mysp.myspbala(p,c)
print("----------------------------------")
mysp.myspf0mean(p,c)
print("----------------------------------")
mysp.myspf0sd(p,c)
print("----------------------------------")
mysp.myspf0med(p,c)
print("----------------------------------")
mysp.myspf0min(p,c)
print("----------------------------------")
mysp.myspf0max(p,c)
print("----------------------------------")
mysp.myspf0q25(p,c)
print("----------------------------------")
mysp.myspf0q75(p,c)
print("----------------------------------")
mysp.mysppron(p,c)
print("----------------------------------")
mysp.myprosody(p,c)
print("----------------------------------")
mysp.mysplev(p,c)

def test(p, c): 
    return mysp.mysptotal(p, c)

print("                    ")
print("                    ")
print(test(p, c))
