---
title: Mathematics of General Relativity (WIP)
description: understand General Relativity and its mathematical tools
pubDate: 1970-01-01
tags: [science]
draft: false
---

## 1. What is General Relativity
Special Relativity (1905) merged space and time into a single four-dimensional spacetime. General Relativity, published by Einstein in 1915, goes one step further: spacetime is not a fixed stage but a curved geometry, shaped by the energy and matter within it. In this picture gravity is not a pulling force. A freely falling object is simply following the straightest possible path through curved spacetime, called a geodesic, in the same way an object in empty space moves in a straight line at constant speed when nothing acts on it.

John Wheeler summarized the two halves of the theory in one sentence: spacetime tells matter how to move, and matter tells spacetime how to curve.

## 2. Spacetime, worldline and proper time

### 2.1 Spacetime
Similar to how we define a position in one-dimension vector via $x$, two-dimension plane surface via $(x,y)$ and three-dimension space via $(x,y,z)$, we label an event in spacetime as four numbers $(x, y, z, t)$. This is merely a coordinate and doesn't have any physical meaning yet. For simplicity, we use $(\vec{x},t)$ in the following discussion.

### 2.2 Worldline
An object's entire history, where it was at every instant, traces out a curve in spacetime. This curve is its worldline. We build coordinate system to describe the worldline, but the curve itself exists independently of coordinates, only its description changes.

### 2.3 Lorentz transformation
After the definition of spacetime event $e = (\vec{x}, t)$ and worldline, we can develop our first important formula: the Lorentz transformation. It reveals the relation of two inertial coordinates $(\vec{x}, t)$ and $(\vec{x^{\prime}}, t^{\prime})$. We assume
- Relativity: physics looks the same in any inertial frame. Changing your velocity does not change the laws.
- Isotropy: physics looks the same in any direction. Rotating your apparatus does not change the laws. In particular $+x$ and $−x$ are equivalent, just opposite direction.
- Homogeneity: physics looks the same at any place or time. Translating your apparatus does not change the laws.
- Light speed. Light travels at a constant speed $c$ in every inertial frame.

#### 2.3.0 the setup
Two inertial frames $S$ and $S^{\prime}$. $S^{\prime}$ moves along the x axis of S with velocity v. The origins coincide at $t = t^{\prime} = 0$. An event has coordinates $(x, t)$ in S and $(x', t')$ in S'. The goal is to find the functions
$$
x^{\prime} = f(x, t)
\\
t^{\prime} = g(x, t)
$$

#### 2.3.1 transformation is linear
We want to express $(\vec{x^{\prime}}, t^{\prime})$ in terms of $(\vec{x}, t)$. Suppose
$$
\begin{aligned}
x^{\prime} = f(x, t)
\end{aligned} \tag{1}
$$
Suppose two pairs of events $(e_1, e_2)$ and $(e_3, e_4)$ have the same separation $(\delta{x}, \delta{t})$ in $S$,
$$
\begin{aligned}
(\delta{x}, \delta{t}) = e_2 - e_1 = e_4 - e_3
\end{aligned} \tag{2}
$$
then described by a different frame, $(e^{\prime}_1, e^{\prime}_2)$ and $(e^{\prime}_3, e^{\prime}_4)$ will still have the same separation $(\delta{x^{\prime}}, \delta{t^{\prime}})$ in $S^{\prime}$,
$$
\begin{aligned}
(\delta{x^{\prime}}, \delta{t^{\prime}}) = e^{\prime}_2 - e^{\prime}_1 = e^{\prime}_4 - e^{\prime}_3
\end{aligned} \tag{3}
$$

A concrete example, at certain time we measure the start and end of the segment. Measuring start of the segment will be our first spacetime coordinate $e_1$, measuring end segment will be our second spacetime coordinate $e_2$. Later we measure the same segment and get $e_3$ and $e_4$. Obviously the physical meaning of separation here in $S$ is the length of segment, so $(e_1, e_2)$ and $(e_3, e_4)$ has the same separation.

In S' the same four events are no longer simultaneous in pairs, so $(\delta{x'}, \delta{t'})$ is not the length of the segment. But by homogeneity the segment's history does not depend on where or when it sits, so $S'$ must still assign the same separation to $(e^{\prime}_1, e^{\prime}_2)$ as to $(e^{\prime}_3, e^{\prime}_4)$.

Suppose
$$
\begin{aligned}
e_1 = (x,t), \qquad e_2 = (x + a, t + b)
\\
e_3 = (y, s), \qquad e_4 = (y + a, s + b)
\end{aligned} \tag{4}
$$
Only considering the first component and combining (1), (3), (4), we have
$$
\begin{aligned}
f(y+a, s+b) - f(y, s) = f(x+a, t+b) - f(x,t)
\end{aligned} \tag{5}
$$
Equation (5) is profound, it means the separation of two points only relies on $(a,b)$, irrelevant from the variable from $f$. Thus
$$
\begin{aligned}
f(x+a, t+b) = f(x,t) + h(a, b)
\end{aligned} \tag{6}
$$
Taking partial derivative of $x$ from both sides of (6),
$$
\begin{aligned}
\frac{\partial f}{\partial x}(x+a, t+b) = \frac{\partial f}{\partial x}(x, t)
\end{aligned} \tag{7}
$$
(6) is true for any choice of $(a, b)$, meaning $\frac{\partial f}{\partial x}$ is independent of $(x, t)$, $f$ is a linear function of x. Same derivation applied for t, so we can rewrite (1) to be
$$
\begin{aligned}
x^{\prime} = f(x, t) = A\cdot x + B \cdot t + E_1
\\
t^{\prime} = C\cdot x + D \cdot t + E_2
\end{aligned} \tag{8}
$$
The event $(x, t) = (0, 0)$ is where the origins coincide, and by convention that event is also $(x^{\prime}, t^{\prime}) = (0, 0)$. This gives $E_1 = E_2 = 0$. The transformation is
$$
\begin{aligned}
x^{\prime} = A\cdot x + B \cdot t
\\
t^{\prime} = C\cdot x + D \cdot t
\end{aligned} \tag{9}
$$
In other words, for two inertial systems, their coordinate transformation is just a linear transformation.

#### 2.3.2 compute the linear coefficients
We want to rewrite (9) as
$$
\begin{aligned}
x^{\prime} = A_v\cdot x + B_v \cdot t
\\
t^{\prime} = C_v\cdot x + D_{v} \cdot t
\end{aligned} \tag{10}
$$
Although the coefficients are constant w.r.t. $x$ and $t$, it is indeed a function of $v$;

**Step 1. Motion of the $S^{\prime}$**  The origin of $S^{\prime}$ is the worldline $x^{\prime} = 0$. Seen from $S$ it moves at velocity $v$, so it is the worldline $x = vt$. Substituting into the first line of (10),
$$
\begin{aligned}
0 = A_v \cdot vt + B_v \cdot t \quad \Rightarrow \quad B_v = -A_{v}v
\end{aligned} \tag{11}
$$
so
$$
\begin{aligned}
x^{\prime} = A_v(x - vt)
\end{aligned} \tag{12}
$$

**Step 2. The inverse transformation**
In 2.3.0, $S'$ moves along the x axis of S with velocity v. Equivalently, from the perspective of $S'$, $S$ moves at the opposite direction but with same speed $-v$. Given isotropy + relativity assumption, describing $(x,t)$ via $(x',t')$ shall follow the same equation of (12), just be replacing $v$ with $-v$
$$
\begin{aligned}
x = A_{-v}(x' + vt')
\end{aligned} \tag{13}
$$

Against from isotropy assumption, if we flip the direction of x axis, athough the speed is oppsite in $S$ and $S'$, the relation from (12),(13) still holds
$$
\begin{aligned}
-x^{\prime} = A_{-v}(-x + vt) \Rightarrow x^{\prime} = A_{-v}(x - vt)
\end{aligned} \tag{14}
$$

Comparing (12) and (14)
$$
\begin{aligned}
A_v = A_{-v}
\end{aligned} \tag{15}
$$
so we can rewrite (13) as
$$
\begin{aligned}
x = A_{v}(x' + vt')
\end{aligned} \tag{16}
$$

**Step 3. A light bulb**. Send a light pulse from the common origin at $t = t^{\prime} = 0$, by our light speed assumption, $x' = c \cdot t'$ and $x = c \cdot t$. Replacing $x'$ and $x$ in (12) and (16),
$$
\begin{aligned}
ct^{\prime} = A_v(ct - vt)
\\
ct = A_{v}(ct' + vt')
\end{aligned} \tag{17}
$$

Multiply the two equation in (17),
$$
\begin{aligned}
c^2tt^{\prime} = {A_v}^2 \cdot tt' (c^2 - v^2)
\end{aligned} \tag{18}
$$
which is equavalent to
$$
\begin{aligned}
\gamma \equiv A_v = \frac{1}{\sqrt{1 - v^2/c^2}}
\end{aligned} \tag{19}
$$

Now resolve $C$ and $D$, rewriting (16) as
$$
\begin{aligned}
t' = \frac{1}{v} \cdot (\frac{x}{\gamma} - x')
\end{aligned} \tag{20}
$$
Using (12) to substitute $x'$ in (20)
$$
\begin{aligned}
t' = \frac{1}{v} \cdot (\frac{x}{\gamma} - \gamma(x - vt)) = \frac{1}{v}(\frac{1}{\gamma} - \gamma)\cdot x + \gamma \cdot t = C \cdot x + D \cdot t
\end{aligned} \tag{21}
$$
Which finally solves into
$$
\begin{aligned}
A = \gamma
\\
B = -\gamma v
\\
C = -\gamma v / c^2
\\
D = \gamma
\end{aligned} \tag{22}
$$
And also it has a equivalent form as
$$
\begin{aligned}
x &= \gamma\,(x^{\prime} + vt^{\prime})
\\
t &= \gamma\left(t^{\prime} + \frac{v}{c^2}x^{\prime}\right)
\end{aligned} \tag{23}
$$

### 2.4 Time dilation
Take a clock at rest in $S^{\prime}$ at its origin $x^{\prime} = 0$. It ticks at $t^{\prime} = 0$ and again at $t^{\prime} = \tau$:
$$
\begin{aligned}
e_1^{\prime} = (0, 0), \qquad e_2^{\prime} = (0, \tau)
\end{aligned} \tag{24}
$$

Substituting $x^{\prime} = 0$ into the second line of (23), the two ticks occur in $S$ at $t = 0$ and $t = \gamma\tau$, so
$$
\begin{aligned}
\Delta t = \gamma\,\Delta\tau, \qquad \gamma = \frac{1}{\sqrt{1 - v^2/c^2}} \ge 1
\end{aligned} \tag{25}
$$
$S$ measures a longer interval than the clock itself by the factor $\gamma$. Now we know time is relative w.r.t the observer.

### 2.5 Spacetime interval and proper time
Time is relative, so different observers disagree on the interval between two events. But there is one quantity built from $(\Delta x, \Delta t)$ that every inertial observer agrees on. Take two events separated by $(\Delta x, \Delta t)$ in $S$ and $(\Delta x', \Delta t')$ in $S'$. Using (22),
$$
\begin{aligned}
c^2\Delta t'^2 - \Delta x'^2
&= \gamma^2\left[\left(c\Delta t - \frac{v}{c}\Delta x\right)^2 - (\Delta x - v\Delta t)^2\right]
\\
&= \gamma^2\left[c^2\Delta t^2\left(1 - \frac{v^2}{c^2}\right) - \Delta x^2\left(1 - \frac{v^2}{c^2}\right)\right]
\\
&= c^2\Delta t^2 - \Delta x^2
\end{aligned} \tag{26}
$$
So the combination $c^2\Delta t^2 - \Delta x^2$ is the same in every inertial frame. It is called the **spacetime interval**.

Now apply this to the clock of 2.4. In its own frame the two ticks have $\Delta x' = 0$ and $\Delta t' = \tau$, so the interval is $c^2\tau^2$. By (26) every other frame computes the same number:
$$
\begin{aligned}
c^2\tau^2 = c^2\Delta t^2 - \Delta x^2
\end{aligned} \tag{27}
$$
Resolve for $\tau$
$$
\begin{aligned}
\tau = \Delta t\sqrt{1 - \frac{\Delta x^2}{c^2\Delta t^2}} = \Delta t\sqrt{1 - \frac{v^2}{c^2}} = \frac{\Delta t}{\gamma}
\end{aligned} \tag{28}
$$
which recovers (25). This is the **proper time** $\tau$ between two events on an object's worldline: the time read by a clock carried along that worldline. $\tau$ is invariant in the sense that whatever frame you use, the $\Delta t$ you measure and the $\gamma$ for the clock's speed in your frame always divide to the same number.

For a worldline that is not straight, apply (27) to each infinitesimal step and add them up:
$$
\begin{aligned}
d\tau = \sqrt{dt^2 - \frac{dx^2}{c^2}}, \qquad \tau = \int d\tau
\end{aligned} \tag{29}
$$

This is the form that survives into general relativity, where the expression under the square root becomes the metric. Based on our initial assumption of inertial system, this metric is called Minkowski Metric, which describes a flat spacetime. This metric is mostly commonly used since vast majority of our space is empty, thus no distortion around its spacetime. At the very last section, lets look closer at (27) and derive couple of conclusions.

### 2.6 Conclusion 1: we all move at speed of light
We rewrite (27) in infinitesimal step
$$
\begin{aligned}
c^2\,d\tau^2 = c^2\,dt^2 - dx^2
\end{aligned} \tag{30}
$$
Divide both sides by $dt^2$ and rearrange:
$$
\begin{aligned}
c^2 \left(\frac{d\tau}{dt}\right)^2 + \left(\frac{dx}{dt}\right)^2 = c^2
\end{aligned} \tag{31}
$$

Here $t$ and $x$ are the coordinates of an inertial frame S, and $\tau$ is the proper time of the object. The first' term measures how fast the object's own time advances compared with the time of S, and the second how fast it advances through space of S.

In other words, giving object some speed w.r.t a coordinate just redistributes how it advances between time and space. Using ourselves as the coordinate $S$, then for light whose $\frac{dx}{dt} = c$, its proper time ratio is 0, meaning light can experience the whole life of universe instantly, although we feel the universe lasts billions of years.


## 3. Geodesics and Christoffel Symbols

## 4. Metric Tensor

## 5. Curvature of the spacetime

## 6. Energy fluxes and Einstein Equation

## 7. Practical problems and Simulation of Sagittarius A*
