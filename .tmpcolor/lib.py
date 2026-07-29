import math
def s2l(c):
    c=c/255.0
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def l2s(c):
    c=max(0.0,min(1.0,c))
    return c*12.92 if c<=0.0031308 else 1.055*(c**(1/2.4))-0.055
def hex2rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def rgb2hex(r,g,b):
    f=lambda x:max(0,min(255,int(round(x*255))))
    return '#%02X%02X%02X'%(f(r),f(g),f(b))
M_XYZ=[[0.4123907993,0.3575843394,0.1804807884],[0.2126390059,0.7151686788,0.0721923154],[0.0193308187,0.1191947798,0.9505321522]]
M_XYZinv=[[3.2409699419,-1.5373831776,-0.4986107603],[-0.9692436363,1.8759675015,0.0415550574],[0.0556300797,-0.2039769589,1.0569715142]]
M1=[[0.8189330101,0.3618667424,-0.1288597137],[0.0329845436,0.9293118715,0.0361456387],[0.0482003018,0.2643662691,0.6338517070]]
M2=[[0.2104542553,0.7936177850,-0.0040720468],[1.9779984951,-2.4285922050,0.4505937099],[0.0259040371,0.7827717662,-0.8086757660]]
def mv(M,v): return [sum(M[i][j]*v[j] for j in range(3)) for i in range(3)]
def inv3(M):
    a,b,c=M[0]; d,e,f=M[1]; g,h,i=M[2]
    det=a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)
    return [[(e*i-f*h)/det,(c*h-b*i)/det,(b*f-c*e)/det],[(f*g-d*i)/det,(a*i-c*g)/det,(c*d-a*f)/det],[(d*h-e*g)/det,(b*g-a*h)/det,(a*e-b*d)/det]]
M1i=inv3(M1); M2i=inv3(M2)
def lin2oklab(rgbl):
    lms=mv(M1,mv(M_XYZ,rgbl))
    lms=[math.copysign(abs(x)**(1/3),x) for x in lms]
    return mv(M2,lms)
def oklab2lin(lab):
    lms=[x**3 for x in mv(M2i,lab)]
    return mv(M_XYZinv,mv(M1i,lms))
def hex2oklch(h):
    r,g,b=hex2rgb(h); L,a,bb=lin2oklab([s2l(r),s2l(g),s2l(b)])
    return L,math.hypot(a,bb),math.degrees(math.atan2(bb,a))%360
def oklch2hex(L,C,H):
    a=C*math.cos(math.radians(H)); b=C*math.sin(math.radians(H))
    rl=oklab2lin([L,a,b]); ins=all(-1e-4<=x<=1+1e-4 for x in rl)
    return rgb2hex(l2s(rl[0]),l2s(rl[1]),l2s(rl[2])), ins
def maxC(L,H,hi=0.5):
    lo=0.0
    for _ in range(60):
        mid=(lo+hi)/2
        if oklch2hex(L,mid,H)[1]: lo=mid
        else: hi=mid
    return lo
def Y(h):
    r,g,b=hex2rgb(h); return 0.2126*s2l(r)+0.7152*s2l(g)+0.0722*s2l(b)
def wcag(h1,h2):
    a,b=Y(h1),Y(h2)
    if a<b: a,b=b,a
    return (a+0.05)/(b+0.05)
def apca_Ys(h):
    r,g,b=hex2rgb(h)
    return 0.2126729*(r/255)**2.4+0.7151522*(g/255)**2.4+0.0721750*(b/255)**2.4
def apca(txt,bg):
    Ytx=apca_Ys(txt); Ybg=apca_Ys(bg); bt,bc=0.022,1.414
    Ytx = Ytx if Ytx>bt else Ytx+(bt-Ytx)**bc
    Ybg = Ybg if Ybg>bt else Ybg+(bt-Ybg)**bc
    if abs(Ybg-Ytx)<0.0005: return 0.0
    if Ybg>Ytx:
        S=(Ybg**0.56-Ytx**0.57)*1.14; return 0.0 if S<0.1 else (S-0.027)*100
    S=(Ybg**0.65-Ytx**0.62)*1.14; return 0.0 if S>-0.1 else (S+0.027)*100
