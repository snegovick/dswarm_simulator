from plan_chromosome import Chromosome as Plan
import string
import random

class Population:
    def __init__(self, number_of_individuals, executors, tasks):
        self.number_of_individuals = number_of_individuals
        self.executors = executors
        self.tasks = tasks
        
    def _create_random_individual(self):
        untaken = [i for i in range(len(self.tasks))]
        split_form = []
        for i in range(len(self.tasks)):
            while True:
                task_id = random.randint(0, len(self.tasks)-1)
                if self.tasks[task_id] in untaken:
                    executor_id = random.randint(0, len(self.executors)-1)
                    split_form.append((self.tasks[task_id], self.executors[executor_id]))
                    untaken.remove(untaken.index(task_id))
                    break
        print "split_form:", split_form

    def _create_initial_population(self):
        pass

if __name__=="__main__":
    individuals = 10
    executors = []
    number_of_executors = 3

    tasks = [i for i in range(100)]

    for i in string.letters[:number_of_executors]:
        executors.append(i)

    print "tasks:", tasks
    print "executors:", executors
    p = Population(individuals, executors, tasks)
    p._create_random_individual()
