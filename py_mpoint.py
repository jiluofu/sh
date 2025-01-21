import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

# Constants for motion
start_point_A = -10  # Starting position of A
start_point_B = 20   # Starting position of B
speed_A = 4          # Speed of A moving right
speed_B = 3          # Speed of B moving left

start_point_P = -10
start_point_Q = 20
speed_P = 4
speed_Q = -6

# Calculate meeting time and position
meeting_time = (start_point_B - start_point_A) / (speed_A + speed_B)
meeting_position = start_point_A + speed_A * meeting_time

# Setup the animation figure
fig, ax = plt.subplots()
ax.set_xlim((start_point_A - 5, start_point_B + 5))
ax.set_ylim((0, 2))
ax.set_title("A and B Moving Towards Each Other")
ax.set_xlabel("Position")
ax.set_ylabel("Trajectory")

# Initialize the points for A and B
point_A, = ax.plot([], [], 'ro', label='Point A')  # 'ro' means red dot
point_B, = ax.plot([], [], 'bo', label='Point B')  # 'bo' means blue dot
ax.legend()

# Update function for animation
def update(frame):
    t = frame / 10  # Time in seconds
    if t <= meeting_time:
        x_A = start_point_A + speed_A * t
        x_B = start_point_B - speed_B * t
    else:
        x_A = x_B = meeting_position  # Both stop at the meeting point

    # Update positions as lists
    point_A.set_data([x_A], [1])
    point_B.set_data([x_B], [1])
    return point_A, point_B

# Update function for animation
def update1(frame):

    t = frame / 10  # Time in seconds
    turing_time = (start_point_B - start_point_A) / speed_P
    
    # P到B点后，速度变为1.5倍，向负方向运动
    if t > turing_time:
        x_P = start_point_Q + -1.5 * speed_P * (t - turing_time)
    else:
        x_P = start_point_P + speed_P * t

    Q_Change_Speed_Time = (start_point_Q - start_point_P) / (speed_P - speed_Q)
    
    if t >= Q_Change_Speed_Time:
        x_Q = start_point_Q + speed_Q * Q_Change_Speed_Time + 0.5 * speed_Q * (t - Q_Change_Speed_Time)
    else:
        x_Q = start_point_Q + speed_Q * t


    # Update positions as lists
    point_A.set_data([x_P], [1])
    point_B.set_data([x_Q], [1])
    return point_A, point_B

# Generate the animation
# frames = int(meeting_time * 10) + 10  # Extra frames to pause at the meeting point
frames = int(10 * 10) + 10  # Extra frames to pause at the meeting point
ani = FuncAnimation(fig, update1, frames=frames, blit=False, repeat=False)

# Save the animation as an MP4
mp4_path = "AB_meeting_motion.mp4"
ani.save(mp4_path, writer=FFMpegWriter(fps=10))

print(f"Animation saved as '{mp4_path}'")

# import matplotlib.pyplot as plt
# from matplotlib.animation import FuncAnimation
# import time

# # 初始化绘图区域
# fig, ax = plt.subplots()
# ax.set_xlim(0, 10)
# ax.set_ylim(0, 1)

# # 初始化点
# point, = ax.plot([], [], 'ro')

# # 控制暂停的参数
# pause = False  # 是否暂停
# pause_frame = 50  # 暂停的帧数
# pause_duration = 2  # 暂停时长（秒）

# # 更新时间
# last_pause_time = 0  # 上一次暂停的时间戳

# def update(frame):
#     global pause, last_pause_time

#     # 检查是否需要暂停
#     if pause and (time.time() - last_pause_time < pause_duration):
#         return point,  # 在暂停期间，不更新动画

#     # 暂停结束后，恢复动画
#     if pause:
#         pause = False  # 恢复正常状态
#         return point,

#     # 正常更新动画逻辑
#     x = frame / 10
#     y = 0.5
#     point.set_data([x], [y])

#     # 到指定帧暂停
#     if frame == pause_frame:
#         pause = True
#         last_pause_time = time.time()  # 记录暂停开始的时间

#     return point,

# # 创建动画
# ani = FuncAnimation(fig, update, frames=100, blit=True, repeat=False)

# # 显示动画
# plt.show()