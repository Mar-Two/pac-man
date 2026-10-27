class Game():
    def __init__(self, lives: int, pacgum: int,
                 points_per_pacgum: int,
                 points_per_super_pacgum: int,
                 points_per_ghost: int,
                 level_max_time: int, levels: list[dict], seed):
        self.lives = lives
        self.pacgum = pacgum
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.level_max_time = level_max_time
        self.levels = levels
        self.seed = seed
