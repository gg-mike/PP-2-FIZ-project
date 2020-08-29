import simulation
import multiprocessing

Window = False
WIDTH, HEIGHT = 1000, 1000
FPS = 600
ParticleRadius = 16
ParticleSpeed = 1
SIMULATIONTIME = 10000
ThreadCount = 5
ParticleCount_MIN = 10
ParticleCount_MAX = 100
ParticleCount_STEP = 10
M = (10, 20, 50, 100)

# results localisation
tempPath = "tempResults/result"
ResultPath = "results/result"


def doTests(particles, M):
    # create result file
    tempResultPath = tempPath + f"{particles},{M}.txt"
    file = open(tempResultPath, "w")
    file.close()
    # create threads
    threads = []
    for i in range(ThreadCount):
        windowed = False
        if i == 0 and Window:
            windowed = True
        threads.append(multiprocessing.Process(target=simulation.run_simulation, args=(
            i, tempResultPath, M, WIDTH, HEIGHT, ParticleRadius, particles, ParticleSpeed, SIMULATIONTIME, FPS,
            windowed)))
    # start threads
    for i in range(ThreadCount):
        threads[i].start()
    # wait for threads
    for i in range(ThreadCount):
        threads[i].join()
    lamSum = nSum = 0
    file = open(tempResultPath, "r")
    for i in range(ThreadCount):
        line = file.readline().split(";")
        nSum += float(line[0])
        lamSum += float(line[1][:-1])
    file.close()
    print(f"Test Particles: {particles} done")
    return nSum / ThreadCount, lamSum / ThreadCount


if __name__ == '__main__':
    for m in M:
        file = open(ResultPath + f"{m}.txt", "w")
        file.write("Particles;Collisions;Distance\n")
        for i in range(ParticleCount_MIN, ParticleCount_MAX + ParticleCount_STEP, ParticleCount_STEP):
            result = doTests(i, m)
            file.write(f"{i};{result[0]};{result[1]}\n")
        file.close()
        print(f"Tests M: {m} done")