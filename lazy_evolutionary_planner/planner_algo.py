import random
# Chromosome compact form: <task index> <executor>
class Chromosome:
    def __init__(self, compact="", split_form=[]):
        if compact!="":
            self.compact_form = compact
            self._split()
        elif split_form!=[]:
            self.split_form = split_form
            self._join()
        else:
            self.split_form = []
            self.compact_form = ""

    def __len__(self):
        return len(self.split_form)

    def __repr__(self):
        return "<Chromosome "+str(self._shortForm())+">"

    def _shortForm(self):
        return self.compact_form.replace(" ", "")

    def mutate(self, amount):
        for i in amount:
            

    def crossover(self, chromosome2):
        # 
        start = random.randint(0, len(self))
        end = random.randint(start, len(self))+start
        new_split_form = []
        for i, v in enumerate(self.split_form):
            if (i<start):
                new_split_form.append(v)
            elif i>=start and i<end:
                new_split_form.append(chromosome2.split_form[i])
            else:
                new_split_form.append(v)                
        return Chromosome()

    def _split(self):
        self.split_form = []
        data = self.compact_form.split(" ")
        chromosome_len = len(data)
        for i in range(0, chromosome_len, 2):
            self.split_form.append((data[i], data[i+1]))

    def _join(self):
        self.compact_form = ""
        for k, v in self.split_form:
            self.compact_form += str(k)+" "+str(v)+" "
        self.compact_form = self.compact_form[:-1]

if __name__=="__main__":
    c = Chromosome("1 a 2 b 3 c")
    print c
    print "len(c):", len(c)
