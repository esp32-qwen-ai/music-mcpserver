from fastmcp import FastMCP
import os
import subprocess

MUSIC_DIR = "C:\\Users\\caft\\Desktop\\mp3"
PLAYER_PATH = r"C:\Program Files\DAUM\PotPlayer\PotPlayerMini64.exe"
playing_handler = [None, None]

mcp = FastMCP(name="CalculatorServer")

@mcp.tool()
def add(a: int, b: int) -> int:
    """add two integer numbers together."""
    return a + b

@mcp.tool()
def list_music() -> int:
    """
    获取音乐目录下的所有音频文件列表（不包含子目录中的文件），当要搜索歌曲时很有用。

    该方法用于检索 MUSIC_DIR 指定路径下的所有非目录项（即文件），
    可用于前端展示或查询可用的音乐资源。

    返回:
        dict: 包含音乐目录路径和文件列表的字典，结构如下：
            {
                "path": "C:\\Users\\caft\\Desktop\\mp3",  # 音乐文件所在目录
                "playlist": ["song1.mp3", "song2.mp3", ...]  # 文件名列表
            }

    注意:
        - 不会递归搜索子目录。
        - 只返回文件名，不包含完整路径。
    """

    playlist = []
    for item in os.listdir(MUSIC_DIR):
        if os.path.isdir(item):
            continue
        playlist.append(item)
    return {"path": MUSIC_DIR, "playlist": playlist}

@mcp.tool()
def play_music(name: str) -> str:
    """
    播放指定歌曲，要播放歌曲时很有用。

    参数:
        name (str): 带歌曲类型后缀的歌曲全名称（如 `青花.mp3`）

    返回:
        str: 播放状态信息。
    """

    global playing_handler

    if playing_handler[1]:
        playing_handler[1].terminate()
        # 等待几秒钟确认进程已结束，如果未结束则强制杀死进程
        try:
            playing_handler[1].wait(timeout=2)  # 等待进程结束，最多等2秒
        except subprocess.TimeoutExpired:
            playing_handler[1].kill()  # 如果进程没有正常结束，则强制杀死

    msg = ""
    for item in os.listdir(MUSIC_DIR):
        if os.path.isdir(item):
            continue
        if name in item and name != item:
            msg = f"自动补全歌名！已自动将 {name} 修改为 {item}"
            name = item
            break
    else:
        raise ValueError(f"未找到歌曲 {name}")

    playing_handler[0] = name
    playing_handler[1] = subprocess.Popen([PLAYER_PATH, os.path.join(MUSIC_DIR, name)])

    return f"{msg} 正在播放 {name}"

@mcp.tool()
def stop_music() -> str:
    """
    停止正在播放的歌曲。

    返回:
        str: 被停止歌曲的信息。
    """

    if playing_handler[1]:
        playing_handler[1].terminate()
        # 等待几秒钟确认进程已结束，如果未结束则强制杀死进程
        try:
            playing_handler[1].wait(timeout=2)  # 等待进程结束，最多等2秒
        except subprocess.TimeoutExpired:
            playing_handler[1].kill()  # 如果进程没有正常结束，则强制杀死
        return f"停止播放 {playing_handler[0]}"
    else:
        return "没有在播放任何音乐"

@mcp.tool()
def query_playing_music() -> str:
    """
    查询正在播放的歌曲信息。

    返回:
        str: 正在播放的歌曲信息。
    """

    if playing_handler[1]:
        return f"正在播放 {playing_handler[0]}"
    else:
        return "没有在播放任何音乐"

if __name__ == "__main__":
    mcp.run(transport = "sse", host = "0.0.0.0", port = 8000)
