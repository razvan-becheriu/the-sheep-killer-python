import math
import random
from typing import List, Optional, Any
from core.math_utils import Vector2, angle_dist, sign, get_vector2
from core.model import RealTimeModel, Animation, ModelTreeNode, GraphicElementType
from core.animation import AnimationHandler
from core.globals import global_vars
from core.media import MediaManager # For loading sounds and models

# Constants from gameunit.pas
ANIM_STAND = 0
ANIM_WALK = 1
ANIM_ATTACK = 2
ANIM_HIT = 3
ANIM_DIE = 4
ANIM_ATTACKB = 5

TILESIZE = 4
AREASIZE = 12

class BaseList(list): # Inheriting from list for simplicity. Pascal uses TObjectList
    def __init__(self):
        super().__init__()
        self._num_sheep: int = 0
        self._player: Optional['Viking'] = None
        self.anim_viking: Optional[RealTimeModel] = None
        self.anim_sheep: Optional[RealTimeModel] = None
        self.anim_tree: Optional[RealTimeModel] = None
        self.anim_wolf: Optional[RealTimeModel] = None

        self.level: int = 0
        self.last_level_life: int = 5
        self.score: int = 0

    def initialize_models(self, media_manager: MediaManager):
        # These models are loaded once and shared by all instances of entities
        print("Initializing game models...")
        self.anim_viking = RealTimeModel()
        if not self.anim_viking.load_from_file('media/viking_weapon.model', media_manager):
            print("Error: Failed to load viking_weapon.model")
        self.anim_sheep = RealTimeModel()
        if not self.anim_sheep.load_from_file('media/sheep.model', media_manager):
            print("Error: Failed to load sheep.model")
        self.anim_tree = RealTimeModel()
        self.anim_fence = RealTimeModel() # Add fence model
        if not self.anim_fence.load_from_file('media/fence.model', media_manager):
            print("Error: Failed to load fence.model")
        if not self.anim_tree.load_from_file('media/tree1.model', media_manager):
            print("Error: Failed to load tree1.model")
        self.anim_wolf = RealTimeModel()
        if not self.anim_wolf.load_from_file('media/ram.model', media_manager):
            print("Error: Failed to load ram.model")
        print("Game model initialization complete.")

    @property
    def player(self) -> Optional['Viking']:
        return self._player

    @property
    def num_sheep(self) -> int:
        return self._num_sheep

    def get_base(self, index: int) -> 'Base':
        return self[index]

    def _adjust_collision(self, a: 'Base', b: 'Base', comp: float):
        v = a.position - b.position
        v.normalize()
        if a.pushable == b.pushable:
            # If both are pushable or not pushable, subdivide the push
            v_scaled = v * (comp / 2)
            a.position = a.position - v_scaled
            b.position = b.position + v_scaled
        else:
            # Only one is pushable. Apply all to it.
            v_scaled = v * comp
            if a.pushable:
                a.position = a.position - v_scaled
            else:
                b.position = b.position + v_scaled

    def update(self, delta: float):
        # Update all entities
        for entity in self:
            entity.update(delta)

        # Collision detection and response
        for i in range(len(self)):
            a = self[i]
            for j in range(i + 1, len(self)): # Avoid self-collision and duplicate checks
                b = self[j]
                d = (a.position - b.position).magnitude() - (a.size + b.size) # Compenetrating value
                if d < 0:
                    self._adjust_collision(a, b, d)

        # Boundary checks
        for entity in self:
            entity.position.x = max(entity.size, min(entity.position.x, TILESIZE * AREASIZE - entity.size))
            entity.position.y = max(entity.size, min(entity.position.y, TILESIZE * AREASIZE - entity.size))

        # Dead harvesting
        i = 0
        while i < len(self):
            entity = self[i]
            if entity.dead and entity != self._player:
                if isinstance(entity, Sheep):
                    self._num_sheep -= 1
                self.pop(i)
            else:
                i += 1

        # Sort entities (Pascal code sorts by X position, not strictly necessary for Python list)
        # self.sort(key=lambda e: e.position.x)

    def add(self, item: Any) -> int:
        if isinstance(item, Sheep):
            self._num_sheep += 1
        super().append(item)
        return len(self) - 1 # Return index of added item

    def restart(self):
        self.clear()
        self._num_sheep = 0
        self._player = None
        self.level = 0
        self.last_level_life = 5
        self.score = 0
        self.next_level()

    def next_level(self):
        if self._player is not None:
            self.last_level_life = self._player.life

        self.clear()
        self._num_sheep = 0
        self._player = None

        self.level += 1

        # Add player
        self._player = Viking(self, self.anim_viking)
        self._player.position.x = random.uniform(0, TILESIZE * AREASIZE)
        self._player.position.y = random.uniform(0, TILESIZE * AREASIZE)
        self._player.size = 1.1
        self._player.modelsize = 2.0
        self._player.life = self.last_level_life
        self.add(self._player)

        # Add trees
        for _ in range(4):
            tree = Tree(self, self.anim_tree)
            tree.position.x = random.uniform(0, TILESIZE * AREASIZE)
            tree.position.y = random.uniform(0, TILESIZE * AREASIZE)
            tree.size = 1.1
            tree.modelsize = 4.0
            tree.pushable = False
            tree.speed = 0.0
            self.add(tree)

        # Add sheep
        for _ in range(self.level * 2 + 1):
            sheep = Sheep(self, self.anim_sheep)
            sheep.position.x = random.uniform(0, TILESIZE * AREASIZE)
            sheep.position.y = random.uniform(0, TILESIZE * AREASIZE)
            sheep.size = 1.4
            sheep.modelsize = 1.8
            sheep.angle = random.uniform(0, 2 * math.pi)
            self.add(sheep)

        # Add wolves
        for _ in range(self.level):
            wolf = Wolf(self, self.anim_wolf)
            wolf.position.x = random.uniform(0, TILESIZE * AREASIZE)
            wolf.position.y = random.uniform(0, TILESIZE * AREASIZE)
            wolf.patrol = get_vector2(random.uniform(0, TILESIZE * AREASIZE), random.uniform(0, TILESIZE * AREASIZE))
            wolf.patrolarea = 20.0
            wolf.size = 1.4
            wolf.modelsize = 1.8
            wolf.pushable = True
            wolf.life = 8
            wolf.speed = 0.0
            wolf.angle = random.uniform(0, 2 * math.pi)
            self.add(wolf)

        # The last two wolves always follow the player (if they exist)
        if len(self) >= 2 and isinstance(self[-1], Wolf):
            self[-1].patrolarea = 1000.0
        if len(self) >= 3 and isinstance(self[-2], Wolf):
            self[-2].patrolarea = 1000.0


class Base:
    def __init__(self, a_list: BaseList, a_model: RealTimeModel):
        self.life: int = 4
        self.list: BaseList = a_list
        self.speed: float = 0.0
        self.angle: float = 0.0 # Radians
        self.anim: AnimationHandler = AnimationHandler(a_model)
        self.anim.start(ANIM_STAND, 3.0)
        self.anim.position = random.random() # To avoid all units synchronized
        self.pushable: bool = True
        self.dead: bool = False
        self.position: Vector2 = get_vector2(random.uniform(0, TILESIZE * AREASIZE), random.uniform(0, TILESIZE * AREASIZE))
        self.size: float = 1.0 # Default collision radius
        self.modelsize: float = 1.0 # Default for rendering/occlusion
        self.sound_time: float = 0.0
        self.displacement: Vector2 = get_vector2(0, 0)

        # Initialize default animation
        if self.anim and self.anim.model:
            self.anim.start(ANIM_STAND, 3.0) # Assume ANIM_STAND is 0, duration 3.0
            self.anim.update(random.random()) # Randomize start position

    def do_attack(self, delta: float):
        for entity in self.list:
            if entity != self and self.is_valid_target(entity):
                entity.do_hit()

    def is_valid_target(self, other: 'Base') -> bool:
        if other.dead or other.life <= 0:
            return False
        # Check if 'other' is in front and near enough
        if (self.position - other.position).magnitude() < 5.0:
            # Create a vector pointing forward from self
            forward_vec = get_vector2(0, self.size + 1).rotate(self.angle)
            target_check_pos = self.position + forward_vec
            if (other.position - target_check_pos).magnitude() < other.size:
                return True
        return False

    def do_hit(self):
        raise NotImplementedError("do_hit must be implemented by subclasses.")

    def update(self, delta: float):
        self.sound_time += delta

        self.displacement.x = 0.0
        self.displacement.y = self.speed * delta
        self.displacement = self.displacement.rotate(self.angle)
        self.position = self.position + self.displacement

        self.anim.interpolate() # Always interpolate the model


class Tree(Base):
    def __init__(self, a_list: BaseList, a_model: RealTimeModel):
        super().__init__(a_list, a_model)
        self.pushable = False # Trees are not pushable

    def do_hit(self):
        # Trees don't take damage or die in the original Pascal code
        pass

class Viking(Base):
    def __init__(self, a_list: BaseList, a_model: RealTimeModel):
        super().__init__(a_list, a_model)
        self.life = 5 # Initial life for Viking

    def _handle_no_key(self):
        if self.anim.current_anim in (ANIM_HIT, ANIM_DIE):
            return
        self.speed = 0.0
        if self.anim.current_anim != ANIM_STAND:
            self.anim.start(ANIM_STAND, 3.0)

    def _handle_key_up(self):
        if self.anim.current_anim in (ANIM_ATTACK, ANIM_ATTACKB, ANIM_HIT, ANIM_DIE):
            return
        if self.anim.current_anim == ANIM_WALK:
            self.speed = 6.5
        else:
            self.anim.start(ANIM_WALK, 1.0)
            self.speed = 6.5

    def _handle_key_down(self):
        if self.anim.current_anim in (ANIM_ATTACK, ANIM_ATTACKB, ANIM_HIT, ANIM_DIE):
            return
        if self.anim.current_anim == ANIM_WALK:
            self.speed = -6.5
        else:
            self.anim.start(ANIM_WALK, 1.0)
            self.speed = -6.5

    def _handle_key_ctrl(self):
        if self.anim.current_anim in (ANIM_HIT, ANIM_DIE):
            return
        self.speed = 0.0
        if self.anim.current_anim not in (ANIM_ATTACK, ANIM_ATTACKB):
            if random.randint(0, 1) == 1:
                self.anim.start(ANIM_ATTACK, 0.6)
            else:
                self.anim.start(ANIM_ATTACKB, 0.6)

    def update(self, delta: float):
        if self.dead:
            return

        # Rotation
        if global_vars.keystate.left:
            self.angle += 4 * delta
        if global_vars.keystate.right:
            self.angle -= 4 * delta

        # Movement/Action
        if global_vars.keystate.ctrl or global_vars.keystate.space:
            self._handle_key_ctrl()
        elif global_vars.keystate.up:
            self._handle_key_up()
        elif global_vars.keystate.down:
            self._handle_key_down()
        else:
            self._handle_no_key()

        # Handle animation triggers
        if self.anim.current_anim in (ANIM_ATTACK, ANIM_ATTACKB):
            if self.anim.trigger():
                global_vars.media_manager.play_sound('swhoosh0')
                self.do_attack(delta)

        if self.anim.update(delta): # Animation looped
            if self.anim.current_anim == ANIM_HIT and self.life == 0:
                self.anim.start(ANIM_DIE, 1.0)
            elif self.anim.current_anim == ANIM_DIE:
                self.dead = True
                self.anim.position = 1.0 - 1e-12 # To have the player rest when he dies (EPSILON)
                return
            else:
                self.anim.start(ANIM_STAND, 3.0)

        if not self.dead:
            super().update(delta) # Call base class update for movement

    def do_hit(self):
        if not self.dead and self.life > 0 and self.anim.current_anim not in (ANIM_HIT, ANIM_DIE):
            self.speed = 0.0
            self.anim.start(ANIM_HIT, 0.3)
            self.life -= 1

            global_vars.media_manager.play_sound('hit0')
            if self.life == 0:
                global_vars.media_manager.play_sound('scream')


class Sheep(Base):
    def choose_activity(self):
        if random.randint(0, 9) == 9:
            self.anim.start(ANIM_STAND, 2.0)
            self.speed = 0.0
        else:
            self.anim.start(ANIM_WALK, 1.0)
            self.speed = 2.0

    def update(self, delta: float):
        if self.anim.current_anim == ANIM_WALK:
            self.angle -= 0.2 * delta # Random turning

        if self.anim.update(delta): # Animation looped
            if self.anim.current_anim == ANIM_HIT:
                if self.life == 0:
                    self.anim.start(ANIM_DIE, 0.3)
                    self.speed = 0.0
                else:
                    self.choose_activity()
            elif self.anim.current_anim == ANIM_DIE:
                self.dead = True
                self.list.score += 5
            else:
                self.choose_activity()
        super().update(delta)

    def do_hit(self):
        if self.anim.current_anim not in (ANIM_HIT, ANIM_DIE):
            self.speed = 0.0
            self.anim.start(ANIM_HIT, 0.3)
            self.life -= 1

            global_vars.media_manager.play_sound('hit0')
            if self.life == 0:
                global_vars.media_manager.play_sound('sheep')


class Wolf(Base):
    def __init__(self, a_list: BaseList, a_model: RealTimeModel):
        super().__init__(a_list, a_model)
        self.patrol: Vector2 = get_vector2(0, 0)
        self.patrolarea: float = 0.0 # Distance threshold for patrol vs player target

    def choose_activity(self):
        if random.randint(0, 9) == 9:
            self.anim.start(ANIM_STAND, 2.0)
            self.speed = 0.0
        else:
            self.anim.start(ANIM_WALK, 1.0)
            self.speed = 2.0

    def get_target(self) -> Vector2:
        if (self.position - self.patrol).magnitude() > self.patrolarea:
            return self.patrol
        return self.list.player.position

    def update(self, delta: float):
        if self.anim.current_anim == ANIM_WALK:
            target = self.get_target()
            target_angle = (target - self.position).get_angle()
            angle_diff = angle_dist(self.angle, target_angle)
            turn_amount = sign(angle_diff) * delta # Turn towards target
            if abs(turn_amount) > abs(angle_diff):
                turn_amount = angle_diff # Don't overshoot
            self.angle += turn_amount

            if self.is_valid_target(self.list.player):
                self.anim.start(ANIM_ATTACK, 1.0)
                self.speed = 0.0

        if self.anim.current_anim == ANIM_ATTACK:
            if self.anim.trigger():
                global_vars.media_manager.play_sound('rambite')
                self.do_attack(delta)

        if self.anim.update(delta): # Animation looped
            if self.anim.current_anim == ANIM_HIT:
                if self.life == 0:
                    self.anim.start(ANIM_DIE, 0.3)
                    self.speed = 0.0
                else:
                    self.choose_activity()
            elif self.anim.current_anim == ANIM_DIE:
                self.dead = True
                self.list.score += 15
            else:
                self.choose_activity()
        super().update(delta)

    def do_hit(self):
        if self.anim.current_anim not in (ANIM_HIT, ANIM_DIE):
            self.speed = 0.0
            self.anim.start(ANIM_HIT, 0.3)
            self.life -= 1

            global_vars.media_manager.play_sound('hit0')
            if self.life == 0:
                global_vars.media_manager.play_sound('ramdie')