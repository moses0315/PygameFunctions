import sdl2
import sdl2.ext

# SDL 초기화
sdl2.ext.init()

# DPI 스케일링 설정
sdl2.SDL_SetHint(sdl2.SDL_HINT_VIDEO_HIGHDPI_DISABLED, b"0")

# 창 생성
window = sdl2.ext.Window("SDL2 DPI Scaling", size=(800, 600))
window.show()

# 메인 루프
running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False

    window.refresh()

# SDL 종료
sdl2.ext.quit()
