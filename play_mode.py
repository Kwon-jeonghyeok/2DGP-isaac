from pico2d import *
import game_framework
import game_world
import title_mode

from isaac import Isaac
from stage_1 import Stage_1
from stage_2 import Stage_2
from host import Host
from sucker import Sucker
from stage_3 import Stage_3
import common

#isaac = None
stage = None
host = None
suckers = []
stage_index = 1
def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            if common.isaac is not None:
                common.isaac.handle_event(event)

def init():
    global isaac, stage, stage_index, host, suckers

    stage = Stage_1()
    game_world.add_object(stage, 0)

    host = [Host() for i in range(3)]

    common.isaac = Isaac()
    game_world.add_object(common.isaac, 2)
    stage_index = 1

    game_world.add_collision_pair('isaac:host', common.isaac, None)
    game_world.add_collision_pair('isaac:sucker', common.isaac, None)

    suckers = []

def _remove_projectiles():
    for layer in list(game_world.world):
        for o in list(layer):
            if o is None:
                continue
            name = o.__class__.__name__
            if name in ('Tear', 'HostBullet'):
                try:
                    game_world.remove_object(o)
                except Exception:
                    pass

def update():
    global stage, stage_index, isaac, host, suckers

    if common.isaac is None or stage is None:
        return

    game_world.update()

    bounds = stage.get_map_bounds()
    common.isaac.apply_map_bounds(bounds)

    vp_w = game_world.camera.get('w', 1000.0)
    vp_h = game_world.camera.get('h', 800.0)

    left = bounds.get('map_left', -1e9)
    right = bounds.get('map_right', 1e9)
    bottom = bounds.get('map_bottom', -1e9)
    top = bounds.get('map_top', 1e9)
    cam_x = common.isaac.x - vp_w / 2.0
    cam_y = common.isaac.y - vp_h / 2.0

    map_w = right - left
    map_h = top - bottom
    if map_w <= vp_w:
        cam_x = left + (map_w - vp_w) / 2.0
    else:
        cam_x = max(left, min(cam_x, right - vp_w))

    if map_h <= vp_h:
        cam_y = bottom + (map_h - vp_h) / 2.0
    else:
        cam_y = max(bottom, min(cam_y, top - vp_h))

    game_world.camera['x'] = cam_x
    game_world.camera['y'] = cam_y

    game_world.handle_collision()

    # Stage_1 -> Stage_2
    if common.isaac.y > 750 and stage_index == 1:
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
        except ValueError:
            pass
        stage = Stage_2()
        game_world.add_object(stage, 0)
        stage_index = 2

        for h in host:
            game_world.add_object(h, 1)
            game_world.add_collision_pair('isaac:host', None, h)
            game_world.add_collision_pair('host:tear', h, None)

        common.isaac.y = 175

    # Stage_2 -> Stage_1 (돌아갈 때)
    if common.isaac.y < 125 and stage_index == 2:
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
            for h in host:
                try:
                    game_world.remove_object(h)
                except Exception:
                    pass
        except ValueError:
            pass
        stage = Stage_1()
        game_world.add_object(stage, 0)
        stage_index = 1
        common.isaac.y = 700

    # Stage_2 -> Stage_3 (진입)
    if common.isaac.y > 750 and stage_index == 2:
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
            for h in host:
                try:
                    game_world.remove_object(h)
                except Exception:
                    pass
        except ValueError:
            pass

        stage = Stage_3()
        game_world.add_object(stage, 0)
        stage_index = 3
        common.isaac.y = 175

        # Sucker 6마리 생성 및 등록(클래스 메서드 사용)
        suckers = Sucker.spawn_many(4, depth=1)

    # Stage_3 -> Stage_2 (이탈 시 sucker 안전 제거)
    if common.isaac.y < 125 and stage_index == 3:
        _remove_projectiles()
        try:
            game_world.remove_object(stage)
        except ValueError:
            pass

        # Sucker들에게 제거 책임을 맡기고 리스트 초기화
        for s in list(suckers):
            try:
                s.destroy()
            except Exception:
                pass
        suckers = []

        stage = Stage_2()
        game_world.add_object(stage, 0)
        stage_index = 2
        for h in host:
            game_world.add_object(h, 1)
            game_world.add_collision_pair('isaac:host', None, h)
            game_world.add_collision_pair('host:tear', h, None)

    if common.isaac.hp <= 0:
        _remove_projectiles()
        game_world.clear()
        stage_index = 1
        stage = Stage_1()
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    # 모든 객체 정리
    for s in list(suckers):
        try:
            s.destroy()
        except Exception:
            pass
    game_world.clear()

def pause(): pass
def resume(): pass
