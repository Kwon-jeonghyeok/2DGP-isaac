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
from stage_4 import Stage_4
from charger import Charger
import common

#isaac = None
stage = None
host = None
sucker = None
chargers = None
stage_index = 1
stage_2_instance = None
stage_3_instance = None
stage_4_instance = None
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
    global isaac, stage, stage_index, host, sucker, stage_3_instance, chargers, stage_2_instance, stage_4_instance

    stage = Stage_1()
    common.stage = stage
    game_world.add_object(stage, 0)

    host = [Host() for i in range(3)]
    sucker = [Sucker() for _ in range(4)]
    common.isaac = Isaac()
    game_world.add_object(common.isaac, 2)
    stage_index = 1
    stage_3_instance = Stage_3()
    stage_2_instance = Stage_2()
    stage_4_instance = Stage_4()

    chargers = [Charger() for _ in range(2)]

    game_world.add_collision_pair('isaac:host', common.isaac, None)
    game_world.add_collision_pair('isaac:sucker', common.isaac, None)
    game_world.add_collision_pair('isaac:charger', common.isaac, None)
    game_world.add_collision_pair('isaac:coin', common.isaac, None)


def _remove_projectiles():
    for layer in list(game_world.world):
        for o in list(layer):
            if o is None:
                continue
            name = o.__class__.__name__
            if name in ('tear', 'HostBullet'):
                try:
                    game_world.remove_object(o)
                except Exception:
                    pass

def update():
    global stage, stage_index, isaac, host, sucker, stage_3_instance, chargers , stage_2_instance, stage_4_instance

    if common.isaac is None or stage is None:
        return

    game_world.update()
    # 스테이지 클리어 조건 검사 테스트용으로 주석처리
    # if stage_index == 2:
    #     # Host가 모두 죽으면 클리어
    #     alive_host = [h for h in host if h.hp > 0]
    #     if len(alive_host) == 0:
    #         stage.is_cleared = True
    #     else:
    #         stage.is_cleared = False
    # elif stage_index == 3:
    #     # Sucker와 Charger가 모두 죽으면 클리어
    #     alive_sucker = [s for s in sucker if s.hp > 0]
    #     alive_charger = [c for c in chargers if c.hp > 0]
    #     if len(alive_sucker) == 0 and len(alive_charger) == 0:
    #         stage.is_cleared = True
    #     else:
    #         stage.is_cleared = False
    # elif stage_index == 1:
    #     # 스테이지 1은 몬스터가 없으므로 항상 클리어
    #     stage.is_cleared = True

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
        stage = stage_2_instance
        common.stage = stage
        game_world.add_object(stage, 0)
        if hasattr(stage, 'ensure_obstacles'):
            stage.ensure_obstacles()
        stage_index = 2
        host = [h for h in host if h.hp > 0]
        for h in host:
            # 돌, 똥이 이미 깔려 있으므로 이를 인식해서 안전한 곳으로 감
            h.set_safe_position()
            game_world.add_object(h, 1)
            game_world.add_collision_pair('isaac:host', None, h)
            game_world.add_collision_pair('host:tear', h, None)
        common.isaac.y = 175

    # Stage_2 -> Stage_1 (돌아갈 때)
    if common.isaac.y < 125 and stage_index == 2:
        _remove_projectiles()
        try:
            if hasattr(stage, 'clear_obstacles'):
                stage.clear_obstacles()
            game_world.remove_object(stage)
            for h in host:
                try:
                    game_world.remove_object(h)
                except Exception:
                    pass
        except ValueError:
            pass
        stage = Stage_1()
        common.stage = stage
        game_world.add_object(stage, 0)
        stage_index = 1
        common.isaac.y = 700

    # Stage_2 -> Stage_3 (진입)
    if common.isaac.y > 750 and stage_index == 2:
        _remove_projectiles()
        try:
            if hasattr(stage, 'clear_obstacles'):
                stage.clear_obstacles()
            game_world.remove_object(stage)
            for h in host:
                try:
                    game_world.remove_object(h)
                except Exception:
                    pass
        except ValueError:
            pass

        stage = stage_3_instance
        common.stage = stage
        if hasattr(stage, 'ensure_obstacles'):
            stage.ensure_obstacles()
        game_world.add_object(stage, 0)
        stage_index = 3
        common.isaac.y = 175
        for s in list(sucker):
            # 죽은 애는 리스트에서 제거
            if s.hp <= 0:
                try:
                    sucker.remove(s)
                except ValueError:
                    pass
                continue
            # 살아 있는 애는 HP 리셋 후 다시 추가
            s.hp = 2
            try:
                game_world.add_object(s, 1)
                game_world.add_collision_pair('isaac:sucker', None, s)
                game_world.add_collision_pair('sucker:tear', s, None)
            except Exception:
                pass
        if chargers:
            for c in list(chargers):
                if getattr(c, 'hp', 1) <= 0:
                    try:
                        chargers.remove(c)
                    except ValueError:
                        pass
                    continue
                try:
                    game_world.add_object(c, 1)
                    # isaac 충돌 그룹과 charger:tear 등록
                    if common.isaac is not None:
                        game_world.add_collision_pair('isaac:charger', common.isaac, c)
                    else:
                        game_world.add_collision_pair('isaac:charger', None, c)
                    game_world.add_collision_pair('charger:tear', c, None)
                except Exception:
                    pass
    # Stage_3 -> Stage_2 (이탈 시 sucker 안전 제거)
    if common.isaac.y < 125 and stage_index == 3:
        _remove_projectiles()
        try:
            try:
                if hasattr(stage, 'clear_obstacles'):
                    stage.clear_obstacles()
            except Exception:
                pass

            game_world.remove_object(stage)
            for s in sucker:
                try:
                    game_world.remove_object(s)
                except Exception:
                    pass

            for c in chargers:
                try:
                    game_world.remove_object(c)
                except Exception:
                    pass
        except ValueError:
            pass


        stage = stage_2_instance
        common.stage = stage
        game_world.add_object(stage, 0)

        if hasattr(stage, 'ensure_obstacles'):
            stage.ensure_obstacles()
        stage_index = 2
        common.isaac.y = 700

        host = [h for h in host if h.hp > 0]
        for h in host:
            h.set_safe_position()
            game_world.add_object(h, 1)
            game_world.add_collision_pair('isaac:host', None, h)
            game_world.add_collision_pair('host:tear', h, None)

    if common.isaac.x > 1450 and stage_index == 3 and stage.is_cleared:
        _remove_projectiles()
        try:
            if hasattr(stage, 'clear_obstacles'): stage.clear_obstacles()
            game_world.remove_object(stage)
            # Stage 3 몬스터 제거 로직 (sucker, charger)
            for s in sucker:
                try:
                    game_world.remove_object(s)
                except:
                    pass
            for c in chargers:
                try:
                    game_world.remove_object(c)
                except:
                    pass
        except ValueError:
            pass

        stage = stage_4_instance
        common.stage = stage

        game_world.add_object(stage, 0)
        if hasattr(stage, 'ensure_obstacles'):
            stage.ensure_obstacles()

        stage_index = 4
        # Stage 4(상점)의 왼쪽 문 앞(150, 400)으로 아이작 이동
        common.isaac.x = 150
        common.isaac.y = 400

        #Stage_4 -> Stage_3 (왼쪽 문으로 복귀 시)
    if common.isaac.x < 125 and stage_index == 4:
        _remove_projectiles()
        try:
            if hasattr(stage, 'clear_obstacles'): stage.clear_obstacles()
            game_world.remove_object(stage)
            # Stage 4에는 몬스터가 없으므로 몬스터 제거 로직 불필요 (하지만 머신은 clear_obstacles에서 제거됨)
        except ValueError:
            pass

        stage = stage_3_instance
        common.stage = stage

        game_world.add_object(stage, 0)
        if hasattr(stage, 'ensure_obstacles'):
            stage.ensure_obstacles()

        stage_index = 3
        # Stage 3의 오른쪽 문 앞(1400, 440)으로 아이작 이동
        common.isaac.x = 1400
        common.isaac.y = 440

        # Stage 3 몬스터 복구 (죽은 애 빼고)
        for s in list(sucker):
            if s.hp > 0:
                game_world.add_object(s, 1)
                game_world.add_collision_pair('isaac:sucker', None, s)
                game_world.add_collision_pair('sucker:tear', s, None)
        for c in list(chargers):
            if c.hp > 0:
                game_world.add_object(c, 1)
                if common.isaac: game_world.add_collision_pair('isaac:charger', common.isaac, c)
                game_world.add_collision_pair('charger:tear', c, None)
    if common.isaac.hp <= 0:
        _remove_projectiles()
        game_world.clear()
        stage_index = 1
        stage = Stage_1()
        common.stage = stage
        game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    # 모든 객체 정리
    for s in list(sucker):
        try:
            s.destroy()
        except Exception:
            pass
    for c in list(chargers):
        try:
            c.destroy()
        except Exception:
            pass
    game_world.clear()

def pause(): pass
def resume(): pass
