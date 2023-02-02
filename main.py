import random
import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Body
import random


class DiseaseVector:
    def __init__(self, coll, color):
        global speed
        self.body = pymunk.Body()
        self.body.mass = .001
        self.body.position = random.randint(10, 990), random.randint(10, 990)
        self.body.moment = pymunk.moment_for_circle(self.body.mass, 0, 10, (0, 0))
        self.body.velocity = (random.randint(-speed, speed), random.randint(-speed, speed))
        self.shape = pymunk.Circle(self.body, 10)
        self.shape.elasticity = 1.0
        self.shape.friction = .001
        self.shape.collision_type = coll
        self.age = 0
        self.shape.color = color

    @staticmethod
    def infect(arbiter, space, dummy):
        global infectiousness
        if random.randint(0, 100) < infectiousness:
            shapes = arbiter.shapes
            shapes[0].collision_type = 2
            shapes[0].color = (255, 0, 0, 255)
        return True

    def increment_age(self):
        if self.shape.collision_type == 2:
            self.age += 1

    def end_infection(self):
        global death_rate
        if random.randint(1, 100) > death_rate:
            self.shape.collision_type = 3
            self.shape.color = (0, 255, 0, 255)
        else:
            self.shape.collision_type = 4
            self.shape.sensor = True
            self.shape.color = (0, 0, 0, 0)
            self.body.velocity = 0, 0


class DiseaseSim:
    def __init__(self):
        self.space = pymunk.Space()
        self.dt = 1.0 / 50.0
        self.physics_steps_per_frame = 1
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 1000))
        self.clock = pygame.time.Clock()
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.people = []
        self.running = True

    def run(self):
        global number
        global infection_length
        self.create_border()
        self.collision_handling()
        for _ in range(number):
            self.create_vector(1, (0, 0, 255, 255))
        self.create_vector(2, (255, 0, 0, 255))
        while self.running:
            for x in range(self.physics_steps_per_frame):
                self.space.step(self.dt)
            self.process_events()
            self.screen.fill(pygame.Color("white"))
            self.draw_objects()
            pygame.display.flip()
            self.clock.tick(50)
            for person in self.people:
                DiseaseVector.increment_age(person)
                if person.age > infection_length and person.shape.collision_type == 2:
                    DiseaseVector.end_infection(person)
            pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
            if not self.detect_infected():
                self.running = False
        self.summary()

    def create_vector(self, coll, color):
        person = DiseaseVector(coll, color)
        self.space.add(person.body, person.shape)
        self.people.append(person)

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def draw_objects(self):
        self.space.debug_draw(self.draw_options)

    def create_border(self):
        static_body = self.space.static_body
        static_lines = [
            pymunk.Segment(static_body, (0, 0), (0, 1000), 0.0),
            pymunk.Segment(static_body, (0, 1000), (1000, 1000), 0.0),
            pymunk.Segment(static_body, (1000, 1000), (1000, 0), 0.0),
            pymunk.Segment(static_body, (1000, 0), (0, 0), 0.0)
        ]
        for line in static_lines:
            line.elasticity = 1
            line.friction = 0
        self.space.add(*static_lines)

    def collision_handling(self):
        infecting = self.space.add_collision_handler(1, 2)
        infecting.begin = DiseaseVector.infect

    def detect_infected(self):
        for person in self.people:
            if person.shape.collision_type == 2:
                return True
        return False

    def summary(self):
        healthy = 0
        recovered = 0
        dead = 0
        for person in self.people:
            if person.shape.collision_type == 1:
                healthy += 1
            elif person.shape.collision_type == 3:
                recovered += 1
            else:
                dead += 1
        print(f'{healthy} individuals remained uninfected. {recovered} recovered from illness. {dead} Succumbed '
              f'to the infection.')


if __name__ == "__main__":
    number = int(input('Input a number of uninfected people for the simulation (<=500): '))
    speed = int(input('Input the speed at which people move (<=200): '))
    infectiousness = int(input('Input the chance of infection on contact with an infected individual (1-100): '))
    infection_length = int(input('Input the length of the infection in fiftieths of seconds: '))
    death_rate = int(input('Input the chance of death at the end of infection (1-100): '))
    game = DiseaseSim()
    game.run()
