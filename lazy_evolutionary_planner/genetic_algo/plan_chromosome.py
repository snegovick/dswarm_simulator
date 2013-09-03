import random
# Chromosome compact form: <task index> <executor>
class Chromosome(object):
    def __init__(self, compact="", split_form=[], mutation_probability=0.3, task_costs=None):
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

        self.task_costs = task_costs
        if task_costs == None:
            # lets assume uniform cost
            self.task_costs = [1 for t in split_form]

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

        c1 = []
        c2 = []
        p1_sorted_split_form = self.split_form[:]
        p1_sorted_split_form.sort()
        p2_sorted_split_form = chromosome2.split_form[:]
        p2_sorted_split_form.sort()
        for i, (p1, p2) in enumerate(zip(p1_sorted_split_form, p2_sorted_split_form)):
            if (i<start):
                c1.append(p1)
                c2.append(p2)
            elif i>=start and i<=end:
                c1.append(p2)
                c2.append(p1)
            else:
                c1.append(p1)
                c2.append(p2)
        return (Chromosome(split_form=c1), Chromosome(split_form=c2))

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

    def evaluate(self):
        executor_queues = {}
        for t, e in self.split_form:
            if e in executor_queues:
                executor_queues[e]+=1
            else:
                executor_queues[e]=1
#        keys = executor_queues.keys()
#        values = executor_queues.values()
        
        return 1.0/max(executor_queues.values())

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
