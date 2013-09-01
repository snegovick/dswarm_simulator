from plan_chromosome import Chromosome as Plan
import string
import random

class Population(object):
    def __init__(self, number_of_individuals, executors, tasks):
        self.number_of_individuals = number_of_individuals
        self.executors = executors
        self.tasks = tasks
        self.individuals = []
        self._create_initial_population()
        self.values = []
        self.mutation_amount = len(tasks)/3
        
    def _create_random_individual(self):
        untaken = [i for i in range(len(self.tasks))]
        split_form = []
        for i in range(len(self.tasks)):
            while True:
                task_id = random.randint(0, len(self.tasks)-1)
                if self.tasks[task_id] in untaken:
                    executor_id = random.randint(0, len(self.executors)-1)
                    split_form.append((self.tasks[task_id], self.executors[executor_id]))
                    untaken.pop(untaken.index(task_id))
                    break
        return Plan(split_form=split_form)

    def _create_initial_population(self):
        for i in range(self.number_of_individuals):
            self.individuals.append(self._create_random_individual())

    def step(self):
        population = self.individuals[:]
        if self.values == []:
            for individual in population:
                self.values.append(individual.evaluate())
            self.evaluated_population = sorted(zip(self.values, population), reverse=True)
        # choose best 30% of parents
        parents = self.evaluated_population[:len(self.evaluated_population)/3]
        new_population = []
        while len(new_population)<len(self.evaluated_population):
            id1 = random.randint(0, len(parents)-1)
            id2 = random.randint(0, len(parents)-1)
            if id1!=id2:
                p1 = parents[id1][1]
                p2 = parents[id2][1]
                c1, c2 = p1.crossover(p2)
                c1.mutate(self.mutation_amount, self.executors)
                c2.mutate(self.mutation_amount, self.executors)
                new_population.append(c1)
                new_population.append(c2)
        population = new_population
        for individual in population:
            self.values.append(individual.evaluate())
        self.evaluated_population = sorted(zip(self.values, population), reverse=True)
        self.individuals = population


if __name__=="__main__":
    individuals = 10
    executors = []
    number_of_executors = 3

    tasks = [i for i in range(1000)]

    for i in string.letters[:number_of_executors]:
        executors.append(i)

    print "tasks:", tasks
    print "executors:", executors
    p = Population(individuals, executors, tasks)
    while True:
        p.step()
        for i in p.evaluated_population:
            print i
        print ""
