import numpy as np, wave
sr=48000
# same melody as the sample, sung 5 cents sharp, starting after 0.0s; loop-friendly
notes=[];t=0.6
def add(m,d,gap=0.06):
    global t; notes.append((m,t,d)); t+=d+gap
for m in [60,62,64,65,67]: add(m,0.5)
add(67,1.8); t+=0.5
for m in [67,65,64,62,60]: add(m,0.5)
add(60,1.8); t+=0.5
for m in [64,67,69,67,64]: add(m,0.45)
add(60,1.6)
dur=t+0.8+1.5  # count-in lead 1.5s is before track; fake mic loops so alignment is arbitrary anyway
x=np.zeros(int(dur*sr))
for m,s,d in notes:
    s+=1.5
    n=int(d*sr); tt=np.arange(n)/sr
    f=440*2**((m-69)/12)*2**(5/1200)*2**(0.2*np.sin(2*np.pi*5*tt)/12)
    ph=2*np.pi*np.cumsum(f)/sr
    env=np.minimum(1,np.minimum(tt/0.03,(d-tt)/0.04))
    x[int(s*sr):int(s*sr)+n]+=0.3*env*(np.sin(ph)+0.4*np.sin(2*ph)+0.2*np.sin(3*ph))
x+=np.random.randn(len(x))*0.001
w=wave.open('voice.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
w.writeframes((np.clip(x,-1,1)*32767).astype('<i2').tobytes());w.close()
print(dur)
