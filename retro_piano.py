import curses
import os
import math
import wave
import struct
import time

KEYS_WHITE = {'a': 261.63, 's': 293.66, 'd': 329.63, 'f': 349.23, 'g': 392.00, 'h': 440.00, 'j': 493.88, 'k': 523.25}
KEYS_BLACK = {'w': 277.18, 'e': 311.13, 't': 369.99, 'y': 415.30, 'u': 466.16}
NOTE_NAMES = {
    'a': 'C4', 'w': 'C#4', 's': 'D4', 'e': 'D#4', 'd': 'E4', 
    'f': 'F4', 't': 'F#4', 'g': 'G4', 'y': 'G#4', 'h': 'A4', 'u': 'A#4', 'j': 'B4', 'k': 'C5'
}

last_played_time = {}
COOLDOWN_TIME = 0.22 

def generate_and_play_piano_tone(frequency, duration=1.2):
    # Generates a rich, resonant tone simulating a physical piano string strike
    sample_rate = 44100
    file_path = "/tmp/piano_note.wav"
    
    num_samples = int(sample_rate * duration)
    wave_file = wave.open(file_path, 'w')
    wave_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
    
    for i in range(num_samples):
        t = i / sample_rate
        
        # 1. Fundamental frequency wave
        fundamental = math.sin(2.0 * math.pi * frequency * t)
        
        # 2. Rich Overtones (Harmonics that give a physical acoustic piano its warm tone)
        harmonic2 = 0.5 * math.sin(2.0 * math.pi * (frequency * 2) * t)
        harmonic3 = 0.25 * math.sin(2.0 * math.pi * (frequency * 3) * t)
        harmonic4 = 0.12 * math.sin(2.0 * math.pi * (frequency * 4) * t)
        
        combined_wave = fundamental + harmonic2 + harmonic3 + harmonic4
        
        # 3. Acoustic ADSR Envelope (Sharp attack spike followed by a slow, natural fade)
        if t < 0.03:  # Sharp, crisp hammer strike (first 30ms)
            envelope = t / 0.03
        else:         # Smooth acoustic decay trailing off over 1.2 seconds
            envelope = math.exp(-2.5 * (t - 0.03) / (duration - 0.03))
            
        value = int(16000.0 * combined_wave * envelope)
        
        # Clipping protection
        value = max(-32767, min(32767, value))
        
        data = struct.pack('<h', value)
        wave_file.writeframesraw(data)
        
    wave_file.close()
    os.system(f"afplay {file_path} &")

def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    
    stdscr.addstr("=== WORKSPACE ACOUSTIC PIANO ===\n", curses.A_BOLD)
    stdscr.addstr(" Black Keys:   [W] [E]     [T] [Y] [U]\n")
    stdscr.addstr("               C#  D#      F#  G#  A#\n")
    stdscr.addstr(" White Keys: [A] [S] [D] [F] [G] [H] [J] [K]\n")
    stdscr.addstr("              C   D   E   F   G   A   B   C\n\n")
    stdscr.addstr("-> Keyboard ready. Press 'Q' to slide back to terminal.\n")
    stdscr.refresh()

    while True:
        try:
            key = stdscr.getkey().lower()
        except:
            continue
            
        if key == 'q':
            break
            
        freq = None
        if key in KEYS_WHITE:
            freq = KEYS_WHITE[key]
        elif key in KEYS_BLACK:
            freq = KEYS_BLACK[key]
            
        if freq:
            current_time = time.time()
            if key in last_played_time and (current_time - last_played_time[key]) < COOLDOWN_TIME:
                continue
                
            last_played_time[key] = current_time
            generate_and_play_piano_tone(freq)
            stdscr.addstr(8, 0, f" Current Note: {NOTE_NAMES[key]} ({int(freq)} Hz)             ")
            stdscr.refresh()

if __name__ == '__main__':
    curses.wrapper(main)

