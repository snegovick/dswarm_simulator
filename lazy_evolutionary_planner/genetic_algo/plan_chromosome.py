import random
# Chromosome compact form: <task index> <executor>
class Chromosome:
    def __init__(self, compact="", split_form=[], mutation_probability=0.3):
        self.mutation_probability = mutation_probability
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

    def mutate(self, amount, executors):
        for i in range(amount):
            if (random.random()<self.mutation_probability):
                if random.random()>0.5:
                    # permutation mutation
                    index1 = random.randint(0, len(self.split_form)-1)
                    index2 = random.randint(0, len(self.split_form)-1)
                    if index1!=index2:
                        t = self.split_form[index1]
                        self.split_form[index1] = self.split_form[index2]
                        self.split_form[index2] = t
                else:
                    # change of executor mutation
                    index = random.randint(0, len(self.split_form)-1)
                    self.split_form[index] = (self.split_form[index][0], executors[random.randint(0, len(executors)-1)])
        # repair the split form
        repaired_split_form = []
        added_tasks = []
        for i in self.split_form:
            if not (i[0] in added_tasks):
                repaired_split_form.append(i)
        self._join()

    def crossover(self, chromosome2):
        start = random.randint(0, len(self)-2)
        end = random.randint(0, (len(self)-1-start)/2)+start

        new_split_form = []
        sorted_split_form = self.split_form[:]
        sorted_split_form.sort()
        print ""
        for i, v in enumerate(sorted_split_form):
            if (i<start):
                new_split_form.append(v)
            elif i>=start and i<=end:
                new_split_form.append(chromosome2.split_form[i])
            else:
                new_split_form.append(v)                
        return Chromosome(split_form=new_split_form)

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
    c1 = Chromosome("1 a 2 b 3 c 4 d")
    c2 = Chromosome("1 b 2 d 3 c 4 b")
    print c1
    print "len(c1):", len(c1)
    print c2
    print "len(c2):", len(c2)

    executors = ['a', 'b', 'c', 'd']
    for i in range(1000):
        print "c1 X c2:", c1.crossover(c2)
        c1.mutate(len(c1)/3, executors)
        print "c1 after mutation:", c1
