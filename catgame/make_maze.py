import random
import sys
WIDTH = 16
HEIGHT = 16

MOVER = [(0, -1), (1, 0), (0, 1), (-1, 0)]

def make_maze(width, height, binary = False):
    #init map
    maze = []
    for i in range(height):
        line = []
        for j in range(width):
            #walls at border
            if i == 0 or i == height - 1 or j == 0 or j == width - 1:
                line.append(-1)
            else:
                line.append('x')
        maze.append(line)

    #start pos 1,1
    count = 0
    path = [(1,1)]
    maze[path[0][1]][path[0][0]] = count
    #from here, generate maze paths
    done = False
    while not done:
        #e.g.
        #         7  x  x  x
        #         x  x  x  x
        #before:  0  x  x  x
        #         x  x  x  x
        #         x  x  x  x
        # rand chooses -->
        #         7  x  x  x
        #        -1 -1  x  x
        #after:   0  1  1  x
        #         x -1  x  x
        #         x  x  x  x
        deadend = False
        while not deadend:
            #add necessary walls around current pos & check for valid dirs
            valids = []
            for m in MOVER:
                if maze[path[-1][1] + 2 * m[1]][path[-1][0] + 2 * m[0]] == 'x':
                    valids.append(m)
                elif abs(maze[path[-1][1] + 2 * m[1]][path[-1][0] + 2 * m[0]] - maze[path[-1][1]][path[-1][0]]) > 1:
                    maze[path[-1][1] + m[1]][path[-1][0] + m[0]] = -1

            #deal with case of no valid directions before proceeding
            if not valids:
                deadend = True
                count -= 1
            else:
                d = random.choice(valids)
                #check for wall/path two over in dir d
                new_pos = (path[-1][0] + 2 * d[0], path[-1][1] + 2 * d[1])

                #this path segment is path[count]
                count += 1
                path.append(new_pos)

                #step 1
                maze[new_pos[1] - d[1]][new_pos[0] - d[0]] = count
                #step 2
                maze[new_pos[1]][new_pos[0]] = count
                #walls flanking step 1
                maze[new_pos[1] - d[1]
                + MOVER[(MOVER.index(d) + 1) % 4][1]][new_pos[0] - d[0] + MOVER[(MOVER.index(d) + 1) % 4][0]] = -1
                maze[new_pos[1] - d[1]
                + MOVER[(MOVER.index(d) + 3) % 4][1]][new_pos[0] - d[0] + MOVER[(MOVER.index(d) + 3) % 4][0]] = -1
        #once we hit a deadend: retrace steps one step, by popping path[-1] off the list (hope this works!)
        #if we are back at step one & it's a deadend, we're done!
        if path[-1] == (1,1):
            done = True
        else:
            path.pop()

    #if binary flag, convert maze to 0=path, 1=wall before returning
    for i in range(height):
        for j in range(width):
            if maze[i][j] == -1:
                maze[i][j] = 1
            else:
                maze[i][j] = 0
    return maze

def print_maze(maze):
    for i in range(len(maze)):
        line = ''
        for j in range(len(maze[i])):
            if maze[i][j] == -1:
                line = line + "\033[40m  \033[0m "
            else:
                for s in range(len(str(maze[i][j])), 2):
                    line = line + ' '
                line = line + str(maze[i][j]) + ' '
        sys.stdout.write(line)
        print()

if __name__ == '__main__':
    maze = make_maze(WIDTH, HEIGHT)
    print_maze(maze)
