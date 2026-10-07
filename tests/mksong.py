# A 30 s "guide vocal" style melody (Twinkle-like, public domain) with vibrato, as a test MP3 track.
import numpy as np, wave
sr=44100; bpm=100; beat=60/bpm
mel=[(60,1),(60,1),(67,1),(67,1),(69,1),(69,1),(67,2),(65,1),(65,1),(64,1),(64,1),(62,1),(62,1),(60,2),
     (67,1),(67,1),(65,1),(65,1),(64,1),(64,1),(62,2),(67,1),(67,1),(65,1),(65,1),(64,1),(64,1),(62,2)]
t=0.5; x=np.zeros(int(32*sr))
for m,d in mel:
    dur=d*beat*0.92; n=int(dur*sr); tt=np.arange(n)/sr
    f=440*2**((m-69)/12)*2**(0.25*np.sin(2*np.pi*5.5*tt)*np.minimum(1,tt/0.3)/12)
    ph=2*np.pi*np.cumsum(f)/sr; env=np.minimum(1,np.minimum(tt/0.04,(dur-tt)/0.06))
    s=int(t*sr); x[s:s+n]+=0.25*env*(np.sin(ph)+0.5*np.sin(2*ph)+0.25*np.sin(3*ph)); t+=d*beat
x=x[:int((t+1)*sr)]
w=wave.open('song.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes());w.close()
print(round(t+1,1))
