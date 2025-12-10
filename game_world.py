world = [[], [], []] # layers for game objects

camera = {'x':0.0, 'y':0.0, 'w':1000, 'h':800}

def world_to_screen(x, y):
    return x - camera['x'], y - camera['y']

def screen_to_world(sx,sy):
    return sx + camera['x'], sy + camera['y']

def set_viewport(w, h):
    camera['w'] = float(w)
    camera['h'] = float(h)

def add_object(o, depth):
    world[depth].append(o)

def add_objects(ol, depth):
    world[depth] += ol

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return

    raise Exception("World 에 존재하지 않는 오브젝트를 지우려고 시도함")

def clear():

    global world, collision_pairs
    world = [[], [], []]
    collision_pairs.clear()
    camera['x'] = 0.0
    camera['y'] = 0.0
    for layer in world:
        layer.clear()
def update():
    for layer in world:
        for o in layer:
            o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw()



collision_pairs = {}
def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        #print(f'Add new pair: {group}')
        collision_pairs[group] = [[], []]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def handle_collision():
    # collision_pairs의 아이템을 수정 도중 안전하게 순회하기 위해 items()의 복사본 사용
    for group, pairs in list(collision_pairs.items()):
        # 검사할 때 원본 리스트를 직접 순회하지 않고 얕은 복사본을 만듦
        a_candidates = list(pairs[0])
        b_candidates = list(pairs[1])

        for a in a_candidates:
            if a is None:
                continue
            for b in b_candidates:
                if b is None:
                    continue

                # 이미 누군가의 handle_collision에서 제거됐으면 건너뜀
                if a not in pairs[0] or b not in pairs[1]:
                    continue

                try:
                    if collide(a, b):
                        # 먼저 a의 충돌 처리 실행
                        a.handle_collision(group, b)
                        # 만약 b가 a.handle_collision() 안에서 제거되지 않았다면 b의 핸들러 호출
                        if b in pairs[1]:
                            b.handle_collision(group, a)
                except Exception:
                    # 개별 충돌 처리에서 예외가 나와도 전체 루프는 계속되도록 방지
                    continue

# 충돌검사
def collide(a, b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True

# 객체의 충돌정보 삭제
def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            remove_collision_object(o)
            return

    raise ValueError('Cannot delete non existing object')

