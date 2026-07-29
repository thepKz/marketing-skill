import math,sys
sys.path.insert(0,'.')
from lib import *
print("=== HSL lies: same HSL L=50%, S=100% ===")
for nm,h in [('yellow hsl(60)','#FFFF00'),('green hsl(120)','#00FF00'),('cyan hsl(180)','#00FFFF'),('red hsl(0)','#FF0000'),('blue hsl(240)','#0000FF'),('magenta hsl(300)','#FF00FF')]:
    L,C,H=hex2oklch(h)
    print("%-16s %s relY=%.4f OkL=%.4f OkC=%.4f OkH=%.1f WCAGvsWhite=%.2f APCA blk-on=%.1f"%(nm,h,Y(h),L,C,H,wcag(h,'#FFFFFF'),apca('#000000',h)))
print("\n=== Constant OkL=0.75, k=0.95*Cmax, 6 hues ===")
for hh in [25,85,145,205,265,325]:
    cm=maxC(0.75,hh); hx,_=oklch2hex(0.75,cm*0.95,hh)
    print("H=%3d Cmax=%.4f %s relY=%.4f WCAG/blk=%.2f WCAG/wht=%.2f APCA blk-on=%.1f"%(hh,cm,hx,Y(hx),wcag(hx,'#000000'),wcag(hx,'#FFFFFF'),apca('#000000',hx)))
P3=[[0.4865709486,0.2656676932,0.1982172852],[0.2289745641,0.6917385218,0.0792869141],[0.0,0.0451133819,1.0439443689]]
P3i=inv3(P3)
def oklch2p3(L,C,Hh):
    a=C*math.cos(math.radians(Hh)); b=C*math.sin(math.radians(Hh))
    lms=[x**3 for x in mv(M2i,[L,a,b])]; rl=mv(P3i,mv(M1i,lms))
    return rl, all(-1e-4<=x<=1+1e-4 for x in rl)
def maxC_p3(L,Hh,hi=0.5):
    lo=0.0
    for _ in range(60):
        mid=(lo+hi)/2
        if oklch2p3(L,mid,Hh)[1]: lo=mid
        else: hi=mid
    return lo
print("\n=== sRGB vs Display P3 max OkLCh chroma ===")
for Ls in [0.50,0.577,0.65,0.75]:
    row=[]
    for hh in [22.31,85.0,145.0,245.0]:
        a=maxC(Ls,hh); b=maxC_p3(Ls,hh); row.append("H%5.1f s%.4f p%.4f %+5.1f%%"%(hh,a,b,100*(b/a-1)))
    print("L=%.3f  "%Ls+" | ".join(row))
print("\n=== Gamut failure: P3 red at L=0.60 H=25 ===")
L0,H0=0.60,25.0
Cp=maxC_p3(L0,H0)*0.98; Cs=maxC(L0,H0)
a=Cp*math.cos(math.radians(H0)); b=Cp*math.sin(math.radians(H0))
rl=oklab2lin([L0,a,b]); clip=[max(0.0,min(1.0,x)) for x in rl]
hx_clip=rgb2hex(l2s(clip[0]),l2s(clip[1]),l2s(clip[2]))
Lc,Cc,Hc=hex2oklch(hx_clip)
hx_red,_=oklch2hex(L0,Cs*0.995,H0)
Lr,Cr,Hr=hex2oklch(hx_red)
print("target oklch(%.3f %.4f %.1f) C_P3max=%.4f  C_sRGBmax=%.4f  unclipped linear sRGB=%s"%(L0,Cp,H0,maxC_p3(L0,H0),Cs,["%.4f"%x for x in rl]))
print("naive clip  -> %s  L=%.4f C=%.4f H=%.2f  (dL=%+.4f dH=%+.2f)"%(hx_clip,Lc,Cc,Hc,Lc-L0,Hc-H0))
print("chroma red. -> %s  L=%.4f C=%.4f H=%.2f  (dL=%+.4f dH=%+.2f)"%(hx_red,Lr,Cr,Hr,Lr-L0,Hr-H0))
def lab_d65(h):
    r,g,b=hex2rgb(h); X,Yy,Z=mv(M_XYZ,[s2l(r),s2l(g),s2l(b)])
    Xn,Yn,Zn=0.95047,1.0,1.08883
    def f(t): return t**(1/3) if t>216/24389 else (841/108)*t+4/29
    fx,fy,fz=f(X/Xn),f(Yy/Yn),f(Z/Zn)
    return (116*fy-16,500*(fx-fy),200*(fy-fz))
def de2000(h1,h2):
    L1,a1,b1=lab_d65(h1); L2,a2,b2=lab_d65(h2)
    C1=math.hypot(a1,b1); C2=math.hypot(a2,b2); Cb=(C1+C2)/2
    G=0.5*(1-math.sqrt(Cb**7/(Cb**7+25**7))) if Cb>0 else 0.5
    a1p,a2p=(1+G)*a1,(1+G)*a2
    C1p,C2p=math.hypot(a1p,b1),math.hypot(a2p,b2)
    h1p=math.degrees(math.atan2(b1,a1p))%360; h2p=math.degrees(math.atan2(b2,a2p))%360
    dLp=L2-L1; dCp=C2p-C1p
    if C1p*C2p==0: dhp=0
    else:
        dh=h2p-h1p; dhp=dh if abs(dh)<=180 else (dh-360 if dh>180 else dh+360)
    dHp=2*math.sqrt(C1p*C2p)*math.sin(math.radians(dhp/2))
    Lbp=(L1+L2)/2; Cbp=(C1p+C2p)/2
    if C1p*C2p==0: hbp=h1p+h2p
    elif abs(h1p-h2p)<=180: hbp=(h1p+h2p)/2
    elif h1p+h2p<360: hbp=(h1p+h2p+360)/2
    else: hbp=(h1p+h2p-360)/2
    T=1-0.17*math.cos(math.radians(hbp-30))+0.24*math.cos(math.radians(2*hbp))+0.32*math.cos(math.radians(3*hbp+6))-0.20*math.cos(math.radians(4*hbp-63))
    dth=30*math.exp(-((hbp-275)/25)**2)
    Rc=2*math.sqrt(Cbp**7/(Cbp**7+25**7))
    Sl=1+(0.015*(Lbp-50)**2)/math.sqrt(20+(Lbp-50)**2); Sc=1+0.045*Cbp; Sh=1+0.015*Cbp*T
    Rt=-Rc*math.sin(math.radians(2*dth))
    return math.sqrt((dLp/Sl)**2+(dCp/Sc)**2+(dHp/Sh)**2+Rt*(dCp/Sc)*(dHp/Sh))
print("\ndE00 clip vs chroma-reduced = %.2f"%de2000(hx_clip,hx_red))
print("dE00 #C8102E vs #E20032 = %.2f ; vs #D92B3C = %.2f"%(de2000('#C8102E','#E20032'),de2000('#C8102E','#D92B3C')))
print("Lab(D65) #C8102E =",["%.2f"%x for x in lab_d65('#C8102E')])
print("\n=== Skin patches ===")
for nm,h in [('very light','#F5D5BC'),('light','#F1C9A5'),('mid-light','#D9A066'),('mid','#C68642'),('deep','#7C4A2D'),('very deep','#4A2E20')]:
    L,a,b=lab_d65(h); hab=math.degrees(math.atan2(b,a))%360; Cc=math.hypot(a,b)
    Lo,Co,Ho=hex2oklch(h)
    print("%-11s %s Lab %.1f/%.1f/%.1f C*=%.1f hab=%.1f | OkLCh %.3f/%.4f/%.1f"%(nm,h,L,a,b,Cc,hab,Lo,Co,Ho))
