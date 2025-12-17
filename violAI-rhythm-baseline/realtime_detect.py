import os
import time
import threading
import numpy as np
import pygame
import verovio
import sounddevice as sd
import pretty_midi
import crepe
from io import BytesIO
from music21 import converter, tempo, note
from music21.musicxml.m21ToXml import GeneralObjectExporter
import subprocess

# ======== [1] 樂譜載入與音符時間計算 ========
score = converter.parse("Four_Seasons_Spring_I_Violin.mxl")
if not list(score.recurse().getElementsByClass(tempo.MetronomeMark)):
    score.insert(0, tempo.MetronomeMark(number=120))
bpm = score.recurse().getElementsByClass(tempo.MetronomeMark).first().number
notes = list(score.flatten().notes)
target_notes = []
for i, n in enumerate(notes):
    start = n.offset / bpm * 60
    end = start + n.quarterLength / bpm * 60
    pitch = int(n.pitch.midi)
    name = n.pitch.nameWithOctave
    target_notes.append({'start': start, 'end': end, 'pitch': pitch, 'note_name': name, 'id': f"n{i}"})
    n.editorial.id = f"n{i}"

detection_status = {note['id']: None for note in target_notes}

# ======== [2] 音高偵測背景執行緒 ========
SAMPLE_RATE = 16000
FRAME_DURATION = 0.05
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION)
AMPLITUDE_THRESHOLD = 0.01

def detection_loop(get_start_time):
    while True:
        audio = sd.rec(FRAME_SIZE, samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()
        if np.max(np.abs(audio)) < AMPLITUDE_THRESHOLD:
            continue
        _, freq, conf, _ = crepe.predict(audio, SAMPLE_RATE, viterbi=True)
        midi_number = pretty_midi.hz_to_note_number(freq[0])
        t = time.time() - get_start_time()
        for note in target_notes:
            if note["start"] <= t <= note["end"]:
                if detection_status[note["id"]] is None:
                    correct = abs(midi_number - note["pitch"]) <= 0.5
                    detection_status[note["id"]] = correct
                    symbol = "✅" if correct else "❌"
                    print(f"[{symbol}] t={t:.2f}s | Expected: {note['note_name']}, Got: {pretty_midi.note_number_to_name(midi_number)}")
                break

# ======== [3] Verovio + Pygame 初始化 ========
tk = verovio.toolkit()
tk.setOptions({"scale": 40, "adjustPageHeight": True})
exporter = GeneralObjectExporter()
pygame.init()
pygame.mixer.init()
screen_width, screen_height = 1200, 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Real-time Score Display")

# ======== [4] 播放 MIDI 並啟動時間基準 ========
midi_path = "temp.mid"
score.write("midi", fp=midi_path)
pygame.mixer.music.load(midi_path)
start_time = time.time()
#pygame.mixer.music.play()

# 啟動偵測執行緒
threading.Thread(target=detection_loop, args=(lambda: start_time,), daemon=True).start()

# ======== [5] 每幀渲染並顯示 ========
running = True
while running:
    now = time.time() - start_time  # ✅ 改為真實時間

    for n in notes:
        n.style.color = None
    for note in target_notes:
        match_note = next((n for n in notes if n.editorial.id == note["id"]), None)
        if not match_note:
            continue

        if now > note["end"] and detection_status[note["id"]] is None:
            detection_status[note["id"]] = False  # 錯過未演奏視為錯誤

        # 染色邏輯
        if detection_status[note["id"]] is False:
            match_note.style.color = "#d64848"
        elif note["start"] <= now <= note["end"] and detection_status[note["id"]] is True:
            match_note.style.color = "#6ca6d6"

    xml = exporter.parse(score).decode("utf-8")
    tk.loadData(xml)
    svg = tk.renderToSVG(1)

    proc = subprocess.Popen(["rsvg-convert", "-f", "png"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    png_bytes, _ = proc.communicate(svg.encode("utf-8"))
    image = pygame.image.load(BytesIO(png_bytes)).convert_alpha()
    image_width, image_height = image.get_size()

    screen.fill((255, 255, 255))
    scale = min(screen_width / image_width, screen_height / image_height)
    new_size = (int(image_width * scale), int(image_height * scale))
    image = pygame.transform.smoothscale(image, new_size)
    x = (screen_width - new_size[0]) // 2
    y = (screen_height - new_size[1]) // 2
    screen.blit(image, (x, y))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
print("✅ 播放完成")