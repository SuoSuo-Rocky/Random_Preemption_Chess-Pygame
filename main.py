




import random
import sys

# 导入pygame 及常量库
import pygame
from pygame import freetype
from pygame.locals import *
from pygame_widgets import Button


class Ele_Sprite(pygame.sprite.Sprite):
    """ 自定义精灵类 """

    def __init__(self, img_file, *args, **kwargs):
        """ 精灵初始化 """
        super(Ele_Sprite, self).__init__()
        combi = None
        if isinstance(img_file, str):  # 图片文件名
            self.image = pygame.image.load(img_file)
        elif isinstance(img_file, (list, tuple)):                          # Surface 对象的 大小
            self.image = pygame.Surface(img_file, pygame.SRCALPHA, 32) # 透明图像
            # self.image = pygame.Surface(img_file)
        else:  # Font 对象
            assert isinstance(img_file, freetype.Font)
            assert isinstance(args[0], str) # 必须要有文本
            # 表示前景色
            if len(args) >= 2 and isinstance(args[1], (list, tuple, pygame.Color)):
                # 表示背景色
                if len(args) >=  3 and isinstance(args[2], (list, tuple, pygame.Color)):
                    combi = img_file.render(*args, **kwargs)
                else:
                    combi = img_file.render(args[0], args[1], **kwargs)
            else:
                combi = img_file.render(args[0], **kwargs)
        if combi:
            self.image, self.rect = combi
        else:
            self.rect = self.image.get_rect()
        self.orig_image = self.image
        self.orig_rec = self.rect
        self.is_move = True


    def draw(self, screen, angle = 0):
        """ 绘制精灵 """
        self.rotate(angle)
        screen.blit(self.image, self.rect)

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, angle)
        if angle != 0:
            wid = int(self.orig_rec.w * 1.6)
            hei = int(self.orig_rec.h * 1.6)
            self.image = pygame.transform.scale(self.image, (wid, hei))
        # self.image = pygame.transform.scale(self.image, (1.2, 1.2))
        self.rect = self.image.get_rect(center=self.rect.center)



class MySprite(pygame.sprite.Sprite):

    dir_dict = {pygame.K_UP: (3, 0, -2), \
                pygame.K_RIGHT: (2, 2, 0), \
                pygame.K_DOWN: (0, 0, 2), \
                pygame.K_LEFT: (1, -2, 0)}

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.master_image = None # 精灵序列图(主图)
        self.image = None        # 帧图 Surface 对象
        self.rect = None         # 帧图 Rect 对象
        self.topleft = 0, 0      # 帧图左上顶点坐标
        self.area = 0            # 精灵序列号
        self.area_width = 1      # 帧图宽
        self.area_height = 1     # 帧图高
        self.first_area = 0      # 动画帧图起始序列号
        self.last_area = 0       # 动画帧图终止序列号
        self.columns = 1         # 精灵序列图列数（每个动画的帧数）
        self.old_area = -1       # 绘制的前一帧图序列号
        self.last_time = 0       # 前一帧图绘制的时间
        self.is_move = False     # 移动开关
        self.vel = pygame.Vector2(0, 0) # 移动速度
        self.old_dir = self.direction
        self.direction = 0           # 移动方向， 代表精灵总图的第几行
        self.auto_move_switch = False # 自动移动开关
        self.current_index = 0   # 在路径列表中的当前下标
        self.step_num = 0        # 移动的方格数
        self.curr_remove_num = 1 # 当前已移动的步数
        self.divide_num = 0      # 记录移动的步数

    def _get_dir(self):
        return (self.first_area, self.last_area)
    def _set_dir(self, direction):
        if direction == self.old_dir:
            return
        self.first_area = direction * self.columns
        self.last_area = self.first_area + self.columns - 1
    # 通过移动方向 控制帧图区间
    direction = property(_get_dir, _set_dir)

    def load_img(self, filename, width, height, columns):
        """加载序列（精灵）图"""
        self.master_image = pygame.image.load(filename).convert_alpha()
        # 帧图宽度
        self.area_width = width
        # 帧图高度
        self.area_height = height
        self.rect = pygame.Rect(0, 0, width, height)
        # 序列图中的帧图列数
        self.columns = columns
        rect = self.master_image.get_rect()
        # 序列图中的终止帧图序号(从0开始)
        self.last_area = (rect.width // width) - 1

    def update(self, current_time, rate=100):
        """更新帧图"""
        # 移动控制
        if not self.is_move:
            self.area = self.first_area = self.last_area
            self.vel = pygame.Vector2(0, 0)
        # 控制动画的绘制速率
        if current_time > self.last_time + rate:
            self.area += 1
            # 帧区间边界判断
            if self.area > self.last_area:
                self.area = self.first_area
            if self.area < self.first_area:
                self.area = self.first_area
            # 记录当前时间
            self.last_time = current_time
        # 只有当帧号发生更改时才更新 self.image
        if self.area != self.old_area:
            area_x = (self.area % self.columns) * self.area_width
            area_y = (self.area // self.columns) * self.area_height
            rect = pygame.Rect(area_x, area_y, self.area_width, self.area_height)
            # 子表面 Surface
            try:
                self.image = self.master_image.subsurface(rect)
            except Exception as e:
                print(e + " \n图片剪裁超出范围........")
            self.old_area = self.area

    def draw(self, screen):
        """绘制帧图"""
        screen.blit(self.image, self.rect)

    def move(self):
        """ 移动 """
        self.rect.move_ip(self.vel)

    def goto(self, x, y):
        """
        :param x: 目标坐标
        :param y: 目标坐标
        """
        self.next_x = x
        self.next_y = y

        # 设置人物面向
        if self.next_x > self.rect.centerx:
            self.direction, self.vel.x, self.vel.y = self.dir_dict[pygame.K_RIGHT]
        elif self.next_x < self.rect.centerx:
            self.direction, self.vel.x, self.vel.y  = self.dir_dict[pygame.K_LEFT]
        if self.next_y > self.rect.bottom:
            self.direction, self.vel.x, self.vel.y  = self.dir_dict[pygame.K_DOWN]
        elif self.next_y < self.rect.bottom:
            self.direction, self.vel.x, self.vel.y  = self.dir_dict[pygame.K_UP]
        self.move()
        self.auto_move_switch = True


    def auto_move(self):
        """ 自动移动 """
        global Dir_li
        if self.auto_move_switch:
            if self.curr_remove_num <= self.step_num:
                curr_pos = self.rect.midbottom
                index = self.current_index + 1
                if index < len(Dir_li):
                    dir = Dir_li[index]
                else:
                    return
                next_pos = pygame.Vector2(curr_pos) + pygame.Vector2(self.dir_dict[dir][1:])
                self.goto(int(next_pos.x), int(next_pos.y))
                if self.divide_num == 30:
                    self.curr_remove_num += 1
                    self.divide_num = 0
                    self.current_index += 1
                self.divide_num += 1
            else:
                self.auto_move_switch = False
                self.is_move = False
                # self.current_index += self.step_num
                self.curr_remove_num = 1
                self.step_num = 0
                if self.current_index < (len(Dir_li) - 1):
                    self.direction = self.dir_dict[Dir_li[self.current_index + 1]][0]

    def charge_succ(self):
        """ 到达终点判断 """
        global is_sample, Dir_li, game_switch, random_switch, winner_obj
        if self.current_index == len(Dir_li) - 1:
            self.auto_move_switch = False
            self.is_move = False
            self.step_num = 0
            game_switch = False
            random_switch = False
            is_sample = False
            winner_obj = self
            print(f'winner_obj = {winner_obj}')
            return True
        return False

    def manual_move(self, keys):
        """ 人为操作  使其  移动  """
        dir = [keys[K_DOWN], keys[K_LEFT], keys[K_RIGHT], \
               keys[K_UP], (0, 2), (-2, 0), (2, 0), (0, -2)]
        if not self.auto_move_switch:
            for k, v in enumerate(dir[0:4]):  # 判断移动方向
                if v:
                    self.direction = k
                    self.vel = pygame.Vector2(dir[k + 4])
                    self.is_move = v
                    self.move()
                    break
            else:                             # 无移动
                self.is_move = False


def get_center_pos(start_pos, dir):
    """ 获取下一方格 中心点坐标 """
    global  remove_dic
    start_vec = pygame.Vector2(start_pos)
    offset_vec = pygame.Vector2(remove_dic[dir])
    end_vec = start_vec + offset_vec
    return int(end_vec.x), int(end_vec.y)


def buttonOnClick(*args):
    return
    global is_sample
    if not is_sample:
        is_sample = True
        return
    is_sample = bool(1 - args[0])


def sample_sieve(obj_li):
    res = random.sample(obj_li, 1)[0]
    return res, res.num


def auto_swing(current_time, ticks = 2000 * 2):
    """ 自动摇筛子 """
    global is_sample, last_time
    if not is_sample:
        is_sample = bool((1 - is_sample))
        last_time = current_time
    if is_sample:
        if current_time > last_time + ticks:
            is_sample = bool((1 - is_sample))


def  charge_game_over():
    """ 游戏结束， 其中一人到达终点 """
    global winner_obj
    if super_man.charge_succ():
        return False
    if shadow_man.charge_succ():
        return False
    else:
        return True


SIZE = WIDTH, HEIGHT = 840, 600    # 窗体的尺寸
FPS = 60                           # 帧率
GRID_SIZE = GRID_W, GRID_H = 60, 60   # 方格的尺寸
START_POS = (750, 510)              # 起始点中心点坐标
IMG_LI =  ("img/start.png", 'img/1.png', 'img/2.png', 'img/3.png', 'img/4.png', \
           'img/5.png', 'img/6.png', 'img/7.png', 'img/8.png', 'img/9.png', \
           'img/10.png', 'img/goal.png')
img_bg = 'img/bg.jpg'
win_img = ("img/win_01.jpg", "img/win_02.jpg")
Dir_li = [K_s, K_LEFT, K_LEFT, K_LEFT, K_LEFT, \
          K_UP, K_UP, K_UP, K_UP, \
          K_LEFT, K_LEFT, K_LEFT, K_LEFT, K_LEFT, K_LEFT, K_LEFT, \
          K_UP, K_UP, K_UP, \
          K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, \
          K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT]
# 方格移动的字典
remove_dic = {K_UP: (0, -GRID_H), K_RIGHT: (GRID_W, 0), \
              K_DOWN: (0, GRID_H), K_LEFT: (-GRID_W, 0)}

pygame.init()
screen = pygame.display.set_mode(SIZE)
scr_rec = screen.get_rect()
pygame.display.set_caption("抢手棋__SuoSuo")
clock = pygame.time.Clock()


grid_sprite_group = pygame.sprite.Group()
# 添加起始方格
start_obj = Ele_Sprite(IMG_LI[0])
start_obj.rect.center = START_POS
grid_sprite_group.add(start_obj)
# 添加中部 方格
for k, dir in enumerate(Dir_li[1:]):
    if k == len(Dir_li) - 2:
        img_file = IMG_LI[-1]
    else:
        img_file = random.sample(IMG_LI[1: len(IMG_LI) - 1], 1)[0]
    obj = Ele_Sprite(img_file)
    obj.rect.center = get_center_pos(grid_sprite_group.sprites()[-1].rect.center, dir)
    grid_sprite_group.add(obj)
# 创建 超级人物
super_man = MySprite()
super_man.load_img("img/super_man.png", 120, 120, 4)
shadow_man = MySprite()
shadow_man.load_img("img/fox.png", 85, 113, 4)

super_man.rect.midbottom = grid_sprite_group.sprites()[0].rect.centerx, \
                            grid_sprite_group.sprites()[0].rect.bottom
shadow_man.rect.midbottom = super_man.rect.midbottom

is_sample = False  # 出牌开关
# 创建按钮
button = Button(screen, 195, 388, 150, 64,  text = "Click", \
                font=pygame.font.Font("font/songti.otf", 40,), fontSize = 30, \
                textColour = pygame.Color('green'), onClick = buttonOnClick,\
                margin = 6, textVAlign = "left", pressedColour = pygame.Color('red'), \
                hoverColour = pygame.Color('blue'), \
                onClickParams = [is_sample, ], )
# button.setImage(image = pygame.image.load("img/button.png").convert_alpha())
# 创建筛子
local_var = locals()
sieve_group = pygame.sprite.Group()
for i in range(1, 7):
    obj = local_var["num_0" + str(i)] = Ele_Sprite("img/" + str(i) * 2 + ".png")
    obj.num = i
    obj.rect.center = 670, 300
    sieve_group.add(obj)
show_obj = sieve_group.sprites()[0]  # 所要显示的筛子对象
swing_num = 0                        # 摇筛子的 次数
random_num = 0                       # 筛子的点数
random_switch = False                # 摇筛子的开关
game_switch = True                   # 游戏的开关
last_time = pygame.time.get_ticks()  # 时间
# 创建字体对象
font = freetype.Font("font/songti.otf", 30, )

bg_obj = Ele_Sprite(img_bg)
divide_num = 0  # 分解移动的步数
angle = 0       # 筛子的旋转角度
winner_obj = None # 记录到达终点者
win_switch =  True   # 绘制 游戏结束 开关
super_man.win_img = Ele_Sprite(win_img[0])
shadow_man.win_img = Ele_Sprite(win_img[1])

running = True
# 主体循环
while running:
    # 1. 清屏
    screen.fill((25, 102, 173))
    ticks = pygame.time.get_ticks()
    # 2. 绘制
    # bg_obj.draw(screen)   # 背景绘制

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]: exit()
    super_man.manual_move(keys)    # 人为移动
    shadow_man.manual_move(keys)

    if random_switch:
        if not super_man.auto_move_switch:
            if swing_num < 2:
                auto_swing(ticks, ticks = 500)
                if not is_sample:
                    if swing_num == 0:
                        super_man.step_num = random_num
                        super_man.auto_move_switch = True
                        super_man.is_move = True
                    else:
                        shadow_man.step_num = random_num
                        shadow_man.auto_move_switch = True
                        shadow_man.is_move = True
                    swing_num += 1
            else:
                random_switch = False
                swing_num = 0
    super_man.auto_move()         # 自动移动
    shadow_man.auto_move()
    running = charge_game_over()   # 判断游戏结束

    grid_sprite_group.draw(screen) # 绘制方格
    super_man.update(ticks, 90)    # 人物更新
    super_man.draw(screen)         # 绘制小人物

    shadow_man.update(ticks, 90)    # 人物更新
    shadow_man.draw(screen)         # 绘制小人物

    button.draw()                   # 绘制按钮
    # 随时准备摇筛子
    if is_sample:
        show_obj, random_num = sample_sieve(sieve_group.sprites())
        if angle == 360:
            angle = 0
        angle += 20
    else:
        angle = 0

    show_obj.draw(screen, angle)      # 绘制筛子


    for event in pygame.event.get():  # 事件索取
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if game_switch:
                if event.key == K_SPACE and event.mod == 0:
                    random_switch = True
            if event.key == K_h:
                super_man.auto_move_switch = True
                super_man.is_move = True
                super_man.step_num = 5

        button.listen(event)    # 监听按钮
    # 3.刷新
    pygame.display.update()
    clock.tick(FPS)

while win_switch:
    if winner_obj == super_man:
        super_man.win_img.draw(screen)
    if winner_obj == shadow_man:
        shadow_man.win_img.draw(screen)

    if pygame.event.wait().type == QUIT or \
            1 in pygame.mouse.get_pressed():
        win_switch = False
    pygame.display.flip()

exit()
pygame.quit()