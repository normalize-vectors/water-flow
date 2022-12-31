import pygame


def main():

    max_terrain_height = 140

    z = [z for z in range(-max_terrain_height, max_terrain_height + 1, 10)]

    cell_width = 30
    cell_height = 100

    screen = pygame.display.set_mode((len(z)*cell_width, 2*cell_height))

    def f(x): return (x/400) + 0.7

    for x in range(len(z)):

        color_orig = (219, 217, 190)  # brightest color
        mod = f(z[x])
        color = (color_orig[0]*mod, color_orig[1]*mod, color_orig[2]*mod)

        rect = (cell_width*x, 0, cell_width, cell_height*1.5)

        pygame.draw.rect(screen, color, rect)

    for x in range(len(z)):

        color_orig = (109, 137, 219)  # brightest color
        mod = f(z[x])
        color = (color_orig[0]*mod, color_orig[1]*mod, color_orig[2]*mod)

        rect = (cell_width*x, cell_height, cell_width, cell_height)

        pygame.draw.rect(screen, color, rect)

    pygame.display.flip()

    running = True

    clock = pygame.time.Clock()

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
        clock.tick(60)


if __name__ == "__main__":
    main()
    pygame.quit()
