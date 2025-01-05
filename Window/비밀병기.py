import random

class Boss:
    def __init__(self):
        self.hp = 100
        self.phase = 1
        self.current_pattern = 0
        self.player_distance = 0  # 플레이어와의 거리
        self.patterns = {
            1: [self.slash_attack, self.fireball],
            2: [self.dash_attack, self.area_attack],
        }

    def slash_attack(self):
        print("Boss uses Slash Attack!")

    def fireball(self):
        print("Boss casts a Fireball!")

    def dash_attack(self):
        print("Boss dashes towards the player!")

    def area_attack(self):
        print("Boss uses an Area of Effect Attack!")

    def react_to_player(self, player_action):
        """플레이어 행동에 따라 반응"""
        if player_action == "jump":
            print("Boss anticipates and launches an upward strike!")
        elif player_action == "attack":
            print("Boss counters the player's attack!")
        elif player_action == "distance":
            self.ranged_attack()

    def ranged_attack(self):
        print("Boss fires a projectile!")

    def next_action(self, player_action):
        """다음 행동 결정"""
        # 1. 상황 반응: 플레이어 행동에 반응
        self.react_to_player(player_action)

        # 2. 패턴에 따른 행동
        actions = self.patterns[self.phase]
        action = actions[self.current_pattern]
        action()
        self.current_pattern = (self.current_pattern + 1) % len(actions)

        # 3. 랜덤성 추가
        if random.random() < 0.3:  # 30% 확률로 특별 행동
            self.special_attack()

    def special_attack(self):
        print("Boss unleashes a devastating special attack!")

    def update_phase(self):
        """페이즈 업데이트"""
        if self.hp <= 50 and self.phase == 1:
            self.phase = 2
            self.current_pattern = 0
            print("Boss enters Phase 2!")

# 테스트 루프
boss = Boss()
player_actions = ["jump", "attack", "distance"]  # 플레이어 행동
while boss.hp > 0:
    player_action = random.choice(player_actions)
    print(f"Player action: {player_action}")
    boss.next_action(player_action)
    boss.hp -= 10  # 테스트를 위해 체력 감소
    boss.update_phase()
    print(f"Boss HP: {boss.hp}")
